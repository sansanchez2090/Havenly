from sqlalchemy import Column, Integer, BigInteger, Date, Boolean, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class AvailableDate(Base):
    """
    Modelo de Fecha Disponible - Tabla distribuida por region_id en Citus.
    """
    __tablename__ = "available_date"
    
    id = Column(BigInteger, primary_key=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    property_id = Column(BigInteger, nullable=False)
    region_id = Column(Integer, nullable=False, primary_key=True)  # Columna de distribución
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint('end_date >= start_date', name='chk_dates'),
    )
    
    # Relaciones
    property = relationship("Property", back_populates="available_dates")