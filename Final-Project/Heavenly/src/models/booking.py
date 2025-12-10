from sqlalchemy import Column, Enum, Integer, Date, Numeric, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models.enums import BookingStatus
import enum

class Booking(Base):
    __tablename__ = "booking"
    
    id = Column(Integer, primary_key=True, index=True)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    guest_adults = Column(Integer, nullable=False)
    guest_infant = Column(Integer, nullable=False)
    guest_children = Column(Integer, nullable=False)
    guest_pets = Column(Integer, default=0)
    number_nights = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(BookingStatus), nullable=False)  # Usaremos el enum BookingStatus
    user_id = Column(Integer, ForeignKey("user_.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    property_id = Column(Integer, ForeignKey("property.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="bookings")
    property = relationship("Property", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")