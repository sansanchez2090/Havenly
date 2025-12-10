from sqlalchemy import Column, Enum, Integer, BigInteger, Date, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models.enums import BookingStatus


class Booking(Base):
    """
    Modelo de Reserva - Tabla distribuida por region_id en Citus.
    """
    __tablename__ = "booking"
    
    id = Column(BigInteger, primary_key=True, index=True)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    guest_adults = Column(Integer, nullable=False, default=1)
    guest_children = Column(Integer, nullable=False, default=0)
    guest_infant = Column(Integer, nullable=False, default=0)
    guest_pets = Column(Integer, nullable=False, default=0)
    number_nights = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(BookingStatus, name='booking_status'), nullable=False, default=BookingStatus.PENDING)
    user_id = Column(BigInteger, nullable=False)
    property_id = Column(BigInteger, nullable=False)
    region_id = Column(Integer, nullable=False, primary_key=True)  # Columna de distribución
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="bookings")
    property = relationship("Property", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")