
import json
import csv
import os

def scan_and_demote_inactive_tables(manifest_file="outputs/dataset_manifest.json"):
    print("=" * 80)
    print("      SUPPLEMENTARY AUTOMATION: INACTIVE TABLE TIER DEMOTION API ENGINE     ")
    print("=" * 80)

    if not os.path.exists(manifest_file):
        print(f"[-] Manifest file not found at {manifest_file}. Generating dataset first...")
        from dataset_generator import generate_datasets
        generate_datasets()

    with open(manifest_file, "r") as f:
        objects = json.load(f)

    flagged_tables = []
    api_call_audit_trail = []

    print(f"\n[1] Scanning data access logs for table entities with Inactive Days > 90...\n")

    for obj in objects:
        is_table = obj["content_type"] in ["historical_table", "transactional_db"] or obj["object_name"].startswith("db_tables/")
        days_inactive = obj["days_since_last_access"]

        if is_table and days_inactive > 90:
            flagged_tables.append(obj)
            
            # Simulate MinIO / AWS S3 API Call for Storage Class Demotion
            api_endpoint = "https://minio.internal.datacenter:9000"
            bucket_name = "enterprise-datalake"
            object_key = obj["object_name"]
            target_storage_class = "COLD_DEEP_ARCHIVE"
            
            # API payload structure
            api_call = {
                "timestamp": "2026-10-02T10:15:00Z",
                "api_action": "PutObjectStorageClass",
                "bucket": bucket_name,
                "key": object_key,
                "previous_storage_tier": obj["current_tier"],
                "new_storage_tier": target_storage_class,
                "status": "200 OK (SUCCESS)",
                "demotion_reason": f"Table inactive for {days_inactive} days (> 90 days retention threshold)"
            }
            api_call_audit_trail.append(api_call)

            print(f"  [FLAGGED] Table: {obj['object_name']}")
            print(f"            - Size: {obj['size_gb']} GB | Days Unread: {days_inactive}")
            print(f"            - Current Tier: {obj['current_tier']} ---> Demoting to: {target_storage_class}")
            print(f"            - Executing API Call: POST {api_endpoint}/{bucket_name}/{object_key}?x-minio-storage-class={target_storage_class}")
            print(f"            - Response: 200 OK | Storage Tier Successfully Demoted!\n")

    # Write audit log to output file
    audit_file = "outputs/inactive_tables_api_audit.json"
    with open(audit_file, "w") as f:
        json.dump(api_call_audit_trail, f, indent=4)

    print("=" * 80)
    print(f" SUMMARY REPORT:")
    print(f"  - Total Tables Scanned: {len(objects)}")
    print(f"  - Inactive Tables Flagged (>90 Days): {len(flagged_tables)}")
    print(f"  - API Demotion Commands Executed: {len(api_call_audit_trail)}")
    print(f"  - Audit Trail Saved: {audit_file}")
    print("=" * 80)

    return flagged_tables

if __name__ == "__main__":
    scan_and_demote_inactive_tables()
print("24DIT043 Krushil Patel")