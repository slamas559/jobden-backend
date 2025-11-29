# app/schemas/notification.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    notification_type: Optional[str] = None
    related_id: Optional[int] = None

class NotificationRead(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: Optional[str]
    related_id: Optional[int]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    is_read: bool