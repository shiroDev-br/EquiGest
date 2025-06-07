from celery.app import Celery
from celery.schedules import crontab

from equigest.settings import Settings

settings = Settings()
REDIS_URL = settings.REDIS_URL

celery_app = Celery(
    'equigest', 
    broker=REDIS_URL, 
    backend=REDIS_URL
    )

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    timezone='UTC',
)

celery_app.autodiscover_tasks(["equigest"])

celery_app.conf.beat_schedule: dict = {
    "send-webhook-request": {
        "task": "equigest.tasks.send_webhook_request",
        "schedule": crontab(minute="*/2")
    }
}