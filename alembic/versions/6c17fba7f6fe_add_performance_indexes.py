"""add performance indexes

Revision ID: 6c17fba7f6fe
Revises: b39ad62cb77b
Create Date: 2025-11-28 01:49:20.593337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c17fba7f6fe'
down_revision: Union[str, Sequence[str], None] = 'b39ad62cb77b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Job indexes
    op.create_index('idx_jobs_is_active', 'jobs', ['is_active'])
    op.create_index('idx_jobs_created_at', 'jobs', ['created_at'])
    op.create_index('idx_jobs_title', 'jobs', ['title'])
    op.create_index('idx_jobs_location', 'jobs', ['location'])
    op.create_index('idx_jobs_job_type', 'jobs', ['job_type'])
    op.create_index('idx_jobs_employer_id', 'jobs', ['employer_id'])
    
    # Composite index for common query (is_active + created_at)
    op.create_index('idx_jobs_active_created', 'jobs', ['is_active', 'created_at'])
    
    # Application indexes
    op.create_index('idx_applications_user_id', 'applications', ['user_id'])
    op.create_index('idx_applications_job_id', 'applications', ['job_id'])
    op.create_index('idx_applications_status', 'applications', ['status'])
    op.create_index('idx_applications_applied_at', 'applications', ['applied_at'])
    
    # Composite indexes for applications
    op.create_index('idx_applications_user_status', 'applications', ['user_id', 'status'])
    op.create_index('idx_applications_job_status', 'applications', ['job_id', 'status'])
    
    # Bookmark indexes
    op.create_index('idx_bookmarks_user_id', 'bookmarks', ['user_id'])
    op.create_index('idx_bookmarks_job_id', 'bookmarks', ['job_id'])
    op.create_index('idx_bookmarks_created_at', 'bookmarks', ['created_at'])
    
    # Notification indexes
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('idx_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('idx_notifications_type', 'notifications', ['notification_type'])
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'])
    
    # Composite index for notifications (user_id + is_read)
    op.create_index('idx_notifications_user_unread', 'notifications', ['user_id', 'is_read'])
    
    # User indexes
    op.create_index('idx_users_is_employer', 'users', ['is_employer'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])


def downgrade():
    # Drop all indexes in reverse order
    op.drop_index('idx_users_is_active', 'users')
    op.drop_index('idx_users_is_employer', 'users')
    op.drop_index('idx_notifications_user_unread', 'notifications')
    op.drop_index('idx_notifications_created_at', 'notifications')
    op.drop_index('idx_notifications_type', 'notifications')
    op.drop_index('idx_notifications_is_read', 'notifications')
    op.drop_index('idx_notifications_user_id', 'notifications')
    op.drop_index('idx_bookmarks_created_at', 'bookmarks')
    op.drop_index('idx_bookmarks_job_id', 'bookmarks')
    op.drop_index('idx_bookmarks_user_id', 'bookmarks')
    op.drop_index('idx_applications_job_status', 'applications')
    op.drop_index('idx_applications_user_status', 'applications')
    op.drop_index('idx_applications_applied_at', 'applications')
    op.drop_index('idx_applications_status', 'applications')
    op.drop_index('idx_applications_job_id', 'applications')
    op.drop_index('idx_applications_user_id', 'applications')
    op.drop_index('idx_jobs_active_created', 'jobs')
    op.drop_index('idx_jobs_employer_id', 'jobs')
    op.drop_index('idx_jobs_job_type', 'jobs')
    op.drop_index('idx_jobs_location', 'jobs')
    op.drop_index('idx_jobs_title', 'jobs')
    op.drop_index('idx_jobs_created_at', 'jobs')
    op.drop_index('idx_jobs_is_active', 'jobs')
