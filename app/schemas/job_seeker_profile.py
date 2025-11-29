# app/schemas/job_seeker_profile.py
from pydantic import BaseModel, Field
from typing import Optional

class JobSeekerProfileBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    bio: Optional[str] = Field(None, max_length=2000)
    resume_url: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[str] = None
    profile_picture_url: Optional[str] = None

class JobSeekerProfileCreate(JobSeekerProfileBase):
    pass

class JobSeekerProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    bio: Optional[str] = Field(None, max_length=2000)
    resume_url: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[str] = None
    profile_picture_url: Optional[str] = None

class JobSeekerProfileRead(JobSeekerProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class JobSeekerProfileWithStats(JobSeekerProfileRead):
    total_applications: int
    total_bookmarks: int

    class Config:
        from_attributes = True