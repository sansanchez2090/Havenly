"""
Configuración centralizada de la aplicación usando Pydantic Settings.
Todas las variables de entorno se validan y tipan aquí.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    Los valores se cargan desde variables de entorno o archivo .env
    """
    
    # Base de datos
    db_host: str = Field(default="localhost", description="Host de la base de datos")
    db_port: int = Field(default=5434, description="Puerto de la base de datos")
    db_name: str = Field(default="heavenly", description="Nombre de la base de datos")
    db_user: str = Field(default="heavenly", description="Usuario de la base de datos")
    db_password: str = Field(default="", description="Contraseña de la base de datos")
    
    # Redis
    redis_host: str = Field(default="localhost", description="Host de Redis")
    redis_port: int = Field(default=6380, description="Puerto de Redis")
    redis_db: int = Field(default=0, description="Base de datos de Redis")
    
    # Aplicación
    app_name: str = Field(default="Heavenly", description="Nombre de la aplicación")
    app_env: str = Field(default="development", description="Entorno de la aplicación")
    debug: bool = Field(default=False, description="Modo debug")
    secret_key: str = Field(default="", description="Clave secreta de la aplicación")
    
    # JWT
    jwt_secret_key: str = Field(default="", description="Clave secreta para JWT")
    jwt_algorithm: str = Field(default="HS256", description="Algoritmo JWT")
    jwt_expiration_minutes: int = Field(default=30, description="Minutos de expiración del JWT")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def database_url(self) -> str:
        """Genera la URL de conexión a la base de datos."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def database_url_async(self) -> str:
        """Genera la URL de conexión asíncrona a la base de datos."""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def redis_url(self) -> str:
        """Genera la URL de conexión a Redis."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def is_development(self) -> bool:
        """Verifica si estamos en entorno de desarrollo."""
        return self.app_env.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Verifica si estamos en entorno de producción."""
        return self.app_env.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la configuración de la aplicación.
    Usa caché para evitar leer el archivo .env múltiples veces.
    """
    return Settings()


# Instancia global de configuración
settings = get_settings()
