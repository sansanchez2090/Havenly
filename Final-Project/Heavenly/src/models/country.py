from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base

class Country(Base):
    __tablename__ = "country"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    cities = relationship("City", back_populates="country", cascade="all, delete-orphan")