from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base

class Currency(Base):
    __tablename__ = "currency"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    symbol = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    
    payments = relationship("Payment", back_populates="currency")