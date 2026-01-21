from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Transaction, FraudCase, Alert, FraudPattern, CaseNote
from .serializers import (
    TransactionSerializer, TransactionCreateSerializer, TransactionDetailSerializer,
    AlertSerializer, AlertAcknowledgeSerializer,
    FraudCaseListSerializer, FraudCaseDetailSerializer, 
    FraudCaseCreateSerializer, FraudCaseUpdateSerializer,
    CaseNoteSerializer, CaseNoteCreateSerializer,
    FraudPatternSerializer, FraudStatisticsSerializer,
    BulkTransactionSerializer
)
from .services import FraudDetectionService, FraudCaseService
from .tasks import process_transaction_async, bulk_process_transactions
from common.permissions import IsFraudAnalyst, CanManageFraudCases
from common.constants import FraudStatus, AlertSeverity

logger = logging.getLogger(__name__)

class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing transactions and fraud detection.
    
    list: Get all transactions
    create: Submit new transaction for fraud analysis
    retrieve: Get transaction details
    """
    queryset = Transaction.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'risk_level', 'user_id', 'transaction_type']
    search_fields = ['reference', 'user_id', 'account_number']
    ordering_fields = ['transaction_date', 'amount', 'fraud_score', 'created_at']
    ordering = ['-transaction_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer
        elif self.action == 'retrieve':
            return TransactionDetailSerializer
        return TransactionSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Process new transaction through fraud detection system.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Synchronous processing for immediate response
            service = FraudDetectionService()
            transaction = service.process_transaction(serializer.validated_data)
            
            response_serializer = TransactionDetailSerializer(transaction)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error processing transaction: {str(e)}")
            return Response(
                {'error': 'Failed to process transaction', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def submit_async(self, request):
        """
        Submit transaction for asynchronous processing.
        Returns task ID for tracking.
        """
        serializer = TransactionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        task = process_transaction_async.delay(serializer.validated_data)
        
        return Response({
            'task_id': task.id,
            'status': 'processing',
            'message': 'Transaction submitted for processing'
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['post'], permission_classes=[IsFraudAnalyst])
    def bulk_submit(self, request):
        """
        Submit multiple transactions for batch processing.
        """
        serializer = BulkTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        transactions_data = serializer.validated_data['transactions']
        
        task = bulk_process_transactions.delay(transactions_data)
        
        return Response({
            'task_id': task.id,
            'transaction_count': len(transactions_data),
            'status': 'processing',
            'message': f'{len(transactions_data)} transactions submitted for processing'
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get all high-risk transactions."""
        high_risk_txns = self.queryset.filter(
            Q(risk_level='HIGH') | Q(risk_level='CRITICAL')
        ).order_by('-fraud_score')[:50]
        
        serializer = self.get_serializer(high_risk_txns, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def flagged(self, request):
        """Get all flagged transactions pending review."""
        flagged_txns = self.queryset.filter(status='FLAGGED').order_by('-transaction_date')
        
        page = self.paginate_queryset(flagged_txns)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(flagged_txns, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsFraudAnalyst])
    def approve(self, request, pk=None):
        """Manually approve a flagged transaction."""
        transaction = self.get_object()
        transaction.status = 'APPROVED'
        transaction.save()
        
        logger.info(f"Transaction {transaction.reference} approved by {request.user.email}")
        
        serializer = self.get_serializer(transaction)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsFraudAnalyst])
    def reject(self, request, pk=None):
        """Manually reject a flagged transaction."""
        transaction = self.get_object()
        transaction.status = 'REJECTED'
        transaction.save()
        
        logger.info(f"Transaction {transaction.reference} rejected by {request.user.email}")
        
        serializer = self.get_serializer(transaction)
        return Response(serializer.data)

class FraudCaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing fraud cases and investigations.
    """
    queryset = FraudCase.objects.all()
    permission_classes = [IsAuthenticated, CanManageFraudCases]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'severity', 'assigned_to']
    search_fields = ['case_number', 'title', 'transaction__reference']
    ordering_fields = ['created_at', 'updated_at', 'severity']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FraudCaseCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FraudCaseUpdateSerializer
        elif self.action == 'retrieve':
            return FraudCaseDetailSerializer
        return FraudCaseListSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign case to a fraud analyst."""
        case = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            updated_case = FraudCaseService.assign_case(case.id, user_id)
            serializer = FraudCaseDetailSerializer(updated_case)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update case status with optional resolution notes."""
        case = self.get_object()
        new_status = request.data.get('status')
        resolution_notes = request.data.get('resolution_notes', '')
        
        if not new_status:
            return Response({'error': 'status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            updated_case = FraudCaseService.update_case_status(case.id, new_status, resolution_notes)
            serializer = FraudCaseDetailSerializer(updated_case)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """Add investigation note to case."""
        case = self.get_object()
        serializer = CaseNoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        case_note = FraudCaseService.add_case_note(
            case.id,
            request.user.id,
            serializer.validated_data['note'],
            serializer.validated_data.get('is_internal', True)
        )
        
        response_serializer = CaseNoteSerializer(case_note)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def my_cases(self, request):
        """Get cases assigned to current user."""
        my_cases = self.queryset.filter(assigned_to=request.user)
        
        page = self.paginate_queryset(my_cases)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(my_cases, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending cases."""
        pending_cases = self.queryset.filter(status=FraudStatus.PENDING)
        
        page = self.paginate_queryset(pending_cases)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(pending_cases, many=True)
        return Response(serializer.data)

