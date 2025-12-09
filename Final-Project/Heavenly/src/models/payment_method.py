from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base

class PaymentMethod(Base):
    __tablename__ = "payment_method"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    
    payments = relationship("Payment", back_populates="payment_method")