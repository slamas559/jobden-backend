from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Handle Supabase connection pooler URLs
    if "?pgbouncer=true" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("?pgbouncer=true", "")

print(f"DEBUG: Database URL = {DATABASE_URL[:50]}..." if DATABASE_URL else "No DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    future=True, echo=False, 
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "ssl":ssl_context,
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
