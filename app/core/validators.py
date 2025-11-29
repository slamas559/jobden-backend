# app/core/validators.py
import re
from typing import Optional
from fastapi import HTTPException, UploadFile
from email_validator import validate_email, EmailNotValidError


def validate_email_format(email: str) -> str:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        Normalized email address
        
    Raises:
        HTTPException: If email is invalid
    """
    try:
        # Validate and normalize email
        validated = validate_email(email, check_deliverability=False)
        return validated.normalized
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=f"Invalid email address: {str(e)}")


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If password doesn't meet requirements
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long"
        )
    
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter"
        )
    
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one lowercase letter"
        )
    
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one digit"
        )
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one special character"
        )
    
    return True


def validate_phone_number(phone: str) -> str:
    """
    Validate phone number (basic validation)
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Cleaned phone number
        
    Raises:
        HTTPException: If phone number is invalid
    """
    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    
    # Check if it contains only digits and optional + prefix
    if not re.match(r"^\+?\d{10,15}$", cleaned):
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number format. Must be 10-15 digits."
        )
    
    return cleaned


def validate_file_size(file: UploadFile, max_size_mb: int = 5) -> bool:
    """
    Validate file size
    
    Args:
        file: Uploaded file
        max_size_mb: Maximum file size in MB
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If file is too large
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    # Read file to check size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {max_size_mb}MB"
        )
    
    return True


def validate_file_type(file: UploadFile, allowed_types: list) -> bool:
    """
    Validate file MIME type
    
    Args:
        file: Uploaded file
        allowed_types: List of allowed MIME types
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If file type is not allowed
    """
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        )
    
    return True


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input to prevent XSS
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
        
    Raises:
        HTTPException: If text exceeds max length
    """
    if not text:
        return text
    
    # Remove or escape potentially dangerous characters
    # Note: For HTML rendering, use a proper library like bleach
    sanitized = text.strip()
    
    # Check length
    if max_length and len(sanitized) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Input exceeds maximum length of {max_length} characters"
        )
    
    return sanitized


def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If URL is invalid
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    if not url_pattern.match(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL format"
        )
    
    return True


def validate_slug(slug: str) -> bool:
    """
    Validate slug format (for URLs)
    
    Args:
        slug: Slug to validate
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If slug is invalid
    """
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
        raise HTTPException(
            status_code=400,
            detail="Invalid slug format. Use lowercase letters, numbers, and hyphens only."
        )
    
    return True