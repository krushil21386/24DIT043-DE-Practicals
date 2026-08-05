import pandas as pd
import sqlite3
import logging
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOG_DIR, exist_ok=True)

# Logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "ingestion.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Read CSV
df = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))

# Keep only valid records
valid_df = df.dropna(subset=["CustomerID", "Email", "City"])

# Connect SQLite Database
conn = sqlite3.connect(os.path.join(BASE_DIR, "customer.db"))

# Store data
valid_df.to_sql("customers", conn, if_exists="replace", index=False)

conn.close()

logging.info(f"{len(valid_df)} valid records inserted successfully.")
logging.warning(f"{len(df)-len(valid_df)} invalid records skipped.")

print("========== INGESTION REPORT ==========")
print("Database Created Successfully!")
print("Table Name : customers")
print("Valid Records Loaded :", len(valid_df))
print("Invalid Records Skipped :", len(df)-len(valid_df))
print("Log File : logs/ingestion.log")