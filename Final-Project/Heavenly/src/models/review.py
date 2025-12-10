from sqlalchemy import Column, Enum, Integer, BigInteger, Numeric, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models.enums import ReviewStatus


class Review(Base):
    """
    Modelo de Reseña - Tabla distribuida por region_id en Citus.
    """
    __tablename__ = "review"
    
    id = Column(BigInteger, primary_key=True, index=True)
    rating = Column(Numeric(2, 1), nullable=False)
    comment = Column(Text)
    status = Column(Enum(ReviewStatus, name='review_status'), nullable=False, default=ReviewStatus.APPROVED)
    user_id = Column(BigInteger, nullable=False)
    property_id = Column(BigInteger, nullable=False)
    booking_id = Column(BigInteger)  # Opcional: vincular a una reserva específica
    region_id = Column(Integer, nullable=False, primary_key=True)  # Columna de distribución
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint('rating >= 0 AND rating <= 5', name='check_rating_range'),
    )
    
    # Relaciones
    user = relationship("User", back_populates="reviews")
    property = relationship("Property", back_populates="reviews")
    response = relationship("ReviewResponse", back_populates="review", uselist=False, cascade="all, delete-orphan")