from celery.app import Celery

from equigest.settings import Settings

settings = Settings()

REDIS_URL = settings.REDIS_URL if settings.ENVIRONMENT == 'production' else settings.REDIS_URL_DEV

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