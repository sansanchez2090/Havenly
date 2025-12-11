from pydantic import BaseModel

class PaymentResponse(BaseModel):
    id: int
    total: float
    status: str
    booking_id: int
    transaction_id: str
    
    class Config:
        orm_mode = True