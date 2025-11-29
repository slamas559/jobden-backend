from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from app.db.database import Base

class JobSeekerProfile(Base):
    __tablename__ = "job_seeker_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    full_name = Column(String, nullable=False)
    bio = Column(Text, nullable=True)
    resume_url = Column(String, nullable=True)
    education = Column(Text, nullable=True)  # Could store JSON string or formatted text
    experience = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)  # Comma-separated or JSON string
    profile_picture_url = Column(String, nullable=True)

    user = relationship("User", back_populates="job_seeker_profile")
