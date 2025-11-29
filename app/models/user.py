from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_employer = Column(Boolean, default=False)

    employer_profile = relationship("EmployerProfile", back_populates="user", uselist=False)
    job_seeker_profile = relationship("JobSeekerProfile", back_populates="user", uselist=False)
    applications = relationship("Application", back_populates="user")
