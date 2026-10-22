-- 7. Supplementary problem: Add row version numbers
ALTER TABLE inventory
ADD COLUMN IF NOT EXISTS row_version INT NOT NULL DEFAULT 1;

ALTER TABLE cdc_events
ADD COLUMN IF NOT EXISTS row_version INT;

ALTER TABLE analytical_inventory
ADD COLUMN IF NOT EXISTS row_version INT NOT NULL DEFAULT 1;

ALTER TABLE analytical_inventory
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT FALSE;

-- 7.1 Increment version on every update
CREATE OR REPLACE FUNCTION set_inventory_version()
RETURNS TRIGGER AS $$
BEGIN
    NEW.row_version := OLD.row_version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS inventory_version_trigger ON inventory;

CREATE TRIGGER inventory_version_trigger
BEFORE UPDATE ON inventory
FOR EACH ROW
EXECUTE FUNCTION set_inventory_version();

-- 7.2 Update the CDC trigger function to record versions
CREATE OR REPLACE FUNCTION capture_inventory_changes()
RETURNS TRIGGER AS $$
DECLARE
    v_version INT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        v_version := NEW.row_version;

        INSERT INTO cdc_events
            (product_id, operation, old_data, new_data, row_version)
        VALUES
            (NEW.product_id, 'INSERT', NULL,
             to_jsonb(NEW), v_version);

        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        v_version := NEW.row_version;

        INSERT INTO cdc_events
            (product_id, operation, old_data, new_data, row_version)
        VALUES
            (NEW.product_id, 'UPDATE',
             to_jsonb(OLD), to_jsonb(NEW), v_version);

        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        v_version := OLD.row_version + 1;

        INSERT INTO cdc_events
            (product_id, operation, old_data, new_data, row_version)
        VALUES
            (OLD.product_id, 'DELETE',
             to_jsonb(OLD), NULL, v_version);

        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
