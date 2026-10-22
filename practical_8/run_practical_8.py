"""
Practical 8 Execution Runner: Analytical Query Optimization & Plan Analysis
Author: 24DIT043 Krushil Patel
"""

import os
from query_optimizer import run_performance_suite

def main():
    print("=" * 80)
    print("      PRACTICAL 8: MASSIVE DATASET QUERY PLAN PROFILING & OPTIMIZATION")
    print("      Topic: Execution Plan Diagnostics, Subquery Refactoring, and Indexing")
    print("=" * 80)

    # Remove previous temp duckdb file if exists
    if os.path.exists("clickstream_analytics.duckdb"):
        try:
            os.remove("clickstream_analytics.duckdb")
        except Exception:
            pass

    run_performance_suite()

    print("\n[SUCCESS] Practical 8 completed successfully!")
    print("24DIT043 Krushil Patel")

if __name__ == "__main__":
    main()
