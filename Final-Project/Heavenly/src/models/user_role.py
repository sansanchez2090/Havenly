from sqlalchemy import Column, Integer, ForeignKey, Table
from models.base import Base

UserRole = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user_.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("role.id", ondelete="RESTRICT", onupdate="CASCADE"), primary_key=True)
)