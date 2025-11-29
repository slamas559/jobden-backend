# app/services/notification_helpers.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.notification import NotificationCreate
from app.services.notification_service import create_notification


async def notify_employer_new_application(
    db: AsyncSession,
    employer_user_id: int,
    job_title: str,
    applicant_name: str,
    application_id: int
):
    """Notify employer about new application"""
    await create_notification(
        db,
        NotificationCreate(
            user_id=employer_user_id,
            title="New Application Received",
            message=f"{applicant_name} applied to '{job_title}'",
            notification_type="new_application",
            related_id=application_id
        )
    )


async def notify_applicant_status_change(
    db: AsyncSession,
    applicant_user_id: int,
    job_title: str,
    new_status: str,
    application_id: int
):
    """Notify applicant about application status change"""
    status_messages = {
        "reviewed": f"Your application for '{job_title}' is being reviewed",
        "accepted": f"Congratulations! Your application for '{job_title}' has been accepted",
        "rejected": f"Your application for '{job_title}' was not successful this time"
    }
    
    message = status_messages.get(new_status, f"Your application status for '{job_title}' has been updated to {new_status}")
    
    await create_notification(
        db,
        NotificationCreate(
            user_id=applicant_user_id,
            title="Application Status Update",
            message=message,
            notification_type="application_status",
            related_id=application_id
        )
    )


async def notify_employer_application_withdrawn(
    db: AsyncSession,
    employer_user_id: int,
    job_title: str,
    applicant_name: str,
    application_id: int
):
    """Notify employer that applicant withdrew their application"""
    await create_notification(
        db,
        NotificationCreate(
            user_id=employer_user_id,
            title="Application Withdrawn",
            message=f"{applicant_name} withdrew their application for '{job_title}'",
            notification_type="application_withdrawn",
            related_id=application_id
        )
    )