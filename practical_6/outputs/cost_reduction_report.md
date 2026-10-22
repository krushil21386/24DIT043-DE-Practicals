# Practical 6: Automated Storage Lifecycle Policy - Financial Cost Reduction Breakdown

## Executive Cost Reduction Summary
- **Evaluated Data Capacity**: 5,120.0 GB (5.00 TB)
- **Baseline Monthly Cost (All Hot)**: $117.76
- **Optimized Monthly Cost (Tiered ILM)**: $26.86
- **Monthly Net Savings**: **$90.90** (77.19% Cost Reduction)
- **Annualized Net Savings**: **$1,090.76 / year**

## Capacity Breakdown by Storage Class
| Access Tier | Capacity (GB) | Percentage (%) | Unit Cost ($/GB/mo) | Monthly Cost ($) |
|---|---|---|---|---|
| **Hot (NVMe / SSD)** | 570.0 GB | 11.1% | $0.0230 | $13.11 |
| **Warm (Infrequent Access)** | 850.0 GB | 16.6% | $0.0125 | $10.62 |
| **Cold (Deep Archive)** | 3,160.0 GB | 61.7% | $0.00099 | $3.13 |
| **Purged (Expired Temp Data)** | 540.0 GB | 10.5% | $0.0000 | $0.00 |
| **TOTAL** | **5,120.0 GB** | **100.0%** | -- | **$26.86** |
