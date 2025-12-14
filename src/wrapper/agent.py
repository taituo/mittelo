from __future__ import annotations

import os
import socket
import time
import uuid

from .backends import Backend, resolve_backend_argv, run_backend
from .client import JsonlClient


def _backend_from_name(name: str, shell_cmd: str | None) -> Backend:
    name = name.strip().lower()
    if name in {"echo"}:
        return Backend(name="echo", kind="echo")
    if name in {"shell"}:
        if not shell_cmd:
            raise RuntimeError("backend=shell requires --shell-cmd")
        return Backend(name="shell", kind="shell", argv=["bash", "-lc", shell_cmd])

    argv = resolve_backend_argv(name)
    if argv:
        return Backend(name=name, kind="shell", argv=argv)

    raise RuntimeError(f"Unknown backend '{name}'. Add backends/{name}/run or use --backend shell.")


def run_agent(
    host: str,
    port: int,
    backend: str,
    shell_cmd: str | None,
    worker_id: str | None,
    max_tasks: int,
    lease_seconds: int,
    once: bool,
) -> int:
    worker = worker_id or f"{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    backend_obj = _backend_from_name(backend, shell_cmd=shell_cmd)

    while True:
        did_any = False
        with JsonlClient(host, port) as c:
            res = c.call(
                "lease",
                {"worker_id": worker, "max_tasks": max_tasks, "lease_seconds": lease_seconds},
            )
            for t in res["tasks"]:
                did_any = True
                task_id = int(t["task_id"])
                prompt = str(t["prompt"])
                try:
                    out = run_backend(
                        backend_obj,
                        prompt,
                        env={"MITTELO_TASK_ID": str(task_id), "MITTELO_WORKER_ID": worker},
                    )
                    c.call("ack", {"task_id": task_id, "status": "done", "result": out, "error": None})
                except Exception as e:
                    c.call("ack", {"task_id": task_id, "status": "failed", "result": None, "error": str(e)})

        if once:
            return 0
        if not did_any:
            time.sleep(1.0)
