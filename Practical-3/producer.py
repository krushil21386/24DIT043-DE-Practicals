from kafka import KafkaProducer
import pandas as pd
import json
import time


producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda x: json.dumps(x).encode("utf-8")
)

topic = "web_activity"

# Read the dataset generated earlier
df = pd.read_csv("data/user_activity.csv")

print("Producer started")


for _, row in df.iterrows():

    data = {
        "user_id": int(row["user_id"]),
        "event": row["event"],
        "response_time_ms": float(row["response_time_ms"]),
        "cpu_usage": float(row["cpu_usage"]),
        "memory_usage": float(row["memory_usage"]),
        "server_id": int(row["server_id"]),
        "timestamp": time.time()
    }

    producer.send(topic, data)

    print("Sent:", data)

    # Small delay to simulate real-time events
    time.sleep(0.1)


producer.flush()
producer.close()

print("Producer finished")