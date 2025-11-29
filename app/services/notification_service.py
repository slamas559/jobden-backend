# app/services/notification_service.py
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


async def create_notification(
    db: AsyncSession,
    notification_data: NotificationCreate
) -> Notification:
    """Create a new notification and send via WebSocket"""
    notification = Notification(
        user_id=notification_data.user_id,
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        related_id=notification_data.related_id
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    # Send real-time notification via WebSocket
    from app.core.websocket_manager import manager
    await manager.send_notification(
        notification={
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "related_id": notification.related_id,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat()
        },
        user_id=notification_data.user_id
    )
    
    return notification


async def get_user_notifications(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False
) -> List[Notification]:
    """Get all notifications for a user"""
    stmt = select(Notification).where(Notification.user_id == user_id)
    
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)
    
    stmt = stmt.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_notification_by_id(
    db: AsyncSession,
    notification_id: int
) -> Optional[Notification]:
    """Get a specific notification by ID"""
    stmt = select(Notification).where(Notification.id == notification_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def mark_notification_as_read(
    db: AsyncSession,
    notification: Notification
) -> Notification:
    """Mark a notification as read"""
    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


async def mark_all_notifications_as_read(
    db: AsyncSession,
    user_id: int
) -> int:
    """Mark all notifications as read for a user"""
    stmt = select(Notification).where(
        Notification.user_id == user_id,
        Notification.is_read == False
    )
    result = await db.execute(stmt)
    notifications = result.scalars().all()
    
    count = 0
    for notification in notifications:
        notification.is_read = True
        count += 1
    
    await db.commit()
    return count


async def delete_notification(
    db: AsyncSession,
    notification: Notification
) -> None:
    """Delete a notification"""
    await db.delete(notification)
    await db.commit()


async def get_unread_count(
    db: AsyncSession,
    user_id: int
) -> int:
    """Get count of unread notifications"""
    stmt = select(func.count(Notification.id)).where(
        Notification.user_id == user_id,
        Notification.is_read == False
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def create_application_notification(
    db: AsyncSession,
    user_id: int,
    job_title: str,
    application_id: int
) -> Notification:
    """Helper to create application confirmation notification"""
    return await create_notification(
        db,
        NotificationCreate(
            user_id=user_id,
            title="Application Submitted",
            message=f"Your application for '{job_title}' has been submitted successfully.",
            notification_type="application",
            related_id=application_id
        )
    )