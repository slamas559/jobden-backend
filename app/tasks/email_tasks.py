# app/tasks/email_tasks.py
from app.core.celery_config import celery_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path

from app.core.config import settings

# Setup Jinja2 for email templates
template_dir = Path(__file__).parent.parent / "templates" / "emails"
jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))


def render_email_template(template_name: str, context: dict) -> str:
    """Render email template with context"""
    template = jinja_env.get_template(f"{template_name}.html")
    return template.render(**context)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, to_email: str, subject: str, html_content: str):
    """
    Base task to send email via SendGrid
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
    """
    try:
        message = Mail(
            from_email=Email(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME),
            to_emails=To(to_email),
            subject=subject,
            html_content=Content("text/html", html_content)
        )
        
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"Email sent to {to_email}. Status code: {response.status_code}")
        return {
            "status": "success",
            "status_code": response.status_code,
            "to": to_email
        }
    
    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
        # Retry the task
        raise self.retry(exc=e)


@celery_app.task
def send_welcome_email_task(email: str, name: str):
    """Send welcome email to new users"""
    html_content = render_email_template("welcome", {
        "name": name,
        "app_url": settings.APP_URL,
        "app_name": settings.APP_NAME,
        "support_email": settings.SENDGRID_FROM_EMAIL
    })
    
    send_email_task.delay(
        to_email=email,
        subject=f"Welcome to {settings.APP_NAME}!",
        html_content=html_content
    )


@celery_app.task
def send_application_confirmation_task(
    email: str,
    applicant_name: str,
    job_title: str,
    company_name: str,
    application_id: int
):
    """Send application confirmation email"""
    html_content = render_email_template("application_confirmation", {
        "applicant_name": applicant_name,
        "job_title": job_title,
        "company_name": company_name,
        "application_id": application_id,
        "app_url": settings.APP_URL
    })
    
    send_email_task.delay(
        to_email=email,
        subject=f"Application Confirmation - {job_title}",
        html_content=html_content
    )


@celery_app.task
def send_application_status_update_task(
    email: str,
    applicant_name: str,
    job_title: str,
    company_name: str,
    status: str,
    application_id: int
):
    """Send application status update email"""
    status_messages = {
        "reviewed": "Your application is being reviewed",
        "accepted": "Congratulations! Your application has been accepted",
        "rejected": "Thank you for your interest"
    }
    
    html_content = render_email_template("application_status", {
        "applicant_name": applicant_name,
        "job_title": job_title,
        "company_name": company_name,
        "status": status,
        "status_message": status_messages.get(status, f"Status updated to {status}"),
        "application_id": application_id,
        "app_url": settings.APP_URL
    })
    
    send_email_task.delay(
        to_email=email,
        subject=f"Application Update - {job_title}",
        html_content=html_content
    )


@celery_app.task
def send_new_application_notification_task(
    email: str,
    employer_name: str,
    applicant_name: str,
    job_title: str,
    application_id: int
):
    """Send new application notification to employer"""
    html_content = render_email_template("new_application", {
        "employer_name": employer_name,
        "applicant_name": applicant_name,
        "job_title": job_title,
        "application_id": application_id,
        "app_url": settings.APP_URL
    })
    
    send_email_task.delay(
        to_email=email,
        subject=f"New Application for {job_title}",
        html_content=html_content
    )


@celery_app.task
def send_application_withdrawn_notification_task(
    email: str,
    employer_name: str,
    applicant_name: str,
    job_title: str,
    application_id: int
):
    """Send application withdrawn notification to employer"""
    html_content = render_email_template("application_withdrawn", {
        "employer_name": employer_name,
        "applicant_name": applicant_name,
        "job_title": job_title,
        "application_id": application_id,
        "app_url": settings.APP_URL
    })
    
    send_email_task.delay(
        to_email=email,
        subject=f"Application Withdrawn - {job_title}",
        html_content=html_content
    )


@celery_app.task
def send_password_reset_email_task(email: str, name: str, reset_token: str):
    """Send password reset email"""
    reset_url = f"{settings.APP_URL}/reset-password?token={reset_token}"
    
    html_content = render_email_template("password_reset", {
        "name": name,
        "reset_url": reset_url,
        "app_url": settings.APP_URL,
        "app_name": settings.APP_NAME,
        "support_email": settings.SENDGRID_FROM_EMAIL
    })
    
    send_email_task.delay(
        to_email=email,
        subject=f"Password Reset Request - {settings.APP_NAME}",
        html_content=html_content
    )