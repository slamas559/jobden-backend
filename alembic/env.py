from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from alembic import context
import asyncio
import os
from app.db.database import Base
from app.models.user import User
from app.models.employer_profile import EmployerProfile
from app.models.job_seeker_profile import JobSeekerProfile
from app.models.job import Job
from app.models.application import Application

from dotenv import load_dotenv
load_dotenv()

# this is the Alembic Config object
config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
# Interpret the config file for Python logging.
fileConfig(config.config_file_name)
# url = os.getenv("DATABASE_URL")
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    url = config.get_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
    print(f"DEBUG: Database URL = {url}")  # Add this line
    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
