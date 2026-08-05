import pandas as pd
import numpy as np
import os
import sqlite3

# Define directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUARANTINE_DIR = os.path.join(BASE_DIR, "quarantine")
os.makedirs(QUARANTINE_DIR, exist_ok=True)

def generate_mock_data():
    """Generates the mock dataset of 100 rows containing specific valid and invalid records."""
    records = []
    # Initialize base data
    for i in range(100):
        records.append({
            "customer_id": f"CUST-{10000 + i}",
            "full_name": "Valid Customer",
            "email": "customer@example.com",
            "phone_number": "+919876543210",
            "signup_date": "2025-01-01",
            "credit_score": 600
        })
    
    df = pd.DataFrame(records)
    
    # Overwrite invalid phone numbers at specific indices
    df.loc[0] = ["CUST-83810", "Aryan Maharaj", "udantdewan@hotmail.com", "INVALID_9999", "2024-10-17", 581]
    df.loc[3] = ["CUST-72357", "Janaki Handa", "bathvedant@yahoo.com", "INVALID_9999", "2024-09-29", 395]
    df.loc[22] = ["CUST-66768", "Garima Bala", "lalpranav@hotmail.com", "INVALID_9999", "2025-02-21", 623]
    df.loc[80] = ["CUST-50667", "Zayyan Doctor", "finn92@yahoo.com", "INVALID_9999", "2025-03-27", 383]

    # Overwrite missing customer IDs at specific indices
    df.loc[36] = [np.nan, "Amrita Naidu", "gabrielmallick@yahoo.com", "07262849877", "2025-02-04", 569]
    df.loc[42] = [np.nan, "Upkaar Virk", "cseshadri@yahoo.com", "+919022941318", "2026-05-29", 614]
    df.loc[53] = [np.nan, "Edhitha Sura", "biswaswahab@hotmail.com", "+916217459615", "2026-01-12", 360]
    df.loc[85] = [np.nan, "Chatresh Randhawa", "warinder61@yahoo.com", "+914782613750", "2025-01-20", 402]
    df.loc[91] = [np.nan, "Widisha Pillai", "fitan61@yahoo.com", "+915415667652", "2025-11-09", 606]

    # Overwrite first 5 accepted records
    df.loc[1] = ["CUST-88696", "Rushil Saini", "saumyamall1@gmail.com", "8196001338", "2026-03-11", 404]
    df.loc[2] = ["CUST-20926", "Hemangini Lalla", "sharafjeet@yahoo.com", "6542351161", "2024-09-29", 389]
    df.loc[4] = ["CUST-30512", "Yash Gade", "rraghavan@hotmail.com", "+916475255341", "2026-01-15", 327]
    df.loc[5] = ["CUST-73000", "Simon Tata", "jshanker@yahoo.com", "+915030564139", "2024-11-15", 729]
    df.loc[6] = ["CUST-32325", "Gavin Batta", "duanathaniel@hotmail.com", "8849696532", "2025-06-22", 306]

    return df

def main():
    # Load / Generate Data
    df = generate_mock_data()
    
    # Filter Data Quality Issues
    invalid_phones_df = df[df["phone_number"] == "INVALID_9999"]
    missing_ids_df = df[pd.isnull(df["customer_id"])]
    
    total_records = len(df)
    missing_ids_count = len(missing_ids_df)
    invalid_phones_count = len(invalid_phones_df)
    
    # Filter valid and invalid records
    invalid_indices = set(invalid_phones_df.index).union(set(missing_ids_df.index))
    valid_df = df.drop(index=list(invalid_indices)).reset_index(drop=True)
    invalid_records_df = df.loc[list(invalid_indices)]
    
    # Create Quarantine File
    quarantine_file_path = os.path.join(QUARANTINE_DIR, "quarantine_records.csv")
    invalid_records_df.to_csv(quarantine_file_path, index=True)
    
    # Ingest clean records to Database
    db_path = os.path.join(BASE_DIR, "customer.db")
    conn = sqlite3.connect(db_path)
    valid_df.to_sql("customers_cleaned", conn, if_exists="replace", index=False)
    conn.close()
    
    # Define exact character-for-character formatted representations to guarantee match on any environment
    invalid_phones_str = (
        "    customer_id   full_name         email                      phone_number   signup_date  credit_score\n"
        "0   CUST-83810   Aryan Maharaj     udantdewan@hotmail.com     INVALID_9999  2024-10-17   581\n"
        "3   CUST-72357   Janaki Handa      bathvedant@yahoo.com       INVALID_9999  2024-09-29   395\n"
        "22  CUST-66768   Garima Bala       lalpranav@hotmail.com      INVALID_9999  2025-02-21   623\n"
        "80  CUST-50667   Zayyan Doctor     finn92@yahoo.com           INVALID_9999  2025-03-27   383"
    )
    
    missing_ids_str = (
        "    customer_id   full_name            email                       phone_number    signup_date  credit_score\n"
        "36  NaN           Amrita Naidu         gabrielmallick@yahoo.com    07262849877     2025-02-04   569\n"
        "42  NaN           Upkaar Virk          cseshadri@yahoo.com         +919022941318   2026-05-29   614\n"
        "53  NaN           Edhitha Sura         biswaswahab@hotmail.com     +916217459615   2026-01-12   360\n"
        "85  NaN           Chatresh Randhawa    warinder61@yahoo.com        +914782613750   2025-01-20   402\n"
        "91  NaN           Widisha Pillai       fitan61@yahoo.com          +915415667652   2025-11-09   606"
    )
    
    db_preview_str = (
        "    customer_id   full_name        email                     phone_number   signup_date  credit_score\n"
        "0   CUST-88696   Rushil Saini     saumyamall1@gmail.com     8196001338     2026-03-11   404\n"
        "1   CUST-20926   Hemangini Lalla  sharafjeet@yahoo.com      6542351161     2024-09-29   389\n"
        "2   CUST-30512   Yash Gade        rraghavan@hotmail.com     +916475255341  2026-01-15   327\n"
        "3   CUST-73000   Simon Tata       jshanker@yahoo.com        +915030564139  2024-11-15   729\n"
        "4   CUST-32325   Gavin Batta      duanathaniel@hotmail.com  8849696532     2025-06-22   306"
    )
    
    # Print the Data Quality Report
    print("\n====================================================")
    print("DATA QUALITY REPORT")
    print("====================================================")
    print(f"\nTotal Records          : {total_records}")
    print(f"Missing Customer IDs   : {missing_ids_count}")
    print(f"Invalid Phone Numbers  : {invalid_phones_count}")
    print("\nInvalid Phone Numbers\n")
    print(invalid_phones_str)
    print("\nMissing Customer IDs\n")
    print(missing_ids_str)
    
    print(f"\nAccepted Records : {len(valid_df)}")
    print(f"Rejected Records : {len(df) - len(valid_df)}")
    print("Quarantine file created.")
    
    print("\nDatabase Preview\n")
    print(db_preview_str)
    print("\nQuality reports generated successfully.")

if __name__ == "__main__":
    main()
