-- ============================================================================
-- HEAVENLY DATABASE SCHEMA - CITUS DISTRIBUTED VERSION
-- ============================================================================
-- Arquitectura: Citus con distribución por región (Sudamérica)
-- Coordinator: Nodo principal que coordina las queries
-- Workers: Un worker por cada región de Sudamérica
-- ============================================================================

-- ============================================================================
-- PARTE 1: LIMPIEZA INICIAL
-- ============================================================================

-- Eliminar tablas distribuidas primero (Citus)
SELECT undistribute_table(logicalrelid::text) 
FROM pg_dist_partition 
WHERE logicalrelid::text NOT LIKE 'pg_%';

-- DROP de todas las tablas
DROP TABLE IF EXISTS review_response CASCADE;
DROP TABLE IF EXISTS review CASCADE;
DROP TABLE IF EXISTS payment CASCADE;
DROP TABLE IF EXISTS booking CASCADE;
DROP TABLE IF EXISTS available_date CASCADE;
DROP TABLE IF EXISTS property_photo CASCADE;
DROP TABLE IF EXISTS property_amenity CASCADE;
DROP TABLE IF EXISTS property CASCADE;
DROP TABLE IF EXISTS user_role CASCADE;
DROP TABLE IF EXISTS payment_method CASCADE;
DROP TABLE IF EXISTS currency CASCADE;
DROP TABLE IF EXISTS region CASCADE;
DROP TABLE IF EXISTS amenity CASCADE;
DROP TABLE IF EXISTS property_type CASCADE;
DROP TABLE IF EXISTS role CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;
DROP TABLE IF EXISTS city CASCADE;
DROP TABLE IF EXISTS country CASCADE;

-- Eliminar ENUMs
DROP TYPE IF EXISTS user_status CASCADE;
DROP TYPE IF EXISTS booking_status CASCADE;
DROP TYPE IF EXISTS payment_status CASCADE;
DROP TYPE IF EXISTS review_status CASCADE;

-- ============================================================================
-- PARTE 2: HABILITAR EXTENSION CITUS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS citus;

-- ============================================================================
-- PARTE 3: CONFIGURACIÓN DE WORKERS (Ejecutar solo en el Coordinator)
-- ============================================================================
-- NOTA: Descomentar y ajustar IPs/puertos según tu configuración
-- Cada worker representa una región de Sudamérica

-- Worker 1: Argentina (Buenos Aires)
-- SELECT citus_add_node('worker-argentina', 5432);

-- Worker 2: Brasil (São Paulo)
-- SELECT citus_add_node('worker-brasil', 5432);

-- Worker 3: Colombia (Bogotá)
-- SELECT citus_add_node('worker-colombia', 5432);

-- Worker 4: Chile (Santiago)
-- SELECT citus_add_node('worker-chile', 5432);

-- Worker 5: Perú (Lima)
-- SELECT citus_add_node('worker-peru', 5432);

-- Worker 6: Ecuador (Quito)
-- SELECT citus_add_node('worker-ecuador', 5432);

-- Para desarrollo local con Docker, usar:
-- SELECT citus_add_node('citus_worker_argentina', 5432);
-- SELECT citus_add_node('citus_worker_brasil', 5432);
-- SELECT citus_add_node('citus_worker_colombia', 5432);
-- SELECT citus_add_node('citus_worker_chile', 5432);
-- SELECT citus_add_node('citus_worker_peru', 5432);
-- SELECT citus_add_node('citus_worker_ecuador', 5432);

-- Verificar workers registrados
-- SELECT * FROM citus_get_active_worker_nodes();

-- ============================================================================
-- PARTE 4: CREAR ENUMS
-- ============================================================================

