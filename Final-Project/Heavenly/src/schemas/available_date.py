from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AvailableDateBase(BaseModel):
    start_date: date
    end_date: date
    is_available: bool = Field(default=True)
    

    
    model_config = ConfigDict(from_attributes=True)


class AvailableDateCreate(AvailableDateBase):
    property_id: int = Field(..., gt=0)
    region_id: int = Field(..., gt=0)


class AvailableDateBatchCreate(BaseModel):
    property_id: int = Field(..., gt=0)
    region_id: int = Field(..., gt=0)
    dates: List[AvailableDateBase] = Field(..., min_items=1)
    
    model_config = ConfigDict(from_attributes=True)


class AvailableDateUpdate(BaseModel):
    is_available: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    


class AvailableDateRes(AvailableDateBase):
    id: int
    property_id: int
    region_id: int
    created_at: date
    
    model_config = ConfigDict(from_attributes=True)