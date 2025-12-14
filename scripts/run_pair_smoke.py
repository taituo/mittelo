from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import socket
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from wrapper.client import JsonlClient  # noqa: E402

REPORTS_DIR = Path("reports/swarm")


def _json_write(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def _text_write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def can_bind_localhost() -> bool:
    """Check if we can bind to localhost (some environments block this)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return True
    except OSError:
        return False


def _try_doctor_json() -> dict[str, Any]:
    try:
        p = subprocess.run(
            [sys.executable, str(project_root / "scripts" / "doctor.py"), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        if p.returncode != 0:
            return {"ok": False, "rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
        return json.loads(p.stdout or "{}")
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _try_git_sha() -> str | None:
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
        if p.returncode != 0:
            return None
        return (p.stdout or "").strip() or None
    except Exception:
        return None


@dataclass(frozen=True)
class PairSmokeArgs:
    backend_a: str
    backend_b: str
    tasks: int
    timeout_s: float
    lease_seconds: int
    db: str


def run_pair_smoke(args: PairSmokeArgs) -> int:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = REPORTS_DIR / f"{run_id}_{args.backend_a}_{args.backend_b}"
    run_dir.mkdir(parents=True, exist_ok=True)

    run_meta: dict[str, Any] = {
        "run_id": run_id,
        "cwd": str(Path.cwd()),
        "git_sha": _try_git_sha(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "args": {
            "backend_a": args.backend_a,
            "backend_b": args.backend_b,
            "tasks": args.tasks,
            "timeout_s": args.timeout_s,
            "lease_seconds": args.lease_seconds,
            "db": args.db,
        },
        "doctor": _try_doctor_json(),
        "env_model_vars": {k: os.environ.get(k) for k in ["MITTELO_GEMINI_MODEL", "MITTELO_CLAUDE_MODEL", "MITTELO_KIRO_MODEL", "MITTELO_CODEX_MODEL", "MITTELO_KIMI_MODEL"]},
    }
    _json_write(run_dir / "run.json", run_meta)

    if not can_bind_localhost():
        _json_write(run_dir / "result.json", {"ok": True, "skipped": True, "reason": "cannot bind localhost"})
        _text_write(
            run_dir / "summary.md",
            f"# Pair Smoke Summary\n\n- run_id: {run_id}\n- status: SKIPPED\n- reason: cannot bind localhost\n",
        )
        return 0

    agents: list[subprocess.Popen] = []
    hub: subprocess.Popen | None = None
    host = "127.0.0.1"
    port: int | None = None
    tasks_out: list[dict[str, Any]] = []
    ok = False
    error: str | None = None

    try:
        hub = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "mittelo",
                "hub",
                "--db",
                args.db,
                "--host",
                host,
                "--port",
                "0",
                "--lease-seconds",
                str(args.lease_seconds),
                "--print-url",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        hub_url = None
        start_time = time.time()
        while time.time() - start_time < 5:
            line = hub.stdout.readline() if hub.stdout is not None else ""
            if not line:
                break
            if line.startswith("MITTELO_HUB tcp://"):
                hub_url = line.strip().split()[-1]
                break
        if not hub_url:
            error = "hub did not print MITTELO_HUB url"
            return 1

        hostport = hub_url.split("tcp://", 1)[1]
        host, port_s = hostport.rsplit(":", 1)
        port = int(port_s)

        agents.append(
            subprocess.Popen(
                [sys.executable, "-m", "mittelo", "agent", "--host", host, "--port", str(port), "--backend", args.backend_a],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        )
        agents.append(
            subprocess.Popen(
                [sys.executable, "-m", "mittelo", "agent", "--host", host, "--port", str(port), "--backend", args.backend_b],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

        task_ids: list[int] = []
        with JsonlClient(host, port) as c:
            for i in range(args.tasks):
                prompt = f"pair_smoke {i}"
                task_ids.append(int(c.call("enqueue", {"prompt": prompt})["task_id"]))

        deadline = time.time() + args.timeout_s
        while time.time() < deadline:
            with JsonlClient(host, port) as c:
                listed = c.call("list", {"limit": 0})
            tasks_out = list(listed.get("tasks") or [])
            done_or_failed = [t for t in tasks_out if t.get("status") in ("done", "failed")]
            if task_ids and len(done_or_failed) >= len(task_ids):
                ok = True
                break
            time.sleep(0.25)
        if not ok and error is None:
            error = f"timeout after {args.timeout_s}s"
        return 0 if ok else 1
    except Exception as e:
        error = str(e)
        return 1
    finally:
        result = {
            "ok": ok,
            "error": error,
            "tasks": tasks_out,
        }
        _json_write(run_dir / "result.json", result)

        status = "SUCCESS" if ok else "FAILURE"
        _text_write(
            run_dir / "summary.md",
            f"# Pair Smoke Summary\n\n- run_id: {run_id}\n- status: {status}\n- error: {error}\n- tasks_seen: {len(tasks_out)}\n",
        )

        if port is not None:
            try:
                with JsonlClient(host, port) as c:
                    c.call("shutdown", {})
            except Exception:
                pass

        for p in agents:
            try:
                p.terminate()
            except Exception:
                pass
        if hub is not None:
            try:
                hub.terminate()
            except Exception:
                pass

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend-a", default="echo")
    ap.add_argument("--backend-b", default="echo")
    ap.add_argument("--tasks", type=int, default=6)
    ap.add_argument("--timeout-s", type=float, default=15.0)
    ap.add_argument("--lease-seconds", type=int, default=5)
    ap.add_argument("--db", default=":memory:")
    ns = ap.parse_args()
    sys.exit(
        run_pair_smoke(
            PairSmokeArgs(
                backend_a=str(ns.backend_a),
                backend_b=str(ns.backend_b),
                tasks=int(ns.tasks),
                timeout_s=float(ns.timeout_s),
                lease_seconds=int(ns.lease_seconds),
                db=str(ns.db),
            )
        )
    )
