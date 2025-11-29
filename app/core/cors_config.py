# app/core/cors_config.py
import os
from dotenv import load_dotenv
from app.core.config import settings

load_dotenv()

# CORS Configuration
def get_cors_origins():
    """
    Get allowed CORS origins from environment
    
    Returns:
        List of allowed origins
    """
    # Get from environment or use defaults
    origins = settings.BACKEND_CORS_ORIGINS or os.getenv(
        "BACKEND_CORS_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000"
    )

    
    # Split by comma and strip whitespace
    # origins = [origin.strip() for origin in origins_str.split(",")]
    
    # If in development, allow all origins
    if settings.ENVIRONMENT == "development" or os.getenv("ENVIRONMENT", "development") == "development":
        origins.append("http://localhost:*")
    print(origins)
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