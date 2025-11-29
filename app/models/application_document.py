# app/models/application_document.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class ApplicationDocument(Base):
    __tablename__ = "application_documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    document_type = Column(String, nullable=False)  # e.g., "resume", "cover_letter", "portfolio", "certificate"
    document_url = Column(String, nullable=False)  # Cloudinary URL
    file_name = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    application = relationship("Application", back_populates="documents")