"""
PRACTICAL 10: BATCH & STREAM TRANSFORMATION ENGINE WITH WATERMARKING
Author: 24DIT043 Krushil Patel
Tools: Python, Pandas, Datetime Optimization Frameworks
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

def generate_telemetry_and_metadata():
    """Generates out-of-order streaming IoT telemetry and static batch metadata."""
    print("\n[Step 1/5] Generating Out-of-Order IoT Stream & Batch Metadata...")
    
    # 1. Static Batch Reference Metadata
    device_metadata = pd.DataFrame([
        {"device_id": "IOT-DEV-001", "model": "ThermSense-X", "factory_zone": "Building-A", "critical_temp_max": 85.0},
        {"device_id": "IOT-DEV-002", "model": "VibroGuard-Pro", "factory_zone": "Building-B", "critical_temp_max": 90.0},
        {"device_id": "IOT-DEV-003", "model": "OptiPressure-Z", "factory_zone": "Building-A", "critical_temp_max": 80.0},
        {"device_id": "IOT-DEV-004", "model": "FlowMeter-400", "factory_zone": "Building-C", "critical_temp_max": 95.0},
    ])

    # 2. Chronologically Out-of-Order Streaming Telemetry with Late Arrivals
    base_time = datetime(2026, 10, 22, 10, 0, 0)
    
    events = [
        # Normal ordered events
        {"event_id": 1, "device_id": "IOT-DEV-001", "event_time": base_time + timedelta(seconds=10), "arrival_time": base_time + timedelta(seconds=12), "temperature": 72.5, "pressure_psi": 101.2},
        {"event_id": 2, "device_id": "IOT-DEV-002", "event_time": base_time + timedelta(seconds=25), "arrival_time": base_time + timedelta(seconds=27), "temperature": 88.0, "pressure_psi": 104.5},
        {"event_id": 3, "device_id": "IOT-DEV-001", "event_time": base_time + timedelta(seconds=60), "arrival_time": base_time + timedelta(seconds=62), "temperature": 74.0, "pressure_psi": 101.9},
        
        # Acceptable minor late arrival (within 60s lateness threshold)
        {"event_id": 4, "device_id": "IOT-DEV-003", "event_time": base_time + timedelta(seconds=45), "arrival_time": base_time + timedelta(seconds=70), "temperature": 79.2, "pressure_psi": 99.8},
        
        # Current high-watermark advancing event
        {"event_id": 5, "device_id": "IOT-DEV-002", "event_time": base_time + timedelta(seconds=180), "arrival_time": base_time + timedelta(seconds=182), "temperature": 91.5, "pressure_psi": 105.1},
        
        # OBSOLETE LATE ARRIVAL (Event was at +30s, arriving after watermark passed +120s) -> Must be dropped!
        {"event_id": 6, "device_id": "IOT-DEV-001", "event_time": base_time + timedelta(seconds=30), "arrival_time": base_time + timedelta(seconds=190), "temperature": 73.1, "pressure_psi": 101.5},
        
        # Another obsolete late arrival
        {"event_id": 7, "device_id": "IOT-DEV-004", "event_time": base_time + timedelta(seconds=20), "arrival_time": base_time + timedelta(seconds=210), "temperature": 82.0, "pressure_psi": 98.4},

        # Fresh recent event
        {"event_id": 8, "device_id": "IOT-DEV-001", "event_time": base_time + timedelta(seconds=220), "arrival_time": base_time + timedelta(seconds=222), "temperature": 75.8, "pressure_psi": 102.3},
    ]
    stream_df = pd.DataFrame(events)
    print(f"  [OK] Created {len(stream_df)} streaming records (including artificial out-of-order delays).")
    return stream_df, device_metadata

def apply_watermark_stream_filtering(stream_df, allowed_lateness_sec=60):
    """
    Simulates streaming watermark processing:
    Watermark = current_max_event_time - allowed_lateness
    Any incoming record with event_time < watermark is dropped as obsolete.
    """
    print(f"\n[Step 2/5] Enforcing Streaming Watermark Constraints (Allowed Lateness: {allowed_lateness_sec}s)...")
    
    accepted_records = []
    dropped_records = []
    
    current_watermark = stream_df["event_time"].min() - timedelta(seconds=allowed_lateness_sec)
    max_event_time = stream_df["event_time"].min()

    for idx, row in stream_df.iterrows():
        # Update running max event time
        if row["event_time"] > max_event_time:
            max_event_time = row["event_time"]
            current_watermark = max_event_time - timedelta(seconds=allowed_lateness_sec)

        # Check against watermark boundary
        if row["event_time"] >= current_watermark:
            accepted_records.append(row)
            print(f"  [ACCEPTED] Event {row['event_id']} (Device {row['device_id']}) @ {row['event_time'].strftime('%H:%M:%S')} >= Watermark {current_watermark.strftime('%H:%M:%S')}")
        else:
            delay = (current_watermark - row["event_time"]).total_seconds()
            dropped_records.append(row)
            print(f"  [DROPPED OBSOLETE] Event {row['event_id']} (Device {row['device_id']}) @ {row['event_time'].strftime('%H:%M:%S')} is {delay:.0f}s older than Watermark {current_watermark.strftime('%H:%M:%S')}!")

    clean_stream_df = pd.DataFrame(accepted_records)
    print(f"\n  [WATERMARK SUMMARY] Processed: {len(stream_df)} | Accepted: {len(accepted_records)} | Dropped: {len(dropped_records)}")
    return clean_stream_df

def enrich_stream_with_batch(stream_df, metadata_df):
    """Performs cross-source business enrichment join between fast stream and static batch tables."""
    print("\n[Step 3/5] Executing Cross-Source Stream-to-Batch Enrichment Join...")
    enriched_df = pd.merge(stream_df, metadata_df, on="device_id", how="inner")
    
    # Conditional business transformation logic
    enriched_df["is_temp_critical"] = enriched_df["temperature"] > enriched_df["critical_temp_max"]
    print("  [OK] Successfully enriched stream records with factory zone and safety thresholds:")
    for _, r in enriched_df.iterrows():
        status = "ALERT CRITICAL" if r["is_temp_critical"] else "NORMAL"
        print(f"   - Event {r['event_id']}: {r['device_id']} ({r['model']} in {r['factory_zone']}) | Temp: {r['temperature']}C | Status: {status}")
    return enriched_df

def compute_windowed_aggregations(stream_df):
    """
    Compares Tumbling Window (fixed non-overlapping) vs. Rolling Window (sliding).
    """
    print("\n[Step 4/5] Computing Multi-Level Tumbling vs. Rolling Window Aggregations...")
    
    # Sort chronologically by event time
    df_sorted = stream_df.sort_values("event_time").set_index("event_time")
    
    # 1. Tumbling Window Aggregation (Fixed 1-Minute non-overlapping intervals)
    tumbling_df = df_sorted.groupby(["device_id"]).resample("1min")[["temperature", "pressure_psi"]].mean().reset_index()
    print("  [TUMBLING WINDOW (1-Minute Fixed Interval)]")
    for _, r in tumbling_df.dropna().iterrows():
        print(f"    Bucket {r['event_time'].strftime('%H:%M:%S')} | Device: {r['device_id']} | Avg Temp: {r['temperature']:.2f}C")

    # 2. Rolling Window Aggregation (Sliding 2-Minute window)
    print("\n  [ROLLING WINDOW (2-Minute Sliding Interval)]")
    df_sorted["rolling_avg_temp"] = df_sorted.groupby("device_id")["temperature"].rolling("2min").mean().values
    for idx, r in df_sorted.iterrows():
        print(f"    Timestamp {idx.strftime('%H:%M:%S')} | Device: {r['device_id']} | Instant Temp: {r['temperature']}C | Rolling Avg: {r['rolling_avg_temp']:.2f}C")

def run_fraud_detection_stream():
    """
    Supplementary Problem: Stream transformation block that detects financial fraud
    by calculating rolling, windowed transaction volume checks per user ID over 5-minute intervals.
    """
    print("\n[Step 5/5] Supplementary Problem: Real-Time Fraud Detection Engine (Rolling 5-Min Volume)...")
    
    tx_base = datetime(2026, 10, 22, 14, 0, 0)
    tx_events = [
        {"tx_id": "TX-1", "user_id": "USR-101", "amount": 150.0, "time": tx_base + timedelta(minutes=1)},
        {"tx_id": "TX-2", "user_id": "USR-102", "amount": 50.0,  "time": tx_base + timedelta(minutes=2)},
        {"tx_id": "TX-3", "user_id": "USR-101", "amount": 2500.0, "time": tx_base + timedelta(minutes=2, seconds=30)},
        {"tx_id": "TX-4", "user_id": "USR-101", "amount": 3200.0, "time": tx_base + timedelta(minutes=3)}, # FRAUD VELOCITY!
        {"tx_id": "TX-5", "user_id": "USR-102", "amount": 75.0,  "time": tx_base + timedelta(minutes=4)},
        {"tx_id": "TX-6", "user_id": "USR-101", "amount": 1200.0, "time": tx_base + timedelta(minutes=4, seconds=45)}, # FRAUD VELOCITY!
        {"tx_id": "TX-7", "user_id": "USR-101", "amount": 100.0,  "time": tx_base + timedelta(minutes=12)}, # Outside 5-min window (SAFE)
    ]
    df_tx = pd.DataFrame(tx_events).sort_values("time").set_index("time")
    
    # Calculate rolling 5-minute transaction count and cumulative amount per user
    df_tx["rolling_5m_count"] = df_tx.groupby("user_id")["amount"].rolling("5min").count().values
    df_tx["rolling_5m_sum"] = df_tx.groupby("user_id")["amount"].rolling("5min").sum().values

    # Flag fraud if > 2 transactions AND sum > $4,000 within any 5-minute sliding window
    df_tx["fraud_alert"] = (df_tx["rolling_5m_count"] >= 3) & (df_tx["rolling_5m_sum"] >= 4000.0)

    for idx, r in df_tx.iterrows():
        flag_str = ">>> [FRAUD ALERT TRIGGERED!]" if r["fraud_alert"] else "[NORMAL]"
        print(f"  Tx {r['tx_id']} | User: {r['user_id']} | Amt: ${r['amount']} | Rolling 5m Vol: ${r['rolling_5m_sum']:,.2f} ({int(r['rolling_5m_count'])} txs) | {flag_str}")

def run_pipeline():
    print("=" * 80)
    print("     PRACTICAL 10: STREAM & BATCH DATA TRANSFORMATION PIPELINE     ")
    print("     Topic: Watermarking, Rolling Windows, and Real-Time Fraud Detection")
    print("=" * 80)

    stream_df, metadata_df = generate_telemetry_and_metadata()
    clean_stream_df = apply_watermark_stream_filtering(stream_df, allowed_lateness_sec=60)
    enriched_df = enrich_stream_with_batch(clean_stream_df, metadata_df)
    compute_windowed_aggregations(clean_stream_df)
    run_fraud_detection_stream()

if __name__ == "__main__":
    run_pipeline()
