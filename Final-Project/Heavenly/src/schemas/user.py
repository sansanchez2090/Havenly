from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, Field, validator
from models.enums import UserStatus

class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, description="Nombre del usuario")
    last_name: str = Field(..., min_length=1, max_length=50, description="Apellido del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    phone_num: Optional[str] = Field(None, max_length=20, description="Número de teléfono")
    area_code: Optional[str] = Field(None, max_length=10, description="Código de área")
    photo_url: Optional[str] = Field(None, max_length=255)
    city_id: int = Field(..., gt=0, description="ID de la ciudad")
    
    
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Contraseña del usuario (mínimo 8 caracteres)"
    )

   
   

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone_num: Optional[str] = Field(None, max_length=20)
    area_code: Optional[str] = Field(None, max_length=10)
    city_id: Optional[int] = Field(None, gt=0)
    photo_url: Optional[str] = Field(None, max_length=255)
    status: Optional[UserStatus] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserBase):
    id: int
    photo_url: str
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
