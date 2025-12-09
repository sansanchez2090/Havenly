from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=1, description="Contraseña del usuario")

class Token(BaseModel):
    access_token: str = Field(..., description="Token de acceso JWT")
    token_type: str = Field("bearer", description="Tipo de token")
    
