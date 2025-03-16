import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

celery_app = Celery('backend')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    "send-weekly-report": {
        "task": "subscriptions.tasks.send_subscription_report",
        "schedule": crontab(day_of_week='1', hour='9', minute='0'),  # Every Monday at 9 AM
    },
}

@celery_app.task
def send_expiry_notifications():
    """Send notifications to users before expiry"""
    from subscriptions.tasks import notify_users_about_expiry
    notify_users_about_expiry()