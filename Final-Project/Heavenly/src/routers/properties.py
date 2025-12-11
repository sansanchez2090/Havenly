from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from decimal import Decimal

from repositories.database import get_db
from services.property_discovery_service import PropertyDiscoveryService
from schemas.property import PropertyCreate, PropertyRes, PropertySimpleRes, PropertyUpdate
from services.property_service import PropertyService
from utils.get_current_user import get_current_user


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

@router.post("/", response_model=PropertySimpleRes, status_code=status.HTTP_201_CREATED)
def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new property listing
    """
    property = PropertyService.create_property(
        db=db,
        property_data=property_data,
        user_id=current_user["id"]
    )
    return property


@router.get("/", response_model=List[PropertySimpleRes], status_code=status.HTTP_200_OK)
def get_my_properties(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    Get all properties owned by current user
    """
    properties = PropertyService.get_user_properties(
        db=db,
        user_id=current_user["id"],
        skip=skip,
        limit=limit
    )
    return properties


@router.put("/{property_id}/{region_id}", response_model=PropertySimpleRes)
def update_property(
    property_id: int,
    region_id: int,
    update_data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update property listing
    """
    property = PropertyService.update_property(
        db=db,
        property_id=property_id,
        region_id=region_id,
        user_id=current_user["id"],
        update_data=update_data
    )
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found or you don't have permission"
        )
    
    return property


@router.delete("/{property_id}/{region_id}", status_code=status.HTTP_200_OK)
def delete_property(
    property_id: int,
    region_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete property listing (soft delete)
    """
    success = PropertyService.delete_property(
        db=db,
        property_id=property_id,
        region_id=region_id,
        user_id=current_user["id"]
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found or you don't have permission"
        )
    
    return {"message": "Property deleted successfully"}