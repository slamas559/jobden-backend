# app/services/bookmark_service.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List

from app.models.bookmark import Bookmark
from app.models.job import Job


async def create_bookmark(
    db: AsyncSession,
    user_id: int,
    job_id: int
) -> Bookmark:
    """Create a new bookmark"""
    bookmark = Bookmark(
        user_id=user_id,
        job_id=job_id
    )
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)
    return bookmark


async def get_bookmark_by_user_and_job(
    db: AsyncSession,
    user_id: int,
    job_id: int
) -> Optional[Bookmark]:
    """Get a specific bookmark by user and job"""
    stmt = select(Bookmark).where(
        Bookmark.user_id == user_id,
        Bookmark.job_id == job_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_bookmarks(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Bookmark]:
    """Get all bookmarks for a user with job details"""
    stmt = (
        select(Bookmark)
        .options(selectinload(Bookmark.job))
        .where(Bookmark.user_id == user_id)
        .order_by(Bookmark.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_bookmark(
    db: AsyncSession,
    bookmark: Bookmark
) -> None:
    """Delete a bookmark"""
    await db.delete(bookmark)
    await db.commit()


async def is_job_bookmarked(
    db: AsyncSession,
    user_id: int,
    job_id: int
) -> bool:
    """Check if a job is bookmarked by user"""
    bookmark = await get_bookmark_by_user_and_job(db, user_id, job_id)
    return bookmark is not None