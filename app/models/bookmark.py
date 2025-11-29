# app/models/bookmark.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="bookmarks")
    job = relationship("Job", backref="bookmarked_by")

    # Prevent duplicate bookmarks
    __table_args__ = (
        UniqueConstraint('user_id', 'job_id', name='unique_user_job_bookmark'),
    )