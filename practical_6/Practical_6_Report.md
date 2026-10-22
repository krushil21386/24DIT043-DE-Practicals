# DATA ENGINEERING LAB — PRACTICAL REPORT 6

**Course / Lab**: Data Engineering Lab (24DIT014)  
**Practical No**: 6  
**Title**: Automated Storage Lifecycle Policy Matrix & Tiering Management  

---

## 1. Problem Definition & Objectives

Formulate and test an automated storage lifecycle policy matrix defining three distinct access tiers: **Hot** (immediate access), **Warm** (infrequent access), and **Cold** (deep compression archiving). Programmatic policy rules automatically transition data objects across these tiers based on retention targets, query frequency boundaries, and age constraints to minimize operational platform costs.

### Key Evaluation Criteria
- **Hot Tier**: High-throughput SSD/NVMe pools for frequently queried transactional data.
- **Warm Tier**: Lower-cost HDD / Infrequent Access pools for operational logs and monthly analytical tables.
- **Cold Tier**: Deep compression archiving (zstd/lz4) for long-term audit logs and inactive tables (>90 days unread).
- **Expiration Rule**: Automated purge of temporary/staging dumps (>365 days old).

---

## 2. Key Questions & Theoretical Analysis

### Key Point 1: Differentiate Hardware and Software Properties of Hot vs. Cold Storage Tiers

| Feature / Property | Hot Tier (Immediate Access) | Cold Tier (Deep Archiving) |
|---|---|---|
| **Hardware Media** | Enterprise NVMe PCIe 4.0/5.0 SSDs | High-density SAS/SATA HDDs or LTO Tape |
| **IOPS & Throughput** | High IOPS (100k+ IOPS), Sub-millisecond latency (<1ms) | Low IOPS (~100 IOPS), High latency (minutes to hours) |
| **Compression Ratio** | Uncompressed or light dictionary compression (fastest write) | Deep LZ4 / ZSTD / Brotli block compression (high ratio: 5:1 to 10:1) |
| **Access Pattern** | Frequent random reads & intensive writes (OLTP / Live ETL) | Sequential batch reads, rare access (Compliance / Audit) |
| **Unit Storage Cost** | Premium ($0.023 / GB / month) | Ultra-low ($0.00099 / GB / month) |
| **Erasure Coding & Redundancy** | Dual-parity RAID 6 / Multi-region replication | Deep EC (12+4) or cold archive Glacier vaulting |

### Key Point 2: Operational and Financial Cost Penalties of Premature Cold Tier Misclassification

Prematurely demoting active or frequently queried data into Cold storage triggers severe penalties:
1. **Financial Egress & Retrieval Fees**: Cloud object stores charge per-GB data retrieval fees and API request charges for Cold/Archive tiers. Repeatedly querying Cold objects costs significantly more than storing them in Hot.
2. **Latency & SLA Breaches**: Cold objects require unarchiving/thawing windows (ranging from minutes up to 12 hours). Interactive dashboards and analytical queries timing out will break operational SLAs.
3. **Re-hydration Compute Bottlenecks**: Decompressing and restoring dense archive blocks consumes high CPU cycles and network bandwidth on database nodes.

### Key Point 3: How Automated Expiration Safeguards Database Systems Against Performance Degradation

Over long operational windows, databases suffer from **structural performance degradation** due to unconstrained data accumulation:
1. **Index Bloat & Tree Depth**: As tables grow indefinitely, B-tree index depth increases, turning $O(\log N)$ point lookups from 2-3 I/O hops into 6-8 I/O hops.
2. **Sequential Scan Degradation**: Analytical queries performing full table scans must read gigabytes of dead/stale historical rows, exhausting buffer pool memory.
3. **Vacuum & Compaction Overhead**: Storage engines (PostgreSQL, Cassandra, RocksDB) spend excessive IOPS compacting and vacuuming obsolete historical rows.
4. **Backup & Disaster Recovery Windows**: Automated expiration ensures backup snapshots remain lightweight and restore times fit within designated maintenance windows.

---

## 3. Storage Lifecycle Policy Schema (`ilm_lifecycle_policy.json`)

```json
{
  "Rules": [
    {
      "ID": "TransitionToWarmInfrequentAccess",
      "Status": "Enabled",
      "Filter": { "Prefix": "logs/" },
      "Transitions": [ { "Days": 30, "StorageClass": "WARM_INFREQUENT" } ]
    },
    {
      "ID": "DemoteInactiveDataTablesToCold",
      "Status": "Enabled",
      "Filter": { "Prefix": "db_tables/" },
      "Transitions": [
        { "Days": 30, "StorageClass": "WARM_INFREQUENT" },
        { "Days": 90, "StorageClass": "COLD_DEEP_ARCHIVE" }
      ]
    },
    {
      "ID": "ArchiveComplianceAuditRecords",
      "Status": "Enabled",
      "Filter": { "Prefix": "audit/" },
      "Transitions": [
        { "Days": 60, "StorageClass": "WARM_INFREQUENT" },
        { "Days": 180, "StorageClass": "COLD_DEEP_ARCHIVE" }
      ]
    },
    {
      "ID": "ExpireTemporaryStagingDumps",
      "Status": "Enabled",
      "Filter": { "Prefix": "temp/" },
      "Expiration": { "Days": 365 }
    }
  ]
}
```

---

## 4. Supplementary Problem Implementation (Inactive Table API Demotion)

The supplementary automation script (`demote_inactive_tables.py`) scans operational access manifests, identifies data tables unread for **>90 days**, and issues API calls (`PutObjectStorageClass`) to demote their allocation tier:

### Executed API Demotion Audit Trail
- **Table 1**: `db_tables/historical_sales_q1_2026.csv` (620 GB, 95 days unread)  
  *API Action*: `POST https://minio.internal.datacenter:9000/enterprise-datalake/db_tables/historical_sales_q1_2026.csv?x-minio-storage-class=COLD_DEEP_ARCHIVE`  
  *Response*: `200 OK (SUCCESS)`
- **Table 2**: `db_tables/customer_feedback_2025.csv` (310 GB, 120 days unread)  
  *API Action*: `POST https://minio.internal.datacenter:9000/enterprise-datalake/db_tables/customer_feedback_2025.csv?x-minio-storage-class=COLD_DEEP_ARCHIVE`  
  *Response*: `200 OK (SUCCESS)`

---

## 5. Financial Cost Reduction Breakdown

- **Evaluated Dataset Capacity**: **5,120.0 GB (5.00 TB)**
- **Baseline Monthly Cost (All Hot Tier @ $0.023/GB)**: **$117.76 / month**
- **Optimized Monthly Cost (Automated ILM Matrix)**: **$26.86 / month**
- **Monthly Savings**: **$90.90 / month (77.19% Cost Reduction)**
- **Annual Savings**: **$1,090.76 / year**

### Post-Lifecycle Storage Tiering Breakdown
| Access Tier | Allocated Capacity | Unit Rate ($/GB/mo) | Monthly Storage Cost ($) |
|---|---|---|---|
| **Hot (NVMe / SSD)** | 570.0 GB (11.1%) | $0.02300 | $13.11 |
| **Warm (HDD / Infrequent)** | 850.0 GB (16.6%) | $0.01250 | $10.62 |
| **Cold (Deep Archive)** | 3,160.0 GB (61.7%) | $0.00099 | $3.13 |
| **Expired (Purged Temp)** | 540.0 GB (10.5%) | $0.00000 | $0.00 |
| **TOTAL** | **5,120.0 GB (100.0%)** | -- | **$26.86** |

---
