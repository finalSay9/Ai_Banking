from django.db import models

class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrator'
    FRAUD_ANALYST = 'FRAUD_ANALYST', 'Fraud Analyst'
    RISK_MANAGER = 'RISK_MANAGER', 'Risk Manager'
    AUDITOR = 'AUDITOR', 'Auditor'
    VIEWER = 'VIEWER', 'Viewer'

class FraudStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Investigation'
    INVESTIGATING = 'INVESTIGATING', 'Under Investigation'
    CONFIRMED = 'CONFIRMED', 'Confirmed Fraud'
    FALSE_POSITIVE = 'FALSE_POSITIVE', 'False Positive'
    RESOLVED = 'RESOLVED', 'Resolved'

class AlertSeverity(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    CRITICAL = 'CRITICAL', 'Critical'

class TransactionStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    FLAGGED = 'FLAGGED', 'Flagged for Review'

class RiskLevel(models.TextChoices):
    LOW = 'LOW', 'Low Risk'
    MEDIUM = 'MEDIUM', 'Medium Risk'
    HIGH = 'HIGH', 'High Risk'
    CRITICAL = 'CRITICAL', 'Critical Risk'
