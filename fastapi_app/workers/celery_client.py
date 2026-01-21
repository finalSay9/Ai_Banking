"""
Celery client for FastAPI to trigger Django tasks.
"""

from celery import Celery
from core.config import settings

celery_app = Celery(
    'fastapi_worker',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

def trigger_django_task(task_name: str, *args, **kwargs):
    """Trigger a Django Celery task from FastAPI."""
    return celery_app.send_task(task_name, args=args, kwargs=kwargs)
