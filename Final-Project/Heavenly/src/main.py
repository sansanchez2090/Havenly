from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.config import settings
from repositories.database import engine
from routers import users, locations, auth, properties, bookings, payments
import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de inicio y cierre de la aplicación."""
    # Startup
    print("=" * 50)
    print(f"🚀 Iniciando {settings.app_name}")
    print(f"📍 Entorno: {settings.app_env}")
    print(f"🗄️  Base de datos: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    print(f"📦 Redis: {settings.redis_host}:{settings.redis_port}")
    print("=" * 50)
    yield
    # Shutdown
    print(f"👋 Cerrando {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    description="Plataforma de alquiler de propiedades estilo Airbnb",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan
)

app.include_router(users.router)
app.include_router(locations.router)
app.include_router(auth.router)
app.include_router(properties.router)
app.include_router(bookings.router)
app.include_router(payments.router)


@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la aplicación."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.app_env
    }

