-- ====================================================================
-- VISTA MATERIALIZADA para Revenue per Available Room (RevPAR) por Región
-- ====================================================================
CREATE MATERIALIZED VIEW vm_regional_kpis
AS
WITH Property_Summary AS (
    SELECT
        region_id,
        COUNT(DISTINCT id) AS total_active_properties
    FROM property 
    WHERE is_active = TRUE
    GROUP BY region_id
),
Fact_Metrics AS (
    SELECT
        dim_date_id,
        region_id,
        SUM(nights_booked) AS total_nights_booked,
        SUM(total_revenue) AS total_revenue
    FROM fact_booking
    WHERE booking_status IN ('CONFIRMED', 'COMPLETED', 'REVIEWED')
    GROUP BY dim_date_id, region_id
)
SELECT
    dd.full_date,
    r.name AS region_name,
    fm.region_id,
    ps.total_active_properties,
    COALESCE(fm.total_nights_booked, 0) AS nights_booked,
    COALESCE(fm.total_revenue, 0) AS total_revenue,
    
    -- Cálculos de KPIs
    (COALESCE(fm.total_nights_booked, 0) * 100.0) / NULLIF(ps.total_active_properties * 1.0, 0) AS occupancy_rate,
    COALESCE(fm.total_revenue, 0) / NULLIF(COALESCE(fm.total_nights_booked, 0), 0) AS adr, -- Average Daily Rate
    COALESCE(fm.total_revenue, 0) / NULLIF(ps.total_active_properties * 1.0, 0) AS revpar
    
FROM dim_date dd
LEFT JOIN Fact_Metrics fm ON dd.id = fm.dim_date_id
LEFT JOIN region r ON fm.region_id = r.id
LEFT JOIN Property_Summary ps ON fm.region_id = ps.region_id
ORDER BY dd.full_date DESC;

CREATE UNIQUE INDEX idx_vm_revpar_pk ON vm_regional_kpis (region_id, full_date);