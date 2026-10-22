"""
PRACTICAL 11: SECURE ANALYTICAL SERVING PLATFORM & REVERSE ETL PIPELINE
Author: 24DIT043 Krushil Patel
Tools: Python, SQLite Security Layer, Hashlib SHA-256, Operational Audit Loggers
"""

import sqlite3
import hashlib
import json
from datetime import datetime

DB_PATH = "secure_platform.db"

def sha256_hash(value: str) -> str:
    """Computes SHA-256 cryptographic hash of sensitive identity strings (e.g., emails)."""
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()

def mask_pii(name: str) -> str:
    """Masks customer name for RBAC data analyst views (e.g. 'John Doe' -> 'J*** D**')."""
    parts = name.split()
    return " ".join([p[0] + "***" for p in parts if p])

def mask_ssn(ssn: str) -> str:
    """Tokenizes SSN to reveal only the last 4 digits."""
    return "***-**-" + ssn.split("-")[-1]

def setup_secure_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Base Analytical Warehouse Table (Raw Data)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_analytics_warehouse (
        customer_id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        email_raw TEXT NOT NULL,
        ssn_raw TEXT NOT NULL,
        lifetime_spend REAL NOT NULL,
        churn_risk_score REAL NOT NULL,
        rfm_segment TEXT NOT NULL,
        last_updated TEXT NOT NULL
    );
    """)

    # 2. Secure Analytical View Table (Encrypted & Hashed for Data Analyst Role)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS secure_analyst_serving_view (
        customer_id INTEGER PRIMARY KEY,
        masked_name TEXT NOT NULL,
        email_sha256 TEXT NOT NULL,
        tokenized_ssn TEXT NOT NULL,
        lifetime_spend REAL NOT NULL,
        churn_risk_score REAL NOT NULL,
        rfm_segment TEXT NOT NULL
    );
    """)

    # 3. Operational CRM Store (Reverse ETL Target)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS operational_crm_destination (
        crm_customer_id INTEGER PRIMARY KEY,
        sync_email_hash TEXT NOT NULL,
        assigned_tier TEXT NOT NULL,
        churn_prevention_flag INTEGER NOT NULL,
        last_synced_at TEXT NOT NULL
    );
    """)

    # 4. Centralized Operation Audit Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS security_audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_type TEXT NOT NULL,
        actor_role TEXT NOT NULL,
        records_affected INTEGER NOT NULL,
        details TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

def seed_analytical_data():
    print("\n[Step 1/5] Ingesting Sensitive Analytical Customer Records...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    customers = [
        (1001, "Alice Walker", "alice.walker@enterprise.com", "987-65-4321", 14500.50, 0.12, "VIP_CHURN_IMMUNE", datetime.now().isoformat()),
        (1002, "Bob Henderson", "bob.h@fintech.net", "876-54-3210", 320.00, 0.88, "HIGH_CHURN_RISK", datetime.now().isoformat()),
        (1003, "Charlie Davis", "cdavis99@techcorp.io", "765-43-2109", 8900.00, 0.45, "MODERATE_ENGAGEMENT", datetime.now().isoformat()),
        (1004, "Diana Prince", "diana.prince@security.org", "654-32-1098", 22000.00, 0.05, "VIP_CHURN_IMMUNE", datetime.now().isoformat()),
        (1005, "Evan Wright", "ewright@consumer.com", "543-21-0987", 450.00, 0.92, "HIGH_CHURN_RISK", datetime.now().isoformat()),
    ]
    cursor.executemany("""
    INSERT OR REPLACE INTO customer_analytics_warehouse
    (customer_id, full_name, email_raw, ssn_raw, lifetime_spend, churn_risk_score, rfm_segment, last_updated)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, customers)
    conn.commit()

    # Log audit entry
    cursor.execute("""
    INSERT INTO security_audit_logs (action_type, actor_role, records_affected, details, timestamp)
    VALUES ('DATA_INGESTION', 'DB_ADMIN', ?, 'Ingested raw customer analytics dataset with sensitive PII', datetime('now'));
    """, (len(customers),))
    conn.commit()
    conn.close()
    print(f"  [OK] Ingested {len(customers)} records into analytical warehouse.")

