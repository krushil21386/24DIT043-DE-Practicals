# Practical 5: Distributed Storage Paradigms & Hive Partitioning Layouts

This repository module contains the implementation, benchmark engine, metadata crawler, and lab report for **Practical 5: Implement Data Storage Structures Using Distributed Storage Paradigms**.

## 📁 Repository Structure
```text
practical_5/
├── docker-compose.yml        # Docker setup for MinIO S3 object store
├── minio_client.py           # AWS Boto3 SDK wrapper for MinIO connection
├── generate_and_upload.py    # Analytical metrics generator & dataset uploader
├── query_benchmark.py        # Partition pruning vs full table scan benchmark engine
├── partition_crawler.py      # Storage metadata crawler & data skew analyzer
├── run_lab.py                # Master automated verification script
├── LAB_REPORT.md             # Detailed lab report & answers to Key Questions
└── README.md                 # Documentation and user guide
```

## 🚀 Quickstart & Execution Instructions

### Prerequisites
- Docker & Docker Compose
- Python 3.8+ with `boto3` installed (`pip install boto3`)

### Step 1: Start MinIO Object Store
Launch the MinIO distributed object storage server container:
```bash
docker compose up -d
```
*MinIO API endpoint will be available at `http://localhost:9000` and Web Console at `http://localhost:9001` (Credentials: `minioadmin` / `minioadmin`).*

### Step 2: Run Full Automated Verification Suite
To generate multi-year metric tracking data, run query performance benchmarks, and crawl storage partitions:
```bash
python run_lab.py
```

### Step 3: Run Individual Scripts (Optional)
- **Data Generation & Ingestion:** `python generate_and_upload.py`
- **Query Performance Benchmark:** `python query_benchmark.py`
- **Partition Metadata Skew Crawler:** `python partition_crawler.py`

---

## 📊 Benchmark Summary Findings
- **Prefix Partition Query Speedup:** **2.91x faster** execution compared to full table scans.
- **Network I/O Savings:** **99.31% reduction** in transferred bytes over the network.
- **API Call Reduction:** **98.62% fewer** S3 HTTP requests executed.
- **Storage Balance:** **Gini Coefficient = 0.0021** (Uniformly balanced partitions).
