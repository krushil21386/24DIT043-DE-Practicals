-- 1. Create the database tables
CREATE TABLE IF NOT EXISTS inventory (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    stock INT,
    price NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS cdc_events (
    event_id BIGSERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    operation VARCHAR(10) NOT NULL,
    old_data JSONB,
    new_data JSONB,
    event_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS analytical_inventory (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    stock INT,
    price NUMERIC(10, 2)
);
