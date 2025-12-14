#!/usr/bin/env python3
import os
import sys
import subprocess
import re
from pathlib import Path

# Set up PATH for uv and other tools
os.environ["PATH"] = f"{os.path.expanduser('~')}/.local/bin:{os.environ['PATH']}"

# Read the content of the briefing file
BRIEFING_FILE = "codex_takes_lead.md"
try:
    # Ensure the file path is correct
    briefing_path = Path(os.getcwd()) / BRIEFING_FILE
    with open(briefing_path, "r") as f:
        briefing_content = f.read()
except FileNotFoundError:
    print(f"Error: Briefing file '{BRIEFING_FILE}' not found.", file=sys.stderr)
    sys.exit(1)

# Extract the part that Codex is supposed to 'read' from the briefing
# The prompt is "Codex: Read 'codex_takes_lead.md' and act according to the instructions."
# We need to simulate the agent passing this content to the driver's chat method.
# For now, let's just pass the whole briefing directly.
full_prompt_for_codex = f"""I have read the content of '{BRIEFING_FILE}':
```
{briefing_content}
```

Now, act according to the instructions in the briefing, focusing on the architectural design for resilience."""


# --- Simulate CodexCLIDriver's chat method logic ---
binary_path = "codex" # Assume it's in PATH
api_key = os.environ.get("CODEX_API_KEY") 

# Read API key from file if not in env
if not api_key:
    try:
        key_path = os.path.expanduser("~/.ssh/codex.token")
        if os.path.exists(key_path):
            with open(key_path, "r") as f:
                api_key = f.read().strip()
    except Exception:
        pass

env = os.environ.copy()
if api_key:
    env["CODEX_API_KEY"] = api_key # Some CLIs use this


cmd = [
    binary_path,
    "exec", # Use the exec subcommand
    "--model", "gpt-4", # Default to a capable model, can be overridden via config
    "--ask-for-approval", "never", # Avoid interactive prompts
    "--sandbox", "danger-full-access", # For a coding agent, full access is needed (caution)
    full_prompt_for_codex # The actual prompt/content
]

print(f"--- SIMULATING CODEX EXECUTION ---\n", file=sys.stderr)
print(f"Binary: {binary_path}", file=sys.stderr)
print(f"Command: {' '.join(cmd)}", file=sys.stderr)
print(f"Prompt Length: {len(full_prompt_for_codex)} characters", file=sys.stderr)
print(f"API Key present: {bool(api_key)}", file=sys.stderr)
print(f"----------------------------------\n", file=sys.stderr)

try:
    process = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        check=False
    )
    
    if process.returncode != 0:
        print(f"Codex exited with error (Code: {process.returncode}):", file=sys.stderr)
        print(f"STDERR:\n{process.stderr.strip()}", file=sys.stderr)
        print(f"STDOUT:\n{process.stdout.strip()}", file=sys.stdout) # Print stdout even on error to debug
    else:
        print(f"Codex executed successfully. Output:\n{process.stdout.strip()}", file=sys.stdout)

except FileNotFoundError:
    print(f"Error: Codex binary '{binary_path}' not found. Is it in your PATH?", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Unhandled exception during Codex execution: {e}", file=sys.stderr)
    sys.exit(1)
