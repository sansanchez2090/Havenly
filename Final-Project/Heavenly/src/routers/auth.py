from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated, List
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from repositories.database import get_db  # Cambié de repositories.database a src.database
from services.auth_service import AuthService
from schemas.auth import Token
from fastapi import Depends

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/", response_model=Token, status_code=status.HTTP_200_OK)
def authenticate(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)  
):
    return AuthService.authenticate(db, form_data)
