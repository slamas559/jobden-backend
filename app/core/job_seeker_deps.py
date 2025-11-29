# app/core/job_seeker_deps.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.models.user import User
from app.models.job_seeker_profile import JobSeekerProfile
from app.db.database import get_db
from app.services.job_seeker_service import get_job_seeker_profile_by_user_id


async def get_current_job_seeker(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify that the current user is a job seeker (not an employer)"""
    if current_user.is_employer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can access this resource"
        )
    return current_user


async def get_current_job_seeker_profile(
    current_user: User = Depends(get_current_job_seeker),
    db: AsyncSession = Depends(get_db)
) -> JobSeekerProfile:
    """Get the job seeker profile for the current user"""
    profile = await get_job_seeker_profile_by_user_id(db, current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job seeker profile not found. Please create your profile first."
        )
    
    return profile