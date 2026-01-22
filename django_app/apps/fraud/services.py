import logging
import requests
from typing import Dict, Any, Tuple
from decimal import Decimal
from django.contrib.auth import get_user_model
from .models import CaseNote
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from .models import Transaction, FraudCase, Alert, FraudPattern
from common.constants import AlertSeverity, FraudStatus, TransactionStatus, RiskLevel
from common.exceptions import MLServiceUnavailable, FraudDetectionError
from common.utils import calculate_fraud_score_locally, generate_transaction_reference, get_risk_level_from_score

logger = logging.getLogger(__name__)

class FraudDetectionService:
    """Core fraud detection service that orchestrates ML scoring and rule-based checks."""
    
    def __init__(self):
        self.ml_service_url = settings.FASTAPI_ML_URL
        self.high_threshold = settings.FRAUD_THRESHOLD_HIGH
        self.medium_threshold = settings.FRAUD_THRESHOLD_MEDIUM
    
    def process_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        """
        Main entry point for transaction fraud detection.
        
        Steps:
        1. Create transaction record
        2. Get ML fraud score
        3. Apply rule-based checks
        4. Generate alerts if needed
        5. Update transaction status
        """
        try:
            with transaction.atomic():
                # Create transaction
                txn = self._create_transaction(transaction_data)
                
                # Get fraud score from ML service
                fraud_score = self._get_fraud_score(txn)
                
                # Apply additional rule-based checks
                triggered_rules = self._apply_fraud_rules(txn)
                
                # Update transaction with results
                txn.fraud_score = fraud_score
                txn.risk_level = get_risk_level_from_score(fraud_score)
                txn.processed_at = timezone.now()
                
                # Determine transaction status
                if fraud_score >= self.high_threshold:
                    txn.status = TransactionStatus.REJECTED
                elif fraud_score >= self.medium_threshold:
                    txn.status = TransactionStatus.FLAGGED
                else:
                    txn.status = TransactionStatus.APPROVED
                
                txn.save()
                
                # Generate alerts if suspicious
                if fraud_score >= self.medium_threshold or triggered_rules:
                    self._create_alert(txn, triggered_rules, fraud_score)
                
                logger.info(f"Transaction {txn.reference} processed. Score: {fraud_score}, Status: {txn.status}")
                return txn
                
        except Exception as e:
            logger.error(f"Error processing transaction: {str(e)}")
            raise FraudDetectionError(f"Failed to process transaction: {str(e)}")
    
    def _create_transaction(self, data: Dict[str, Any]) -> Transaction:
        """Create transaction record from input data."""
        reference = data.get('reference') or generate_transaction_reference()
        
        return Transaction.objects.create(
            reference=reference,
            user_id=data['user_id'],
            account_number=data.get('account_number', ''),
            amount=Decimal(str(data['amount'])),
            currency=data.get('currency', 'USD'),
            transaction_type=data.get('transaction_type', 'payment'),
            merchant_id=data.get('merchant_id', ''),
            merchant_name=data.get('merchant_name', ''),
            merchant_category=data.get('merchant_category', ''),
            ip_address=data.get('ip_address'),
            country=data.get('country', ''),
            city=data.get('city', ''),
            device_id=data.get('device_id', ''),
            transaction_date=data.get('transaction_date', timezone.now()),
            ml_features=data.get('ml_features', {})
        )
    
    def _get_fraud_score(self, txn: Transaction) -> float:
        """Get fraud score from ML service with fallback."""
        try:
            # Prepare features for ML model
            features = self._prepare_features(txn)
            
            # Call FastAPI ML service
            response = requests.post(
                f"{self.ml_service_url}/api/v1/score",
                json={"transaction": features},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('fraud_score', 0.0)
            else:
                logger.warning(f"ML service returned status {response.status_code}, using fallback")
                return calculate_fraud_score_locally(features)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"ML service unavailable: {str(e)}, using fallback scoring")
            return calculate_fraud_score_locally(self._prepare_features(txn))
    
    def _prepare_features(self, txn: Transaction) -> Dict[str, Any]:
        """Prepare transaction features for ML model."""
        return {
            'user_id': txn.user_id,
            'amount': float(txn.amount),
            'transaction_type': txn.transaction_type,
            'merchant_category': txn.merchant_category,
            'country': txn.country,
            'city': txn.city,
            'hour': txn.transaction_date.hour,
            'day_of_week': txn.transaction_date.weekday(),
            'device_id': txn.device_id,
            **txn.ml_features
        }
    
    def _apply_fraud_rules(self, txn: Transaction) -> list:
        """Apply rule-based fraud detection checks."""
        triggered_rules = []
        
        # Rule 1: High amount transaction
        if txn.amount > settings.MAX_TRANSACTION_AMOUNT:
            triggered_rules.append({
                'rule': 'high_amount',
                'message': f'Transaction amount {txn.amount} exceeds limit'
            })
        
        # Rule 2: Velocity check - multiple transactions in short time
        recent_txns = Transaction.objects.filter(
            user_id=txn.user_id,
            transaction_date__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        if recent_txns > 10:
            triggered_rules.append({
                'rule': 'high_velocity',
                'message': f'{recent_txns} transactions in last hour'
            })
        
        # Rule 3: Location change detection
        last_txn = Transaction.objects.filter(
            user_id=txn.user_id,
            transaction_date__lt=txn.transaction_date
        ).order_by('-transaction_date').first()
        
        if last_txn and last_txn.country != txn.country:
            time_diff = (txn.transaction_date - last_txn.transaction_date).total_seconds() / 3600
            if time_diff < 2:  # Same user in different country within 2 hours
                triggered_rules.append({
                    'rule': 'location_change',
                    'message': f'Location changed from {last_txn.country} to {txn.country} in {time_diff:.1f} hours'
                })
        
        # Rule 4: Unusual time
        if txn.transaction_date.hour < 6 or txn.transaction_date.hour > 23:
            triggered_rules.append({
                'rule': 'unusual_time',
                'message': f'Transaction at unusual hour: {txn.transaction_date.hour}:00'
            })
        
        # Rule 5: Check against known fraud patterns
        active_patterns = FraudPattern.objects.filter(is_active=True)
        for pattern in active_patterns:
            if self._matches_pattern(txn, pattern):
                triggered_rules.append({
                    'rule': 'pattern_match',
                    'message': f'Matches fraud pattern: {pattern.pattern_name}'
                })
                pattern.detection_count += 1
                pattern.save()
        
        return triggered_rules
    
    def _matches_pattern(self, txn: Transaction, pattern: FraudPattern) -> bool:
        """Check if transaction matches a fraud pattern."""
        conditions = pattern.conditions
        
        # Simple pattern matching (extend based on your needs)
        if 'amount_range' in conditions:
            min_amt, max_amt = conditions['amount_range']
            if not (min_amt <= float(txn.amount) <= max_amt):
                return False
        
        if 'merchant_category' in conditions:
            if txn.merchant_category not in conditions['merchant_category']:
                return False
        
        if 'countries' in conditions:
            if txn.country not in conditions['countries']:
                return False
        
        return True
    
    def _create_alert(self, txn: Transaction, triggered_rules: list, fraud_score: float):
        """Create fraud alert for suspicious transaction."""
        severity = self._determine_severity(fraud_score, triggered_rules)
        
        alert = Alert.objects.create(
            alert_id=f"ALERT-{txn.reference}",
            transaction=txn,
            alert_type='fraud_detection',
            severity=severity,
            message=f"Suspicious transaction detected with fraud score {fraud_score:.2f}",
            triggered_rules=triggered_rules,
            metadata={
                'fraud_score': fraud_score,
                'risk_level': txn.risk_level,
                'amount': str(txn.amount),
                'user_id': txn.user_id
            }
        )
        
        # Auto-create fraud case for high severity alerts
        if severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            self._create_fraud_case(alert)
        
        logger.info(f"Alert {alert.alert_id} created for transaction {txn.reference}")
    
    def _determine_severity(self, fraud_score: float, triggered_rules: list) -> str:
        """Determine alert severity based on score and rules."""
        if fraud_score >= 0.9 or len(triggered_rules) >= 3:
            return AlertSeverity.CRITICAL
        elif fraud_score >= 0.7 or len(triggered_rules) >= 2:
            return AlertSeverity.HIGH
        elif fraud_score >= 0.5:
            return AlertSeverity.MEDIUM
        return AlertSeverity.LOW
    
    def _create_fraud_case(self, alert: Alert):
        """Auto-create fraud case from high-severity alert."""
        txn = alert.transaction
        case_number = f"CASE-{timezone.now().strftime('%Y%m%d')}-{txn.reference[-8:]}"
        
        FraudCase.objects.create(
            case_number=case_number,
            transaction=txn,
            title=f"Suspicious transaction: {txn.reference}",
            description=alert.message,
            status=FraudStatus.PENDING,
            severity=alert.severity,
            estimated_loss=txn.amount,
        )
        
        logger.info(f"Fraud case {case_number} created from alert {alert.alert_id}")

class FraudCaseService:
    """Service for managing fraud case investigations."""
    
    @staticmethod
    def assign_case(case_id: int, user_id: int) -> FraudCase:
        """Assign fraud case to analyst."""
      
        User = get_user_model()
        
        case = FraudCase.objects.get(id=case_id)
        user = User.objects.get(id=user_id)
        
        case.assigned_to = user
        case.status = FraudStatus.INVESTIGATING
        case.save()
        
        logger.info(f"Case {case.case_number} assigned to {user.email}")
        return case
    
    @staticmethod
    def update_case_status(case_id: int, status: str, resolution_notes: str = '') -> FraudCase:
        """Update fraud case status."""
        case = FraudCase.objects.get(id=case_id)
        case.status = status
        
        if resolution_notes:
            case.resolution_notes = resolution_notes
        
        if status == FraudStatus.RESOLVED:
            case.resolved_at = timezone.now()
        
        case.save()
        logger.info(f"Case {case.case_number} status updated to {status}")
        return case
    
    @staticmethod
    def add_case_note(case_id: int, user_id: int, note: str, is_internal: bool = True):
        """Add investigation note to case."""
        
        User = get_user_model()
        
        case = FraudCase.objects.get(id=case_id)
        user = User.objects.get(id=user_id)
        
        case_note = CaseNote.objects.create(
            case=case,
            author=user,
            note=note,
            is_internal=is_internal
        )
        
        return case_note
