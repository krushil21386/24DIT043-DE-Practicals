# DATA ENGINEERING LAB — PRACTICAL REPORT 8

**Student Name**: Krushil Patel  
**Student ID**: 24DIT043  
**Practical No**: 8  
**Title**: Complex Analytical Aggregation Queries & Database Execution Engine Optimization  

---

## 1. Problem Definition & Objectives

Execute complex analytical aggregation queries across high-cardinality multi-million row datasets and inspect their internal database execution engines. Diagnose execution bottlenecks (such as full table linear disk scans or sorting overheads) using execution plan tools (`EXPLAIN` and `EXPLAIN ANALYZE`), and apply performance fixes like indexing, columnar projection, and query refactoring using Common Table Expressions (CTEs).

---

## 2. Key Questions & Theoretical Analysis

### Key Point 1: Explain what a full table disk scan operation means within an execution plan, and describe its computational impact on large datasets.

A **Full Table Scan (Sequential Scan)** occurs when the database execution engine must read every single physical data page and block of a table from storage into RAM because no relevant index or partition pruning constraint can filter the target rows.
- **Computational Impact**:
  1. **Massive Disk I/O**: For a 50-million row table, gigabytes of data must be pulled through storage buses into memory.
  2. **Buffer Cache Eviction**: Full scans flood the database buffer pool cache with cold data pages, evicting hot pages and causing cache misses for other concurrent queries.
  3. **High CPU Cycles**: Decompressing and deserializing every column for every row consumes immense CPU overhead even if only 0.1% of rows match the predicate.

### Key Point 2: How does a columnar storage layout fundamentally change query processing and optimization compared to a traditional row-oriented layout?

| Architectural Feature | Row-Oriented Layout (OLTP - e.g., standard PostgreSQL) | Columnar Layout (OLAP - e.g., DuckDB / Parquet) |
|---|---|---|
| **Data Organization** | Consecutive disk blocks store entire tuples (`col1, col2, col3...`). | Consecutive disk blocks store all values of a single column (`col1, col1, col1...`). |
| **I/O Projection Pruning** | Must read all columns across disk pages even if the query only selects 2 columns. | Reads **only** the specific columns referenced in `SELECT` or `WHERE` clauses. |
| **Compression Ratio** | Moderate (heterogeneous column data types limit compression). | Extremely High (homogeneous data types enable run-length encoding, dictionary encoding, bit-packing). |
| **SIMD Vectorization** | Row-by-row iteration (Volcano model). | Vectorized execution processing 1024-element column vectors in CPU registers. |

### Key Point 3: What are the architectural costs and performance penalties associated with creating too many secondary indices on volatile, frequently updated database tables?

1. **Write Amplification (DML Penalty)**: Every `INSERT`, `UPDATE`, and `DELETE` must synchronously update the heap table AND every secondary index tree. If a table has 8 indexes, one insert triggers 9 discrete write operations.
2. **Locking & Concurrency Contention**: Modifying index nodes causes page splits and tree rebalancing locks, creating concurrency bottlenecks for write transactions.
3. **Storage Bloat**: Secondary indexes duplicate indexed column values, often growing larger than the original base table itself.

---

## 3. Supplementary Problem: Refactoring Nested Queries with CTEs

### Unoptimized Nested SQL (Repeated Table Rescans):
```sql
SELECT 
    c.country, c.event_type, c.user_id, c.dwell_time_sec,
    (SELECT AVG(sub1.dwell_time_sec) FROM raw_clickstream sub1 WHERE sub1.country = c.country) AS avg_country_dwell,
    (SELECT COUNT(*) FROM raw_clickstream sub2 WHERE sub2.user_id = c.user_id AND sub2.event_type = 'CHECKOUT') AS user_checkout_count
FROM raw_clickstream c
WHERE c.dwell_time_sec > (
    SELECT AVG(sub3.dwell_time_sec) * 1.5 FROM raw_clickstream sub3 WHERE sub3.country = c.country
)
ORDER BY c.dwell_time_sec DESC LIMIT 20;
```

### Optimized Refactored SQL (Single-Pass Aggregations with CTEs):
```sql
WITH country_stats AS (
    SELECT country, AVG(dwell_time_sec) AS avg_country_dwell, AVG(dwell_time_sec) * 1.5 AS high_dwell_threshold
    FROM raw_clickstream
    WHERE country IN ('US', 'IN', 'UK')
    GROUP BY country
),
user_checkouts AS (
    SELECT user_id, COUNT(*) AS user_checkout_count
    FROM raw_clickstream
    WHERE event_type = 'CHECKOUT'
    GROUP BY user_id
)
SELECT c.country, c.event_type, c.user_id, c.dwell_time_sec, cs.avg_country_dwell, COALESCE(uc.user_checkout_count, 0)
FROM raw_clickstream c
JOIN country_stats cs ON c.country = cs.country
LEFT JOIN user_checkouts uc ON c.user_id = uc.user_id
WHERE c.dwell_time_sec > cs.high_dwell_threshold
ORDER BY c.dwell_time_sec DESC LIMIT 20;
```

---
*Verified and submitted by: 24DIT043 Krushil Patel*
