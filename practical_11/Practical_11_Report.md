# DATA ENGINEERING LAB — PRACTICAL REPORT 11

**Student Name**: Krushil Patel  
**Student ID**: 24DIT043  
**Practical No**: 11  
**Title**: Secure Analytical Serving Platform, Data Privacy Protection & Reverse ETL  

---

## 1. Problem Definition & Objectives

Create a secure analytical serving platform that shares data with downstream users, and build a **Reverse ETL** workflow to sync computed user metrics back to operational tools (e.g., CRM). Implement security controls, including column-level data masking, SHA-256 identity hashing, database Role-Based Access Controls (RBAC), and centralized operation log tracking.

---

## 2. Key Questions & Theoretical Analysis

### Key Point 1: Why do organizations deploy Reverse ETL workflows to sync analytical insights back to production tools instead of having production apps query warehouses directly?

1. **OLTP vs. OLAP Latency Incompatibility**: Analytical data warehouses (Snowflake, BigQuery, Redshift) are optimized for large batch scans taking seconds or minutes. Production applications (e.g., Salesforce, Zendesk, Stripe) require sub-second (10-50ms) single-row lookups.
2. **Connection Starvation & Cost**: Thousands of production app API calls hitting an analytical warehouse directly would exhaust connection pools and incur massive cloud warehouse compute query costs.
3. **Data Activation at Point of Work**: Reverse ETL pushes computed ML metrics (like Churn Risk Scores and Customer Lifetime Value) directly into the native dashboards sales and customer support teams use daily without forcing them to write SQL.

### Key Point 2: How do column-level hashing and tokenization techniques help an enterprise meet strict privacy data regulations like GDPR or CCPA?

- **Cryptographic One-Way Hashing (SHA-256)**: Replaces sensitive plaintext emails with fixed 256-bit hashes. This allows cross-database joins and identity matching across datasets without storing or exposing raw Personally Identifiable Information (PII).
- **Tokenization & Masking**: Replaces sensitive identifiers (e.g., Social Security Numbers or Credit Card Numbers) with non-sensitive surrogate tokens (`***-**-4321`). If an unauthorized breach occurs on the analytical layer, the leaked data contains zero usable raw PII, protecting the organization from severe GDPR compliance fines.

### Key Point 3: Detail the architectural differences between exposing data to analytical clients via direct views, data virtualization layers, and pre-computed data marts.

| Serving Architecture | Mechanism | Latency / Freshness | Compute & Governance Profile |
|---|---|---|---|
| **Direct SQL Views** | Virtual SQL query evaluated at runtime against base warehouse tables. | Real-time (shows latest table state). | High compute query cost; repeated runs re-scan base tables. |
| **Data Virtualization Layers** | Abstraction federating queries across multiple heterogeneous databases without copying data. | Near real-time; depends on remote network I/O. | Centralized governance policy engine; query performance limited by slowest remote source. |
| **Pre-Computed Data Marts** | Physically materialized, pre-aggregated tables tailored to specific business domains. | Fast sub-second reads; periodic batch refresh. | Highly performant for BI dashboards; requires scheduled refresh orchestration pipelines. |

---

## 3. Supplementary Problem: RBAC Masking & Anonymized Analyst View

A secure data serving view was constructed to mask names and hash email identities:
```sql
SELECT 
    customer_id,
    masked_name,        -- 'A**** W****'
    email_sha256,       -- 'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
    tokenized_ssn,      -- '***-**-4321'
    lifetime_spend,
    churn_risk_score,
    rfm_segment
FROM secure_analyst_serving_view;
```

---
*Verified and submitted by: 24DIT043 Krushil Patel*
