# app/services/application_service.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime

from app.models.application import Application
from app.models.application_document import ApplicationDocument
from app.models.job import Job
from app.schemas.application import ApplicationCreate, ApplicationUpdate


async def create_application(
    db: AsyncSession,
    user_id: int,
    application_data: ApplicationCreate
) -> Application:
    """Create a new job application"""
    app_dict = application_data.model_dump()  
    # Convert question_answers to JSON
    if app_dict.get('question_answers'):
        app_dict['question_answers'] = [
            q.model_dump() for q in application_data.question_answers
        ]

    application = Application(
        user_id=user_id,
        **app_dict
        
    )
    db.add(application)
    await db.commit()
    await db.refresh(application, ["documents"])  # Load documents relationship
    return application


async def get_application_by_id(
    db: AsyncSession,
    application_id: int
) -> Optional[Application]:
    """Get application by ID with documents loaded"""
    stmt = (
        select(Application)
        .options(
            selectinload(Application.documents),
            selectinload(Application.job)
        )
        .where(Application.id == application_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_application_by_user_and_job(
    db: AsyncSession,
    user_id: int,
    job_id: int
) -> Optional[Application]:
    """Check if user has already applied to a job"""
    stmt = select(Application).where(
        Application.user_id == user_id,
        Application.job_id == job_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_applications(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
) -> List[Application]:
    """Get all applications for a user"""
    stmt = (
        select(Application)
        .options(
            selectinload(Application.documents),
            selectinload(Application.job)
        )
        .where(Application.user_id == user_id)
    )
    
    if status:
        stmt = stmt.where(Application.status == status)
    
    stmt = stmt.order_by(Application.applied_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_application(
    db: AsyncSession,
    application: Application,
    update_data: ApplicationUpdate
) -> Application:
    """Update an application"""
    update_dict = update_data.model_dump(exclude_unset=True)
    
    # Job seekers can only update cover_letter or set status to "withdrawn"
    for field, value in update_dict.items():
        if field == "status" and value not in ["withdrawn"]:
            continue  # Skip invalid status updates from job seekers
        setattr(application, field, value)
    
    application.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(application)
    return application


async def withdraw_application(
    db: AsyncSession,
    application: Application
) -> Application:
    """Withdraw an application"""
    application.status = "withdrawn"
    application.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(application)
    return application

async def is_job_applied(
    db: AsyncSession,
    user_id: int,
    job_id: int
) -> bool:
    """Check if a job is applied by the user"""
    application = await get_application_by_user_and_job(db, user_id, job_id)
    return application is not None

async def delete_application(
    db: AsyncSession,
    application: Application
) -> None:
    """Delete an application (cascade deletes documents)"""
    await db.delete(application)
    await db.commit()


# --- Application Document Functions ---

async def add_document_to_application(
    db: AsyncSession,
    application_id: int,
    document_type: str,
    document_url: str,
    file_name: str
) -> ApplicationDocument:
    """Add a document to an application"""
    document = ApplicationDocument(
        application_id=application_id,
        document_type=document_type,
        document_url=document_url,
        file_name=file_name
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def get_application_documents(
    db: AsyncSession,
    application_id: int
) -> List[ApplicationDocument]:
    """Get all documents for an application"""
    stmt = (
        select(ApplicationDocument)
        .where(ApplicationDocument.application_id == application_id)
        .order_by(ApplicationDocument.uploaded_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_document_by_id(
    db: AsyncSession,
    document_id: int
) -> Optional[ApplicationDocument]:
    """Get a specific document by ID"""
    stmt = select(ApplicationDocument).where(ApplicationDocument.id == document_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def delete_document(
    db: AsyncSession,
    document: ApplicationDocument
) -> None:
    """Delete a document"""
    await db.delete(document)
    await db.commit()