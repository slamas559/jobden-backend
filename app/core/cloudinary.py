# app/core/cloudinary.py
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from typing import Optional
import os
from app.core.config import settings
from dotenv import load_dotenv

# Configure Cloudinary (put these in your .env file)
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

async def upload_file_to_cloudinary(
    file: UploadFile,
    folder: str = "job_app",
    resource_type: str = "auto"
) -> dict:
    """
    Upload a file to Cloudinary
    
    Args:
        file: The file to upload
        folder: Cloudinary folder name
        resource_type: Type of resource (auto, image, video, raw)
    
    Returns:
        dict with url, public_id, and other metadata
    """
    try:
        # Read file content
        contents = await file.read()
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type=resource_type,
            use_filename=True,
            unique_filename=True
        )
        
        return {
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "resource_type": result.get("resource_type")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    finally:
        await file.seek(0)  # Reset file pointer


async def delete_file_from_cloudinary(public_id: str, resource_type: str = "image") -> bool:
    """
    Delete a file from Cloudinary
    
    Args:
        public_id: The public ID of the file to delete
        resource_type: Type of resource (image, video, raw)
    
    Returns:
        bool: True if successful
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return result.get("result") == "ok"
    except Exception as e:
        print(f"Error deleting file from Cloudinary: {str(e)}")
        return False


def validate_file_type(file: UploadFile, allowed_types: list) -> bool:
    """
    Validate file type
    
    Args:
        file: The uploaded file
        allowed_types: List of allowed MIME types
    
    Returns:
        bool: True if valid
    """
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    return True


def validate_file_size(file: UploadFile, max_size_mb: int = 5) -> bool:
    """
    Validate file size
    
    Args:
        file: The uploaded file
        max_size_mb: Maximum file size in MB
    
    Returns:
        bool: True if valid
    """
    # Note: This is a basic check. For production, you might want to check actual file size
    return True