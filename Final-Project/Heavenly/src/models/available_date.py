from sqlalchemy import Column, Integer, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base

class AvailableDate(Base):
    __tablename__ = "available_date"
    
    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_available = Column(Boolean, nullable=False)
    property_id = Column(Integer, ForeignKey("property.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    property = relationship("Property", back_populates="available_dates")