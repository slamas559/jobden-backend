# app/services/job_service.py
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


async def create_job(
    db: AsyncSession,
    employer_id: int,
    job_data: JobCreate
) -> Job:
    """Create a new job posting"""
    job = Job(
        employer_id=employer_id,
        title=job_data.title,
        description=job_data.description,
        location=job_data.location,
        salary=job_data.salary,
        job_type=job_data.job_type,
        requirements=job_data.requirements,
        is_active=job_data.is_active
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def get_job_by_id(db: AsyncSession, job_id: int) -> Optional[Job]:
    """Get a single job by ID"""
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_jobs(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    min_salary: Optional[float] = None,
    search: Optional[str] = None,
    active_only: bool = True
) -> List[Job]:
    """Get jobs with optional filters"""
    stmt = select(Job)
    
    # Filter by active status
    if active_only:
        stmt = stmt.where(Job.is_active == True)
    
    # Filter by location
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))
    
    # Filter by job type
    if job_type:
        stmt = stmt.where(Job.job_type.ilike(f"%{job_type}%"))
    
    # Filter by minimum salary
    if min_salary:
        stmt = stmt.where(Job.salary >= min_salary)
    
    # Search in title, description, or requirements
    if search:
        search_pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Job.title.ilike(search_pattern),
                Job.description.ilike(search_pattern),
                Job.requirements.ilike(search_pattern)
            )
        )
    
    # Apply pagination and ordering
    stmt = stmt.offset(skip).limit(limit).order_by(Job.created_at.desc())
    
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_job(
    db: AsyncSession,
    job: Job,
    job_update: JobUpdate
) -> Job:
    """Update a job posting"""
    update_data = job_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(job, field, value)
    
    await db.commit()
    await db.refresh(job)
    return job


async def delete_job(db: AsyncSession, job: Job) -> None:
    """Delete a job (soft delete by setting is_active to False)"""
    job.is_active = False
    await db.commit()