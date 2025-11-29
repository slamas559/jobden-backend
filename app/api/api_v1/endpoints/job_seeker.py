# app/api/api_v1/endpoints/job_seeker.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.job_seeker_deps import get_current_job_seeker, get_current_job_seeker_profile
from app.models.user import User
from app.models.job_seeker_profile import JobSeekerProfile
from app.schemas.job_seeker_profile import (
    JobSeekerProfileCreate,
    JobSeekerProfileRead,
    JobSeekerProfileUpdate,
    JobSeekerProfileWithStats
)
from app.services import job_seeker_service
from app.core.cloudinary import upload_file_to_cloudinary, validate_file_type

router = APIRouter()


@router.post("/profile", response_model=JobSeekerProfileRead, status_code=status.HTTP_201_CREATED)
async def create_job_seeker_profile(
    profile_data: JobSeekerProfileCreate,
    current_user: User = Depends(get_current_job_seeker),
    db: AsyncSession = Depends(get_db)
):
    """Create job seeker profile for the current user"""
    # Check if profile already exists
    existing = await job_seeker_service.get_job_seeker_profile_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job seeker profile already exists"
        )
    
    profile = await job_seeker_service.create_job_seeker_profile(
        db=db,
        user_id=current_user.id,
        profile_data=profile_data
    )
    
    return profile


@router.get("/profile", response_model=JobSeekerProfileRead)
async def get_my_profile(
    profile: JobSeekerProfile = Depends(get_current_job_seeker_profile)
):
    """Get current job seeker's profile"""
    return profile


@router.put("/profile", response_model=JobSeekerProfileRead)
async def update_my_profile(
    profile_update: JobSeekerProfileUpdate,
    profile: JobSeekerProfile = Depends(get_current_job_seeker_profile),
    db: AsyncSession = Depends(get_db)
):
    """Update current job seeker's profile"""
    updated_profile = await job_seeker_service.update_job_seeker_profile(
        db=db,
        profile=profile,
        update_data=profile_update
    )
    return updated_profile


@router.get("/profile/stats", response_model=JobSeekerProfileWithStats)
async def get_profile_with_stats(
    profile: JobSeekerProfile = Depends(get_current_job_seeker_profile),
    current_user: User = Depends(get_current_job_seeker),
    db: AsyncSession = Depends(get_db)
):
    """Get job seeker profile with statistics"""
    stats = await job_seeker_service.get_job_seeker_statistics(db, current_user.id)
    
    return JobSeekerProfileWithStats(
        id=profile.id,
        user_id=profile.user_id,
        full_name=profile.full_name,
        bio=profile.bio,
        resume_url=profile.resume_url,
        education=profile.education,
        experience=profile.experience,
        skills=profile.skills,
        profile_picture_url=profile.profile_picture_url,
        total_applications=stats["total_applications"],
        total_bookmarks=stats["total_bookmarks"]
    )


@router.post("/profile/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    profile: JobSeekerProfile = Depends(get_current_job_seeker_profile),
    db: AsyncSession = Depends(get_db)
):
    """Upload resume/CV to Cloudinary"""
    # Validate file type (PDF, DOC, DOCX)
    allowed_types = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    validate_file_type(file, allowed_types)
    
    # Upload to Cloudinary
    upload_result = await upload_file_to_cloudinary(
        file=file,
        folder="resumes",
        resource_type="raw"
    )
    
    # Update profile with resume URL
    profile.resume_url = upload_result["url"]
    await db.commit()
    await db.refresh(profile)
    
    return {
        "message": "Resume uploaded successfully",
        "resume_url": upload_result["url"]
    }


@router.post("/profile/upload-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    profile: JobSeekerProfile = Depends(get_current_job_seeker_profile),
    db: AsyncSession = Depends(get_db)
):
    """Upload profile picture to Cloudinary"""
    # Validate file type (images only)
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    validate_file_type(file, allowed_types)
    
    # Upload to Cloudinary
    upload_result = await upload_file_to_cloudinary(
        file=file,
        folder="profile_pictures",
        resource_type="image"
    )
    
    # Update profile with picture URL
    profile.profile_picture_url = upload_result["url"]
    await db.commit()
    await db.refresh(profile)
    
    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture_url": upload_result["url"]
    }