from sqlalchemy import Column, Enum, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models.enums import UserStatus

class User(Base):
    __tablename__ = "user_" 
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    photo_url = Column(String(255), nullable=False)
    hash_password = Column(String(255), nullable=False)
    status = Column(Enum(UserStatus), nullable=False)  
    phone_num = Column(String(20))
    area_code = Column(String(10))
    city_id = Column(Integer, ForeignKey("city.id"),nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    
    city = relationship("City", back_populates="users")
    roles = relationship("Role", secondary="user_role", back_populates="users")
    properties = relationship("Property", back_populates="owner", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"