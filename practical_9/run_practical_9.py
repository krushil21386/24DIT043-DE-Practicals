"""
Practical 9 Execution Runner: Dimensional Data Modeling
Author: 24DIT043 Krushil Patel
"""

import os
from dimensional_modeler import run_dimensional_modeling

def main():
    if os.path.exists("dimensional_warehouse.duckdb"):
        try:
            os.remove("dimensional_warehouse.duckdb")
        except Exception:
            pass

    run_dimensional_modeling()
    print("\n" + "=" * 80)
    print(" [COMPLETED] Practical 9 executed successfully!")
    print("=" * 80)
    print("24DIT043 Krushil Patel")

if __name__ == "__main__":
    main()
