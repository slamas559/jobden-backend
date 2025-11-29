from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class EmployerProfile(Base):
    __tablename__ = "employer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    company_website = Column(String, nullable=True)
    company_description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="employer_profile")
    jobs = relationship("Job", back_populates="employer")