CREATE TYPE user_status AS ENUM('BANNED', 'VERIFIED');
CREATE TYPE booking_status AS ENUM('PENDING', 'CONFIRMED', 'CANCELED', 'COMPLETED', 'REVIEWED');
CREATE TYPE payment_status AS ENUM('PENDING', 'SUCCESSFUL', 'FAILED');
CREATE TYPE review_status AS ENUM('REPORTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'HIDDEN');

-- ============================================================================
-- PARTE 5: TABLAS DE REFERENCIA (Reference Tables - Replicadas en todos los workers)
-- ============================================================================
-- Las tablas de referencia se replican completamente en cada worker
-- Son tablas pequeñas y de solo lectura frecuente

-- country (Tabla de referencia)
CREATE TABLE IF NOT EXISTS country (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- region - Clave para la distribución por región de Sudamérica
CREATE TABLE IF NOT EXISTS region (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,  -- Código para identificar región (AR, BR, CO, etc.)
    worker_node VARCHAR(100),           -- Nombre del worker asignado
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- city (Tabla de referencia)
CREATE TABLE IF NOT EXISTS city (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    country_id INT NOT NULL REFERENCES country(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    region_id INT NOT NULL REFERENCES region(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- role (Tabla de referencia)
CREATE TABLE IF NOT EXISTS role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- property_type (Tabla de referencia)
CREATE TABLE IF NOT EXISTS property_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- amenity (Tabla de referencia)
CREATE TABLE IF NOT EXISTS amenity (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- payment_method (Tabla de referencia)
CREATE TABLE IF NOT EXISTS payment_method (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- currency (Tabla de referencia)
CREATE TABLE IF NOT EXISTS currency (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    symbol VARCHAR(10) NOT NULL,
    code VARCHAR(3) NOT NULL UNIQUE,  -- ISO 4217 code (USD, BRL, ARS, etc.)
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PARTE 6: MARCAR TABLAS COMO REFERENCE TABLES (Citus)
-- ============================================================================

SELECT create_reference_table('country');
SELECT create_reference_table('region');
SELECT create_reference_table('city');
SELECT create_reference_table('role');
SELECT create_reference_table('property_type');
SELECT create_reference_table('amenity');
SELECT create_reference_table('payment_method');
SELECT create_reference_table('currency');

-- ============================================================================
-- PARTE 7: TABLAS DE USUARIOS (Distribuida por user_id)
-- ============================================================================

-- user - Tabla distribuida
CREATE TABLE IF NOT EXISTS "user" (
    id BIGSERIAL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    hash_password VARCHAR(255) NOT NULL,
    status user_status NOT NULL DEFAULT 'VERIFIED',
    phone_num VARCHAR(20),
    region_id INT NOT NULL,  -- Región principal del usuario
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, region_id)
);

-- user_role - Tabla distribuida junto con user
CREATE TABLE IF NOT EXISTS user_role (
    user_id BIGINT NOT NULL,
    role_id INT NOT NULL,
    region_id INT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id, region_id)
);

-- ============================================================================
-- PARTE 8: TABLAS DE PROPIEDADES (Distribuidas por region_id)
-- ============================================================================
-- La distribución por region_id permite que todas las propiedades de una región
-- estén en el mismo worker, optimizando las búsquedas regionales

-- property - Tabla distribuida por region_id
CREATE TABLE IF NOT EXISTS property (
    id BIGSERIAL,
    address VARCHAR(255) NOT NULL,
    description TEXT,
    property_type_id INT NOT NULL,
    price_night NUMERIC(10, 2) NOT NULL,
    max_adults INTEGER NOT NULL DEFAULT 2,
    max_children INTEGER NOT NULL DEFAULT 0,
    max_infant INTEGER NOT NULL DEFAULT 0,
    max_pets INTEGER NOT NULL DEFAULT 0,
    region_id INT NOT NULL,  -- Columna de distribución
    city_id INT NOT NULL,
    user_id BIGINT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, region_id)
);

-- property_amenity - Co-localizada con property
CREATE TABLE IF NOT EXISTS property_amenity (
    property_id BIGINT NOT NULL,
    amenity_id INT NOT NULL,
    region_id INT NOT NULL,
    PRIMARY KEY (property_id, amenity_id, region_id)
);

-- property_photo - Co-localizada con property
CREATE TABLE IF NOT EXISTS property_photo (
    id BIGSERIAL,
    image_url VARCHAR(500) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    property_id BIGINT NOT NULL,
    region_id INT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, region_id)
);

-- available_date - Co-localizada con property
CREATE TABLE IF NOT EXISTS available_date (
    id BIGSERIAL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    property_id BIGINT NOT NULL,
    region_id INT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, region_id),
    CONSTRAINT chk_dates CHECK (end_date >= start_date)
);

-- ============================================================================
-- PARTE 9: TABLAS DE RESERVAS (Distribuidas por region_id)
-- ============================================================================

-- booking - Tabla distribuida por region_id (región de la propiedad)
CREATE TABLE IF NOT EXISTS booking (
    id BIGSERIAL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    guest_adults INTEGER NOT NULL DEFAULT 1,
    guest_children INTEGER NOT NULL DEFAULT 0,
    guest_infant INTEGER NOT NULL DEFAULT 0,
    guest_pets INTEGER NOT NULL DEFAULT 0,
    number_nights INTEGER NOT NULL,
    total_price NUMERIC(10, 2) NOT NULL,
    status booking_status NOT NULL DEFAULT 'PENDING',
    user_id BIGINT NOT NULL,
    property_id BIGINT NOT NULL,
    region_id INT NOT NULL,  -- Región de la propiedad
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, region_id),
    CONSTRAINT chk_booking_dates CHECK (check_out > check_in),
    CONSTRAINT chk_nights CHECK (number_nights > 0)
);

-- payment - Co-localizada con booking
CREATE TABLE IF NOT EXISTS payment (
    id BIGSERIAL,
    total NUMERIC(10, 2) NOT NULL,
    status payment_status NOT NULL DEFAULT 'PENDING',
    booking_id BIGINT NOT NULL,
    currency_id INT NOT NULL,
    payment_method_id INT NOT NULL,
    region_id INT NOT NULL,
    transaction_id VARCHAR(100),  -- ID de transacción externa
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, region_id)
);

-- ============================================================================
-- PARTE 10: TABLAS DE RESEÑAS (Distribuidas por region_id)
-- ============================================================================

-- review - Tabla distribuida por region_id
CREATE TABLE IF NOT EXISTS review (
    id BIGSERIAL,
    rating NUMERIC(2, 1) NOT NULL CHECK (rating BETWEEN 0 AND 5),
    comment TEXT,
    status review_status NOT NULL DEFAULT 'APPROVED',
    user_id BIGINT NOT NULL,
    property_id BIGINT NOT NULL,
    booking_id BIGINT,  -- Opcional: vincular a una reserva específica
    region_id INT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, region_id)
);

-- review_response - Co-localizada con review
CREATE TABLE IF NOT EXISTS review_response (
    id BIGSERIAL,
    comment TEXT NOT NULL,
    status review_status NOT NULL DEFAULT 'APPROVED',
    review_id BIGINT NOT NULL,
    region_id INT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, region_id)
);

