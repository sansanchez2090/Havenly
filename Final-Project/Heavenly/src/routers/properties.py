from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from decimal import Decimal

from repositories.database import get_db
from services.property_discovery_service import PropertyDiscoveryService
from schemas.property import PropertyRes

router = APIRouter(
    prefix="/properties",
    tags=["properties"]
)


@router.get("/", response_model=List[PropertyRes], status_code=status.HTTP_200_OK)
def list_properties(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    property_type_id: Optional[int] = None,
    city_id: Optional[int] = None,
    region_id: Optional[int] = None,
    min_adults: Optional[int] = None,
    min_children: Optional[int] = None,
    min_infants: Optional[int] = None,
    min_pets: Optional[int] = None,
    amenities: Optional[List[int]] = Query(None),
    check_in: Optional[date] = None,
    check_out: Optional[date] = None,
    sort_by: str = Query("created_at", regex="^(price|rating|created_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    """
    Get properties with filtering and pagination
    """
    try:
        return PropertyDiscoveryService.list_properties(
            db=db,
            skip=skip,
            limit=limit,
            min_price=min_price,
            max_price=max_price,
            property_type_id=property_type_id,
            city_id=city_id,
            region_id=region_id,
            min_adults=min_adults,
            min_children=min_children,
            min_infants=min_infants,
            min_pets=min_pets,
            amenities=amenities,
            check_in=check_in,
            check_out=check_out,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving properties: {str(e)}"
        )


@router.get("/{property_id}", response_model=PropertyRes, status_code=status.HTTP_200_OK)
def get_property(property_id: int, db: Session = Depends(get_db)):
    """
    Get property by ID
    """
    property = PropertyDiscoveryService.get_property(db, property_id)
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    return property