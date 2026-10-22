import json
import random
import time
import uuid
from datetime import datetime
from minio_client import get_s3_client, ensure_bucket_exists, DEFAULT_BUCKET

YEARS = [2023, 2024, 2025]
MONTHS = [f"{m:02d}" for m in range(1, 13)]
REGIONS = ["us-east", "us-west", "eu-central", "ap-south"]
SERVICES = ["auth-service", "payment-api", "user-service", "recommendation-engine", "analytics-pipeline"]
STATUS_CODES = [200, 200, 200, 201, 400, 404, 500, 502]

def generate_metric_record(year, month_str, region):
    """
    Generates a realistic analytical application tracking metric.
    """
    month = int(month_str)
    day = random.randint(1, 28)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    ts = datetime(year, month, day, hour, minute, second)
    
    return {
        "metric_id": str(uuid.uuid4()),
        "timestamp": ts.isoformat(),
        "year": year,
        "month": month_str,
        "region": region,
        "user_id": f"usr_{random.randint(10000, 99999)}",
        "service_name": random.choice(SERVICES),
        "response_time_ms": round(random.expovariate(1.0 / 120.0) + 10, 2),
        "status_code": random.choice(STATUS_CODES),
        "bytes_transferred": random.randint(512, 1048576)
    }

def generate_and_upload_data(records_per_partition=150, bucket_name=DEFAULT_BUCKET):
    """
    Generates multi-year metric tracking dataset and uploads to MinIO in both:
    1. Structured Hive-style partition layout (year=YYYY/month=MM/region=REGION/)
    2. Unpartitioned flat layout (full_table/)
    """
    s3 = get_s3_client()
    ensure_bucket_exists(bucket_name, s3)
    
    print(f"[*] Starting Data Generation & Upload...")
    print(f"[*] Partition Structure: year=YYYY / month=MM / region=REGION")
    print(f"[*] Years: {YEARS}, Months: 01-12, Regions: {REGIONS}")
    
    total_partitions = len(YEARS) * len(MONTHS) * len(REGIONS)
    print(f"[*] Total Partition Keys: {total_partitions} partitions")
    
    total_records = 0
    total_bytes = 0
    upload_start = time.time()
    
    chunk_index = 0
    
    for year in YEARS:
        for month in MONTHS:
            for region in REGIONS:
                chunk_index += 1
                partition_records = [generate_metric_record(year, month, region) for _ in range(records_per_partition)]
                json_bytes = json.dumps(partition_records, indent=2).encode('utf-8')
                
                # 1. Hive-style Partition Key Path
                partition_key = f"partitioned/year={year}/month={month}/region={region}/metrics_data.json"
                s3.put_object(
                    Bucket=bucket_name,
                    Key=partition_key,
                    Body=json_bytes,
                    ContentType='application/json'
                )
                
                # 2. Unpartitioned Flat Key Path (for full table linear scan)
                flat_key = f"full_table/chunk_{chunk_index:03d}.json"
                s3.put_object(
                    Bucket=bucket_name,
                    Key=flat_key,
                    Body=json_bytes,
                    ContentType='application/json'
                )
                
                total_records += len(partition_records)
                total_bytes += len(json_bytes)
                
                if chunk_index % 36 == 0 or chunk_index == total_partitions:
                    print(f"  [+] Uploaded {chunk_index}/{total_partitions} partitions ({total_records} records, {total_bytes / 1024 / 1024:.2f} MB)...")
                    
    duration = time.time() - upload_start
    print(f"\n[OK] Ingestion Complete!")
    print(f"    - Total Objects Uploaded (Partitioned): {total_partitions}")
    print(f"    - Total Objects Uploaded (Flat): {total_partitions}")
    print(f"    - Total Analytical Records: {total_records}")
    print(f"    - Total Data Payload Size: {total_bytes / (1024 * 1024):.2f} MB")
    print(f"    - Ingestion Duration: {duration:.2f} seconds")

if __name__ == "__main__":
    generate_and_upload_data()