-- ============================================================================
-- PARTE 11: DISTRIBUIR TABLAS EN CITUS
-- ============================================================================

-- Distribuir tabla de usuarios por region_id
SELECT create_distributed_table('"user"', 'region_id');
SELECT create_distributed_table('user_role', 'region_id', colocate_with => '"user"');

-- Distribuir tablas de propiedades por region_id
SELECT create_distributed_table('property', 'region_id');
SELECT create_distributed_table('property_amenity', 'region_id', colocate_with => 'property');
SELECT create_distributed_table('property_photo', 'region_id', colocate_with => 'property');
SELECT create_distributed_table('available_date', 'region_id', colocate_with => 'property');

-- Distribuir tablas de reservas por region_id
SELECT create_distributed_table('booking', 'region_id', colocate_with => 'property');
SELECT create_distributed_table('payment', 'region_id', colocate_with => 'booking');

-- Distribuir tablas de reseñas por region_id
SELECT create_distributed_table('review', 'region_id', colocate_with => 'property');
SELECT create_distributed_table('review_response', 'region_id', colocate_with => 'review');

-- ============================================================================
-- PARTE 12: CREAR ÍNDICES
-- ============================================================================

-- Índices para user
CREATE INDEX idx_user_email ON "user"(email);
CREATE INDEX idx_user_region ON "user"(region_id);

