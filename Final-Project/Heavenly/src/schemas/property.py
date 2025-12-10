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