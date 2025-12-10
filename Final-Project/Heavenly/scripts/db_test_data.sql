-- =======================================================
-- WARNING: Este script asume que las tablas ya están creadas 
-- y distribuidas (si aplica) por su respectiva clave.
-- =======================================================

-- =======================================================
-- PASO 1: INSERTAR DATOS DE REFERENCIA (DIMENSIONES)
-- Corregidos errores de columnas NOT NULL faltantes (code, region_id)
-- =======================================================

-- 1. Regiones (Añadida columna 'code')
INSERT INTO region (id, name, code) VALUES 
(1, 'Andean Region', 'AND'), 
(2, 'Pacific Region', 'PAC') 
ON CONFLICT (id) DO NOTHING;

-- 2. Países y Ciudades
INSERT INTO country (id, name) VALUES (1, 'Colombia') ON CONFLICT (id) DO NOTHING;
-- Corregido: Añadida columna 'region_id' para city
INSERT INTO city (id, country_id, name, region_id) VALUES 
(1, 1, 'Bogota', 1) 
ON CONFLICT (id) DO NOTHING;

-- 3. Roles
INSERT INTO role (id, name) VALUES (1, 'Host'), (2, 'Guest') ON CONFLICT (id) DO NOTHING;

-- 4. Tipo de Propiedad
INSERT INTO property_type (id, name) VALUES (1, 'Apartment') ON CONFLICT (id) DO NOTHING;

-- 5. Moneda (Añadida columna 'code')
INSERT INTO currency (id, name, symbol, code) VALUES 
(1, 'Colombian Peso', 'COP', 'COP') 
ON CONFLICT (id) DO NOTHING;

-- 6. Método de Pago
INSERT INTO payment_method (id, name) VALUES (1, 'Credit Card') ON CONFLICT (id) DO NOTHING;

-- 7. Usuarios (Hosts y Guests)
-- Corregido: Eliminada la columna "status_enm"
INSERT INTO "user" (id, first_name, last_name, email, hash_password, status) VALUES 
(1, 'Host', 'User', 'hosta@heavenly.com', 'hashedpass', 'VERIFIED') ON CONFLICT (id) DO NOTHING;
INSERT INTO "user" (id, first_name, last_name, email, hash_password, status) VALUES 
(2, 'Guest', 'User', 'guestb@heavenly.com', 'hashedpass', 'VERIFIED') ON CONFLICT (id) DO NOTHING;

-- 8. Asignar Roles
INSERT INTO user_role (user_id, role_id) VALUES (1, 1), (2, 2) ON CONFLICT DO NOTHING;

-- 9. Propiedades (Distribuida por region_id)
INSERT INTO property (id, user_id, region_id, city_id, property_type_id, address, price_night, max_adults, max_children, max_infant, max_pets) VALUES
(101, 1, 1, 1, 1, 'Calle 100 # 10', 100.00, 4, 2, 1, 0) ON CONFLICT (id) DO NOTHING;


-- =======================================================
-- PASO 2: TRANSACCIONES (DATOS CLAVE PARA EL DW)
-- Corregido: Añadida la columna "region_id" para Citus.
-- =======================================================

-- 10. Reservas (Booking) - CLAVE DISTRIBUIDA
INSERT INTO booking (id, user_id, property_id, check_in, check_out, guest_adults, guest_infant, guest_children, number_nights, total_price, status, region_id) VALUES
(1000, 2, 101, '2025-01-10', '2025-01-13', 2, 0, 0, 3, 300.00, 'CONFIRMED', 1),
(1001, 2, 101, '2025-02-15', '2025-02-17', 2, 0, 0, 2, 200.00, 'COMPLETED', 1);


-- 11. Pagos (Payment) - CLAVE DISTRIBUIDA
-- Corregido: Usada columna 'total' en lugar de 'amount'. Añadida la columna region_id.
INSERT INTO payment (id, booking_id, currency_id, payment_method_id, total, status, region_id) VALUES
(5000, 1000, 1, 1, 300.00, 'SUCCESSFUL', 1),
(5001, 1001, 1, 1, 200.00, 'SUCCESSFUL', 1);