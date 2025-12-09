from sqlalchemy import Column, Enum, Integer, Numeric, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models.enums import PaymentStatus
import enum

class Payment(Base):
    __tablename__ = "payment"
    
    id = Column(Integer, primary_key=True, index=True)
    total = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False)  # Usaremos el enum PaymentStatus
    booking_id = Column(Integer, ForeignKey("booking.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, unique=True)
    currency_id = Column(Integer, ForeignKey("currency.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_method.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    booking = relationship("Booking", back_populates="payment")
    currency = relationship("Currency", back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="payments")