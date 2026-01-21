from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import timedelta
import logging
from .models import Transaction, Alert, FraudCase
from .services import FraudDetectionService
from common.constants import AlertSeverity, FraudStatus

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_transaction_async(self, transaction_data: dict):
    """
    Asynchronously process transaction for fraud detection.
    Used for batch processing or when immediate response is not required.
    """
    try:
        service = FraudDetectionService()
        transaction = service.process_transaction(transaction_data)
        
        return {
            'success': True,
            'transaction_id': transaction.id,
            'reference': transaction.reference,
            'fraud_score': transaction.fraud_score,
            'status': transaction.status
        }
    except Exception as e:
        logger.error(f"Task failed for transaction: {str(e)}")
        raise self.retry(exc=e, countdown=60)

@shared_task
def process_pending_alerts():
    """
    Periodic task to process unacknowledged alerts.
    Runs every 5 minutes via Celery Beat.
    """
    pending_alerts = Alert.objects.filter(
        is_acknowledged=False,
        severity__in=[AlertSeverity.HIGH, AlertSeverity.CRITICAL]
    ).order_by('-created_at')[:50]
    
    processed_count = 0
    for alert in pending_alerts:
        try:
            # Check if alert needs escalation
            alert_age = (timezone.now() - alert.created_at).total_seconds() / 60
            
            if alert_age > 30 and not alert.case:  # 30 minutes unhandled
                # Create fraud case
                from .services import FraudDetectionService
                service = FraudDetectionService()
                service._create_fraud_case(alert)
                processed_count += 1
                
        except Exception as e:
            logger.error(f"Error processing alert {alert.alert_id}: {str(e)}")
    
    logger.info(f"Processed {processed_count} pending alerts")
    return {'processed': processed_count}

@shared_task
def generate_daily_fraud_report():
    """
    Generate daily fraud detection report.
    Runs daily at 1 AM via Celery Beat.
    """
    yesterday = timezone.now().date() - timedelta(days=1)
    start_time = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()))
    end_time = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.max.time()))
    
    # Gather statistics
    stats = {
        'date': str(yesterday),
        'total_transactions': Transaction.objects.filter(
            transaction_date__range=(start_time, end_time)
        ).count(),
        'flagged_transactions': Transaction.objects.filter(
            transaction_date__range=(start_time, end_time),
            fraud_score__gte=0.5
        ).count(),
        'total_alerts': Alert.objects.filter(
            created_at__range=(start_time, end_time)
        ).count(),
        'high_severity_alerts': Alert.objects.filter(
            created_at__range=(start_time, end_time),
            severity__in=[AlertSeverity.HIGH, AlertSeverity.CRITICAL]
        ).count(),
        'new_cases': FraudCase.objects.filter(
            created_at__range=(start_time, end_time)
        ).count(),
        'resolved_cases': FraudCase.objects.filter(
            resolved_at__range=(start_time, end_time)
        ).count(),
    }
    
    # Calculate total amounts
    flagged_amount = Transaction.objects.filter(
        transaction_date__range=(start_time, end_time),
        fraud_score__gte=0.5
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    stats['flagged_amount'] = float(flagged_amount)
    
    logger.info(f"Daily fraud report generated: {stats}")
    
    # TODO: Send email report to stakeholders
    # send_fraud_report_email(stats)
    
    return stats

@shared_task
def cleanup_old_transactions():
    """
    Archive or delete old processed transactions.
    Runs weekly via Celery Beat.
    """
    cutoff_date = timezone.now() - timedelta(days=90)
    
    old_transactions = Transaction.objects.filter(
        created_at__lt=cutoff_date,
        status='APPROVED',
        fraud_score__lt=0.3
    )
    
    count = old_transactions.count()
    
    # Archive to separate table or delete (implement based on requirements)
    # For now, just log
    logger.info(f"Found {count} old transactions eligible for cleanup")
    
    return {'eligible_for_cleanup': count}

@shared_task
def bulk_process_transactions(transaction_list: list):
    """
    Bulk process multiple transactions efficiently.
    Useful for batch imports or historical data processing.
    """
    service = FraudDetectionService()
    results = []
    
    for txn_data in transaction_list:
        try:
            txn = service.process_transaction(txn_data)
            results.append({
                'reference': txn.reference,
                'success': True,
                'fraud_score': txn.fraud_score
            })
        except Exception as e:
            results.append({
                'reference': txn_data.get('reference', 'unknown'),
                'success': False,
                'error': str(e)
            })
    
    successful = sum(1 for r in results if r['success'])
    logger.info(f"Bulk processed {successful}/{len(transaction_list)} transactions")
    
    return {
        'total': len(transaction_list),
        'successful': successful,
        'failed': len(transaction_list) - successful,
        'results': results
    }
