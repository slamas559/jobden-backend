# app/api/api_v1/endpoints/jobs.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.database import get_db
from app.core.employer_deps import get_current_employer_profile
from app.core.deps import get_current_user
from app.models.employer_profile import EmployerProfile
from app.models.user import User
from app.schemas.job import JobCreate, JobRead, JobUpdate
from app.services import job_service

router = APIRouter()


@router.post("/", response_model=JobRead, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    profile: EmployerProfile = Depends(get_current_employer_profile),
    db: AsyncSession = Depends(get_db)
):
    """Create a new job posting (Employer only)"""
    job = await job_service.create_job(
        db=db,
        employer_id=profile.id,
        job_data=job_data
    )
    return job


@router.get("/", response_model=List[JobRead])
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    min_salary: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all active jobs with optional filters (Public endpoint)"""
    jobs = await job_service.get_jobs(
        db=db,
        skip=skip,
        limit=limit,
        location=location,
        job_type=job_type,
        min_salary=min_salary,
        search=search
    )
    # Return the jobs with the profile of the employer included
    # This can be done in the job_service.get_jobs method if needed
    # for job in jobs:
    #     job.employer_profile = await employer_service.get_employer_profile_by_id(db, job.employer_id)  
    
    return jobs



@router.get("/{job_id}", response_model=JobRead)
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a single job by ID (Public endpoint)"""
    job = await job_service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job


@router.put("/{job_id}", response_model=JobRead)
async def update_job(
    job_id: int,
    job_update: JobUpdate,
    profile: EmployerProfile = Depends(get_current_employer_profile),
    db: AsyncSession = Depends(get_db)
):
    """Update a job posting (Employer only - can only update own jobs)"""
    job = await job_service.get_job_by_id(db, job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Verify the job belongs to this employer
    if job.employer_id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this job"
        )
    
    updated_job = await job_service.update_job(db, job, job_update)
    return updated_job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    profile: EmployerProfile = Depends(get_current_employer_profile),
    db: AsyncSession = Depends(get_db)
):
    """Delete/deactivate a job posting (Employer only - can only delete own jobs)"""
    job = await job_service.get_job_by_id(db, job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Verify the job belongs to this employer
    if job.employer_id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this job"
        )
    
    await job_service.delete_job(db, job)
    return None