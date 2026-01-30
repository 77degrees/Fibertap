from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "fibertap",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Beat schedule for periodic tasks
    beat_schedule={
        # Run full scan daily at 3 AM UTC
        "daily-full-scan": {
            "task": "app.tasks.scanning.scheduled_full_scan",
            "schedule": crontab(hour=3, minute=0),
        },
        # Run breach scan every 6 hours
        "breach-scan-6h": {
            "task": "app.tasks.scanning.scheduled_breach_scan",
            "schedule": crontab(hour="*/6", minute=0),
        },
        # Sync Incogni status every hour (when implemented)
        "sync-incogni-hourly": {
            "task": "app.tasks.scanning.sync_incogni_status",
            "schedule": crontab(minute=30),
        },
    },
)

# Import tasks to register them
from app.tasks import scanning  # noqa: F401, E402
