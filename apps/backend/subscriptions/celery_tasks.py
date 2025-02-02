from celery.schedules import crontab
from celery import Celery
from subscriptions.tasks import auto_renew_subscriptions


app = Celery('backend', broker='redis://localhost:6379/0')

app.conf.beat_schedule['send-renewal-reminders-daily'] = {
    'task': 'subscriptions.tasks.send_renewal_reminders',
    'schedule': crontab(hour='6', minute='0'),  # Runs daily at 6 AM
}

app.conf.beat_schedule[''] = {
    'auto-renew-subscriptions-daily': {
        'task': 'subscriptions.tasks.auto_renew_subscriptions',
        'schedule': crontab(hour='0', minute='0'),  # Runs daily at midnight
    },
    'auto-renew-subscriptions-weekly': {
        'task': 'subscriptions.tasks.auto_renew_subscriptions',
        'schedule': crontab(hour='0', minute='0', day_of_week='sunday'),  # Runs weekly on Sunday at midnight
    },
    'auto-renew-subscriptions-monthly': {
        'task': 'subscriptions.tasks.auto_renew_subscriptions',
        'schedule': crontab(hour='0', minute='0', day_of_month='1'),  # Runs monthly on the 1st at midnight
    },
    'auto-renew-subscriptions-yearly': {
        'task': 'subscriptions.tasks.auto_renew_subscriptions',
        'schedule': crontab(hour='0', minute='0', day_of_month='1', month_of_year='1'),  # Runs yearly on January 1st at midnight
    },
}