class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and managing fraud alerts.
    """
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['severity', 'is_acknowledged', 'alert_type']
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert."""
        alert = self.get_object()
        
        if alert.is_acknowledged:
            return Response(
                {'error': 'Alert already acknowledged'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.is_acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unacknowledged(self, request):
        """Get all unacknowledged alerts."""
        unack_alerts = self.queryset.filter(is_acknowledged=False).order_by('-severity', '-created_at')
        
        page = self.paginate_queryset(unack_alerts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unack_alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Get critical alerts."""
        critical_alerts = self.queryset.filter(severity=AlertSeverity.CRITICAL).order_by('-created_at')[:20]
        
        serializer = self.get_serializer(critical_alerts, many=True)
        return Response(serializer.data)

class FraudPatternViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing fraud patterns.
    """
    queryset = FraudPattern.objects.all()
    serializer_class = FraudPatternSerializer
    permission_classes = [IsAuthenticated, IsFraudAnalyst]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['pattern_name', 'pattern_type', 'description']
    ordering_fields = ['detection_count', 'accuracy', 'created_at']
    ordering = ['-detection_count']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active fraud patterns."""
        active_patterns = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_patterns, many=True)
        return Response(serializer.data)

class FraudStatisticsViewSet(viewsets.ViewSet):
    """
    ViewSet for fraud detection statistics and dashboards.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get fraud detection dashboard statistics."""
        # Time range filter
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        # Calculate statistics
        total_transactions = Transaction.objects.filter(created_at__gte=start_date).count()
        flagged_transactions = Transaction.objects.filter(
            created_at__gte=start_date,
            fraud_score__gte=0.5
        ).count()
        
        total_alerts = Alert.objects.filter(created_at__gte=start_date).count()
        high_severity_alerts = Alert.objects.filter(
            created_at__gte=start_date,
            severity__in=[AlertSeverity.HIGH, AlertSeverity.CRITICAL]
        ).count()
        
        active_cases = FraudCase.objects.filter(
            status__in=[FraudStatus.PENDING, FraudStatus.INVESTIGATING]
        ).count()
        
        resolved_cases = FraudCase.objects.filter(
            resolved_at__gte=start_date
        ).count()
        
        total_estimated_loss = FraudCase.objects.filter(
            created_at__gte=start_date
        ).aggregate(total=Sum('estimated_loss'))['total'] or 0
        
        fraud_rate = (flagged_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        avg_fraud_score = Transaction.objects.filter(
            created_at__gte=start_date
        ).aggregate(avg=Avg('fraud_score'))['avg'] or 0
        
        stats = {
            'total_transactions': total_transactions,
            'flagged_transactions': flagged_transactions,
            'total_alerts': total_alerts,
            'high_severity_alerts': high_severity_alerts,
            'active_cases': active_cases,
            'resolved_cases': resolved_cases,
            'total_estimated_loss': total_estimated_loss,
            'fraud_rate': round(fraud_rate, 2),
            'average_fraud_score': round(avg_fraud_score, 3)
        }
        
        serializer = FraudStatisticsSerializer(data=stats)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get fraud detection trends over time."""
        days = int(request.query_params.get('days', 30))
        
        daily_stats = []
        for i in range(days):
            date = timezone.now().date() - timedelta(days=i)
            start = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.min.time()))
            end = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.max.time()))
            
            txn_count = Transaction.objects.filter(transaction_date__range=(start, end)).count()
            flagged_count = Transaction.objects.filter(
                transaction_date__range=(start, end),
                fraud_score__gte=0.5
            ).count()
            
            daily_stats.append({
                'date': str(date),
                'total_transactions': txn_count,
                'flagged_transactions': flagged_count,
                'fraud_rate': (flagged_count / txn_count * 100) if txn_count > 0 else 0
            })
        
        return Response({'trends': daily_stats})
