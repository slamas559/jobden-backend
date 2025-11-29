# app/schemas/employer_profile.py
from pydantic import BaseModel, Field
from typing import Optional

class EmployerProfileBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    company_website: Optional[str] = Field(None, max_length=500)
    company_description: Optional[str] = Field(None, max_length=2000)

class EmployerProfileCreate(EmployerProfileBase):
    """Schema for creating employer profile (auto-created on registration)"""
    pass

class EmployerProfileUpdate(BaseModel):
    """Schema for updating employer profile - all fields optional"""
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    company_website: Optional[str] = Field(None, max_length=500)
    company_description: Optional[str] = Field(None, max_length=2000)

class EmployerProfileRead(EmployerProfileBase):
    """Schema for reading employer profile"""
    id: int
    user_id: int

    class Config:
        from_attributes = True

class EmployerProfileWithStats(EmployerProfileRead):
    """Extended profile with job statistics"""
    total_jobs: int
    active_jobs: int
    total_applications: int

    class Config:
        from_attributes = True