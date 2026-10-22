"""
Practical 11 Execution Runner: Secure Analytical Serving Platform & Reverse ETL
Author: 24DIT043 Krushil Patel
"""

import os
from secure_reverse_etl import run_suite

def main():
    if os.path.exists("secure_platform.db"):
        try:
            os.remove("secure_platform.db")
        except Exception:
            pass

    run_suite()
    print("\n" + "=" * 80)
    print(" [COMPLETED] Practical 11 executed successfully!")
    print("=" * 80)
    print("24DIT043 Krushil Patel")

if __name__ == "__main__":
    main()
