# DATA ENGINEERING LAB — PRACTICAL REPORT 10

**Student Name**: Krushil Patel  
**Student ID**: 24DIT043  
**Practical No**: 10  
**Title**: Comprehensive Batch & Streaming Transformations with Watermarking & Fraud Detection  

---

## 1. Problem Definition & Objectives

Implement comprehensive data transformation modules across both batch environments and streaming runtime pipelines. Handle advanced operations including conditional data filtering, cross-source business enrichment joins, multi-level rolling window aggregations, and managing late-arriving stream records via system **watermark constraints**.

---

## 2. Key Questions & Theoretical Analysis

### Key Point 1: Explain how a streaming engine uses watermarks to differentiate between acceptable late-arriving data and obsolete records that should be dropped.

In a streaming engine (like Apache Spark Structured Streaming or Apache Flink), event generation time differs from system arrival time due to network congestion or IoT offline caching:
$$\text{Watermark} = \max(\text{Event Time Seen So Far}) - \text{Allowed Lateness Threshold}$$
- **Acceptable Late-Arriving Data**: If an event arrives out-of-order but its timestamp satisfies $\text{Event Time} \ge \text{Watermark}$, the engine accepts it and updates the corresponding window aggregate.
- **Obsolete Dropped Data**: Once the watermark advances past the close time of a window, that window's state is finalized and committed to downstream storage. Any subsequent record with $\text{Event Time} < \text{Watermark}$ is safely dropped to prevent state memory from leaking infinitely.

### Key Point 2: Compare the processing mechanics and memory footprints of a rolling window aggregation against a standard tumbling window block in streaming pipelines.

| Dimension | Tumbling Window | Rolling (Sliding) Window |
|---|---|---|
| **Boundary Definition** | Fixed, non-overlapping intervals (e.g., 00:00-00:05, 00:05-00:10). | Overlapping intervals with a slide frequency (e.g., 5-minute window sliding every 1 minute). |
| **Record Membership** | Every record belongs to exactly **one** window bucket. | A single record belongs to **multiple** concurrent window slices. |
| **State Memory Footprint** | Low. Once a bucket ends, its state is materialized and cleared from memory. | High. The engine must maintain multiple overlapping state accumulators simultaneously in memory. |
| **Output Frequency** | Emits aggregated metrics only at the end of each fixed interval. | Emits updated rolling trends continuously as each slide arrives. |

### Key Point 3: What are the primary structural and operational challenges encountered when joining a fast real-time event stream with a slow batch metadata table?

1. **Temporal Skew & Static Cache Invalidation**: The static batch table in memory may become stale as dimensions change in the source database. The streaming engine must implement periodic broadcast reloading without pausing stream ingestion.
2. **Backpressure & Memory Asymmetry**: If the batch metadata lookup requires remote database network roundtrips, it can block high-velocity stream processing, causing incoming stream message buffers to overflow.
3. **Out-of-Order Enrichment**: If a stream event arrives referencing a newly registered entity that has not yet synced to the batch table, the join can silently fail or drop records unless outer joins and delayed retry buffers are configured.

---

## 3. Supplementary Problem: Real-Time Fraud Detection Engine

The streaming transformation block monitors high-velocity transaction bursts within a rolling 5-minute window:
```python
# Calculate rolling 5-minute window volume per user
df_tx["rolling_5m_count"] = df_tx.groupby("user_id")["amount"].rolling("5min").count().values
df_tx["rolling_5m_sum"] = df_tx.groupby("user_id")["amount"].rolling("5min").sum().values

# Trigger fraud alert if velocity thresholds exceeded
df_tx["fraud_alert"] = (df_tx["rolling_5m_count"] >= 3) & (df_tx["rolling_5m_sum"] >= 4000.0)
```

---
*Verified and submitted by: 24DIT043 Krushil Patel*
