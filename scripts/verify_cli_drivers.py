#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path

def verify_backend(name: str):
    print(f"--- Verifying {name} ---")
    script_path = Path(f"backends/{name}/run")
    if not script_path.exists():
        print(f"FAIL: Script {script_path} not found.")
        return False

    # Check if we can run it (even if it fails due to missing binary)
    # We pipe "echo hello" to it.
    try:
        env = os.environ.copy()
        env.setdefault("MITTELO_SUBPROCESS_HOME", str(Path("reports") / "verify_cli_drivers" / name / "home"))
        process = subprocess.run(
            [str(script_path)],
            input="echo hello",
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            env=env,
        )
        if process.returncode != 0:
            msg = (process.stderr or process.stdout).strip()
            print(f"FAIL: rc={process.returncode}: {msg}")
            return False

        out = (process.stdout or "").strip()
        err = (process.stderr or "").strip()
        if err:
            print(f"FAIL: stderr not empty: {err}")
            return False
        if out.lower().startswith("error:"):
            print(f"FAIL: backend returned error output: {out}")
            return False
        print(f"PASS: Script ran successfully. Output: {out[:50]}...")
        return True

    except Exception as e:
        print(f"FAIL: Execution failed: {e}")
        return False

def main():
    backends = ["gemini", "claude_code", "codex", "kiro", "kimi"]
    ok = True
    for b in backends:
        if not verify_backend(b):
            ok = False
    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