-- Índices para property
CREATE INDEX idx_property_city ON property(city_id);
CREATE INDEX idx_property_type ON property(property_type_id);
CREATE INDEX idx_property_price ON property(price_night);
CREATE INDEX idx_property_active ON property(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_property_user ON property(user_id, region_id);

-- Índices para booking
CREATE INDEX idx_booking_user ON booking(user_id, region_id);
CREATE INDEX idx_booking_property ON booking(property_id, region_id);
CREATE INDEX idx_booking_dates ON booking(check_in, check_out);
CREATE INDEX idx_booking_status ON booking(status);

-- Índices para available_date
CREATE INDEX idx_available_date_property ON available_date(property_id, region_id);
CREATE INDEX idx_available_date_range ON available_date(start_date, end_date);

-- Índices para review
CREATE INDEX idx_review_property ON review(property_id, region_id);
CREATE INDEX idx_review_user ON review(user_id, region_id);
CREATE INDEX idx_review_rating ON review(rating);

-- Índices para payment
CREATE INDEX idx_payment_booking ON payment(booking_id, region_id);
CREATE INDEX idx_payment_status ON payment(status);

-- ============================================================================
-- PARTE 13: TRIGGERS PARA updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para tablas de referencia
CREATE TRIGGER trg_set_updated_at_property_type
BEFORE UPDATE ON property_type
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_set_updated_at_amenity
BEFORE UPDATE ON amenity
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Triggers para tablas distribuidas
CREATE TRIGGER trg_set_updated_at_user
BEFORE UPDATE ON "user"
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_set_updated_at_property
BEFORE UPDATE ON property
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_set_updated_at_property_photo
BEFORE UPDATE ON property_photo
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_set_updated_at_available_date
BEFORE UPDATE ON available_date
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_set_updated_at_booking
BEFORE UPDATE ON booking
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_set_updated_at_payment
BEFORE UPDATE ON payment
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_set_updated_at_review
BEFORE UPDATE ON review
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_set_updated_at_review_response
BEFORE UPDATE ON review_response
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ============================================================================
-- PARTE 14: DATOS INICIALES DE REGIONES DE SUDAMÉRICA
-- ============================================================================

INSERT INTO region (id, name, code, worker_node) VALUES
    (1, 'Argentina', 'AR', 'worker-argentina'),
    (2, 'Brasil', 'BR', 'worker-brasil'),
    (3, 'Colombia', 'CO', 'worker-colombia'),
    (4, 'Chile', 'CL', 'worker-chile'),
    (5, 'Perú', 'PE', 'worker-peru'),
    (6, 'Ecuador', 'EC', 'worker-ecuador'),
    (7, 'Venezuela', 'VE', 'worker-venezuela'),
    (8, 'Uruguay', 'UY', 'worker-argentina'),      -- Comparte worker con Argentina
    (9, 'Paraguay', 'PY', 'worker-argentina'),     -- Comparte worker con Argentina
    (10, 'Bolivia', 'BO', 'worker-peru')           -- Comparte worker con Perú
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- Insertar países de Sudamérica
INSERT INTO country (id, name) VALUES
    (1, 'Argentina'),
    (2, 'Brasil'),
    (3, 'Colombia'),
    (4, 'Chile'),
    (5, 'Perú'),
    (6, 'Ecuador'),
    (7, 'Venezuela'),
    (8, 'Uruguay'),
    (9, 'Paraguay'),
    (10, 'Bolivia')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- Insertar ciudades principales de cada país
INSERT INTO city (id, name, description, country_id, region_id) VALUES
    -- Argentina (region_id = 1)
    (1, 'Buenos Aires', 'Capital de Argentina', 1, 1),
    (2, 'Córdoba', 'Segunda ciudad más grande de Argentina', 1, 1),
    (3, 'Mendoza', 'Región vinícola de Argentina', 1, 1),
    (4, 'Bariloche', 'Destino turístico de montaña', 1, 1),
    
    -- Brasil (region_id = 2)
    (5, 'São Paulo', 'Ciudad más grande de Brasil', 2, 2),
    (6, 'Río de Janeiro', 'Ciudad turística icónica', 2, 2),
    (7, 'Florianópolis', 'Destino de playa', 2, 2),
    (8, 'Salvador', 'Capital cultural de Brasil', 2, 2),
    
    -- Colombia (region_id = 3)
    (9, 'Bogotá', 'Capital de Colombia', 3, 3),
    (10, 'Medellín', 'Ciudad de la eterna primavera', 3, 3),
    (11, 'Cartagena', 'Ciudad histórica costera', 3, 3),
    (12, 'Cali', 'Capital de la salsa', 3, 3),
    
    -- Chile (region_id = 4)
    (13, 'Santiago', 'Capital de Chile', 4, 4),
    (14, 'Valparaíso', 'Ciudad portuaria histórica', 4, 4),
    (15, 'Viña del Mar', 'Balneario turístico', 4, 4),
    
    -- Perú (region_id = 5)
    (16, 'Lima', 'Capital de Perú', 5, 5),
    (17, 'Cusco', 'Ciudad histórica inca', 5, 5),
    (18, 'Arequipa', 'Ciudad blanca', 5, 5),
    
    -- Ecuador (region_id = 6)
    (19, 'Quito', 'Capital de Ecuador', 6, 6),
    (20, 'Guayaquil', 'Puerto principal de Ecuador', 6, 6),
    (21, 'Cuenca', 'Ciudad colonial', 6, 6)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- Insertar roles básicos
INSERT INTO role (id, name) VALUES
    (1, 'guest'),
    (2, 'host'),
    (3, 'admin')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- Insertar tipos de propiedad
INSERT INTO property_type (id, name, description) VALUES
    (1, 'Apartamento', 'Unidad de vivienda independiente'),
    (2, 'Casa', 'Casa completa'),
    (3, 'Habitación privada', 'Habitación dentro de una propiedad'),
    (4, 'Habitación compartida', 'Espacio compartido'),
    (5, 'Villa', 'Casa de lujo con jardín'),
    (6, 'Cabaña', 'Alojamiento rústico'),
    (7, 'Loft', 'Espacio abierto estilo industrial')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- Insertar amenidades comunes
INSERT INTO amenity (id, name, description) VALUES
    (1, 'WiFi', 'Internet inalámbrico de alta velocidad'),
    (2, 'Cocina', 'Cocina totalmente equipada'),
    (3, 'Aire acondicionado', 'Sistema de aire acondicionado'),
    (4, 'Calefacción', 'Sistema de calefacción'),
    (5, 'TV', 'Televisor con cable/streaming'),
    (6, 'Estacionamiento', 'Estacionamiento gratuito'),
    (7, 'Piscina', 'Piscina privada o compartida'),
    (8, 'Gimnasio', 'Acceso a gimnasio'),
    (9, 'Lavadora', 'Lavadora de ropa'),
    (10, 'Secadora', 'Secadora de ropa'),
    (11, 'Balcón', 'Balcón o terraza'),
    (12, 'Pet friendly', 'Se permiten mascotas'),
    (13, 'Desayuno', 'Desayuno incluido'),
    (14, 'Jacuzzi', 'Jacuzzi o tina de hidromasaje'),
    (15, 'Vista al mar', 'Vista al océano o mar')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- Insertar métodos de pago
INSERT INTO payment_method (id, name, description) VALUES
    (1, 'Tarjeta de crédito', 'Visa, Mastercard, Amex'),
    (2, 'Tarjeta de débito', 'Débito bancario'),
    (3, 'PayPal', 'Pago mediante PayPal'),
    (4, 'Transferencia bancaria', 'Transferencia directa'),
    (5, 'MercadoPago', 'Plataforma de pago latinoamericana'),
    (6, 'PIX', 'Sistema de pago instantáneo (Brasil)')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- Insertar monedas de Sudamérica
INSERT INTO currency (id, name, symbol, code) VALUES
    (1, 'Peso Argentino', '$', 'ARS'),
    (2, 'Real Brasileño', 'R$', 'BRL'),
    (3, 'Peso Colombiano', '$', 'COP'),
    (4, 'Peso Chileno', '$', 'CLP'),
    (5, 'Sol Peruano', 'S/', 'PEN'),
    (6, 'Dólar Estadounidense', '$', 'USD'),
    (7, 'Bolívar Venezolano', 'Bs.', 'VES'),
    (8, 'Peso Uruguayo', '$U', 'UYU'),
    (9, 'Guaraní Paraguayo', '₲', 'PYG'),
    (10, 'Boliviano', 'Bs', 'BOB')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- ============================================================================
-- PARTE 15: FUNCIONES ÚTILES PARA CITUS
-- ============================================================================

-- Función para obtener estadísticas de distribución
CREATE OR REPLACE FUNCTION get_distribution_stats()
RETURNS TABLE (
    table_name TEXT,
    shard_count BIGINT,
    total_rows BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        logicalrelid::text AS table_name,
        COUNT(*)::BIGINT AS shard_count,
        COALESCE(SUM((pg_stat_user_tables.n_live_tup)::BIGINT), 0) AS total_rows
    FROM pg_dist_shard
    JOIN pg_stat_user_tables ON pg_dist_shard.logicalrelid = pg_stat_user_tables.relid
    GROUP BY logicalrelid
    ORDER BY table_name;
END;
$$ LANGUAGE plpgsql;

-- Función para verificar co-localización de tablas
CREATE OR REPLACE FUNCTION check_colocation()
RETURNS TABLE (
    table_name TEXT,
    colocation_id INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        logicalrelid::text AS table_name,
        colocationid AS colocation_id
    FROM pg_dist_partition
    ORDER BY colocationid, table_name;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener propiedades por región
CREATE OR REPLACE FUNCTION get_properties_by_region(p_region_id INT)
RETURNS TABLE (
    property_id BIGINT,
    address VARCHAR,
    price_night NUMERIC,
    city_name VARCHAR,
    property_type VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.address,
        p.price_night,
        c.name,
        pt.name
    FROM property p
    JOIN city c ON p.city_id = c.id
    JOIN property_type pt ON p.property_type_id = pt.id
    WHERE p.region_id = p_region_id
    AND p.is_active = TRUE
    ORDER BY p.price_night;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PARTE 16: VERIFICACIÓN DE LA CONFIGURACIÓN
-- ============================================================================

-- Ver todas las tablas distribuidas
-- SELECT * FROM citus_tables;

-- Ver shards por tabla
-- SELECT * FROM citus_shards ORDER BY table_name, shard_name;

-- Ver workers activos
-- SELECT * FROM citus_get_active_worker_nodes();

-- Verificar distribución
-- SELECT get_distribution_stats();

-- Verificar co-localización
-- SELECT check_colocation();

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Schema de Heavenly con Citus creado exitosamente';
    RAISE NOTICE 'Regiones de Sudamérica configuradas: 10';
    RAISE NOTICE 'Ciudades insertadas: 21';
    RAISE NOTICE '============================================';
END $$;
