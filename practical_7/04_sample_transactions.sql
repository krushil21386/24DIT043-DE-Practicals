-- 4. Insert, update and delete sample records

-- INSERT operation
INSERT INTO inventory (product_id, product_name, stock, price)
VALUES
    (101, 'Laptop', 50, 55000.00),
    (102, 'Keyboard', 100, 1200.00);

-- UPDATE operation
UPDATE inventory
SET stock = 45
WHERE product_id = 101;

-- DELETE operation
DELETE FROM inventory
WHERE product_id = 102;
