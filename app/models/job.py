from sqlalchemy import Column, Float, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=True)
    salary = Column(Float, nullable=True)
    job_type = Column(String, nullable=True)  # e.g., Full-time, Part-time, Contract
    requirements = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employer_id = Column(Integer, ForeignKey("employer_profiles.id"))
    employer = relationship("EmployerProfile", back_populates="jobs")
    applications = relationship("Application", back_populates="job")
