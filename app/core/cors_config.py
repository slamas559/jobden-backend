# app/core/cors_config.py
import os
from dotenv import load_dotenv
from app.core.config import settings

load_dotenv()

# CORS Configuration
def get_cors_origins():
    env_origins = settings.BACKEND_CORS_ORIGINS

    # If Pydantic parsed into AnyHttpUrl list, convert to strings
    if isinstance(env_origins, list):
        origins = [str(origin).rstrip("/") for origin in env_origins]
    else:
        # If string, split by comma
        origins = [o.strip() for o in env_origins.split(",")]

    # Add wildcard localhost only in dev
    if settings.ENVIRONMENT == "development":
        origins.append("http://localhost")

    print("Final Origins:", origins)
    return origins


CORS_CONFIG = {
    "allow_origins": get_cors_origins(),
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    "allow_headers": [
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "User-Agent",
        "DNT",
        "Cache-Control",
        "X-Requested-With"
    ],
    "expose_headers": ["Content-Length", "X-Request-ID"],
    "max_age": 600,  # Cache preflight requests for 10 minutes
}