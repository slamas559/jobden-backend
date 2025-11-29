# app/api/api_v1/endpoints/bookmarks.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.bookmark import BookmarkCreate, BookmarkRead, BookmarkWithJob
from app.services import bookmark_service, job_service

router = APIRouter()


@router.post("/", response_model=BookmarkRead, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    bookmark_data: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bookmark a job"""
    # Check if job exists
    job = await job_service.get_job_by_id(db, bookmark_data.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if already bookmarked
    existing = await bookmark_service.get_bookmark_by_user_and_job(
        db, current_user.id, bookmark_data.job_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job already bookmarked"
        )
    
    bookmark = await bookmark_service.create_bookmark(
        db=db,
        user_id=current_user.id,
        job_id=bookmark_data.job_id
    )
    
    return bookmark


@router.get("/", response_model=List[BookmarkWithJob])
async def get_my_bookmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all bookmarked jobs for current user"""
    bookmarks = await bookmark_service.get_user_bookmarks(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return bookmarks


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bookmark(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a bookmark"""
    bookmark = await bookmark_service.get_bookmark_by_user_and_job(
        db, current_user.id, job_id
    )
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    await bookmark_service.delete_bookmark(db, bookmark)
    return None


@router.get("/check/{job_id}")
async def check_bookmark_status(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if a job is bookmarked"""
    is_bookmarked = await bookmark_service.is_job_bookmarked(
        db, current_user.id, job_id
    )
    return {"is_bookmarked": is_bookmarked}