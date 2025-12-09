from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base, TimestampMixin

class City(Base):
    __tablename__ = "city"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country_id = Column(Integer, ForeignKey("country.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    
    country = relationship("Country", back_populates="cities")
    users = relationship("User", back_populates="city")
    properties = relationship("Property", back_populates="city")