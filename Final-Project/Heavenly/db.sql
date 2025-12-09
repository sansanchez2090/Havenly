-- REBOOT
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

-- 3. Eliminar ENUMs sin error
DROP TYPE IF EXISTS user_status CASCADE;
DROP TYPE IF EXISTS booking_status CASCADE;
DROP TYPE IF EXISTS payment_status CASCADE;
DROP TYPE IF EXISTS review_status CASCADE;



--enums 
--user_status
CREATE TYPE  user_status as ENUM('BANNED', 'VERIFIED');
---booking_status
CREATE TYPE booking_status as ENUM('PENDING', 'CONFIRMED', 'CANCELED','COMPLETED','REVIEWED');
---payment_status
CREATE TYPE payment_status as ENUM('PENDING','SUCCESSFUL','FAILED');
-- review_status 
CREATE TYPE review_status as ENUM('REPORTED','UNDER_REVIEW','APPROVED','REJECTED','HIDDEN');


-- country
CREATE TABLE IF NOT EXISTS country (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- city (Depende de country)
CREATE TABLE IF NOT EXISTS city (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    country_id INT NOT NULL,
    CONSTRAINT fk_country
        FOREIGN KEY (country_id) REFERENCES country (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- user 
-- the name user is in quotes due to is a keyword
CREATE TABLE IF NOT EXISTS "user" ( 
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    hash_password VARCHAR(255) NOT NULL,
    status user_status not null, 
    phone_num VARCHAR(20),
    status_enm VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP

);

-- role
CREATE TABLE IF NOT EXISTS role(
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);


-- property_type
CREATE TABLE IF NOT EXISTS property_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,   
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);



-- amenity

CREATE TABLE IF NOT EXISTS amenity (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- region
CREATE TABLE IF NOT EXISTS region (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);




-- payment_method
CREATE TABLE IF NOT EXISTS payment_method (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- currency
CREATE TABLE IF NOT EXISTS currency (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


---Tables that depend of others

-- user_role
CREATE TABLE IF NOT EXISTS user_role (
    user_id INT NOT NULL,
    role_id INT NOT NULL,

    PRIMARY KEY (user_id, role_id),

    -- user table forean key 
    CONSTRAINT fk_user
        FOREIGN KEY (user_id) REFERENCES "user" (id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    -- role table forean key
    CONSTRAINT fk_role
        FOREIGN KEY (role_id) REFERENCES role (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- property 
CREATE TABLE IF NOT EXISTS property (
    id SERIAL PRIMARY KEY,
    address VARCHAR(255) NOT NULL,
    description TEXT,
    property_type_id INT NOT NULL,
    price_night NUMERIC(10, 2) NOT NULL, 
    max_adults INTEGER NOT NULL,
    max_children INTEGER NOT NULL,
    max_infant INTEGER NOT NULL,
    max_pets INTEGER NOT NULL,
    region_id INT NOT NULL,
    city_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_property_type
        FOREIGN KEY (property_type_id) REFERENCES property_type (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_region
        FOREIGN KEY (region_id) REFERENCES region (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_city
        FOREIGN KEY (city_id) REFERENCES city (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_user
        FOREIGN KEY (user_id) REFERENCES "user" (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- property_amenity
CREATE TABLE IF NOT EXISTS property_amenity (
    property_id INT NOT NULL,
    amenity_id INT NOT NULL,

    PRIMARY KEY (property_id, amenity_id),

     -- property table forean key 
    CONSTRAINT fk_property
        FOREIGN KEY (property_id) REFERENCES property (id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    -- amenity table forean key
    CONSTRAINT fk_amenity
        FOREIGN KEY (amenity_id) REFERENCES amenity (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);


-- property_photo 
CREATE TABLE IF NOT EXISTS property_photo (
    id SERIAL PRIMARY KEY,
    image_url VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    property_id INT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_property
        FOREIGN KEY (property_id) REFERENCES property (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- available_date 
CREATE TABLE IF NOT EXISTS available_date (
    id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_available BOOLEAN NOT NULL,
    property_id INT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_property
        FOREIGN KEY (property_id) REFERENCES property (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);


--booking
CREATE TABLE IF NOT EXISTS booking (
    id SERIAL PRIMARY KEY,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    guest_adults INTEGER NOT NULL,
    guest_infant INTEGER NOT NULL,
    guest_children INTEGER NOT NULL,
    guest_pets INTEGER NOT NULL DEFAULT 0,
    number_nights INTEGER NOT NULL,
    total_price NUMERIC(10, 2) NOT NULL,
    status booking_status NOT NULL,
    user_id INT NOT NULL, -- FK del usuario que reserva
    property_id INT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user
        FOREIGN KEY (user_id) REFERENCES "user" (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_property
        FOREIGN KEY (property_id) REFERENCES property (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);



-- payment 
CREATE TABLE IF NOT EXISTS payment (
    id SERIAL PRIMARY KEY,
    total NUMERIC(10, 2) NOT NULL,
    status payment_status NOT NULL,
    booking_id INT NOT NULL UNIQUE,
    currency_id INT NOT NULL,
    payment_method_id INT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_booking
        FOREIGN KEY (booking_id) REFERENCES booking (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_currency
        FOREIGN KEY (currency_id) REFERENCES currency (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_payment_method
        FOREIGN KEY (payment_method_id) REFERENCES payment_method (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);


-- review 
CREATE TABLE IF NOT EXISTS review (
    id SERIAL PRIMARY KEY,
    rating NUMERIC(2, 1) NOT NULL CHECK (rating BETWEEN 0 AND 5),
    comment TEXT,
    status review_status NOT NULL,
    user_id INT NOT NULL,
    property_id INT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user
        FOREIGN KEY (user_id) REFERENCES "user" (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_property
        FOREIGN KEY (property_id) REFERENCES property (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- review_response 
CREATE TABLE IF NOT EXISTS review_response (
    id SERIAL PRIMARY KEY,
    comment TEXT,
    status review_status NOT NULL,
    review_id INT NOT NULL UNIQUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_review
        FOREIGN KEY (review_id) REFERENCES review (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

--triggers


CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at := CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- "user"
DROP TRIGGER IF EXISTS trg_set_updated_at_user ON "user";
CREATE TRIGGER trg_set_updated_at_user
BEFORE UPDATE ON "user"
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- property_type
DROP TRIGGER IF EXISTS trg_set_updated_at_property_type ON property_type;
CREATE TRIGGER trg_set_updated_at_property_type
BEFORE UPDATE ON property_type
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- amenity
DROP TRIGGER IF EXISTS trg_set_updated_at_amenity ON amenity;
CREATE TRIGGER trg_set_updated_at_amenity
BEFORE UPDATE ON amenity
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- property
DROP TRIGGER IF EXISTS trg_set_updated_at_property ON property;
CREATE TRIGGER trg_set_updated_at_property
BEFORE UPDATE ON property
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- property_photo
DROP TRIGGER IF EXISTS trg_set_updated_at_property_photo ON property_photo;
CREATE TRIGGER trg_set_updated_at_property_photo
BEFORE UPDATE ON property_photo
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- available_date
DROP TRIGGER IF EXISTS trg_set_updated_at_available_date ON available_date;
CREATE TRIGGER trg_set_updated_at_available_date
BEFORE UPDATE ON available_date
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- booking
DROP TRIGGER IF EXISTS trg_set_updated_at_booking ON booking;
CREATE TRIGGER trg_set_updated_at_booking
BEFORE UPDATE ON booking
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- payment
DROP TRIGGER IF EXISTS trg_set_updated_at_payment ON payment;
CREATE TRIGGER trg_set_updated_at_payment
BEFORE UPDATE ON payment
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- review
DROP TRIGGER IF EXISTS trg_set_updated_at_review ON review;
CREATE TRIGGER trg_set_updated_at_review
BEFORE UPDATE ON review
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- review_response
DROP TRIGGER IF EXISTS trg_set_updated_at_review_response ON review_response;
CREATE TRIGGER trg_set_updated_at_review_response
BEFORE UPDATE ON review_response
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();


