# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from repositories.database import get_db
from services.user_service import UserService
from schemas.user import UserCreate, UserBase, UserUpdate
router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/", response_model=UserBase, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = UserService.create_user(db, user_data)
        return UserBase.from_orm(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserCreate)
def get_user(user_data: int, db: Session = Depends(get_db)):
    user = UserService.get_by_id(db, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserBase.from_orm(user)


@router.put("/{user_id}", response_model=UserBase)
def patch_user(user_data: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = UserService.update_user(db, user_data, payload)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserBase.from_orm(user)
