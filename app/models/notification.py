# app/models/notification.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, nullable=True)  # e.g., "application", "job_update", "general"
    related_id = Column(Integer, nullable=True)  # ID of related entity (job_id, application_id, etc.)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", backref="notifications")