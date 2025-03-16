from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "check_subscription_status": {
        "task": "subscriptions.tasks.check_subscription_status",
        "schedule": crontab(hour='0', minute='0'),  # Runs daily at midnight
    }
}
