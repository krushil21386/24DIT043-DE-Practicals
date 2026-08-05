import pandas as pd
import json
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Data")


# Read Customer CSV


csv_file = os.path.join(DATA_DIR, "customers.csv")

df = pd.read_csv(csv_file)

print("========== CUSTOMER DATA PROFILE ==========\n")

print("Rows :", df.shape[0])
print("Columns :", df.shape[1])

print("\nData Types:")
print(df.dtypes)

print("\nNull Values:")
print(df.isnull().sum())

print("\nSchema:")
for column in df.columns:
    print(f"{column} -> {df[column].dtype}")

# Read API JSON


json_file = os.path.join(DATA_DIR, "api_logs.json")

with open(json_file, "r") as file:
    api_data = json.load(file)

print("\n========== API PROFILE ==========")

print("Total API Records :", len(api_data))

print("\nFirst Record Keys:")

for key in api_data[0]:
    print(key)


# Read Config File


config_file = os.path.join(DATA_DIR, "config.txt")

print("\n========== CONFIG FILE ==========")

with open(config_file, "r") as file:
    print(file.read())