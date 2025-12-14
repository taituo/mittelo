#!/usr/bin/env python3
import subprocess
import json
import os
import sys
from typing import List, Dict, Any
from datetime import datetime

def run_command(command: List[str]) -> str:
    """Run a shell command and return its stdout."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""
    except FileNotFoundError:
        return ""

def get_tmux_sessions() -> List[Dict[str, str]]:
    """Get a list of active tmux sessions."""
    output = run_command(["tmux", "list-sessions", "-F", "#{session_name}:#{session_windows}:#{session_created}"])
    sessions = []
    if output:
        for line in output.split('\n'):
            parts = line.split(':')
            if len(parts) >= 3:
                name = parts[0]
                windows = parts[1]
                created_ts = parts[2]
                try:
                    created = datetime.fromtimestamp(int(created_ts)).strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    created = "Unknown"
                
                sessions.append({
                    "name": name,
                    "windows": windows,
                    "created": created
                })
    return sessions

def get_mittelo_processes() -> List[Dict[str, str]]:
    """Get a list of running python processes related to mittelo."""
    # This is a basic grep. In a real scenario, we might want to be more specific.
    output = run_command(["pgrep", "-fl", "python3.*mittelo"])
    processes = []
    if output:
        for line in output.split('\n'):
            parts = line.split(' ', 1)
            if len(parts) == 2:
                pid = parts[0]
                cmd = parts[1]
                processes.append({
                    "pid": pid,
                    "command": cmd
                })
    return processes

def main():
    print("--- Mittelö Development Monitor ---")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 30)

    print("\n[Tmux Sessions]")
    sessions = get_tmux_sessions()
    if sessions:
        for s in sessions:
            print(f"  * {s['name']} (Windows: {s['windows']}, Created: {s['created']})")
    else:
        print("  No active tmux sessions found.")

    print("\n[Mittelö Processes]")
    procs = get_mittelo_processes()
    if procs:
        for p in procs:
            print(f"  * PID {p['pid']}: {p['command']}")
    else:
        print("  No active Mittelö processes found.")
    
    print("-" * 30)

if __name__ == "__main__":
    main()
