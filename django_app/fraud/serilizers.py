from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Transaction, FraudCase, Alert, FraudPattern, CaseNote
from apps.users.serializers import UserSerializer

User = get_user_model()

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transaction listing and details."""
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'user_id', 'account_number', 'amount', 'currency',
            'transaction_type', 'merchant_id', 'merchant_name', 'merchant_category',
            'ip_address', 'country', 'city', 'device_id',
            'fraud_score', 'risk_level', 'risk_level_display',
            'status', 'status_display', 'transaction_date', 'created_at', 'processed_at'
        ]
        read_only_fields = ['id', 'reference', 'fraud_score', 'risk_level', 'status', 'processed_at']

class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new transactions."""
    ml_features = serializers.JSONField(required=False, default=dict)
    
    class Meta:
        model = Transaction
        fields = [
            'user_id', 'account_number', 'amount', 'currency',
            'transaction_type', 'merchant_id', 'merchant_name', 'merchant_category',
            'ip_address', 'country', 'city', 'device_id',
            'transaction_date', 'ml_features'
        ]
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value
    
    def validate_user_id(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("User ID is required")
        return value

class TransactionDetailSerializer(TransactionSerializer):
    """Detailed transaction serializer with related data."""
    alerts = serializers.SerializerMethodField()
    fraud_cases = serializers.SerializerMethodField()
    
    class Meta(TransactionSerializer.Meta):
        fields = TransactionSerializer.Meta.fields + ['alerts', 'fraud_cases', 'ml_features']
    
    def get_alerts(self, obj):
        alerts = obj.alerts.all()[:5]
        return AlertSerializer(alerts, many=True).data
    
    def get_fraud_cases(self, obj):
        cases = obj.fraud_cases.all()
        return FraudCaseListSerializer(cases, many=True).data

class AlertSerializer(serializers.ModelSerializer):
    """Serializer for fraud alerts."""
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    transaction_reference = serializers.CharField(source='transaction.reference', read_only=True)
    acknowledged_by_email = serializers.EmailField(source='acknowledged_by.email', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'alert_id', 'transaction', 'transaction_reference',
            'alert_type', 'severity', 'severity_display', 'message',
            'triggered_rules', 'metadata', 'is_acknowledged',
            'acknowledged_by', 'acknowledged_by_email', 'acknowledged_at',
            'case', 'created_at'
        ]
        read_only_fields = ['id', 'alert_id', 'created_at']

class AlertAcknowledgeSerializer(serializers.Serializer):
    """Serializer for acknowledging alerts."""
    notes = serializers.CharField(required=False, allow_blank=True)

class FraudCaseListSerializer(serializers.ModelSerializer):
    """Serializer for fraud case listing."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    transaction_reference = serializers.CharField(source='transaction.reference', read_only=True)
    transaction_amount = serializers.DecimalField(source='transaction.amount', max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = FraudCase
        fields = [
            'id', 'case_number', 'transaction', 'transaction_reference', 'transaction_amount',
            'title', 'status', 'status_display', 'severity', 'severity_display',
            'assigned_to', 'assigned_to_email', 'estimated_loss', 'actual_loss',
            'created_at', 'updated_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'case_number', 'created_at', 'updated_at']

class FraudCaseDetailSerializer(FraudCaseListSerializer):
    """Detailed fraud case serializer."""
    transaction_details = TransactionSerializer(source='transaction', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    alerts = AlertSerializer(many=True, read_only=True)
    notes = serializers.SerializerMethodField()
    
    class Meta(FraudCaseListSerializer.Meta):
        fields = FraudCaseListSerializer.Meta.fields + [
            'description', 'investigation_notes', 'resolution_notes',
            'transaction_details', 'assigned_to_details', 'created_by_details',
            'alerts', 'notes'
        ]
    
    def get_notes(self, obj):
        notes = obj.notes.all()[:10]
        return CaseNoteSerializer(notes, many=True).data

class FraudCaseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating fraud cases."""
    
    class Meta:
        model = FraudCase
        fields = [
            'transaction', 'title', 'description', 'severity', 'estimated_loss'
        ]
    
    def validate_transaction(self, value):
        if FraudCase.objects.filter(transaction=value, status__in=['PENDING', 'INVESTIGATING']).exists():
            raise serializers.ValidationError("An active fraud case already exists for this transaction")
        return value

class FraudCaseUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating fraud cases."""
    
    class Meta:
        model = FraudCase
        fields = [
            'status', 'assigned_to', 'investigation_notes', 
            'resolution_notes', 'actual_loss'
        ]

class CaseNoteSerializer(serializers.ModelSerializer):
    """Serializer for case notes."""
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CaseNote
        fields = ['id', 'case', 'author', 'author_email', 'author_name', 'note', 'is_internal', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']
    
    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.email
        return "Unknown"

class CaseNoteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating case notes."""
    
    class Meta:
        model = CaseNote
        fields = ['note', 'is_internal']

class FraudPatternSerializer(serializers.ModelSerializer):
    """Serializer for fraud patterns."""
    accuracy = serializers.ReadOnlyField()
    
    class Meta:
        model = FraudPattern
        fields = [
            'id', 'pattern_name', 'pattern_type', 'description',
            'conditions', 'threshold', 'detection_count',
            'false_positive_count', 'true_positive_count', 'accuracy',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'detection_count', 'false_positive_count', 'true_positive_count', 'created_at', 'updated_at']

class FraudStatisticsSerializer(serializers.Serializer):
    """Serializer for fraud statistics."""
    total_transactions = serializers.IntegerField()
    flagged_transactions = serializers.IntegerField()
    total_alerts = serializers.IntegerField()
    high_severity_alerts = serializers.IntegerField()
    active_cases = serializers.IntegerField()
    resolved_cases = serializers.IntegerField()
    total_estimated_loss = serializers.DecimalField(max_digits=15, decimal_places=2)
    fraud_rate = serializers.FloatField()
    average_fraud_score = serializers.FloatField()

class BulkTransactionSerializer(serializers.Serializer):
    """Serializer for bulk transaction processing."""
    transactions = TransactionCreateSerializer(many=True)
    
    def validate_transactions(self, value):
        if not value:
            raise serializers.ValidationError("At least one transaction is required")
        if len(value) > 100:
            raise serializers.ValidationError("Maximum 100 transactions allowed per batch")
        return value
