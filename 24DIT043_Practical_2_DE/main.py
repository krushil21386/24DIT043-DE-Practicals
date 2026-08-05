import subprocess
import sys
import os
from datetime import datetime

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "Output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Path to the single consolidated output file
report_file_path = os.path.join(OUTPUT_DIR, "pipeline_output.txt")

class Tee:
    """Consolidation logger to write to both stdout (terminal) and a log file."""
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log = open(filepath, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

def run_script(script_name):
    """Executes a sub-script as a subprocess and streams its output."""
    script_path = os.path.join(BASE_DIR, script_name)
    print(f"\n" + "-" * 70)
    print(f"STAGE: {script_name.upper().replace('.PY', '')}")
    print("-" * 70 + "\n")
    
    # Execute the python script
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, cwd=BASE_DIR)
    
    # Write output to Tee
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(f"\n[ERROR] Error in {script_name}:", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        
    return result.returncode == 0

def main():
    # Set up stdout redirection
    tee = Tee(report_file_path)
    sys.stdout = tee

    print("=" * 70)
    print("              DATA ENGINEERING PIPELINE ORCHESTRATOR")
    print("=" * 70)
    print(f"Execution Time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Report  : Output/pipeline_output.txt")
    print("=" * 70)
    
    # List of scripts to run sequentially
    pipeline_stages = [
        "generate_data.py",
        "profile_data.py",
        "validation.py",
        "ingestion.py"
    ]
    
    success = True
    for stage in pipeline_stages:
        if not run_script(stage):
            print(f"\n[FAILURE] Pipeline execution halted due to failure in: {stage}")
            success = False
            break
            
    if success:
        print("\n" + "=" * 70)
        print("PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
    
    print(f"\nConsolidated pipeline report successfully saved to: {report_file_path}\n")
    
    # Restore stdout
    sys.stdout = tee.terminal
    tee.log.close()

if __name__ == "__main__":
    main()
