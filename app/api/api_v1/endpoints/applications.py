# app/api/api_v1/endpoints/applications.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationRead,
    ApplicationWithDocuments,
    ApplicationWithJob,
    ApplicationDocumentRead
)
from app.services import application_service, job_service, notification_service
from app.core.cloudinary import upload_file_to_cloudinary, validate_file_type

router = APIRouter()


@router.post("/", response_model=ApplicationWithDocuments, status_code=status.HTTP_201_CREATED)
async def apply_to_job(
    application_data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Apply to a job"""
    # Check if job exists and is active
    job = await job_service.get_job_by_id(db, application_data.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if not job.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This job is no longer accepting applications"
        )
    
    # Check if user has already applied
    existing = await application_service.get_application_by_user_and_job(
        db, current_user.id, application_data.job_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this job"
        )
    
    # Create application
    application = await application_service.create_application(
        db=db,
        user_id=current_user.id,
        application_data=application_data
    )
    
    # Create notification for job seeker
    await notification_service.create_application_notification(
        db=db,
        user_id=current_user.id,
        job_title=job.title,
        application_id=application.id
    )
    
    # Send email confirmation to job seeker (via Celery)
    from app.services import email_service
    from app.services.job_seeker_service import get_job_seeker_profile_by_user_id
    from app.services.employer_service import get_employer_profile_by_id
    
    job_seeker_profile = await get_job_seeker_profile_by_user_id(db, current_user.id)
    applicant_name = job_seeker_profile.full_name if job_seeker_profile else current_user.email
    
    # Get company name from employer profile
    employer_profile = await get_employer_profile_by_id(db, job.employer_id)
    company_name = employer_profile.company_name if employer_profile else "Company"
    
    # Send confirmation email to applicant
    email_service.send_application_confirmation_email(
        email=current_user.email,
        applicant_name=applicant_name,
        job_title=job.title,
        company_name=company_name,
        application_id=application.id
    )
    
    # Notify employer about new application
    from app.services.notification_helpers import notify_employer_new_application
    from app.services.job_seeker_service import get_job_seeker_profile_by_user_id
    
    # Get applicant name
    job_seeker_profile = await get_job_seeker_profile_by_user_id(db, current_user.id)
    applicant_name = job_seeker_profile.full_name if job_seeker_profile else current_user.email
    
    # Get employer user_id from job
    from app.services.employer_service import get_employer_profile_by_id
    employer_profile = await get_employer_profile_by_id(db, job.employer_id)
    if employer_profile:
        # Send WebSocket notification
        await notify_employer_new_application(
            db=db,
            employer_user_id=employer_profile.user_id,
            job_title=job.title,
            applicant_name=applicant_name,
            application_id=application.id
        )
        
        # Send email notification to employer (via Celery)
        from app.services import email_service
        from app.models.user import User
        from sqlalchemy import select
        
        # Get employer user email
        employer_user_stmt = select(User).where(User.id == employer_profile.user_id)
        employer_user_result = await db.execute(employer_user_stmt)
        employer_user = employer_user_result.scalar_one_or_none()
        
        if employer_user:
            email_service.send_new_application_email(
                email=employer_user.email,
                employer_name=employer_profile.company_name,
                applicant_name=applicant_name,
                job_title=job.title,
                application_id=application.id
            )
    
    return application


@router.get("/", response_model=List[ApplicationWithJob])
async def get_my_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all applications for current user"""
    applications = await application_service.get_user_applications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )
    return applications


@router.get("/{application_id}", response_model=ApplicationWithDocuments)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific application"""
    application = await application_service.get_application_by_id(db, application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Verify ownership
    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this application"
        )
    
    return application


@router.put("/{application_id}", response_model=ApplicationWithDocuments)
async def update_application(
    application_id: int,
    application_update: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an application (cover letter only, can't change status except to withdrawn)"""
    application = await application_service.get_application_by_id(db, application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Verify ownership
    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this application"
        )
    
    # Can't edit withdrawn applications
    if application.status == "withdrawn":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit a withdrawn application"
        )
    
    updated_application = await application_service.update_application(
        db=db,
        application=application,
        update_data=application_update
    )
    
    return updated_application


@router.post("/{application_id}/withdraw", response_model=ApplicationWithDocuments)
async def withdraw_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Withdraw an application"""
    application = await application_service.get_application_by_id(db, application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Verify ownership
    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to withdraw this application"
        )
    
    # Can't withdraw already withdrawn applications
    if application.status == "withdrawn":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application is already withdrawn"
        )
    
    withdrawn_application = await application_service.withdraw_application(db, application)
    
    # Notify employer about withdrawal
    from app.services.notification_helpers import notify_employer_application_withdrawn
    from app.services.job_seeker_service import get_job_seeker_profile_by_user_id
    from app.services.employer_service import get_employer_profile_by_id
    
    # Get applicant name
    job_seeker_profile = await get_job_seeker_profile_by_user_id(db, current_user.id)
    applicant_name = job_seeker_profile.full_name if job_seeker_profile else current_user.email
    
    # Get employer
    job = await job_service.get_job_by_id(db, application.job_id)
    if job:
        employer_profile = await get_employer_profile_by_id(db, job.employer_id)
        if employer_profile:
            await notify_employer_application_withdrawn(
                db=db,
                employer_user_id=employer_profile.user_id,
                job_title=job.title,
                applicant_name=applicant_name,
                application_id=application.id
            )
    
    return withdrawn_application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an application (only if status is withdrawn)"""
    application = await application_service.get_application_by_id(db, application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Verify ownership
    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this application"
        )
    
    await application_service.delete_application(db, application)
    return None


# --- Document Management ---

@router.post("/{application_id}/documents", response_model=ApplicationDocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_application_document(
    application_id: int,
    document_type: str = Query(..., description="Type: resume, cover_letter, portfolio, certificate"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document to an application"""
    # Get application and verify ownership
    application = await application_service.get_application_by_id(db, application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to upload documents to this application"
        )
    
    # Validate document type
    valid_types = ["resume", "cover_letter", "portfolio", "certificate"]
    if document_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Validate file type
    allowed_file_types = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg",
        "image/png"
    ]
    validate_file_type(file, allowed_file_types)
    
    # Upload to Cloudinary
    upload_result = await upload_file_to_cloudinary(
        file=file,
        folder=f"applications/{application_id}",
        resource_type="auto"
    )
    
    # Save document record
    document = await application_service.add_document_to_application(
        db=db,
        application_id=application_id,
        document_type=document_type,
        document_url=upload_result["url"],
        file_name=file.filename
    )
    
    return document


@router.get("/{application_id}/documents", response_model=List[ApplicationDocumentRead])
async def get_application_documents(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all documents for an application"""
    # Verify application exists and user has access
    application = await application_service.get_application_by_id(db, application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view these documents"
        )
    
    documents = await application_service.get_application_documents(db, application_id)
    return documents


@router.delete("/{application_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application_document(
    application_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document from an application"""
    # Get document
    document = await application_service.get_document_by_id(db, document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Verify it belongs to the specified application
    if document.application_id != application_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document does not belong to this application"
        )
    
    # Verify application ownership
    application = await application_service.get_application_by_id(db, application_id)
    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this document"
        )
    
    await application_service.delete_document(db, document)
    return None