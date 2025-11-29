# app/services/job_seeker_service.py
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.job_seeker_profile import JobSeekerProfile
from app.models.application import Application
from app.models.bookmark import Bookmark
from app.schemas.job_seeker_profile import JobSeekerProfileCreate, JobSeekerProfileUpdate


async def create_job_seeker_profile(
    db: AsyncSession,
    user_id: int,
    profile_data: JobSeekerProfileCreate
) -> JobSeekerProfile:
    """Create a new job seeker profile"""
    profile = JobSeekerProfile(
        user_id=user_id,
        full_name=profile_data.full_name,
        bio=profile_data.bio,
        resume_url=profile_data.resume_url,
        education=profile_data.education,
        experience=profile_data.experience,
        skills=profile_data.skills,
        profile_picture_url=profile_data.profile_picture_url
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_job_seeker_profile_by_user_id(
    db: AsyncSession,
    user_id: int
) -> Optional[JobSeekerProfile]:
    """Get job seeker profile by user ID"""
    stmt = select(JobSeekerProfile).where(JobSeekerProfile.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_job_seeker_profile_by_id(
    db: AsyncSession,
    profile_id: int
) -> Optional[JobSeekerProfile]:
    """Get job seeker profile by profile ID"""
    stmt = select(JobSeekerProfile).where(JobSeekerProfile.id == profile_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_job_seeker_profile(
    db: AsyncSession,
    profile: JobSeekerProfile,
    update_data: JobSeekerProfileUpdate
) -> JobSeekerProfile:
    """Update job seeker profile"""
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_job_seeker_statistics(db: AsyncSession, user_id: int) -> dict:
    """Get statistics for job seeker dashboard"""
    # Total applications
    total_applications_stmt = select(func.count(Application.id)).where(
        Application.user_id == user_id
    )
    total_applications_result = await db.execute(total_applications_stmt)
    total_applications = total_applications_result.scalar() or 0
    
    # Total bookmarks
    total_bookmarks_stmt = select(func.count(Bookmark.id)).where(
        Bookmark.user_id == user_id
    )
    total_bookmarks_result = await db.execute(total_bookmarks_stmt)
    total_bookmarks = total_bookmarks_result.scalar() or 0
    
    return {
        "total_applications": total_applications,
        "total_bookmarks": total_bookmarks
    }