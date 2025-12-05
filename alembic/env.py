from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from app.db.database import Base  # Only metadata
from app.core.config import settings

from app.models.user import User
from app.models.employer_profile import EmployerProfile
from app.models.job_seeker_profile import JobSeekerProfile
from app.models.job import Job
from app.models.application import Application

config = context.config
sync_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

# IMPORTANT: Use SYNC DB URL, not async
sync_url = config.get_main_option("sqlalchemy.url", sync_url)
target_metadata = Base.metadata
print(f"SYNC DATABASE URL FOR ALEMBIC: {sync_url}")
fileConfig(config.config_file_name)

def run_migrations_offline():
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool,     # REQUIRED for pgBouncer
        connect_args={
            "prepared_statement_cache_size": 0   # <-- FIX for psycopg
        }
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
