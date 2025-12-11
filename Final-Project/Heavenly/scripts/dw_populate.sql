-- ====================================================================
-- PARTE A: Población de Fechas
-- ====================================================================
CREATE OR REPLACE FUNCTION generate_date_range(start_date DATE, end_date DATE)
RETURNS SETOF dim_date AS $$
SELECT
    (EXTRACT(YEAR FROM g.d) * 10000 + EXTRACT(MONTH FROM g.d) * 100 + EXTRACT(DAY FROM g.d))::INT, 
    g.d, EXTRACT(DOW FROM g.d), TO_CHAR(g.d, 'Day'), EXTRACT(DAY FROM g.d), EXTRACT(DOY FROM g.d),
    EXTRACT(WEEK FROM g.d), EXTRACT(MONTH FROM g.d), EXTRACT(QUARTER FROM g.d), EXTRACT(YEAR FROM g.d)
FROM generate_series(start_date, end_date, '1 day'::interval) AS g(d)
$$ LANGUAGE SQL;

INSERT INTO dim_date (id, full_date, day_of_week, day_name, day_of_month, day_of_year, week_of_year, month_of_year, quarter_of_year, year)
SELECT * FROM generate_date_range('2024-01-01'::DATE, '2026-12-31'::DATE)
ON CONFLICT (id) DO NOTHING;

-- ====================================================================
-- PARTE B: Lógica de Carga Incremental (ELT)
-- Este script debería ser ejecutado por el servicio Python periódicamente.
-- ====================================================================
DO $$
DECLARE
    PLATFORM_COMMISSION_RATE NUMERIC := 0.15; 
    LAST_RUN_TIME TIMESTAMP := (CURRENT_TIMESTAMP - INTERVAL '24 hours'); 
BEGIN
    INSERT INTO fact_booking (
        dim_date_id, dim_host_id, dim_guest_id, dim_property_id, dim_currency_id, region_id, 
        nights_booked, total_revenue, host_commission, platform_commission, 
        guest_adults, guest_children, booking_status, payment_status, check_in_date
    )
    SELECT
        (EXTRACT(YEAR FROM b.check_in) * 10000 + EXTRACT(MONTH FROM b.check_in) * 100 + EXTRACT(DAY FROM b.check_in))::INT AS dim_date_id,
        p.user_id AS dim_host_id,
        b.user_id AS dim_guest_id,
        b.property_id AS dim_property_id,
        py.currency_id AS dim_currency_id, 
        b.region_id,
        b.number_nights,
        b.total_price,
        b.total_price * (1 - PLATFORM_COMMISSION_RATE) AS host_commission,
        b.total_price * PLATFORM_COMMISSION_RATE AS platform_commission,
        b.guest_adults,
        b.guest_children,
        b.status AS booking_status,
        py.status AS payment_status,
        b.check_in
        
    FROM booking b
    JOIN property p ON b.property_id = p.id 
    JOIN payment py ON b.id = py.booking_id AND b.region_id = py.region_id;
    --WHERE b.updated_at >= LAST_RUN_TIME 

    -- ON CONFLICT (booking_key, region_id) DO UPDATE SET
    --     nights_booked = EXCLUDED.nights_booked,
    --     total_revenue = EXCLUDED.total_revenue,
    --     host_commission = EXCLUDED.host_commission,
    --     platform_commission = EXCLUDED.platform_commission,
    --     booking_status = EXCLUDED.booking_status,
    --     payment_status = EXCLUDED.payment_status,
    --     check_in_date = EXCLUDED.check_in_date;

END $$;