from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from repositories.database import get_db
from services.booking_service import BookingService
from schemas.booking import (
    BookingCreate, 
    BookingResponse, 
    BookingDetailResponse,
    BookingUpdate,
    AvailabilityRequest,
    AvailabilityResponse,
    BookingQuery
)
from models.enums import BookingStatus
from utils.get_current_user import get_current_user
from models.user import User

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    try:
        booking_service = BookingService(db)
        
        # Verificar doble reserva específica (FR4.2)
        if booking_service.check_double_booking(
            user_id=current_user.id,
            property_id=booking_data.property_id,
            check_in=booking_data.check_in,
            check_out=booking_data.check_out
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have a booking for this property on the selected dates"
            )
        
        booking = booking_service.create_booking(booking_data, current_user.id)
        return booking
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating booking: {str(e)}"
        )


@router.get("/availability", response_model=List[AvailabilityResponse])
def check_availability(
    property_id: int = Query(..., description="ID de la propiedad"),
    start_date: date = Query(..., description="Fecha inicial"),
    end_date: date = Query(..., description="Fecha final"),
    db: Session = Depends(get_db)
):
    
    try:
        if start_date >= end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be before end_date"
            )
        
        booking_service = BookingService(db)
        availability = booking_service.get_property_availability(
            property_id, start_date, end_date
        )
        return availability
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=List[BookingResponse])
def get_my_bookings(
    status: Optional[BookingStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
  
    try:
        booking_service = BookingService(db)
        bookings = booking_service.get_user_bookings(current_user.id, status)
        return bookings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{booking_id}", response_model=BookingDetailResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    booking_service = BookingService(db)
    booking = booking_service.get_booking_by_id(booking_id, current_user.id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found or access denied"
        )
    
    # Enriquecer respuesta con información adicional
    response = BookingDetailResponse.from_orm(booking)
    
    # Obtener información de la propiedad
    from models.property import Property
    property = db.query(Property).filter(Property.id == booking.property_id).first()
    if property:
        response.property_address = property.address
        response.property_price_night = property.price_night
    
    # Obtener información del pago
    from models.payment import Payment
    payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    if payment:
        response.payment_status = payment.status
    
    return response


@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    try:
        booking_service = BookingService(db)
        booking = booking_service.update_booking_status(
            booking_id, 
            BookingStatus.CANCELED,
            current_user.id
        )
        return booking
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/property/{property_id}", response_model=List[BookingResponse])
def get_property_bookings(
    property_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
  
    from models.property import Property
    property = db.query(Property).filter(
        Property.id == property_id,
        Property.user_id == current_user.id
    ).first()
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found or access denied"
        )
    
    try:
        booking_service = BookingService(db)
        bookings = booking_service.get_property_bookings(
            property_id, start_date, end_date
        )
        return bookings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/validate", status_code=status.HTTP_200_OK)
def validate_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db)
):
    
    try:
        booking_service = BookingService(db)
        
        # Verificar disponibilidad
        available = booking_service.is_property_available(
            booking_data.property_id,
            booking_data.check_in,
            booking_data.check_out
        )
        
        if not available:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Property not available for selected dates"
            )
        
        # Validar capacidad
        valid_capacity = booking_service.validate_guest_capacity(
            booking_data.property_id,
            booking_data.guest_adults,
            booking_data.guest_children,
            booking_data.guest_infant,
            booking_data.guest_pets
        )
        
        if not valid_capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exceeds property guest capacity"
            )
        
        # Calcular precio
        total_price = booking_service.calculate_total_price(
            booking_data.property_id,
            booking_data.check_in,
            booking_data.check_out,
            booking_data.guest_adults,
            booking_data.guest_children,
            booking_data.guest_infant,
            booking_data.guest_pets
        )
        
        nights = (booking_data.check_out - booking_data.check_in).days
        
        return {
            "available": True,
            "total_price": total_price,
            "number_nights": nights,
            "valid_capacity": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )