from sqlalchemy import Column, Integer, BigInteger, String, Text, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class Property(Base):
    """
    Modelo de Propiedad - Tabla distribuida por region_id en Citus.
    """
    __tablename__ = "property"
    
    id = Column(BigInteger, primary_key=True, index=True)
    address = Column(String(255), nullable=False)
    description = Column(Text)
    property_type_id = Column(Integer, ForeignKey("property_type.id"), nullable=False)
    price_night = Column(Numeric(10, 2), nullable=False)
    max_adults = Column(Integer, nullable=False, default=2)
    max_children = Column(Integer, nullable=False, default=0)
    max_infant = Column(Integer, nullable=False, default=0)
    max_pets = Column(Integer, nullable=False, default=0)
    region_id = Column(Integer, nullable=False, primary_key=True)  # Columna de distribución
    city_id = Column(Integer, ForeignKey("city.id"), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    property_type = relationship("PropertyType", back_populates="properties")
    city = relationship("City", back_populates="properties")
    owner = relationship("User", back_populates="properties")
    amenities = relationship("Amenity", secondary="property_amenity", back_populates="properties")
    photos = relationship("PropertyPhoto", back_populates="property", cascade="all, delete-orphan")
    available_dates = relationship("AvailableDate", back_populates="property", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="property", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="property", cascade="all, delete-orphan")