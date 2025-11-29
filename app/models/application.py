# app/models/application.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    cover_letter = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, reviewed, accepted, rejected, withdrawn
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    documents = relationship("ApplicationDocument", back_populates="application", cascade="all, delete-orphan")