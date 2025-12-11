from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr 
    password: str 

class Token(BaseModel):
    access_token: str 
    token_type: str 
    
