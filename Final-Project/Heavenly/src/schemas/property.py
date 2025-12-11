from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PropertyBase(BaseModel):
    address: str = Field(..., max_length=255, description="Dirección completa de la propiedad")
    description: Optional[str] = Field(None, description="Descripción detallada de la propiedad")
    property_type_id: int = Field(..., gt=0, description="ID del tipo de propiedad")
    price_night: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="Precio por noche")
    max_adults: int = Field(..., ge=0, description="Máximo de adultos permitidos")
    max_children: int = Field(..., ge=0, description="Máximo de niños permitidos")
    max_infant: int = Field(..., ge=0, description="Máximo de infantes permitidos")
    max_pets: int = Field(..., ge=0, description="Máximo de mascotas permitidas")
    
    
    model_config = ConfigDict(from_attributes=True)


class PropertyCreate(PropertyBase):
    region_id: int = Field(..., gt=0, description="ID de la región")
    city_id: int = Field(..., gt=0, description="ID de la ciudad")
    user_id: int = Field(..., gt=0, description="ID del propietario")

class PropertyRes(PropertyBase):
    id: int
    city: str
    country: str
    region: str 
    photos: List[str]
    host: str
    host_id: str

class PropertyCreate(BaseModel):
    address: str = Field(..., max_length=255)
    description: Optional[str] = None
    property_type_id: int = Field(..., gt=0)
    price_night: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    max_adults: int = Field(ge=0, default=2)  # SOLO default, no ...
    max_children: int = Field(ge=0, default=0)
    max_infant: int = Field(ge=0, default=0)
    max_pets: int = Field(ge=0, default=0)
    region_id: int = Field(..., gt=0)
    city_id: int = Field(..., gt=0)
    amenities: Optional[List[int]] = Field(default_factory=list)
    photo_urls: Optional[List[str]] = Field(default_factory=list)


class PropertyUpdate(BaseModel):
    address: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    property_type_id: Optional[int] = Field(None, gt=0)
    price_night: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    max_adults: Optional[int] = Field(None, ge=0)
    max_children: Optional[int] = Field(None, ge=0)
    max_infant: Optional[int] = Field(None, ge=0)
    max_pets: Optional[int] = Field(None, ge=0)
    region_id: Optional[int] = Field(None, gt=0)
    city_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    amenities: Optional[List[int]] = None
    photo_urls: Optional[List[str]] = None


class PropertySimpleRes(PropertyBase):
    id: int
    is_active: bool
    photos: List[str]
    
    model_config = ConfigDict(from_attributes=True)