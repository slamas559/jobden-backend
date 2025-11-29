from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class JobBase(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    salary: Optional[float] = None
    job_type: Optional[str] = None  # e.g., Full-time, Part-time, Contract
    requirements: Optional[str] = None
    is_active: Optional[bool] = True

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

class JobRead(JobBase):
    id: int
    employer_id: int
    created_at: datetime

    class Config:
        from_attributes = True