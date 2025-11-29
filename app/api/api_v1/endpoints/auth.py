# app/api/api_v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import UserCreate, UserRead, Token
from app.db.database import get_db
from app.services.auth_service import create_user, authenticate_user, create_token_for_user, get_user_by_email
from app.core.rate_limiter import limiter
from app.core.validators import validate_email_format, validate_password_strength

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")  # Limit to 5 registrations per hour per IP
async def register(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with rate limiting and validation
    """
    # Validate email format
    validated_email = validate_email_format(user_in.email)
    
    # Validate password strength
    validate_password_strength(user_in.password)
    
    # Check if user already exists
    existing = await get_user_by_email(db, validated_email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create user
    user = await create_user(db, validated_email, user_in.password, user_in.is_employer)
    return user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")  # Limit to 10 login attempts per minute per IP
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint with rate limiting to prevent brute force attacks
    """
    # OAuth2PasswordRequestForm provides username & password fields
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    token_data = await create_token_for_user(user)
    return {
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "token_type": token_data.get("token_type", "bearer")
    }


@router.post("/refresh", response_model=Token)
@limiter.limit("20/hour")  # Limit token refresh to 20 per hour
async def refresh_token(
    request: Request,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Use this endpoint to get a new access token using a valid refresh token.
    Expect header: Authorization: Bearer <refresh_token>
    """
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    from app.core.security import decode_refresh_token
    payload = decode_refresh_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    from app.services.auth_service import get_user_by_email
    user = await get_user_by_email(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # issue new access token
    from app.core.security import create_access_token
    access_token = create_access_token(str(user.id))
    return {"access_token": access_token, "refresh_token": token, "token_type": "bearer"}