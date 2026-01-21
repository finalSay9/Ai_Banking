from django.db import models
from django.conf import settings
from apps.fraud.models import FraudCase

class ForensicInvestigation(models.Model):
    """Digital forensics and investigation records."""
    investigation_id = models.CharField(max_length=100, unique=True)
    fraud_case = models.ForeignKey(FraudCase, on_delete=models.CASCADE, related_name='forensic_investigations')
    
    investigation_type = models.CharField(max_length=100)
    findings = models.TextField()
    evidence_collected = models.JSONField(default=list)
    
    investigator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'forensic_investigations'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.investigation_id} - {self.fraud_case.case_number}"
