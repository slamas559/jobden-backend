# app/core/rate_limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from starlette.responses import JSONResponse
import redis
import os
from app.core.config import settings
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = settings.REDIS_URL or os.getenv("REDIS_URL")

# Initialize Redis client
if REDIS_URL and REDIS_URL.startswith("rediss://"):
    # Upstash Redis (with SSL)
    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True,
        ssl_cert_reqs=None
    )
    storage_uri = REDIS_URL
else:
    # Local Redis (no SSL)
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_RATE_LIMIT_DB,
        decode_responses=True
    )
    storage_uri = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_RATE_LIMIT_DB}"

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
    default_limits=["200 per day", "50 per hour"]
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": str(exc.detail)
        }
    )


# Custom rate limit decorator for specific endpoints
def custom_rate_limit(limit: str):
    """
    Custom rate limit decorator
    
    Usage:
        @custom_rate_limit("5 per minute")
        async def my_endpoint():
            ...
    """
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator