import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')

app = Celery('fraud_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'process-pending-alerts': {
        'task': 'apps.fraud.tasks.process_pending_alerts',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'generate-daily-fraud-report': {
        'task': 'apps.fraud.tasks.generate_daily_fraud_report',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    },
    'cleanup-old-transactions': {
        'task': 'apps.fraud.tasks.cleanup_old_transactions',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Weekly
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
