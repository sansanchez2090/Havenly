from sqlalchemy import Column, Integer, BigInteger, ForeignKey, DateTime, Table
from sqlalchemy.sql import func
from models.base import Base

# Tabla de asociación User-Role - Distribuida por region_id
UserRole = Table(
    "user_role",
    Base.metadata,
    Column("user_id", BigInteger, primary_key=True),
    Column("role_id", Integer, ForeignKey("role.id"), primary_key=True),
    Column("region_id", Integer, primary_key=True),  # Columna de distribución
    Column("created_at", DateTime(timezone=False), server_default=func.now())
)