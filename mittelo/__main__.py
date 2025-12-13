from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
import subprocess
import signal

from .agent import run_agent
from .client import JsonlClient
from .hub import run_hub


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="mittelo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    hub = sub.add_parser("hub", help="Run hub (task queue) server")
    hub.add_argument("--db", default="mittelo.db")
    hub.add_argument("--host", default="127.0.0.1")
    hub.add_argument("--port", type=int, default=8765)
    hub.add_argument("--lease-seconds", type=int, default=60)
    hub.add_argument("--print-url", action="store_true")

    enqueue = sub.add_parser("enqueue", help="Enqueue a task prompt")
    enqueue.add_argument("--host", default=os.environ.get("MITTELO_HOST", "127.0.0.1"))
    enqueue.add_argument("--port", type=int, default=int(os.environ.get("MITTELO_PORT", "8765")))
    enqueue.add_argument("--prompt", help="Prompt string to enqueue")
    enqueue.add_argument("--file", type=Path, help="Read prompt from file")
    enqueue.add_argument("--jsonl", type=Path, help="Read JSONL tasks with {prompt} per line")

    status = sub.add_parser("status", help="List tasks")
    status.add_argument("--host", default=os.environ.get("MITTELO_HOST", "127.0.0.1"))
    status.add_argument("--port", type=int, default=int(os.environ.get("MITTELO_PORT", "8765")))
    status.add_argument("--status", default=None, help="Filter status (queued/leased/done/failed)")
    status.add_argument("--limit", type=int, default=50)

    agent = sub.add_parser("agent", help="Run an agent that leases and executes tasks")
    agent.add_argument("--host", default=os.environ.get("MITTELO_HOST", "127.0.0.1"))
    agent.add_argument("--port", type=int, default=int(os.environ.get("MITTELO_PORT", "8765")))
    agent.add_argument("--backend", default="echo", help="Backend name (echo/shell/kiro/gemini/codex/ollama)")
    agent.add_argument("--shell-cmd", default=None, help="If backend=shell, command to run")
    agent.add_argument("--worker-id", default=None)
    agent.add_argument("--max-tasks", type=int, default=1)
    agent.add_argument("--lease-seconds", type=int, default=60)
    agent.add_argument("--once", action="store_true")

    swarm = sub.add_parser("swarm", help="Spawn multiple agents (a small local swarm)")
    swarm.add_argument("--host", default=os.environ.get("MITTELO_HOST", "127.0.0.1"))
    swarm.add_argument("--port", type=int, default=int(os.environ.get("MITTELO_PORT", "8765")))
    swarm.add_argument(
        "--agent",
        action="append",
        default=[],
        help="backend=count (repeatable), example: --agent echo=2 --agent kiro=1",
    )
    swarm.add_argument("--lease-seconds", type=int, default=60)

    shutdown = sub.add_parser("shutdown", help="Shutdown the hub")
    shutdown.add_argument("--host", default=os.environ.get("MITTELO_HOST", "127.0.0.1"))
    shutdown.add_argument("--port", type=int, default=int(os.environ.get("MITTELO_PORT", "8765")))

    return parser.parse_args(argv)


def _cmd_hub(args: argparse.Namespace) -> int:
    return run_hub(
        db_path=args.db,
        host=args.host,
        port=args.port,
        lease_seconds=args.lease_seconds,
        print_url=args.print_url,
    )


def _cmd_enqueue(args: argparse.Namespace) -> int:
    prompts: list[str] = []
    if args.prompt:
        prompts.append(args.prompt)
    if args.file:
        prompts.append(args.file.read_text(encoding="utf-8"))
    if args.jsonl:
        for line in args.jsonl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            prompts.append(str(obj["prompt"]))
    if not prompts:
        raise SystemExit("Provide --prompt, --file, or --jsonl")

    with JsonlClient(args.host, args.port) as c:
        for p in prompts:
            res = c.call("enqueue", {"prompt": p})
            task_id = res["task_id"]
            print(task_id)
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    with JsonlClient(args.host, args.port) as c:
        res = c.call("list", {"status": args.status, "limit": args.limit})
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


def _cmd_agent(args: argparse.Namespace) -> int:
    return run_agent(
        host=args.host,
        port=args.port,
        backend=args.backend,
        shell_cmd=args.shell_cmd,
        worker_id=args.worker_id,
        max_tasks=args.max_tasks,
        lease_seconds=args.lease_seconds,
        once=args.once,
    )


def _cmd_shutdown(args: argparse.Namespace) -> int:
    with JsonlClient(args.host, args.port) as c:
        c.call("shutdown", {})
    return 0


def _cmd_swarm(args: argparse.Namespace) -> int:
    specs: list[tuple[str, int]] = []
    for spec in args.agent:
        if "=" not in spec:
            raise SystemExit("Use --agent backend=count")
        backend, count_s = spec.split("=", 1)
        specs.append((backend.strip(), int(count_s)))
    if not specs:
        raise SystemExit("Provide at least one --agent backend=count")

    procs: list[subprocess.Popen] = []
    try:
        for backend, count in specs:
            for _ in range(count):
                procs.append(
                    subprocess.Popen(
                        [
                            sys.executable,
                            "-m",
                            "mittelo",
                            "agent",
                            "--host",
                            args.host,
                            "--port",
                            str(args.port),
                            "--backend",
                            backend,
                            "--lease-seconds",
                            str(args.lease_seconds),
                        ]
                    )
                )
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for p in procs:
            try:
                p.send_signal(signal.SIGINT)
            except Exception:
                pass
        for p in procs:
            try:
                p.terminate()
            except Exception:
                pass
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    if args.cmd == "hub":
        return _cmd_hub(args)
    if args.cmd == "enqueue":
        return _cmd_enqueue(args)
    if args.cmd == "status":
        return _cmd_status(args)
    if args.cmd == "agent":
        return _cmd_agent(args)
    if args.cmd == "swarm":
        return _cmd_swarm(args)
    if args.cmd == "shutdown":
        return _cmd_shutdown(args)
    raise SystemExit(f"Unknown cmd: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
