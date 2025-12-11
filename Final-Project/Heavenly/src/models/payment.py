from sqlalchemy import Column, Enum, Integer, BigInteger, Numeric, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models.enums import PaymentStatus


class Payment(Base):
    """
    Modelo de Pago - Tabla distribuida por region_id en Citus.
    """
    __tablename__ = "payment"
    
    id = Column(BigInteger, primary_key=True, index=True)
    total = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus, name='payment_status'), nullable=False, default=PaymentStatus.PENDING)
    booking_id = Column(BigInteger, nullable=False)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_method.id"), nullable=False)
    region_id = Column(Integer, nullable=False, primary_key=True)  # Columna de distribución
    transaction_id = Column(String(100))  # ID de transacción externa
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    booking = relationship("Booking", back_populates="payment")
    currency = relationship("Currency", back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="payments")