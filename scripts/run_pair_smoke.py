import asyncio
import json
import os
import subprocess
import time
import sys
import socket
from pathlib import Path
from typing import List

# Ensure we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.wrapper.client import JsonlClient

REPORTS_DIR = Path("reports/swarm")

def can_bind_localhost() -> bool:
    """Check if we can bind to localhost (some environments block this)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return True
    except OSError:
        return False

def run_pair_smoke():
    run_id = time.strftime("%Y%m%d_%H%M%S")
    run_dir = REPORTS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting pair smoke test: {run_id}")

    if not can_bind_localhost():
        print("SKIP: Cannot bind to localhost. Writing skip artifact.")
        with open(run_dir / "summary.md", "w") as f:
            f.write(f"# Pair Smoke Summary\n\nRun ID: {run_id}\n\nStatus: SKIPPED (EPERM)\n")
        return 0
    
    agents: List[subprocess.Popen] = []
    hub_process = None

    try:
        # 1. Start Hub
        hub_process = subprocess.Popen(
            [sys.executable, "-m", "mittelo", "hub", "--db", ":memory:", "--port", "0", "--print-url"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Redirect stderr to stdout to capture everything
            text=True
        )
        
        hub_url = None
        # Wait for hub to print URL
        start_time = time.time()
        while time.time() - start_time < 5:
            line = hub_process.stdout.readline()
            if not line:
                break
            # print(f"[HUB] {line.strip()}") # Debug output
            if "MITTELO_HUB" in line:
                hub_url = line.strip().split()[-1]
                break
            
        if not hub_url:
            print("Failed to start hub (no URL printed)")
            return 1
            
        print(f"Hub started at {hub_url}")
        host = hub_url.split("://")[1].split(":")[0]
        port = int(hub_url.split(":")[-1])
        
        # 2. Start Agents (Echo Backend)
        for i in range(2):
            # Pass host/port directly as arguments
            p = subprocess.Popen(
                [
                    sys.executable, "-m", "mittelo", "agent", 
                    "--backend", "echo",
                    "--host", host,
                    "--port", str(port)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            agents.append(p)
            print(f"Started agent {i+1}")
            
        # 3. Enqueue Tasks
        client = JsonlClient(host, port)
        task_ids = []
        with client:
            for i in range(5):
                resp = client.call("enqueue", {"prompt": f"task {i}"})
                # Client returns the result dict directly
                task_ids.append(resp["task_id"])

        print(f"Enqueued {len(task_ids)} tasks")
        
        # 4. Wait for completion
        start_wait = time.time()
        completed = 0
        results = []
        
        while time.time() - start_wait < 10:
            with client:
                resp = client.call("list", {"limit": 100})
                tasks = resp.get("tasks", [])
                    
                done = [t for t in tasks if t["status"] in ("done", "failed")]
                completed = len(done)
                if completed >= len(task_ids) and len(task_ids) > 0:
                    results = done
                    break
            time.sleep(0.5)
            
        print(f"Completed {completed}/{len(task_ids)} tasks")
        
        # 5. Write Artifacts
        with open(run_dir / "run.json", "w") as f:
            json.dump({"run_id": run_id, "tasks": len(task_ids), "completed": completed}, f, indent=2)
            
        with open(run_dir / "result.json", "w") as f:
            json.dump(results, f, indent=2)
            
        with open(run_dir / "summary.md", "w") as f:
            status = "SUCCESS" if completed == len(task_ids) else "FAILURE"
            f.write(f"# Pair Smoke Summary\n\nRun ID: {run_id}\n\nStatus: {status}\n\nCompleted: {completed}/{len(task_ids)}\n")
            
        return 0 if completed == len(task_ids) else 1
        
    finally:
        # Cleanup
        if hub_process:
            hub_process.terminate()
        for p in agents:
            p.terminate()

if __name__ == "__main__":
    try:
        sys.exit(run_pair_smoke())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
