from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time

import pytest

from tests.conftest import can_bind_localhost


def test_hub_agent_echo_end_to_end() -> None:
    if not can_bind_localhost():
        pytest.skip("Environment cannot bind localhost sockets (skipping hub integration test).")

    with tempfile.TemporaryDirectory() as td:
        db_path = os.path.join(td, "mittelo.db")
        hub = subprocess.Popen(
            [sys.executable, "-m", "mittelo", "hub", "--db", db_path, "--host", "127.0.0.1", "--port", "8765"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            agent = subprocess.Popen(
                [sys.executable, "-m", "mittelo", "agent", "--host", "127.0.0.1", "--port", "8765", "--backend", "echo"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            try:
                time.sleep(0.5)
                tid = subprocess.check_output(
                    [
                        sys.executable,
                        "-m",
                        "mittelo",
                        "enqueue",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "8765",
                        "--prompt",
                        "ping",
                    ],
                    text=True,
                ).strip()

                deadline = time.time() + 5
                while time.time() < deadline:
                    out = subprocess.check_output(
                        [sys.executable, "-m", "mittelo", "status", "--host", "127.0.0.1", "--port", "8765", "--limit", "50"],
                        text=True,
                    )
                    if f"\"task_id\": {tid}" in out and "\"status\": \"done\"" in out:
                        return
                    time.sleep(0.2)
                raise AssertionError("Task did not finish")
            finally:
                agent.terminate()
        finally:
            hub.terminate()
