# app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

ALGORITHM = "HS256"

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    # Use timezone-aware datetime
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=(expires_minutes if expires_minutes is not None else settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate JWT token.
    Returns None if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
def create_refresh_token(subject: str, expires_days: Optional[int] = None) -> str:
    """
    Create a refresh JWT token.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=(expires_days if expires_days is not None else settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_refresh_token(token: str) -> Optional[dict]:
    """
    Decode and validate refresh token.
    Returns None if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
