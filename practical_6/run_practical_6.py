import sys
import os
import time

def run_pipeline():
    print("=" * 85)
    print("        PRACTICAL 6: AUTOMATED STORAGE LIFECYCLE POLICY MATRIX EXECUTION      ")
    print("=" * 85)
    time.sleep(0.5)

    print("\n[STEP 1] Generating Historical System Operational Logs & Access Manifests...")
    from dataset_generator import generate_datasets
    generate_datasets()
    time.sleep(0.5)

    print("\n[STEP 2] Inspecting MinIO JSON Lifecycle Policy Schema (ILM CLI)...")
    from mc_simulator import mc_cli
    mc_cli(["ilm", "import", "ilm_lifecycle_policy.json"])
    print()
    mc_cli(["ilm", "ls"])
    time.sleep(0.5)

    print("\n[STEP 3] Running Background Lifecycle Automation Engine (Evaluating Retention & Access)...")
    from lifecycle_automation import evaluate_and_enforce_lifecycle
    evaluate_and_enforce_lifecycle()
    time.sleep(0.5)

    print("\n[STEP 4] Executing Supplementary Automation: Inactive Data Table API Demotion (>90 Days)...")
    from demote_inactive_tables import scan_and_demote_inactive_tables
    scan_and_demote_inactive_tables()
    time.sleep(0.5)

    print("\n[STEP 5] Calculating Cost Reductions & Generating Financial Charts...")
    from cost_analysis_calculator import analyze_cost_reductions
    analyze_cost_reductions()
    time.sleep(0.5)

    print("\n[STEP 6] Final MinIO Storage Object State & Tier Audit:")
    mc_cli(["ls"])

    print("\n" + "=" * 85)
    print(" [SUCCESS] PRACTICAL 6 COMPLETE! All outputs, logs, and charts saved to 'outputs/'.")
    print("=" * 85)

if __name__ == "__main__":
    run_pipeline()
print("24DIT043 Krushil Patel")