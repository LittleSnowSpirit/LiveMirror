"""Celery 应用配置"""

from celery import Celery
from config import settings

celery_app = Celery(
    "livemirror",
    broker=settings.redis_url if hasattr(settings, 'redis_url') else "redis://localhost:6379/0",
    backend=settings.redis_url if hasattr(settings, 'redis_url') else "redis://localhost:6379/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=60,
    task_max_retries=3,
)

# 自动发现任务模块
celery_app.autodiscover_tasks(["services"])
