from sqlalchemy import Column, Enum, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models.enums import ReviewStatus

class ReviewResponse(Base):
    __tablename__ = "review_response"
    
    id = Column(Integer, primary_key=True, index=True)
    comment = Column(Text)
    status = Column(Enum(ReviewStatus), nullable=False)  # Usaremos el enum ReviewStatus
    review_id = Column(Integer, ForeignKey("review.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    review = relationship("Review", back_populates="response")