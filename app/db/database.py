# app/db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings
import ssl
import uuid

DATABASE_URL = settings.DATABASE_URL

# Fix Protocol
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Handle SSL
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

print(f"FINAL DATABASE URL: {DATABASE_URL}")
# Create Engine
engine = create_engine(
    DATABASE_URL,
    future=True,
    poolclass=NullPool,
    echo=False,
    # connect_args={
    #     "statement_cache_size": 0, # This is the only place you need it
    #     # "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
    #     "ssl": ssl_context,
    # }
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()