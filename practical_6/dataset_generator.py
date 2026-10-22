"""
dataset_generator.py
Generates simulated historical system operational logs, access time manifests,
and server audit records spanning multiple quarters for Practical 6.
"""

import json
import csv
import os
from datetime import datetime, timedelta, timezone

def generate_datasets(output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Reference date representing current system timestamp
    current_time = datetime(2026, 10, 2, 10, 0, 0, tzinfo=timezone.utc)
    
    # Simulated storage objects across 4 quarters
    objects_data = [
        {
            "object_id": "obj_001",
            "object_name": "db_tables/live_orders_2026.parquet",
            "size_gb": 450.0,
            "created_at": (current_time - timedelta(days=12)).isoformat(),
            "last_accessed_at": (current_time - timedelta(hours=2)).isoformat(),
            "days_since_last_access": 0,
            "total_access_count_30d": 3450,
            "current_tier": "Hot",
            "content_type": "transactional_db"
        },
        {
            "object_id": "obj_002",
            "object_name": "db_tables/user_profiles_v2.parquet",
            "size_gb": 120.0,
            "created_at": (current_time - timedelta(days=25)).isoformat(),
            "last_accessed_at": (current_time - timedelta(days=1)).isoformat(),
            "days_since_last_access": 1,
            "total_access_count_30d": 1200,
            "current_tier": "Hot",
            "content_type": "transactional_db"
        },
        {
            "object_id": "obj_003",
            "object_name": "logs/app_server_q2_2026.log",
            "size_gb": 850.0,
            "created_at": (current_time - timedelta(days=40)).isoformat(),
            "last_accessed_at": (current_time - timedelta(days=35)).isoformat(),
            "days_since_last_access": 35,
            "total_access_count_30d": 4,
            "current_tier": "Hot",
            "content_type": "operational_log"
        },
        {
            "object_id": "obj_004",
            "object_name": "db_tables/historical_sales_q1_2026.csv",
            "size_gb": 620.0,
            "created_at": (current_time - timedelta(days=110)).isoformat(),
            "last_accessed_at": (current_time - timedelta(days=95)).isoformat(),
            "days_since_last_access": 95,
            "total_access_count_30d": 0,
            "current_tier": "Warm",
            "content_type": "historical_table"
        },
        {
            "object_id": "obj_005",
            "object_name": "db_tables/customer_feedback_2025.csv",
            "size_gb": 310.0,
            "created_at": (current_time - timedelta(days=140)).isoformat(),
            "last_accessed_at": (current_time - timedelta(days=120)).isoformat(),
            "days_since_last_access": 120,
            "total_access_count_30d": 0,
            "current_tier": "Hot",  # Misclassified hot object needing demotion!
            "content_type": "historical_table"
        },
        {
            "object_id": "obj_006",
            "object_name": "audit/compliance_records_2025_q4.tar.gz",
            "size_gb": 1250.0,
            "created_at": (current_time - timedelta(days=220)).isoformat(),
            "last_accessed_at": (current_time - timedelta(days=180)).isoformat(),
            "days_since_last_access": 180,
            "total_access_count_30d": 0,
            "current_tier": "Warm",
            "content_type": "audit_archive"
        },
        {
            "object_id": "obj_007",
            "object_name": "audit/security_scans_2025_q3.tar.gz",
            "size_gb": 980.0,
            "created_at": (current_time - timedelta(days=310)).isoformat(),
            "last_accessed_at": (current_time - timedelta(days=270)).isoformat(),
            "days_since_last_access": 270,
            "total_access_count_30d": 0,
            "current_tier": "Cold",
            "content_type": "audit_archive"
        },
        {
            "object_id": "obj_008",
            "object_name": "temp/staging_etl_dump_2025.tmp",
            "size_gb": 540.0,
            "created_at": (current_time - timedelta(days=400)).isoformat(),
            "last_accessed_at": (current_time - timedelta(days=390)).isoformat(),
            "days_since_last_access": 390,
            "total_access_count_30d": 0,
            "current_tier": "Cold",
            "content_type": "temporary_dump"
        }
    ]

    # Save manifest JSON
    manifest_path = os.path.join(output_dir, "dataset_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(objects_data, f, indent=4)
        
    # Save system access log CSV
    csv_path = os.path.join(output_dir, "system_access_logs.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "object_id", "object_name", "size_gb", "created_at",
            "last_accessed_at", "days_since_last_access", "total_access_count_30d",
            "current_tier", "content_type"
        ])
        writer.writeheader()
        writer.writerows(objects_data)

    print(f"[+] Dataset successfully generated!")
    print(f"    - Manifest file: {manifest_path}")
    print(f"    - Operational access log: {csv_path}")

if __name__ == "__main__":
    generate_datasets()
