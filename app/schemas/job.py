# app/schemas/job.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CustomQuestion(BaseModel):
    id: str
    type: str  # "short_answer", "multiple_choice", "yes_no", "long_answer"
    question: str
    required: bool = True
    options: Optional[List[str]] = None  # For multiple_choice type

class JobBase(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    salary: Optional[float] = None
    job_type: Optional[str] = None
    requirements: Optional[str] = None
    is_active: Optional[bool] = True
    custom_questions: Optional[List[CustomQuestion]] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    """All fields optional for partial updates"""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[float] = None
    job_type: Optional[str] = None
    requirements: Optional[str] = None
    is_active: Optional[bool] = None
    custom_questions: Optional[List[CustomQuestion]] = None

class JobRead(JobBase):
    id: int
    employer_id: int
    created_at: datetime

    class Config:
        from_attributes = True