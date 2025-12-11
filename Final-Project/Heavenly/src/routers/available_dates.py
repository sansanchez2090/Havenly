# routers/availability.py
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from repositories.database import get_db
from services.availability_service import AvailabilityService
from schemas.available_date import (
    AvailableDateCreate, AvailableDateBatchCreate, 
    AvailableDateUpdate, AvailableDateRes
)
from utils.get_current_user import get_current_user

router = APIRouter(
    prefix="/host/availability",
    tags=["availability-management"]
)


@router.post("/", response_model=AvailableDateRes, status_code=status.HTTP_201_CREATED)
def create_availability(
    availability_data: AvailableDateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create availability date range for a property
    """
    return AvailabilityService.create_availability(
        db=db,
        availability_data=availability_data,
        user_id=current_user["id"]
    )


@router.post("/batch", response_model=List[AvailableDateRes], status_code=status.HTTP_201_CREATED)
def create_batch_availability(
    batch_data: AvailableDateBatchCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create multiple availability date ranges for a property
    """
    return AvailabilityService.create_batch_availability(
        db=db,
        batch_data=batch_data,
        user_id=current_user["id"]
    )


@router.get("/property/{property_id}/{region_id}", response_model=List[AvailableDateRes])
def get_property_availability(
    property_id: int,
    region_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    is_available: Optional[bool] = Query(None)
):
    """
    Get availability calendar for a property
    """
    return AvailabilityService.get_property_availability(
        db=db,
        property_id=property_id,
        region_id=region_id,
        user_id=current_user["id"],
        start_date=start_date,
        end_date=end_date,
        is_available=is_available
    )


@router.put("/{availability_id}/{region_id}", response_model=AvailableDateRes)
def update_availability(
    availability_id: int,
    region_id: int,
    update_data: AvailableDateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update availability date range
    """
    availability = AvailabilityService.update_availability(
        db=db,
        availability_id=availability_id,
        region_id=region_id,
        update_data=update_data,
        user_id=current_user["id"]
    )
    
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability not found or you don't have permission"
        )
    
    return availability


@router.delete("/{availability_id}/{region_id}", status_code=status.HTTP_200_OK)
def delete_availability(
    availability_id: int,
    region_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete availability date range
    """
    success = AvailabilityService.delete_availability(
        db=db,
        availability_id=availability_id,
        region_id=region_id,
        user_id=current_user["id"]
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability not found or you don't have permission"
        )
    
    return {"message": "Availability deleted successfully"}