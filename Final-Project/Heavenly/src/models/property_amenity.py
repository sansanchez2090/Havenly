from sqlalchemy import Column, Integer, ForeignKey, Table
from models.base import Base

PropertyAmenity = Table(
    "property_amenity",
    Base.metadata,
    Column("property_id", Integer, ForeignKey("property.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    Column("amenity_id", Integer, ForeignKey("amenity.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
)