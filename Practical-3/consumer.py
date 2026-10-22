from kafka import KafkaConsumer
import json
import time


# ==============================
# CONFIGURATION
# ==============================

KAFKA_SERVER = "localhost:9092"
TOPIC = "web_activity"
GROUP_ID = "web-activity-group"

TOTAL_MESSAGES = 10000


# ==============================
# CREATE CONSUMER
# ==============================

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_SERVER,

    # Start from earliest message
    auto_offset_reset="earliest",

    # Consumer group
    group_id=GROUP_ID,

    # Convert JSON back to Python dictionary
    value_deserializer=lambda x: json.loads(
        x.decode("utf-8")
    )
)


print("========================================")
print("       KAFKA STREAMING CONSUMER")
print("========================================")

print("Topic:", TOPIC)
print("Waiting for messages...\n")


# ==============================
# VARIABLES
# ==============================

count = 0

total_latency = 0

max_latency = 0

start_time = time.time()


# ==============================
# RECEIVE MESSAGES
# ==============================

for message in consumer:

    data = message.value

    receive_time = time.time()

    # Calculate end-to-end Kafka delivery latency
    latency = (
        receive_time -
        data["producer_timestamp"]
    ) * 1000

    total_latency += latency

    max_latency = max(max_latency, latency)

    count += 1


    # Progress
    if count % 1000 == 0:

        print(
            "Messages received:",
            count,
            "| Latest latency:",
            round(latency, 2),
            "ms"
        )


    # Stop after all records
    if count >= TOTAL_MESSAGES:

        end_time = time.time()

        break


# ==============================
# CALCULATE RESULTS
# ==============================

total_time = end_time - start_time

average_latency = total_latency / count

throughput = count / total_time if total_time > 0 else 0


# ==============================
# DISPLAY RESULTS
# ==============================

print("\n========================================")
print("       STREAMING RESULTS")
print("========================================")

print("Total Messages:", count)

print(
    "Total Time:",
    round(total_time, 4),
    "seconds"
)

print(
    "Average Latency:",
    round(average_latency, 2),
    "ms"
)

print(
    "Maximum Latency:",
    round(max_latency, 2),
    "ms"
)

print(
    "Throughput:",
    round(throughput, 2),
    "messages/sec"
)


consumer.close()

print("\nConsumer finished.")