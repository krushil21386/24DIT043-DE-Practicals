from faker import Faker
import pandas as pd
import random
import json
import os

fake = Faker()

# Create Data folder if it doesn't exist
os.makedirs("Data", exist_ok=True)


# Generate Customer CSV

customers = []

for i in range(1, 21):
    customers.append({
        "CustomerID": i,
        "Name": fake.name(),
        "Email": fake.email(),
        "City": fake.city()
    })

# Intentionally create bad data
customers[2]["Email"] = None
customers[5]["City"] = None
customers[8]["CustomerID"] = None

df = pd.DataFrame(customers)

df.to_csv("Data/customers.csv", index=False)

print("customers.csv generated")

# Generate API JSON


api_data = []

for i in range(1, 11):

    record = {
        "id": i,
        "customer": {
            "name": fake.name(),
            "city": fake.city()
        },
        "order": {
            "amount": random.randint(100, 5000)
        }
    }

    api_data.append(record)

# Create schema drift
del api_data[3]["customer"]["city"]

with open("Data/api_logs.json", "w") as file:
    json.dump(api_data, file, indent=4)

print("api_logs.json generated")

# Generate Config File


with open("Data/config.txt", "w") as file:
    file.write("database=sqlite\n")
    file.write("version=1.0\n")
    file.write("host=localhost\n")

print("config.txt generated")
print("\nData Generation Completed Successfully!")