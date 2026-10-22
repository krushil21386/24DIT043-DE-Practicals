-- 6. Verify the analytical table and audit log

-- Query 1: View synchronized analytical table
SELECT *
FROM analytical_inventory
ORDER BY product_id;

-- Query 2: Inspect all captured CDC events
SELECT
    event_id,
    product_id,
    operation,
    old_data,
    new_data,
    event_time,
    processed
FROM cdc_events
ORDER BY event_id;

-- Query 3: Aggregate events count by operation
SELECT operation, COUNT(*) AS total_events
FROM cdc_events
GROUP BY operation;

-- Query 4: Check if any unprocessed events remain
SELECT *
FROM cdc_events
WHERE processed = FALSE;
