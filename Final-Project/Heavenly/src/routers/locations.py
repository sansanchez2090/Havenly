from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from repositories.database import get_db  
from services.location_service import LocationService
from schemas.location import City 
router = APIRouter(
    prefix="/locations",
    tags=["locations"]
)

@router.get("/", response_model=List[City], status_code=status.HTTP_200_OK)
def list_cities(db: Session = Depends(get_db)):
    """Obtener todas las ciudades"""
    return LocationService.list_cities(db) 

