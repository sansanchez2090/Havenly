from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class Region(Base):
    """
    Modelo de Región - Tabla de referencia en Citus.
    Se replica en todos los workers.
    Define las regiones de Sudamérica para la distribución de datos.
    """
    __tablename__ = "region"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), nullable=False, unique=True)  # AR, BR, CO, etc.
    worker_node = Column(String(100))  # Nombre del worker asignado
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    
    # Relaciones
    cities = relationship("City", back_populates="region")