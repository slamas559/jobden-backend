# app/core/database_indexes.py
"""
Database indexes for performance optimization

Run this migration to add indexes:
    alembic revision --autogenerate -m "add performance indexes"
    alembic upgrade head
"""

# Index definitions to add to your models:

RECOMMENDED_INDEXES = """
# Add these to your models for better query performance:

# User Model
class User(Base):
    # Existing columns...
    email = Column(String, unique=True, index=True)  # Already indexed
    is_employer = Column(Boolean, default=False, index=True)  # Add index
    is_active = Column(Boolean, default=True, index=True)  # Add index

# Job Model
class Job(Base):
    # Existing columns...
    title = Column(String, nullable=False, index=True)  # Add index for search
    location = Column(String, nullable=True, index=True)  # Add index for filtering
    job_type = Column(String, nullable=True, index=True)  # Add index for filtering
    is_active = Column(Boolean, default=True, index=True)  # Add index
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # Add index for sorting
    employer_id = Column(Integer, ForeignKey("employer_profiles.id"), index=True)  # Add index

# Application Model
class Application(Base):
    # Existing columns...
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Add index
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)  # Add index
    status = Column(String, default="pending", index=True)  # Add index for filtering
    applied_at = Column(DateTime, default=datetime.utcnow, index=True)  # Add index for sorting

# Bookmark Model
class Bookmark(Base):
    # Existing columns...
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Add index
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)  # Add index
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # Add index

# Notification Model
class Notification(Base):
    # Existing columns...
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Add index
    is_read = Column(Boolean, default=False, index=True)  # Add index for filtering
    notification_type = Column(String, nullable=True, index=True)  # Add index
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # Add index

# Composite Indexes (add to __table_args__)

# Job Search Performance
Index('idx_job_active_created', Job.is_active, Job.created_at.desc())
Index('idx_job_location_type', Job.location, Job.job_type)

# Application Queries
Index('idx_application_user_status', Application.user_id, Application.status)
Index('idx_application_job_status', Application.job_id, Application.status)

# Notification Queries  
Index('idx_notification_user_unread', Notification.user_id, Notification.is_read)
"""

# SQL to add indexes manually (if needed)
ADD_INDEXES_SQL = """
-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_is_employer ON users(is_employer);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Job indexes
CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_job_type ON jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_employer_id ON jobs(employer_id);

-- Composite indexes for job search
CREATE INDEX IF NOT EXISTS idx_jobs_active_created ON jobs(is_active, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_location_type ON jobs(location, job_type) WHERE is_active = true;

-- Application indexes
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_applied_at ON applications(applied_at DESC);

-- Composite indexes for applications
CREATE INDEX IF NOT EXISTS idx_applications_user_status ON applications(user_id, status);
CREATE INDEX IF NOT EXISTS idx_applications_job_status ON applications(job_id, status);

-- Bookmark indexes
CREATE INDEX IF NOT EXISTS idx_bookmarks_user_id ON bookmarks(user_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_job_id ON bookmarks(job_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_created_at ON bookmarks(created_at DESC);

-- Notification indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);

-- Composite index for notification queries
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_read = false;

-- Full-text search index for job search (PostgreSQL)
CREATE INDEX IF NOT EXISTS idx_jobs_fulltext ON jobs USING GIN (to_tsvector('english', title || ' ' || COALESCE(description, '')));
"""

print(RECOMMENDED_INDEXES)
print("\n\nSQL Commands:")
print(ADD_INDEXES_SQL)