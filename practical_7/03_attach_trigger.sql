-- 3. Attach the trigger
DROP TRIGGER IF EXISTS inventory_cdc_trigger ON inventory;

CREATE TRIGGER inventory_cdc_trigger
AFTER INSERT OR UPDATE OR DELETE
ON inventory
FOR EACH ROW
EXECUTE FUNCTION capture_inventory_changes();
