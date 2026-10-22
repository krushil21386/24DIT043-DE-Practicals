import json
import math
import statistics
from minio_client import get_s3_client, DEFAULT_BUCKET

def compute_gini_coefficient(sizes):
    """
    Computes the Gini coefficient of partition storage sizes.
    0.0 = Perfectly equal balance across all partitions.
    1.0 = Maximum data skew (all data in a single partition).
    """
    if not sizes or len(sizes) == 0:
        return 0.0
    sorted_sizes = sorted(sizes)
    n = len(sorted_sizes)
    mean_val = sum(sorted_sizes) / n
    if mean_val == 0:
        return 0.0
    diff_sum = sum(abs(x - y) for x in sorted_sizes for y in sorted_sizes)
    return diff_sum / (2 * n * n * mean_val)

def crawl_partition_metadata(bucket_name=DEFAULT_BUCKET, prefix="partitioned/"):
    """
    Scans object storage bucket, parses Hive-style partition paths, 
    and computes data balance and skew metrics.
    """
    s3 = get_s3_client()
    print("=" * 80)
    print(f" FILE METADATA CRAWLER & STORAGE PARTITION SKEW ANALYZER")
    print("=" * 80)
    print(f" Bucket: '{bucket_name}', Crawling Target Prefix: '{prefix}'\n")
    
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    
    partition_map = {}
    total_objects = 0
    total_bucket_bytes = 0
    
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                total_objects += 1
                key = obj['Key']
                size = obj['Size']
                last_modified = obj['LastModified']
                total_bucket_bytes += size
                
                # Extract partition directory path (e.g. year=2024/month=05/region=us-east)
                rel_path = key[len(prefix):] if key.startswith(prefix) else key
                parts = rel_path.rsplit('/', 1)
                partition_path = parts[0] if len(parts) > 1 else "root"
                
                if partition_path not in partition_map:
                    partition_map[partition_path] = {
                        "object_count": 0,
                        "total_bytes": 0,
                        "objects": []
                    }
                
                partition_map[partition_path]["object_count"] += 1
                partition_map[partition_path]["total_bytes"] += size
                partition_map[partition_path]["objects"].append({
                    "key": key,
                    "size": size,
                    "last_modified": str(last_modified)
                })

    partition_count = len(partition_map)
    if partition_count == 0:
        print("[!] No storage partitions found under prefix:", prefix)
        return
        
    sizes = [p["total_bytes"] for p in partition_map.values()]
    counts = [p["object_count"] for p in partition_map.values()]
    
    mean_size = statistics.mean(sizes)
    stdev_size = statistics.stdev(sizes) if partition_count > 1 else 0.0
    min_size = min(sizes)
    max_size = max(sizes)
    cv = (stdev_size / mean_size) if mean_size > 0 else 0.0
    gini = compute_gini_coefficient(sizes)
    skew_ratio = (max_size / min_size) if min_size > 0 else float('inf')
    
    # Identify sample partitions
    min_part_path = [k for k, v in partition_map.items() if v["total_bytes"] == min_size][0]
    max_part_path = [k for k, v in partition_map.items() if v["total_bytes"] == max_size][0]
    
    # Classification assessment
    if gini < 0.05:
        skew_status = "PERFECTLY BALANCED (Uniform distribution across partitions)"
    elif gini < 0.20:
        skew_status = "LIGHT SKEW (Acceptable variance)"
    elif gini < 0.40:
        skew_status = "MODERATE SKEW (Consider partition key rebalancing)"
    else:
        skew_status = "HIGH DATA SKEW / HOTSPOT (Severe storage imbalance)"
        
    print("-" * 80)
    print(" PARTITION INVENTORY & SKEW SUMMARY METRICS")
    print("-" * 80)
    print(f"{'Total Active Partitions':<35} : {partition_count}")
    print(f"{'Total Objects Crawled':<35} : {total_objects}")
    print(f"{'Total Storage Payload':<35} : {total_bucket_bytes / (1024 * 1024):.3f} MB ({total_bucket_bytes:,} Bytes)")
    print(f"{'Average Partition Size (Mean)':<35} : {mean_size / 1024:.2f} KB")
    print(f"{'Partition Size Std Deviation':<35} : {stdev_size / 1024:.2f} KB")
    print(f"{'Minimum Partition Size':<35} : {min_size / 1024:.2f} KB ({min_part_path})")
    print(f"{'Maximum Partition Size':<35} : {max_size / 1024:.2f} KB ({max_part_path})")
    print(f"{'Skew Ratio (Max / Min)':<35} : {skew_ratio:.2f}x")
    print(f"{'Coefficient of Variation (CV)':<35} : {cv:.4f}")
    print(f"{'Gini Coefficient (Storage Inequality)':<35} : {gini:.4f}")
    print(f"{'Data Balance Classification':<35} : {skew_status}")
    print("-" * 80)
    
    print("\nSAMPLE PARTITION BREAKDOWN (FIRST 10 PARTITIONS):")
    print(f"{'Partition Prefix Layout':<50} | {'Files':<6} | {'Total Size (KB)':<15}")
    print("-" * 80)
    for p_key in list(partition_map.keys())[:10]:
        p_data = partition_map[p_key]
        print(f"{p_key:<50} | {p_data['object_count']:<6} | {p_data['total_bytes'] / 1024:<15.2f}")
    print("=" * 80 + "\n")

    return {
        "partition_count": partition_count,
        "total_objects": total_objects,
        "total_bytes": total_bucket_bytes,
        "mean_size": mean_size,
        "stdev_size": stdev_size,
        "gini_coefficient": gini,
        "skew_ratio": skew_ratio,
        "status": skew_status
    }

if __name__ == "__main__":
    crawl_partition_metadata()
print("24DIT043 Krushil Patel")