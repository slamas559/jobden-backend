from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl,Field
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Job Den Backend"
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = Field(default_factory=list)
    REDIS_URL: str | None = None
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # refresh token lifespan
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None
    # SendGrid Configuration
    SENDGRID_API_KEY: str | None = None
    SENDGRID_FROM_EMAIL: str | None = None
    SENDGRID_FROM_NAME: str | None = None
    APP_URL: str | None = None
    APP_NAME: str = "JobDen"
    # Celery Configuration
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None
    # Rate Limiting Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_RATE_LIMIT_DB: int = 1  # Separate DB for rate limiting

    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = []
    
    class Config:
        env_file = ".env"
        @classmethod
        def parse_env_var(cls, field_name: str, raw_value: str):
            # only for BACKEND_CORS_ORIGINS
            if field_name == "BACKEND_CORS_ORIGINS":
                return [x.strip() for x in raw_value.split(",") if x.strip()]
            return raw_value

settings = Settings()
