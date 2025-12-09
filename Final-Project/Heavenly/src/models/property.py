from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base

class Property(Base):
    __tablename__ = "property"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), nullable=False)
    description = Column(Text)
    property_type_id = Column(Integer, ForeignKey("property_type.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    price_night = Column(Numeric(10, 2), nullable=False)
    max_adults = Column(Integer, nullable=False)
    max_children = Column(Integer, nullable=False)
    max_infant = Column(Integer, nullable=False)
    max_pets = Column(Integer, nullable=False)
    region_id = Column(Integer, ForeignKey("region.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    city_id = Column(Integer, ForeignKey("city.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    property_type = relationship("PropertyType", back_populates="properties")
    region = relationship("Region", back_populates="properties")
    city = relationship("City", back_populates="properties")
    owner = relationship("User", back_populates="properties")
    amenities = relationship("Amenity", secondary="property_amenity", back_populates="properties")
    photos = relationship("PropertyPhoto", back_populates="property", cascade="all, delete-orphan")
    available_dates = relationship("AvailableDate", back_populates="property", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="property", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="property", cascade="all, delete-orphan")