from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base

class PropertyPhoto(Base):
    __tablename__ = "property_photo"
    
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)
    property_id = Column(Integer, ForeignKey("property.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    property = relationship("Property", back_populates="photos")