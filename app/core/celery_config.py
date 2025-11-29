# app/core/celery_config.py
from celery import Celery
import os
from dotenv import load_dotenv
from app.core.config import settings

load_dotenv()

# Get Redis URL from environment
REDIS_URL = settings.REDIS_URL or settings.CELERY_BROKER_URL or os.getenv("REDIS_URL")

# Celery requires specific format for Upstash (with SSL)
if REDIS_URL and REDIS_URL.startswith("rediss://"):
    # Upstash uses TLS, ensure proper format
    broker_url = REDIS_URL
    result_backend = REDIS_URL
else:
    # Local Redis (no SSL)
    broker_url = settings.CELERY_BROKER_URL or "redis://localhost:6379/0"
    result_backend = settings.CELERY_RESULT_BACKEND or "redis://localhost:6379/0"

print(f"DEBUG: Celery broker = {broker_url[:30]}..." if broker_url else "No broker URL")

# Initialize Celery
celery_app = Celery(
    "jobsearch_tasks",
    broker=broker_url,
    backend=settings.CELERY_RESULT_BACKEND or os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["app.tasks.email_tasks"]  # Import tasks
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,  # Important for free tier
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    # SSL settings for Upstash
    broker_use_ssl={
        'ssl_cert_reqs': None
    } if REDIS_URL and REDIS_URL.startswith("rediss://") else None,
    redis_backend_use_ssl={
        'ssl_cert_reqs': None
    } if REDIS_URL and REDIS_URL.startswith("rediss://") else None,
)


# Optional: Configure periodic tasks (like scheduled emails)
# from celery.schedules import crontab
# celery_app.conf.beat_schedule = {
#     'send-weekly-digest': {
#         'task': 'app.tasks.email_tasks.send_weekly_digest',
#         'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Every Monday at 9 AM
#     },
# }