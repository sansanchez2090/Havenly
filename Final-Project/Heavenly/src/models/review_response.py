from sqlalchemy import Column, Enum, Integer, BigInteger, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models.enums import ReviewStatus


class ReviewResponse(Base):
    """
    Modelo de Respuesta a Reseña - Tabla distribuida por region_id en Citus.
    """
    __tablename__ = "review_response"
    
    id = Column(BigInteger, primary_key=True, index=True)
    comment = Column(Text, nullable=False)
    status = Column(Enum(ReviewStatus, name='review_status'), nullable=False, default=ReviewStatus.APPROVED)
    review_id = Column(BigInteger, nullable=False)
    region_id = Column(Integer, nullable=False, primary_key=True)  # Columna de distribución
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    review = relationship("Review", back_populates="response")