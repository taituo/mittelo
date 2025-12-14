#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from wrapper.backends import resolve_backend_argv, Backend, run_backend

def main():
    print("Verifying Tmux Backend Integration...")
    
    # 1. Test Resolution
    argv = resolve_backend_argv("tmux")
    if not argv:
        print("FAIL: Could not resolve 'tmux' backend.")
        sys.exit(1)
    print(f"PASS: Resolved 'tmux' backend to: {argv}")

    # 2. Test Execution
    # We need a dummy session
    session_name = "integration_test_session"
    os.environ["MITTELO_TMUX_SESSION"] = session_name
    
    # Create backend object
    backend = Backend(name="tmux", kind="shell", argv=argv)
    
    print(f"Running command in tmux session '{session_name}'...")
    try:
        output = run_backend(backend, "echo 'Integration Test Successful'", env={})
        print("--- Output Start ---")
        print(output)
        print("--- Output End ---")
        
        if "Integration Test Successful" in output:
            print("PASS: Output contained expected string.")
        else:
            print("FAIL: Output did not contain expected string.")
            
    except Exception as e:
        print(f"FAIL: Execution failed with error: {e}")
    finally:
        # Cleanup
        os.system(f"tmux kill-session -t {session_name} 2>/dev/null")

if __name__ == "__main__":
    main()
