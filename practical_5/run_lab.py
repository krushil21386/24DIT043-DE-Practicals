import sys
import time
from minio_client import get_s3_client, ensure_bucket_exists
from generate_and_upload import generate_and_upload_data
from query_benchmark import evaluate_performance
from partition_crawler import crawl_partition_metadata

def main():
    print("=" * 80)
    print("      DATA ENGINEERING LAB - PRACTICAL 5 AUTOMATED VERIFICATION SUITE")
    print("      Topic: Distributed Data Storage Structures & Hive Prefix Partitioning")
    print("=" * 80)
    
    # 1. Health check MinIO connection
    print("\n[Step 1/4] Verifying MinIO Object Store Availability...")
    try:
        s3 = get_s3_client()
        ensure_bucket_exists()
        print("  [OK] MinIO container cluster is healthy and accessible at http://localhost:9000.")
    except Exception as e:
        print(f"  [ERROR] Failed to connect to MinIO: {e}")
        print("          Please ensure Docker container is running ('docker compose up -d').")
        sys.exit(1)
        
    # 2. Run Data Generation and Ingestion
    print("\n[Step 2/4] Generating & Ingesting Multi-Year Analytical Metric Tables...")
    generate_and_upload_data(records_per_partition=150)
    
    # 3. Execute Query Performance Benchmark
    print("\n[Step 3/4] Running Query Performance Benchmark (Prefix Pruning vs Linear Scan)...")
    evaluate_performance(target_year=2024, target_month="05", target_region="us-east")
    
    # 4. Crawl File Metadata & Partition Skew Metrics
    print("\n[Step 4/4] Executing File Metadata Crawler & Data Balance Analysis...")
    crawl_partition_metadata()
    
    print("=" * 80)
    print("  [SUCCESS] ALL LAB EXPERIMENTS EXECUTED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
print("24DIT043 Krushil Patel")