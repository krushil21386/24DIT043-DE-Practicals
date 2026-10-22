
import sys
import json
import os

def mc_cli(args):
    if len(args) < 1:
        print("Usage: python mc_simulator.py [ilm|ls|stat|admin] [subcommands...]")
        return

    cmd = args[0].lower()

    if cmd == "ilm":
        subcmd = args[1] if len(args) > 1 else "ls"
        if subcmd in ["rule", "ls"]:
            print("mc: Lifecycle rules configured on alias 'myminio/enterprise-datalake':")
            print("-" * 85)
            print(f"{'RULE ID':<35} {'STATUS':<10} {'PREFIX':<15} {'TRANSITION / EXPIRATION'}")
            print("-" * 85)
            policy_file = "ilm_lifecycle_policy.json"
            if os.path.exists(policy_file):
                with open(policy_file, "r") as f:
                    policy = json.load(f)
                for rule in policy.get("Rules", []):
                    rule_id = rule.get("ID", "")
                    status = rule.get("Status", "")
                    prefix = rule.get("Filter", {}).get("Prefix", "")
                    transitions = rule.get("Transitions", [])
                    exp = rule.get("Expiration", {})
                    t_str = ""
                    if transitions:
                        t_str = ", ".join([f"{t['Days']}d -> {t['StorageClass']}" for t in transitions])
                    elif exp:
                        t_str = f"Expire after {exp.get('Days')} days"
                    print(f"{rule_id:<35} {status:<10} {prefix:<15} {t_str}")
            print("-" * 85)
        elif subcmd in ["import", "add"]:
            target_file = args[2] if len(args) > 2 else "ilm_lifecycle_policy.json"
            print(f"mc: Successfully imported lifecycle policy rule matrix from '{target_file}' to bucket 'myminio/enterprise-datalake'.")
            print("mc: Enforcing ILM rules on active object instances...")
        elif subcmd == "export":
            print("mc: Exporting active ILM policy rules JSON schema:")
            with open("ilm_lifecycle_policy.json", "r") as f:
                print(f.read())
    elif cmd == "ls":
        print("mc: Listing objects in bucket 'myminio/enterprise-datalake':")
        manifest_file = "outputs/updated_dataset_manifest.json" if os.path.exists("outputs/updated_dataset_manifest.json") else "outputs/dataset_manifest.json"
        if os.path.exists(manifest_file):
            with open(manifest_file, "r") as f:
                objects = json.load(f)
            print(f"{'DATE':<20} {'SIZE':<10} {'STORAGE TIER':<15} {'OBJECT NAME'}")
            print("-" * 75)
            for obj in objects:
                created = obj['created_at'][:19].replace('T', ' ')
                size = f"{obj['size_gb']} GiB"
                tier = obj['current_tier']
                name = obj['object_name']
                print(f"{created:<20} {size:<10} {tier:<15} {name}")

if __name__ == "__main__":
    mc_cli(sys.argv[1:])
