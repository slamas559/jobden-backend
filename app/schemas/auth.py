# app/schemas/auth.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_employer: Optional[bool] = False

class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_employer: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
