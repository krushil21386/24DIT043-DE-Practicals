"""
CDC Replication Engine: Replays captured CDC events onto analytical replica table.
Course: Data Engineering Lab (Practical 7)
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

def replicate_cdc_events():
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
                print(f"[*] Found {len(events)} pending CDC events to replicate.")

                for event in events:
                    operation = event["operation"]
                    new_data = event["new_data"]
                    old_data = event["old_data"]

                    if operation in ("INSERT", "UPDATE"):
                        cur.execute("""
                            INSERT INTO analytical_inventory
                                (product_id, product_name, stock, price)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (product_id)
                            DO UPDATE SET
                                product_name = EXCLUDED.product_name,
                                stock = EXCLUDED.stock,
                                price = EXCLUDED.price;
                        """, (
                            new_data["product_id"],
                            new_data["product_name"],
                            new_data["stock"],
                            new_data["price"]
                        ))
                    elif operation == "DELETE":
                        cur.execute("""
                            DELETE FROM analytical_inventory
                            WHERE product_id = %s;
                        """, (old_data["product_id"],))

                    # Mark the event processed in the same transaction
                    cur.execute("""
                        UPDATE cdc_events
                        SET processed = TRUE
                        WHERE event_id = %s;
                    """, (event["event_id"],))

                    print(f"Event {event['event_id']}: {operation} replicated")

        print("CDC replication completed successfully.")
    except Exception:
        print("Replication failed.")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    replicate_cdc_events()
