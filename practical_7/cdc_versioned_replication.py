"""
Version-Aware CDC Replication with Deduplication
Course: Data Engineering Lab (Practical 7 Supplementary Problem)
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", 5432)),
    "dbname": os.getenv("PG_DB", "postgres"),
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASSWORD", "postgrespassword")
}

def replicate_versioned_events():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Lock and read pending events in order
                cur.execute("""
                    SELECT *
                    FROM cdc_events
                    WHERE processed = FALSE
                    ORDER BY event_id
                    FOR UPDATE;
                """)
                events = cur.fetchall()
                print(f"[*] Found {len(events)} pending versioned CDC events.")

                for event in events:
                    operation = event["operation"]
                    version = event["row_version"]
                    old_data = event["old_data"]
                    new_data = event["new_data"]

                    if version is None:
                        raise ValueError(f"Event {event['event_id']} has no version")

                    if operation in ("INSERT", "UPDATE"):
                        cur.execute("""
                            INSERT INTO analytical_inventory
                                (product_id, product_name, stock, price, row_version, is_deleted)
                            VALUES (%s, %s, %s, %s, %s, FALSE)
                            ON CONFLICT (product_id)
                            DO UPDATE SET
                                product_name = EXCLUDED.product_name,
                                stock = EXCLUDED.stock,
                                price = EXCLUDED.price,
                                row_version = EXCLUDED.row_version,
                                is_deleted = FALSE
                            WHERE analytical_inventory.row_version < EXCLUDED.row_version;
                        """, (
                            new_data["product_id"],
                            new_data["product_name"],
                            new_data["stock"],
                            new_data["price"],
                            version
                        ))

                    elif operation == "DELETE":
                        cur.execute("""
                            INSERT INTO analytical_inventory
                                (product_id, product_name, stock, price, row_version, is_deleted)
                            VALUES (%s, %s, %s, %s, %s, TRUE)
                            ON CONFLICT (product_id)
                            DO UPDATE SET
                                row_version = EXCLUDED.row_version,
                                is_deleted = TRUE
                            WHERE analytical_inventory.row_version < EXCLUDED.row_version;
                        """, (
                            old_data["product_id"],
                            old_data["product_name"],
                            old_data["stock"],
                            old_data["price"],
                            version
                        ))

                    cur.execute("""
                        UPDATE cdc_events
                        SET processed = TRUE
                        WHERE event_id = %s;
                    """, (event["event_id"],))

                    print(f"Event {event['event_id']} (v{version}): {operation} replicated")

        print("Version-aware CDC replication completed successfully.")
    except Exception:
        print("Replication failed.")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    replicate_versioned_events()
