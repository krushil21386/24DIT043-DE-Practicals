-- 2. Create the CDC trigger function
CREATE OR REPLACE FUNCTION capture_inventory_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO cdc_events
            (product_id, operation, old_data, new_data)
        VALUES
            (NEW.product_id, 'INSERT', NULL, to_jsonb(NEW));

        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO cdc_events
            (product_id, operation, old_data, new_data)
        VALUES
            (NEW.product_id, 'UPDATE',
             to_jsonb(OLD), to_jsonb(NEW));

        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO cdc_events
            (product_id, operation, old_data, new_data)
        VALUES
            (OLD.product_id, 'DELETE', to_jsonb(OLD), NULL);

        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
