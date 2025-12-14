#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path

def verify_backend(name: str):
    print(f"--- Verifying {name} ---")
    script_path = Path(f"backends/{name}/run")
    if not script_path.exists():
        print(f"FAIL: Script {script_path} not found.")
        return

    # Check if we can run it (even if it fails due to missing binary)
    # We pipe "echo hello" to it.
    try:
        process = subprocess.run(
            [str(script_path)],
            input="echo hello",
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        # We expect it to run. If the binary is missing, the python script catches it and yields "Exception: ..."
        # So return code should be 0 from the python script itself, unless it crashes.
        if process.returncode == 0:
            output = process.stdout.strip()
            if "Exception" in output or "Error" in output:
                print(f"WARN: Script ran but reported error (likely missing binary): {output}")
            else:
                print(f"PASS: Script ran successfully. Output: {output[:50]}...")
        else:
            print(f"FAIL: Script crashed with code {process.returncode}. Stderr: {process.stderr}")

    except Exception as e:
        print(f"FAIL: Execution failed: {e}")

def main():
    backends = ["gemini", "claude_code", "codex", "kiro", "kimi"]
    for b in backends:
        verify_backend(b)

if __name__ == "__main__":
    main()
