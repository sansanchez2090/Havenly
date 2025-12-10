-- ====================================================================
-- DW: Dimension Time (Dim_Date)
-- ====================================================================
CREATE TABLE IF NOT EXISTS dim_date (
    id INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_week SMALLINT,
    day_name VARCHAR(9),
    day_of_month SMALLINT,
    day_of_year SMALLINT,
    week_of_year SMALLINT,
    month_of_year SMALLINT,
    quarter_of_year SMALLINT,
    year SMALLINT
);
SELECT create_reference_table('dim_date');

-- ====================================================================
-- DW: Tabla de Hechos (Fact_Booking)
-- ====================================================================
CREATE TABLE IF NOT EXISTS fact_booking (
    booking_key BIGSERIAL,
    dim_date_id INT NOT NULL REFERENCES dim_date(id),
    dim_host_id BIGINT NOT NULL,
    dim_guest_id BIGINT NOT NULL,
    dim_property_id BIGINT NOT NULL,
    dim_currency_id INT NOT NULL, 
    region_id INT NOT NULL,
    nights_booked INT NOT NULL,
    total_revenue NUMERIC(10, 2) NOT NULL,
    host_commission NUMERIC(10, 2) NOT NULL,         
    platform_commission NUMERIC(10, 2) NOT NULL,     
    guest_adults INT NOT NULL,
    guest_children INT NOT NULL,
    booking_status booking_status NOT NULL,          
    payment_status payment_status NOT NULL,
    check_in_date DATE NOT NULL,
    PRIMARY KEY (booking_key, region_id)
);
SELECT create_distributed_table('fact_booking', 'region_id', colocate_with => 'booking');