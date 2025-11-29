# app/core/employer_deps.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.models.user import User
from app.models.employer_profile import EmployerProfile
from app.db.database import get_db
from app.services.employer_service import get_employer_profile_by_user_id


async def get_current_employer(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify that the current user is an employer"""
    if not current_user.is_employer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can access this resource"
        )
    return current_user


async def get_current_employer_profile(
    current_user: User = Depends(get_current_employer),
    db: AsyncSession = Depends(get_db)
) -> EmployerProfile:
    """Get the employer profile for the current employer user"""
    profile = await get_employer_profile_by_user_id(db, current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer profile not found. Please create your profile first."
        )
    
    return profile