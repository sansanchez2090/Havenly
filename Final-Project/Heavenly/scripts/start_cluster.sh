#!/bin/bash
# ==============================================================================
# SCRIPT DE INICIO DEL CLUSTER CITUS - HEAVENLY
# ==============================================================================
# Este script configura y ejecuta todo el cluster de Citus en Docker
# ==============================================================================

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   HEAVENLY - CLUSTER CITUS SETUP${NC}"
echo -e "${BLUE}============================================${NC}"

# ==============================================================================
# PASO 1: Verificar Docker
# ==============================================================================
echo -e "\n${YELLOW}[1/6] Verificando Docker...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker no está instalado${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker está instalado y funcionando${NC}"

# ==============================================================================
# PASO 2: Detener contenedores anteriores si existen
# ==============================================================================
echo -e "\n${YELLOW}[2/6] Limpiando contenedores anteriores...${NC}"

cd "$PROJECT_DIR"

# Usar docker compose o docker-compose según disponibilidad
if docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

$DOCKER_COMPOSE down -v --remove-orphans 2>/dev/null || true

echo -e "${GREEN}✓ Contenedores anteriores eliminados${NC}"

# ==============================================================================
# PASO 3: Crear archivo .env si no existe
# ==============================================================================
echo -e "\n${YELLOW}[3/6] Configurando variables de entorno...${NC}"

if [ ! -f "$PROJECT_DIR/.env" ]; then
    cat > "$PROJECT_DIR/.env" << EOF
# ==============================================================================
# HEAVENLY - VARIABLES DE ENTORNO
# ==============================================================================

# Base de datos Citus
POSTGRES_USER=heavenly
POSTGRES_PASSWORD=heavenly_secret_2024
POSTGRES_DB=heavenly

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Aplicación
APP_ENV=development
DEBUG=true
EOF
    echo -e "${GREEN}✓ Archivo .env creado${NC}"
else
    echo -e "${GREEN}✓ Archivo .env ya existe${NC}"
fi

# ==============================================================================
# PASO 4: Construir e iniciar los contenedores
# ==============================================================================
echo -e "\n${YELLOW}[4/6] Iniciando cluster de Citus...${NC}"
echo -e "${BLUE}Esto puede tomar varios minutos la primera vez...${NC}"

$DOCKER_COMPOSE up -d

echo -e "${GREEN}✓ Contenedores iniciados${NC}"

# ==============================================================================
# PASO 5: Esperar a que los servicios estén listos
# ==============================================================================
echo -e "\n${YELLOW}[5/6] Esperando a que los servicios estén listos...${NC}"

# Función para esperar a PostgreSQL
wait_for_postgres() {
    local host=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec citus_coordinator pg_isready -U heavenly -d heavenly &> /dev/null; then
            return 0
        fi
        echo -e "  Esperando coordinator... (intento $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    return 1
}

if wait_for_postgres "citus_coordinator"; then
    echo -e "${GREEN}✓ Coordinator está listo${NC}"
else
    echo -e "${RED}Error: El coordinator no está respondiendo${NC}"
    exit 1
fi

# Esperar un poco más para que el manager registre los workers
echo -e "  Esperando registro de workers..."
sleep 15

# ==============================================================================
# PASO 6: Verificar el cluster
# ==============================================================================
echo -e "\n${YELLOW}[6/6] Verificando configuración del cluster...${NC}"

echo -e "\n${BLUE}Workers activos:${NC}"
docker exec citus_coordinator psql -U heavenly -d heavenly -c \
    "SELECT * FROM citus_get_active_worker_nodes();" 2>/dev/null || echo "Verificando workers..."

echo -e "\n${BLUE}Tablas distribuidas:${NC}"
docker exec citus_coordinator psql -U heavenly -d heavenly -c \
    "SELECT table_name, citus_table_type, distribution_column 
     FROM citus_tables 
     ORDER BY table_name;" 2>/dev/null || echo "Verificando tablas..."

echo -e "\n${BLUE}Regiones configuradas:${NC}"
docker exec citus_coordinator psql -U heavenly -d heavenly -c \
    "SELECT id, name, code, worker_node FROM region ORDER BY id;" 2>/dev/null || echo "Verificando regiones..."

# ==============================================================================
# RESUMEN FINAL
# ==============================================================================
echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}   ¡CLUSTER CITUS INICIADO EXITOSAMENTE!${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e ""
echo -e "${BLUE}Conexión al Coordinator:${NC}"
echo -e "  Host:     localhost"
echo -e "  Puerto:   5432"
echo -e "  Usuario:  heavenly"
echo -e "  Password: heavenly_secret_2024"
echo -e "  Database: heavenly"
echo -e ""
echo -e "${BLUE}Conexión a Redis:${NC}"
echo -e "  Host:     localhost"
echo -e "  Puerto:   6379"
echo -e ""
echo -e "${BLUE}Comandos útiles:${NC}"
echo -e "  Ver logs:           $DOCKER_COMPOSE logs -f"
echo -e "  Detener cluster:    $DOCKER_COMPOSE down"
echo -e "  Reiniciar:          $DOCKER_COMPOSE restart"
echo -e "  Conectar a psql:    docker exec -it citus_coordinator psql -U heavenly -d heavenly"
echo -e ""
echo -e "${BLUE}Estado de los contenedores:${NC}"
$DOCKER_COMPOSE ps
