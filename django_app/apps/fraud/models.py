from django.db import models
from django.conf import settings
from common.constants import FraudStatus, AlertSeverity, TransactionStatus, RiskLevel
from decimal import Decimal

class Transaction(models.Model):
    """Store all financial transactions for fraud analysis."""
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    user_id = models.CharField(max_length=100, db_index=True)
    account_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Transaction details
    transaction_type = models.CharField(max_length=50)  # transfer, withdrawal, payment
    merchant_id = models.CharField(max_length=100, blank=True)
    merchant_name = models.CharField(max_length=200, blank=True)
    merchant_category = models.CharField(max_length=100, blank=True)
    
    # Location data
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    device_id = models.CharField(max_length=200, blank=True)
    
    # Fraud scoring
    fraud_score = models.FloatField(null=True, blank=True)
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.LOW)
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    
    # ML features (stored as JSON for feature extraction)
    ml_features = models.JSONField(null=True, blank=True)
    
    # Timestamps
    transaction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['user_id', '-transaction_date']),
            models.Index(fields=['status', 'risk_level']),
            models.Index(fields=['fraud_score']),
        ]
    
    def __str__(self):
        return f"{self.reference} - {self.amount} {self.currency}"

class FraudCase(models.Model):
    """Fraud case management and investigation tracking."""
    case_number = models.CharField(max_length=50, unique=True, db_index=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='fraud_cases')
    
    # Case details
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=FraudStatus.choices, default=FraudStatus.PENDING)
    severity = models.CharField(max_length=20, choices=AlertSeverity.choices)
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='assigned_cases'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_cases'
    )
    
    # Investigation
    investigation_notes = models.TextField(blank=True)
    resolution_notes = models.TextField(blank=True)
    estimated_loss = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    actual_loss = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'fraud_cases'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        return f"{self.case_number} - {self.title}"

class Alert(models.Model):
    """Real-time fraud alerts triggered by ML model."""
    alert_id = models.CharField(max_length=100, unique=True, db_index=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='alerts')
    
    alert_type = models.CharField(max_length=100)  # high_amount, velocity, location_change, etc.
    severity = models.CharField(max_length=20, choices=AlertSeverity.choices)
    message = models.TextField()
    
    # Alert details
    triggered_rules = models.JSONField(default=list)  # List of rules that triggered the alert
    metadata = models.JSONField(default=dict)
    
    # Status
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Follow-up
    case = models.ForeignKey(FraudCase, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['severity', '-created_at']),
            models.Index(fields=['is_acknowledged']),
        ]
    
    def __str__(self):
        return f"{self.alert_id} - {self.alert_type}"

class FraudPattern(models.Model):
    """Detected fraud patterns for learning and rule updates."""
    pattern_name = models.CharField(max_length=200)
    pattern_type = models.CharField(max_length=100)  # velocity, amount, location, behavioral
    description = models.TextField()
    
    # Pattern rules
    conditions = models.JSONField()  # Store pattern matching conditions
    threshold = models.FloatField()
    
    # Effectiveness tracking
    detection_count = models.IntegerField(default=0)
    false_positive_count = models.IntegerField(default=0)
    true_positive_count = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fraud_patterns'
        ordering = ['-detection_count']
    
    def __str__(self):
        return self.pattern_name
    
    @property
    def accuracy(self):
        total = self.true_positive_count + self.false_positive_count
        if total == 0:
            return 0.0
        return (self.true_positive_count / total) * 100

class CaseNote(models.Model):
    """Investigation notes and case updates."""
    case = models.ForeignKey(FraudCase, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    note = models.TextField()
    is_internal = models.BooleanField(default=True)  # Internal vs customer-facing
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'case_notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.case.case_number}"
