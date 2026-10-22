import pandas as pd
import time
import os


# Configuration
DATA_FILE = "data/user_activity.csv"

# Number of records processed in one batch
BATCH_SIZE = 1000


print("========================================")
print("       BATCH DATA PROCESSING")
print("========================================")


# Check whether dataset exists
if not os.path.exists(DATA_FILE):
    print("Dataset not found!")
    print("Run generate_data.py first.")
    exit()


# Read dataset
df = pd.read_csv(DATA_FILE)

print("Total records:", len(df))
print("Batch size:", BATCH_SIZE)
print()


# Store benchmark results
results = []

total_records = len(df)

batch_number = 0

overall_start = time.time()


# Process data in blocks
for start in range(0, total_records, BATCH_SIZE):

    batch_number += 1

    end = min(start + BATCH_SIZE, total_records)

    batch = df.iloc[start:end].copy()

    print("----------------------------------------")
    print("Processing Batch:", batch_number)
    print("Records:", len(batch))

    # Start processing timer
    processing_start = time.time()


    # Simulate batch processing

    # Average response time
    average_response_time = batch["response_time_ms"].mean()

    # Average CPU usage
    average_cpu = batch["cpu_usage"].mean()

    # Average memory usage
    average_memory = batch["memory_usage"].mean()

    # Count events
    event_counts = batch["event"].value_counts()


    # End processing timer
    processing_end = time.time()

    processing_time = processing_end - processing_start


    # Calculate throughput
    throughput = len(batch) / processing_time if processing_time > 0 else 0


    print(
        "Processing Time:",
        round(processing_time, 6),
        "seconds"
    )

    print(
        "Throughput:",
        round(throughput, 2),
        "records/sec"
    )

    print(
        "Average Response Time:",
        round(average_response_time, 2),
        "ms"
    )

    print(
        "Average CPU:",
        round(average_cpu, 2),
        "%"
    )

    print(
        "Average Memory:",
        round(average_memory, 2),
        "%"
    )


    # Store result
    results.append({
        "batch": batch_number,
        "records": len(batch),
        "processing_time_sec": processing_time,
        "throughput_records_sec": throughput,
        "average_response_time_ms": average_response_time,
        "average_cpu": average_cpu,
        "average_memory": average_memory
    })


overall_end = time.time()

total_time = overall_end - overall_start


# Convert results to DataFrame
results_df = pd.DataFrame(results)


# Overall statistics
total_throughput = total_records / total_time


print("\n========================================")
print("          BATCH RESULTS")
print("========================================")

print("Total Records:", total_records)

print(
    "Total Processing Time:",
    round(total_time, 4),
    "seconds"
)

print(
    "Overall Throughput:",
    round(total_throughput, 2),
    "records/sec"
)

print(
    "Average Batch Throughput:",
    round(
        results_df["throughput_records_sec"].mean(),
        2
    ),
    "records/sec"
)


# Save benchmark results
os.makedirs("results", exist_ok=True)

results_file = "results/batch_results.csv"

results_df.to_csv(results_file, index=False)


print("\nBenchmark results saved to:")
print(results_file)

print("\nBatch processing completed!")