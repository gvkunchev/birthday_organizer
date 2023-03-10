import os
from celery import Celery
from celery.schedules import crontab


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'birthday_organizer.settings')


app = Celery('birthday_organizer')


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'create_birthday_event_per_user': {
        'task': 'create_birthday_event_per_user',
        'schedule': crontab(minute=5, hour=0), # Daily at 5 minutes past midnight
    },
    'alert_for_events_without_host': {
        'task': 'alert_for_events_without_host',
        'schedule': crontab(minute=0, hour=0), # Daily at midnight
    },
    'alert_for_new_comments': {
        'task': 'alert_for_new_comments',
        'schedule': crontab(minute=0), # Hourly
    },
    'archive_events': {
        'task': 'archive_events',
        'schedule': crontab(minute=10, hour=0), # Daily at 10 minutes midnight
    }
}
