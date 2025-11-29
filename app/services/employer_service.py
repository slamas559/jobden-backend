# app/services/employer_service.py
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional

from app.models.employer_profile import EmployerProfile
from app.models.job import Job
from app.models.user import User
from app.models.application import Application
from app.schemas.employer_profile import EmployerProfileCreate, EmployerProfileUpdate


async def create_employer_profile(
    db: AsyncSession,
    user_id: int,
    company_name: str = "My Company",
    company_website: Optional[str] = None,
    company_description: Optional[str] = None
) -> EmployerProfile:
    """Create a new employer profile for a user"""
    profile = EmployerProfile(
        user_id=user_id,
        company_name=company_name,
        company_website=company_website,
        company_description=company_description
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_employer_profile_by_user_id(db: AsyncSession, user_id: int) -> Optional[EmployerProfile]:
    """Get employer profile by user ID"""
    stmt = select(EmployerProfile).where(EmployerProfile.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_employer_profile_by_id(db: AsyncSession, profile_id: int) -> Optional[EmployerProfile]:
    """Get employer profile by profile ID"""
    stmt = select(EmployerProfile).where(EmployerProfile.id == profile_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_employer_profile(
    db: AsyncSession,
    profile: EmployerProfile,
    update_data: EmployerProfileUpdate
) -> EmployerProfile:
    """Update employer profile with provided data"""
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_employer_jobs(
    db: AsyncSession,
    employer_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
) -> list[Job]:
    """Get all jobs posted by an employer"""
    stmt = select(Job).where(Job.employer_id == employer_id)
    
    if active_only:
        stmt = stmt.where(Job.is_active == True)
    
    stmt = stmt.offset(skip).limit(limit).order_by(Job.created_at.desc())
    
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_employer_statistics(db: AsyncSession, employer_id: int) -> dict:
    """Get statistics for employer dashboard"""
    # Total jobs
    total_jobs_stmt = select(func.count(Job.id)).where(Job.employer_id == employer_id)
    total_jobs_result = await db.execute(total_jobs_stmt)
    total_jobs = total_jobs_result.scalar() or 0
    
    # Active jobs
    active_jobs_stmt = select(func.count(Job.id)).where(
        Job.employer_id == employer_id,
        Job.is_active == True
    )
    active_jobs_result = await db.execute(active_jobs_stmt)
    active_jobs = active_jobs_result.scalar() or 0
    
    # Total applications across all jobs
    total_applications_stmt = (
        select(func.count(Application.id))
        .join(Job, Application.job_id == Job.id)
        .where(Job.employer_id == employer_id)
    )
    total_applications_result = await db.execute(total_applications_stmt)
    total_applications = total_applications_result.scalar() or 0
    
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applications": total_applications
    }


async def get_job_applicants(
    db: AsyncSession,
    job_id: int,
    employer_id: int,
    skip: int = 0,
    limit: int = 100
):
    """Get all applicants for a specific job (with verification that job belongs to employer)"""
    # First verify the job belongs to this employer
    job_stmt = select(Job).where(Job.id == job_id, Job.employer_id == employer_id)
    job_result = await db.execute(job_stmt)
    job = job_result.scalar_one_or_none()
    
    if not job:
        return None  # Job doesn't exist or doesn't belong to this employer
    
    # Get applications with user and job_seeker_profile loaded
    stmt = (
        select(Application)
        .options(
            selectinload(Application.user).selectinload(User.job_seeker_profile)
        )
        .where(Application.job_id == job_id)
        .order_by(Application.applied_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    applications = list(result.scalars().all())
    
    return applications