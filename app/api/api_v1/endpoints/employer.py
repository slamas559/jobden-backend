# app/api/api_v1/endpoints/employer.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.core.employer_deps import get_current_employer, get_current_employer_profile
from app.models.user import User
from app.models.employer_profile import EmployerProfile
from app.schemas.employer_profile import (
    EmployerProfileCreate,
    EmployerProfileRead,
    EmployerProfileUpdate,
    EmployerProfileWithStats
)
from app.schemas.job import JobRead  # You'll need to import your job schema
from app.services import employer_service

router = APIRouter()


@router.post("/profile", response_model=EmployerProfileRead, status_code=status.HTTP_201_CREATED)
async def create_employer_profile(
    profile_data: EmployerProfileCreate,
    current_user: User = Depends(get_current_employer),
    db: AsyncSession = Depends(get_db)
):
    """Create employer profile for the current user"""
    # Check if profile already exists
    existing = await employer_service.get_employer_profile_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employer profile already exists"
        )
    
    profile = await employer_service.create_employer_profile(
        db=db,
        user_id=current_user.id,
        company_name=profile_data.company_name,
        company_website=profile_data.company_website,
        company_description=profile_data.company_description
    )
    
    return profile


@router.get("/profile", response_model=EmployerProfileRead)
async def get_my_employer_profile(
    profile: EmployerProfile = Depends(get_current_employer_profile)
):
    """Get current employer's profile"""
    return profile


@router.put("/profile", response_model=EmployerProfileRead)
async def update_my_employer_profile(
    profile_update: EmployerProfileUpdate,
    profile: EmployerProfile = Depends(get_current_employer_profile),
    db: AsyncSession = Depends(get_db)
):
    """Update current employer's profile"""
    updated_profile = await employer_service.update_employer_profile(
        db=db,
        profile=profile,
        update_data=profile_update
    )
    return updated_profile


@router.get("/profile/stats", response_model=EmployerProfileWithStats)
async def get_employer_profile_with_stats(
    profile: EmployerProfile = Depends(get_current_employer_profile),
    db: AsyncSession = Depends(get_db)
):
    """Get employer profile with statistics"""
    stats = await employer_service.get_employer_statistics(db, profile.id)
    
    return EmployerProfileWithStats(
        id=profile.id,
        user_id=profile.user_id,
        company_name=profile.company_name,
        company_website=profile.company_website,
        company_description=profile.company_description,
        total_jobs=stats["total_jobs"],
        active_jobs=stats["active_jobs"],
        total_applications=stats["total_applications"]
    )


@router.get("/dashboard/statistics")
async def get_dashboard_statistics(
    profile: EmployerProfile = Depends(get_current_employer_profile),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for employer dashboard"""
    stats = await employer_service.get_employer_statistics(db, profile.id)
    return stats


@router.get("/jobs")
async def get_my_jobs(
    active_only: bool = Query(False, description="Filter for active jobs only"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    profile: EmployerProfile = Depends(get_current_employer_profile),
    db: AsyncSession = Depends(get_db)
):
    """Get all jobs posted by current employer"""
    jobs = await employer_service.get_employer_jobs(
        db=db,
        employer_id=profile.id,
        skip=skip,
        limit=limit,
        active_only=active_only
    )    
    return jobs


@router.get("/jobs/{job_id}/applicants")
async def get_job_applicants(
    job_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    profile: EmployerProfile = Depends(get_current_employer_profile),
    db: AsyncSession = Depends(get_db)
):
    """Get all applicants for a specific job"""
    applications = await employer_service.get_job_applicants(
        db=db,
        job_id=job_id,
        employer_id=profile.id,
        skip=skip,
        limit=limit
    )
    
    if applications is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or you don't have permission to view its applicants"
        )
    
    # Format response with applicant details
    applicants_data = []
    for app in applications:
        applicant_info = {
            "application_id": app.id,
            "applied_at": app.applied_at,
            "cover_letter": app.cover_letter,
            "status": app.status,
            "applicant": {
                "user_id": app.user.id,
                "email": app.user.email,
            }
        }
        
        # Add job seeker profile info if available
        if app.user.job_seeker_profile:
            profile_data = app.user.job_seeker_profile
            applicant_info["applicant"]["full_name"] = profile_data.full_name
            applicant_info["applicant"]["bio"] = profile_data.bio
            applicant_info["applicant"]["resume_url"] = profile_data.resume_url
            applicant_info["applicant"]["skills"] = profile_data.skills
            applicant_info["applicant"]["experience"] = profile_data.experience
            applicant_info["applicant"]["education"] = profile_data.education
            applicant_info["applicant"]["profile_picture_url"] = profile_data.profile_picture_url
        
        applicants_data.append(applicant_info)
    
    return {
        "job_id": job_id,
        "total_applicants": len(applicants_data),
        "applicants": applicants_data
    }


@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    status: str = Query(..., regex="^(pending|reviewed|accepted|rejected)$"),
    profile: EmployerProfile = Depends(get_current_employer_profile),
    db: AsyncSession = Depends(get_db)
):
    """Update application status (Employer only)"""
    from app.services import application_service, job_service
    from app.services.notification_helpers import notify_applicant_status_change
    
    # Get application
    application = await application_service.get_application_by_id(db, application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Verify the job belongs to this employer
    job = await job_service.get_job_by_id(db, application.job_id)
    if not job or job.employer_id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this application"
        )
    
    # Update status
    from app.schemas.application import ApplicationUpdate
    updated_application = await application_service.update_application(
        db=db,
        application=application,
        update_data=ApplicationUpdate(status=status)
    )
    
    # Notify applicant about status change
    await notify_applicant_status_change(
        db=db,
        applicant_user_id=application.user_id,
        job_title=job.title,
        new_status=status,
        application_id=application.id
    )
    
    # Send email notification (via Celery)
    from app.services import email_service
    from app.models.user import User
    from app.services.job_seeker_service import get_job_seeker_profile_by_user_id
    from sqlalchemy import select
    
    # Get applicant details
    applicant_stmt = select(User).where(User.id == application.user_id)
    applicant_result = await db.execute(applicant_stmt)
    applicant = applicant_result.scalar_one_or_none()
    
    if applicant:
        job_seeker_profile = await get_job_seeker_profile_by_user_id(db, applicant.id)
        applicant_name = job_seeker_profile.full_name if job_seeker_profile else applicant.email
        
        email_service.send_application_status_email(
            email=applicant.email,
            applicant_name=applicant_name,
            job_title=job.title,
            company_name=profile.company_name,
            status=status,
            application_id=application.id
        )
    
    return {
        "message": "Application status updated successfully",
        "application_id": application_id,
        "new_status": status
    }