from sqlalchemy import Column, Enum, Integer, BigInteger, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models.enums import UserStatus


class User(Base):
    """
    Modelo de Usuario - Tabla distribuida por region_id en Citus.
    La clave primaria compuesta (id, region_id) es requerida para tablas distribuidas.
    """
    __tablename__ = "user"
    
    id = Column(BigInteger, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, index=True)
    hash_password = Column(String(255), nullable=False)
    status = Column(Enum(UserStatus, name='user_status'), nullable=False, default=UserStatus.VERIFIED)
    phone_num = Column(String(20))
    region_id = Column(Integer, nullable=False, primary_key=True)  # Columna de distribución
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    roles = relationship("Role", secondary="user_role", back_populates="users")
    properties = relationship("Property", back_populates="owner", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"