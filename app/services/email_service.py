# app/services/email_service.py
"""
Email service wrapper for Celery tasks
This provides a clean interface to trigger email tasks
"""
from app.tasks.email_tasks import (
    send_welcome_email_task,
    send_application_confirmation_task,
    send_application_status_update_task,
    send_new_application_notification_task,
    send_application_withdrawn_notification_task,
    send_password_reset_email_task
)


def send_welcome_email(email: str, name: str):
    """Queue welcome email task"""
    send_welcome_email_task.delay(email, name)


def send_application_confirmation_email(
    email: str,
    applicant_name: str,
    job_title: str,
    company_name: str,
    application_id: int
):
    """Queue application confirmation email task"""
    send_application_confirmation_task.delay(
        email, applicant_name, job_title, company_name, application_id
    )


def send_application_status_email(
    email: str,
    applicant_name: str,
    job_title: str,
    company_name: str,
    status: str,
    application_id: int
):
    """Queue application status update email task"""
    send_application_status_update_task.delay(
        email, applicant_name, job_title, company_name, status, application_id
    )


def send_new_application_email(
    email: str,
    employer_name: str,
    applicant_name: str,
    job_title: str,
    application_id: int
):
    """Queue new application notification email task"""
    send_new_application_notification_task.delay(
        email, employer_name, applicant_name, job_title, application_id
    )


def send_application_withdrawn_email(
    email: str,
    employer_name: str,
    applicant_name: str,
    job_title: str,
    application_id: int
):
    """Queue application withdrawn notification email task"""
    send_application_withdrawn_notification_task.delay(
        email, employer_name, applicant_name, job_title, application_id
    )


def send_password_reset_email(email: str, name: str, reset_token: str):
    """Queue password reset email task"""
    send_password_reset_email_task.delay(email, name, reset_token)