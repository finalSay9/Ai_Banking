from django.db import models
from django.conf import settings
from common.constants import RiskLevel

class ITRiskAssessment(models.Model):
    """IT and operational risk assessments."""
    assessment_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    risk_category = models.CharField(max_length=100)  # system, network, data, operational
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices)
    likelihood = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5
    impact = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5
    
    mitigation_plan = models.TextField()
    status = models.CharField(max_length=50, default='OPEN')
    
    assessed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    assessed_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'it_risk_assessments'
        ordering = ['-assessed_at']
    
    def __str__(self):
        return f"{self.assessment_id} - {self.title}"
