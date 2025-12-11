from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from models.enums import BookingStatus, PaymentStatus


class BookingBase(BaseModel):
    property_id: int 
    check_in: date 
    check_out: date 
    guest_adults: int = Field(default=1, ge=1)
    guest_children: int = Field(default=0, ge=0)
    guest_infant: int = Field(default=0, ge=0)
    guest_pets: int = Field(default=0, ge=0)
    payment_method_id: int = Field(default=1)



class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    guest_adults: Optional[int] = None
    guest_children: Optional[int] = None
    guest_infant: Optional[int] = None
    guest_pets: Optional[int] = None
    status: Optional[BookingStatus] = None


class BookingResponse(BaseModel):
    id: int
    check_in: date
    check_out: date
    guest_adults: int
    guest_children: int
    guest_infant: int
    guest_pets: int
    number_nights: int
    total_price: Decimal
    status: BookingStatus
    user_id: int
    property_id: int
    region_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class BookingDetailResponse(BookingResponse):
    property_address: Optional[str] = None
    property_price_night: Optional[Decimal] = None
    payment_status: Optional[PaymentStatus] = None
    
    class Config:
        orm_mode = True


class AvailabilityRequest(BaseModel):
    property_id: int
    start_date: date
    end_date: date
    
  


class AvailabilityResponse(BaseModel):
    date: date
    available: bool
    price: Optional[Decimal] = None


class BookingQuery(BaseModel):
    status: Optional[BookingStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    property_id: Optional[int] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)