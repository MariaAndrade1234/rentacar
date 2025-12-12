"""
Celery configuration for RentACar project.
Handles asynchronous task processing.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('rentacar')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'check-overdue-rentals': {
        'task': 'rentals.tasks.check_overdue_rentals',
        'schedule': crontab(hour='*/1'),  # Every hour
    },
    'cleanup-expired-tokens': {
        'task': 'authentication.tasks.cleanup_expired_tokens',
        'schedule': crontab(hour='2', minute='0'),  # Daily at 2 AM
    },
    'generate-daily-reports': {
        'task': 'rentals.tasks.generate_daily_reports',
        'schedule': crontab(hour='23', minute='30'),  # Daily at 11:30 PM
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
