from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class City(Base):
    """
    Modelo de Ciudad - Tabla de referencia en Citus.
    Se replica en todos los workers.
    """
    __tablename__ = "city"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    
    # Relaciones
    country = relationship("Country", back_populates="cities")
    region = relationship("Region", back_populates="cities")
    properties = relationship("Property", back_populates="city")