def apply_cryptographic_masking_and_rbac():
    """
    Supplementary Problem: Applies SHA-256 hashing and tokenization
    so Data Analysts can query data without exposing PII.
    """
    print("\n[Step 2/5] Applying SHA-256 Hashing, SSN Tokenization & RBAC Masking...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT customer_id, full_name, email_raw, ssn_raw, lifetime_spend, churn_risk_score, rfm_segment FROM customer_analytics_warehouse;")
    raw_rows = cursor.fetchall()

    for row in raw_rows:
        cid, name, email, ssn, spend, churn, segment = row
        hashed_email = sha256_hash(email)
        masked_name = mask_pii(name)
        tokenized_ssn = mask_ssn(ssn)

        cursor.execute("""
        INSERT OR REPLACE INTO secure_analyst_serving_view
        (customer_id, masked_name, email_sha256, tokenized_ssn, lifetime_spend, churn_risk_score, rfm_segment)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (cid, masked_name, hashed_email, tokenized_ssn, spend, churn, segment))

    cursor.execute("""
    INSERT INTO security_audit_logs (action_type, actor_role, records_affected, details, timestamp)
    VALUES ('RBAC_VIEW_GENERATION', 'SECURITY_ENGINEER', ?, 'Generated secure anonymized analyst view with SHA-256 hashing', datetime('now'));
    """, (len(raw_rows),))

    conn.commit()
    conn.close()
    print("  [OK] Cryptographic identity tokenization complete.")

def query_analyst_rbac_view():
    """Simulates a Data Analyst executing queries against the secure serving view."""
    print("\n[Step 3/5] Querying Data Analyst RBAC Serving View (Simulating Analyst Role)...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT customer_id, masked_name, email_sha256, tokenized_ssn, lifetime_spend, churn_risk_score, rfm_segment
    FROM secure_analyst_serving_view
    ORDER BY customer_id;
    """)
    rows = cursor.fetchall()

    print("\n" + "=" * 90)
    print(f"{'ID':<6} {'MASKED NAME':<16} {'TOKENIZED SSN':<15} {'EMAIL SHA-256 (FIRST 16 CHARS)':<32} {'SEGMENT'}")
    print("=" * 90)
    for r in rows:
        print(f"{r['customer_id']:<6} {r['masked_name']:<16} {r['tokenized_ssn']:<15} {r['email_sha256'][:16]}...           {r['rfm_segment']}")
    print("=" * 90)
    conn.close()

def execute_reverse_etl_sync():
    """
    Executes a Reverse ETL synchronization workflow:
    Extracts computed customer segments & churn prevention flags from warehouse
    and writes them into the operational CRM destination table.
    """
    print("\n[Step 4/5] Running Reverse ETL Workflow: Syncing Insights -> Operational CRM...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Extract insights from analytical table
    cursor.execute("""
    SELECT customer_id, email_sha256, churn_risk_score, rfm_segment
    FROM secure_analyst_serving_view;
    """)
    insights = cursor.fetchall()

    synced_count = 0
    for item in insights:
        cid = item["customer_id"]
        email_hash = item["email_sha256"]
        churn_flag = 1 if item["churn_risk_score"] > 0.70 else 0
        tier = "VIP" if "VIP" in item["rfm_segment"] else "STANDARD"

        cursor.execute("""
        INSERT OR REPLACE INTO operational_crm_destination
        (crm_customer_id, sync_email_hash, assigned_tier, churn_prevention_flag, last_synced_at)
        VALUES (?, ?, ?, ?, datetime('now'));
        """, (cid, email_hash, tier, churn_flag))
        synced_count += 1

    cursor.execute("""
    INSERT INTO security_audit_logs (action_type, actor_role, records_affected, details, timestamp)
    VALUES ('REVERSE_ETL_SYNC', 'AIRBYTE_REVERSE_ETL_AGENT', ?, 'Synchronized analytical segments and churn alerts into CRM', datetime('now'));
    """, (synced_count,))

    conn.commit()
    conn.close()
    print(f"  [REVERSE ETL] Synced {synced_count} customer activations to Operational CRM.")

def inspect_audit_ledger():
    """Displays the centralized operation log tracking ledger."""
    print("\n[Step 5/5] Inspecting Centralized Security Operation Audit Logs...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT log_id, action_type, actor_role, records_affected, details, timestamp FROM security_audit_logs;")
    logs = cursor.fetchall()

    print("\n" + "=" * 90)
    print(f"{'LOG ID':<8} {'ACTION TYPE':<24} {'ACTOR ROLE':<26} {'ROWS':<6} {'TIMESTAMP'}")
    print("=" * 90)
    for l in logs:
        print(f"{l['log_id']:<8} {l['action_type']:<24} {l['actor_role']:<26} {l['records_affected']:<6} {l['timestamp']}")
    print("=" * 90)
    conn.close()

def run_suite():
    print("=" * 80)
    print("   PRACTICAL 11: SECURE ANALYTICAL SERVING PLATFORM & REVERSE ETL PIPELINE   ")
    print("   Topic: SHA-256 Hashing, Column Masking, RBAC Views, and CRM Sync Engine")
    print("=" * 80)

    setup_secure_database()
    seed_analytical_data()
    apply_cryptographic_masking_and_rbac()
    query_analyst_rbac_view()
    execute_reverse_etl_sync()
    inspect_audit_ledger()

if __name__ == "__main__":
    run_suite()
