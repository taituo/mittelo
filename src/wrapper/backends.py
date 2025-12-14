from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class Backend:
    name: str
    kind: str
    argv: list[str] | None = None


def run_backend(backend: Backend, prompt: str, env: dict[str, str]) -> str:
    if backend.kind == "echo":
        return f"echo:{prompt}"

    if backend.kind == "shell":
        if not backend.argv:
            raise ValueError("shell backend requires argv")
        proc = subprocess.run(
            backend.argv,
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, **env},
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode("utf-8", errors="replace").strip() or "backend failed")
        return proc.stdout.decode("utf-8", errors="replace").strip()

    raise ValueError(f"Unknown backend kind: {backend.kind}")


def resolve_backend_argv(name: str) -> list[str] | None:
    backends_dir = os.environ.get("MITTELO_BACKENDS_DIR")
    candidates: list[Path] = []
    if backends_dir:
        candidates.append(Path(backends_dir))
    candidates.append(Path.cwd() / "backends")
    candidates.append(Path(__file__).resolve().parents[1] / "backends")

    for base in candidates:
        run_path = base / name / "run"
        if run_path.is_file():
            if run_path.suffix == ".py":
                return [sys.executable, str(run_path)]
            if os.access(run_path, os.X_OK):
                return [str(run_path)]
            return ["bash", str(run_path)]
    return None
