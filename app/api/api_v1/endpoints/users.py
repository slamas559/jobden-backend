from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user
from app.db.database import get_db


router = APIRouter()

class UserOut(BaseModel):
    id: int
    email: str
    is_employer: bool = False

@router.get("/me", response_model=UserOut)
async def read_current_user(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return current_user
