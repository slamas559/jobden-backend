# app/services/auth_service.py
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.employer_profile import EmployerProfile
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token

async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    return user

async def create_user(db: AsyncSession, email: str, password: str, is_employer: bool = False):
    hashed = get_password_hash(password)

    user = User(email=email, hashed_password=hashed, is_employer=is_employer)
    db.add(user)
    await db.flush()  # assigns id
    
    # Auto-create employer profile if user is an employer
    if is_employer:
        employer_profile = EmployerProfile(
            user_id=user.id,
            company_name=f"Company ({email.split('@')[0]})",  # Default name from email
            company_website=None,
            company_description=None
        )
        db.add(employer_profile)
    
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def create_token_for_user(user):
    """
    Generate both access and refresh tokens for the user
    """
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
