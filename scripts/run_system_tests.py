#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from wrapper.backends import resolve_backend_argv  # noqa: E402


def _run_backend(backend: str, prompt: str) -> dict[str, object]:
    argv = resolve_backend_argv(backend)
    if not argv:
        return {"backend": backend, "ok": False, "error": f"backend not found: backends/{backend}/run"}

    # Redirect external CLI home/config into the run artifact folder (best-effort).
    # This avoids failures in sandboxed environments where writing to the real HOME is blocked.
    env = os.environ.copy()
    # Caller sets MITTELO_SUBPROCESS_HOME via env before invoking, but keep a default.
    env.setdefault("MITTELO_SUBPROCESS_HOME", str(Path.cwd() / ".mittelo_home" / backend))

    start = time.time()
    p = subprocess.run(
        argv,
        input=prompt,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    dur_ms = int((time.time() - start) * 1000)
    ok = p.returncode == 0
    return {
        "backend": backend,
        "ok": ok,
        "rc": p.returncode,
        "latency_ms": dur_ms,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True, help="backend name under backends/<name>/run")
    ap.add_argument("--prompt", required=True, help="prompt to send to the backend")
    ap.add_argument("--out-dir", default=None, help="output directory (default: reports/e2e/<timestamp>_<backend>)")
    args = ap.parse_args(argv)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out_dir) if args.out_dir else Path("reports") / "e2e" / f"{ts}_{args.backend}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Per-run home for external CLIs (prevents writing to real ~/.config in sandboxes)
    os.environ["MITTELO_SUBPROCESS_HOME"] = str(out_dir / "home")

    run = {
        "backend": args.backend,
        "timestamp": ts,
        "cwd": str(Path.cwd()),
        "env": {
            k: os.environ.get(k)
            for k in [
                "MITTELO_GEMINI_MODEL",
                "MITTELO_CLAUDE_MODEL",
                "MITTELO_KIRO_MODEL",
                "MITTELO_CODEX_MODEL",
                "MITTELO_KIMI_MODEL",
                "MITTELO_KIRO_TRUST_ALL_TOOLS",
            ]
        },
    }
    (out_dir / "run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")

    res = _run_backend(args.backend, args.prompt)
    (out_dir / "result.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = [
        f"# System run ({args.backend})",
        "",
        f"- ok: {res.get('ok')}",
        f"- rc: {res.get('rc')}",
        f"- latency_ms: {res.get('latency_ms')}",
        "",
        "## stderr (first 4000 chars)",
        "```",
        (res.get("stderr") or "")[:4000],
        "```",
        "",
        "## stdout (first 4000 chars)",
        "```",
        (res.get("stdout") or "")[:4000],
        "```",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary), encoding="utf-8")

    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
