-- ==============================================================================
-- SCRIPT DE CONFIGURACIÓN DE CITUS DESPUÉS DE CREAR EL SCHEMA
-- ==============================================================================
-- Este script se ejecuta después de db_citus.sql
-- Configura la replicación y ajustes de Citus
-- ==============================================================================

-- Configuraciones de rendimiento de Citus
SET citus.shard_count = 6;  -- Un shard por worker (por región)
SET citus.shard_replication_factor = 1;  -- Sin replicación por ahora

-- Habilitar estadísticas de ejecución
SET citus.explain_all_tasks = true;

-- Configurar el modo de ejecución
SET citus.multi_shard_modify_mode = 'parallel';

-- Verificar configuración actual
SELECT name, setting, unit, short_desc 
FROM pg_settings 
WHERE name LIKE 'citus%'
ORDER BY name;

-- ==============================================================================
-- INFORMACIÓN DEL CLUSTER
-- ==============================================================================

DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE 'CONFIGURACIÓN DE CITUS COMPLETADA';
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Coordinator: localhost:5432';
    RAISE NOTICE 'Workers esperados: 6 (uno por región)';
    RAISE NOTICE '  - Argentina (region_id=1)';
    RAISE NOTICE '  - Brasil (region_id=2)';
    RAISE NOTICE '  - Colombia (region_id=3)';
    RAISE NOTICE '  - Chile (region_id=4)';
    RAISE NOTICE '  - Perú (region_id=5)';
    RAISE NOTICE '  - Ecuador (region_id=6)';
    RAISE NOTICE '============================================';
END $$;
