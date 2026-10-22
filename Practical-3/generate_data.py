import pandas as pd
import random
import time
from datetime import datetime


# Number of records to generate
NUM_RECORDS = 10000


events = [
    "login",
    "logout",
    "page_view",
    "search",
    "add_to_cart",
    "purchase"
]

records = []

print(f"Generating {NUM_RECORDS} records...")


for i in range(NUM_RECORDS):

    # Generate timestamp
    timestamp = time.time()

    record = {
        "timestamp": timestamp,
        "datetime": datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        ),
        "user_id": random.randint(1000, 9999),
        "event": random.choice(events),

        # Simulated server metrics
        "response_time_ms": round(random.uniform(50, 500), 2),
        "cpu_usage": round(random.uniform(10, 95), 2),
        "memory_usage": round(random.uniform(20, 90), 2),
        "server_id": random.randint(1, 3)
    }

    records.append(record)


# Convert to Pandas DataFrame
df = pd.DataFrame(records)


# Create data directory if it doesn't exist
import os

os.makedirs("data", exist_ok=True)


# Save dataset
file_path = "data/user_activity.csv"

df.to_csv(file_path, index=False)


print("\nDataset generated successfully!")
print("File:", file_path)
print("Total records:", len(df))

print("\nFirst 5 records:")
print(df.head())