from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, Field, validator
from models.enums import UserStatus

class City(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=50, description="city name")
    