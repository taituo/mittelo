from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from wrapper.client import JsonlClient


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        db_path = os.path.join(td, "mittelo.db")
        hub = subprocess.Popen(
            [sys.executable, "-m", "mittelo", "hub", "--db", db_path, "--host", "127.0.0.1", "--port", "0", "--print-url"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            line = hub.stdout.readline().strip()  # type: ignore[union-attr]
            if not line.startswith("MITTELO_HUB tcp://"):
                raise RuntimeError(f"Unexpected hub output: {line}")
            hostport = line.split("tcp://", 1)[1]
            host, port_s = hostport.rsplit(":", 1)
            port = int(port_s)

            agent = subprocess.Popen(
                [sys.executable, "-m", "mittelo", "agent", "--host", host, "--port", str(port), "--backend", "echo", "--once"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            try:
                with JsonlClient(host, port) as c:
                    tid = c.call("enqueue", {"prompt": "ping"})["task_id"]
                agent.wait(timeout=10)

                deadline = time.time() + 5
                while time.time() < deadline:
                    with JsonlClient(host, port) as c:
                        tasks = c.call("list", {"limit": 20})["tasks"]
                    done = [t for t in tasks if int(t["task_id"]) == tid and t["status"] == "done"]
                    if done:
                        assert done[0]["result"] == "echo:ping"
                        break
                    time.sleep(0.1)
                else:
                    raise RuntimeError("Task did not finish")
            finally:
                agent.kill()

            with JsonlClient(host, port) as c:
                c.call("shutdown", {})
        finally:
            hub.kill()

    print(json.dumps({"ok": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
