from celery import Celery
import os
from app.core.config import settings

celery_app = Celery(
    "silence_cutter",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.video_tasks", "app.tasks.user_tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour time limit for tasks
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks to prevent memory leaks
    task_routes={
        'app.tasks.video_tasks.*': {'queue': 'video_processing'},
        'app.tasks.user_tasks.*': {'queue': 'user_tasks'},
    }
)

# Start Celery if this module is executed
if __name__ == "__main__":
    celery_app.start() 