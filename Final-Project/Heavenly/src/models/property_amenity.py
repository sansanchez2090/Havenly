from sqlalchemy import Column, Integer, BigInteger, ForeignKey, Table
from models.base import Base

# Tabla de asociación Property-Amenity - Distribuida por region_id
PropertyAmenity = Table(
    "property_amenity",
    Base.metadata,
    Column("property_id", BigInteger, primary_key=True),
    Column("amenity_id", Integer, ForeignKey("amenity.id"), primary_key=True),
    Column("region_id", Integer, primary_key=True)  # Columna de distribución
)