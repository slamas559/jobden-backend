# app/schemas/bookmark.py
from pydantic import BaseModel
from datetime import datetime
from app.schemas.job import JobRead

class BookmarkCreate(BaseModel):
    job_id: int

class BookmarkRead(BaseModel):
    id: int
    user_id: int
    job_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class BookmarkWithJob(BookmarkRead):
    job: JobRead

    class Config:
        from_attributes = True