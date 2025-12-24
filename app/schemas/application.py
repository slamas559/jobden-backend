# app/schemas/application.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.job import JobRead


class QuestionAnswer(BaseModel):
    question_id: str
    question: str
    answer: str

class ApplicationDocumentBase(BaseModel):
    document_type: str
    document_url: str
    file_name: str

class ApplicationDocumentRead(ApplicationDocumentBase):
    id: int
    application_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True

class ApplicationCreate(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None
    question_answers: Optional[List[QuestionAnswer]] = None  # NEW

class ApplicationUpdate(BaseModel):
    cover_letter: Optional[str] = None
    status: Optional[str] = None

class ApplicationRead(BaseModel):
    id: int
    user_id: int
    job_id: int
    cover_letter: Optional[str]
    status: str
    applied_at: datetime
    updated_at: datetime
    question_answers: Optional[List[QuestionAnswer]] = None  # NEW

    class Config:
        from_attributes = True

class ApplicationWithDocuments(ApplicationRead):
    documents: List[ApplicationDocumentRead] = []

    class Config:
        from_attributes = True

class ApplicationWithJob(ApplicationWithDocuments):
    job: JobRead

    class Config:
        from_attributes = True