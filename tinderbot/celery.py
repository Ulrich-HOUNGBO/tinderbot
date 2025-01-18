import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tinderbot.settings")

app = Celery("tinderbot")

# Set the Redis broker URL
app.conf.broker_url = "redis://redis:6379/0"
app.conf.result_backend = "redis://redis:6379/0"

# Define the Celery beat schedule
app.conf.beat_schedule = {
    "task_swiper": {
        "task": "account.tasks.automate_all_account_process_scheduler",
        "schedule": 60.0,  # Run every 10 seconds
    },
    "task_update_process_day": {
        "task": "account.tasks.automate_update_process_day",
        "schedule": crontab(hour=1, minute=0),  # Run daily at 1:00 AM
    },
    "task_update_bio": {
        "task": "account.tasks.automate_all_account_update_bio",
        "schedule": crontab(hour=10, minute=0),  # Run daily at 10:00 AM
    },
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
