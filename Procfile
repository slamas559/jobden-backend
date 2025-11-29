web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: celery -A app.core.celery_config.celery_app worker --loglevel=info --pool=solo