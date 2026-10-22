import json
import csv
import os
from datetime import datetime

def evaluate_and_enforce_lifecycle(input_file="outputs/dataset_manifest.json", output_file="outputs/lifecycle_execution_log.txt"):
    os.makedirs("outputs", exist_ok=True)

    if not os.path.exists(input_file):
        print(f"[-] Error: {input_file} not found. Running dataset generator first...")
        from dataset_generator import generate_datasets
        generate_datasets()

    with open(input_file, "r") as f:
        objects = json.load(f)

    log_entries = []
    log_entries.append("================================================================================")
    log_entries.append("           AUTOMATED STORAGE LIFECYCLE POLICY ENFORCEMENT ENGINE             ")
    log_entries.append(f" Execution Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    log_entries.append("================================================================================\n")

    transitioned_objects = []

    for obj in objects:
        original_tier = obj["current_tier"]
        days_inactive = obj["days_since_last_access"]
        size_gb = obj["size_gb"]
        name = obj["object_name"]
        
        target_tier = original_tier
        action = "NO_CHANGE"
        rationale = "Object access pattern within operational threshold."

        # Lifecycle Matrix Evaluation Logic:
        # 1. If days_since_last_access >= 365 and content_type == 'temporary_dump' -> EXPIRE / DELETE
        if days_inactive >= 365 and "temp/" in name:
            target_tier = "EXPIRED (DELETED)"
            action = "EXPIRE_OBJECT"
            rationale = "Exceeded 365-day retention policy limit for temporary/staging objects."
        # 2. If days_since_last_access >= 180 or (days_inactive >= 90 and obj['total_access_count_30d'] == 0) -> COLD
        elif days_inactive >= 180 or (days_inactive >= 90 and obj["total_access_count_30d"] == 0):
            if original_tier != "Cold":
                target_tier = "Cold"
                action = "TRANSITION_TO_COLD"
                rationale = f"Inactive for {days_inactive} days (>90 day boundary with 0 queries). Demoted to Deep Compression Archiving."
        # 3. If days_since_last_access >= 30 and original_tier == "Hot" -> WARM
        elif days_inactive >= 30 and original_tier == "Hot":
            target_tier = "Warm"
            action = "TRANSITION_TO_WARM"
            rationale = f"Inactive for {days_inactive} days (>30 day threshold). Demoted from Hot to Warm Infrequent Access."

        obj_copy = dict(obj)
        obj_copy["previous_tier"] = original_tier
        obj_copy["current_tier"] = target_tier
        obj_copy["action_taken"] = action
        obj_copy["rationale"] = rationale
        transitioned_objects.append(obj_copy)

        status_flag = "[TRANSITION]" if action != "NO_CHANGE" else "[NO CHANGE]"
        entry = (
            f"{status_flag} Object: {name}\n"
            f"    - Size: {size_gb:.1f} GB | Inactive Days: {days_inactive} | 30d Query Count: {obj['total_access_count_30d']}\n"
            f"    - Tier Transition: {original_tier} ---> {target_tier}\n"
            f"    - Policy Rationale: {rationale}\n"
        )
        log_entries.append(entry)
        print(entry)

    # Save execution log
    with open(output_file, "w") as f:
        f.write("\n".join(log_entries))

    # Save updated manifest
    with open("outputs/updated_dataset_manifest.json", "w") as f:
        json.dump(transitioned_objects, f, indent=4)

    print(f"[+] Lifecycle policy enforcement complete. Detailed log saved to: {output_file}")
    return transitioned_objects

if __name__ == "__main__":
    evaluate_and_enforce_lifecycle()
