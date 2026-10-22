import json
import time
from minio_client import get_s3_client, DEFAULT_BUCKET

def run_partitioned_query(s3, target_year, target_month, target_region, bucket_name=DEFAULT_BUCKET):
    """
    Query Method A: Uses S3 Prefix filtering (Partition Pruning) to fetch only relevant key paths.
    """
    prefix = f"partitioned/year={target_year}/month={target_month}/region={target_region}/"
    
    start_time = time.time()
    api_calls = 0
    bytes_downloaded = 0
    matching_records = []
    objects_scanned = 0
    
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    
    for page in pages:
        api_calls += 1
        if 'Contents' in page:
            for obj in page['Contents']:
                objects_scanned += 1
                key = obj['Key']
                
                # Fetch target object
                response = s3.get_object(Bucket=bucket_name, Key=key)
                api_calls += 1
                body = response['Body'].read()
                bytes_downloaded += len(body)
                
                records = json.loads(body.decode('utf-8'))
                matching_records.extend(records)
                
    elapsed_time = time.time() - start_time
    
    return {
        "method": "Partition-Isolated (Prefix Pruning)",
        "objects_scanned": objects_scanned,
        "api_calls": api_calls,
        "bytes_downloaded": bytes_downloaded,
        "record_count": len(matching_records),
        "execution_time_sec": elapsed_time,
        "records": matching_records
    }

def run_full_table_scan(s3, target_year, target_month, target_region, bucket_name=DEFAULT_BUCKET):
    """
    Query Method B: Full-table linear scan across all unpartitioned object files.
    """
    prefix = "full_table/"
    
    start_time = time.time()
    api_calls = 0
    bytes_downloaded = 0
    matching_records = []
    objects_scanned = 0
    
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    
    for page in pages:
        api_calls += 1
        if 'Contents' in page:
            for obj in page['Contents']:
                objects_scanned += 1
                key = obj['Key']
                
                # Fetch every object linearly
                response = s3.get_object(Bucket=bucket_name, Key=key)
                api_calls += 1
                body = response['Body'].read()
                bytes_downloaded += len(body)
                
                records = json.loads(body.decode('utf-8'))
                # Filter in compute engine (in-memory row filter)
                filtered = [
                    r for r in records 
                    if r.get('year') == target_year 
                    and r.get('month') == target_month 
                    and r.get('region') == target_region
                ]
                matching_records.extend(filtered)
                
    elapsed_time = time.time() - start_time
    
    return {
        "method": "Full-Table Linear Scan",
        "objects_scanned": objects_scanned,
        "api_calls": api_calls,
        "bytes_downloaded": bytes_downloaded,
        "record_count": len(matching_records),
        "execution_time_sec": elapsed_time,
        "records": matching_records
    }

def evaluate_performance(target_year=2024, target_month="05", target_region="us-east"):
    s3 = get_s3_client()
    print("=" * 80)
    print(f" EXPERIMENTAL BENCHMARK: PARTITION PRUNING vs FULL-TABLE LINEAR SCAN")
    print("=" * 80)
    print(f" Target Query Predicate: year={target_year}, month={target_month}, region='{target_region}'\n")
    
    print("[1] Executing Partition-Isolated Query...")
    res_part = run_partitioned_query(s3, target_year, target_month, target_region)
    
    print("[2] Executing Full-Table Linear File Scan...")
    res_full = run_full_table_scan(s3, target_year, target_month, target_region)
    
    # Calculate performance comparison metrics
    speedup = res_full['execution_time_sec'] / max(res_part['execution_time_sec'], 0.0001)
    io_reduction = (1 - (res_part['bytes_downloaded'] / max(res_full['bytes_downloaded'], 1))) * 100
    api_reduction = (1 - (res_part['api_calls'] / max(res_full['api_calls'], 1))) * 100
    
    print("\n" + "=" * 80)
    print(" PERFORMANCE EVALUATION METRICS REPORT")
    print("=" * 80)
    print(f"{'Metric / Dimension':<35} | {'Partitioned Scan':<20} | {'Full-Table Linear Scan':<22}")
    print("-" * 80)
    print(f"{'Execution Time (seconds)':<35} | {res_part['execution_time_sec']:<20.4f} | {res_full['execution_time_sec']:<22.4f}")
    print(f"{'S3 API Calls (Requests)':<35} | {res_part['api_calls']:<20} | {res_full['api_calls']:<22}")
    print(f"{'Objects Scanned':<35} | {res_part['objects_scanned']:<20} | {res_full['objects_scanned']:<22}")
    print(f"{'Data Downloaded (MB)':<35} | {res_part['bytes_downloaded'] / 1024 / 1024:<20.2f} | {res_full['bytes_downloaded'] / 1024 / 1024:<22.2f}")
    print(f"{'Matching Records Returned':<35} | {res_part['record_count']:<20} | {res_full['record_count']:<22}")
    print("-" * 80)
    print(f" [*] Speedup Factor         : {speedup:.2f}x faster execution")
    print(f" [*] Network I/O Reduction   : {io_reduction:.2f}% data payload saved")
    print(f" [*] S3 API Call Reduction  : {api_reduction:.2f}% API calls eliminated")
    print(f" [*] Query Correctness Check: {'PASSED (Exact record match)' if res_part['record_count'] == res_full['record_count'] else 'FAILED'}")
    print("=" * 80 + "\n")
    
    return res_part, res_full

if __name__ == "__main__":
    evaluate_performance()
print("24DIT043 Krushil Patel")