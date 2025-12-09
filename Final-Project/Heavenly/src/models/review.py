from sqlalchemy import Column, Enum, Integer, Numeric, String, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models.enums import ReviewStatus

class Review(Base):
    __tablename__ = "review"
    
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Numeric(2, 1), nullable=False)
    comment = Column(Text)
    status = Column(Enum(ReviewStatus), nullable=False)  # Usaremos el enum ReviewStatus
    user_id = Column(Integer, ForeignKey("user_.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    property_id = Column(Integer, ForeignKey("property.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint('rating >= 0 AND rating <= 5', name='check_rating_range'),
    )
    
    user = relationship("User", back_populates="reviews")
    property = relationship("Property", back_populates="reviews")
    response = relationship("ReviewResponse", back_populates="review", uselist=False, cascade="all, delete-orphan")