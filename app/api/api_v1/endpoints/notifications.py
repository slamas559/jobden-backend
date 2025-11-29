# app/api/api_v1/endpoints/notifications.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationRead, NotificationUpdate
from app.services import notification_service

router = APIRouter()


@router.get("/", response_model=List[NotificationRead])
async def get_my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all notifications for current user"""
    notifications = await notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )
    return notifications


@router.get("/unread-count")
async def get_unread_notification_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications"""
    count = await notification_service.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.put("/{notification_id}/read", response_model=NotificationRead)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a notification as read"""
    notification = await notification_service.get_notification_by_id(db, notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Verify ownership
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this notification"
        )
    
    updated_notification = await notification_service.mark_notification_as_read(db, notification)
    return updated_notification


@router.put("/mark-all-read")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read for current user"""
    count = await notification_service.mark_all_notifications_as_read(db, current_user.id)
    return {
        "message": f"Marked {count} notifications as read",
        "count": count
    }


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a notification"""
    notification = await notification_service.get_notification_by_id(db, notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Verify ownership
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this notification"
        )
    
    await notification_service.delete_notification(db, notification)
    return None