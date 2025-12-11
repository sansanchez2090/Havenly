from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class PropertyPhoto(Base):
    """
    Modelo de Foto de Propiedad - Tabla distribuida por region_id en Citus.
    """
    __tablename__ = "property_photo"
    
    id = Column(BigInteger, primary_key=True, index=True)
    image_url = Column(String(500), nullable=False)
    is_primary = Column(Boolean, default=False)
    property_id = Column(BigInteger, nullable=False)
    region_id = Column(Integer, nullable=False, primary_key=True)  # Columna de distribución
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    property = relationship("Property", back_populates="photos")