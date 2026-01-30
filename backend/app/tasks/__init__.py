from celery import Celery

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
)

# Import tasks to register them
from app.tasks import scanning  # noqa: F401, E402
