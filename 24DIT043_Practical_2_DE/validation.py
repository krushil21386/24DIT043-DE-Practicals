import pandas as pd
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Data")
QUARANTINE_DIR = os.path.join(BASE_DIR, "quarantine")

os.makedirs(QUARANTINE_DIR, exist_ok=True)

# Read CSV
df = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))

valid_records = []
invalid_records = []

# Validate each row
for _, row in df.iterrows():

    if (
        pd.isnull(row["CustomerID"]) or
        pd.isnull(row["Email"]) or
        pd.isnull(row["City"])
    ):
        invalid_records.append(row)
    else:
        valid_records.append(row)

# Convert to DataFrame
valid_df = pd.DataFrame(valid_records)
invalid_df = pd.DataFrame(invalid_records)

# Save invalid records
invalid_file = os.path.join(QUARANTINE_DIR, "bad_records.csv")
invalid_df.to_csv(invalid_file, index=False)

print("========== VALIDATION REPORT ==========")
print("Total Records :", len(df))
print("Valid Records :", len(valid_df))
print("Invalid Records :", len(invalid_df))

print("\nInvalid records saved in:")
print(invalid_file)