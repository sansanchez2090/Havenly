"""
Configuración de la conexión a la base de datos PostgreSQL (Citus).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Annotated, Generator
from fastapi import Depends

from core.config import settings


# Crear el engine de SQLAlchemy
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=10,        # Tamaño del pool de conexiones
    max_overflow=20,     # Conexiones adicionales permitidas
    echo=settings.debug  # Muestra queries SQL en modo debug
)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency que proporciona una sesión de base de datos.
    La sesión se cierra automáticamente al finalizar la request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Type alias para usar en los endpoints
db_dependency = Annotated[Session, Depends(get_db)]