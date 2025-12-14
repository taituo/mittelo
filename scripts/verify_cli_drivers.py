#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

# Add src/ to import path when running from repo checkout.
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from wrapper.backends import resolve_backend_argv  # noqa: E402
from wrapper.prereqs import preflight_backend  # noqa: E402


@dataclass(frozen=True)
class BackendResult:
    backend: str
    status: str  # PASS/FAIL/SKIP
    reason: str | None = None
    rc: int | None = None
    stdout_head: str | None = None
    stderr_head: str | None = None


def _run_backend(argv: list[str], prompt: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        input=prompt,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def verify_backend(name: str, prompt: str, *, run_on_warn: bool, strict: bool) -> BackendResult:
    sandbox_home = str(Path("reports") / "verify_cli_drivers" / name / "home")
    Path(sandbox_home).mkdir(parents=True, exist_ok=True)
    old_sp_home = os.environ.get("MITTELO_SUBPROCESS_HOME")
    os.environ["MITTELO_SUBPROCESS_HOME"] = sandbox_home
    try:
        pf = preflight_backend(name)
    finally:
        if old_sp_home is None:
            os.environ.pop("MITTELO_SUBPROCESS_HOME", None)
        else:
            os.environ["MITTELO_SUBPROCESS_HOME"] = old_sp_home

    if pf.status == "fail":
        if strict:
            return BackendResult(backend=name, status="FAIL", reason="preflight:fail")
        return BackendResult(backend=name, status="SKIP", reason="preflight:fail")

    if pf.status == "warn" and not run_on_warn:
        if strict:
            return BackendResult(backend=name, status="FAIL", reason="preflight:warn")
        return BackendResult(backend=name, status="SKIP", reason="preflight:warn")

    argv = resolve_backend_argv(name)
    if not argv:
        return BackendResult(backend=name, status="FAIL", reason="backend not found")

    env = os.environ.copy()
    env["MITTELO_SUBPROCESS_HOME"] = sandbox_home

    p = _run_backend(argv, prompt, env=env)
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()

    if p.returncode != 0:
        reason = err or out or "non-zero exit"
        return BackendResult(
            backend=name,
            status="FAIL",
            reason=reason[:300],
            rc=p.returncode,
            stdout_head=out[:200],
            stderr_head=err[:200],
        )

    if err:
        return BackendResult(
            backend=name,
            status="FAIL",
            reason="stderr not empty",
            rc=p.returncode,
            stdout_head=out[:200],
            stderr_head=err[:200],
        )

    if not out:
        return BackendResult(backend=name, status="FAIL", reason="empty stdout", rc=p.returncode)

    if out.lower().startswith("error:"):
        return BackendResult(backend=name, status="FAIL", reason="error-like stdout", rc=p.returncode, stdout_head=out[:200])

    return BackendResult(backend=name, status="PASS", rc=p.returncode, stdout_head=out[:200])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify backend wrapper scripts (SKIP-aware).")
    ap.add_argument(
        "--backend",
        action="append",
        default=[],
        help="Backend name (repeatable). Default: common LLM backends.",
    )
    ap.add_argument("--prompt", default="echo hello")
    ap.add_argument("--run-on-warn", action="store_true", help="Run even if preflight returns warnings.")
    ap.add_argument("--strict", action="store_true", help="Treat WARN/FAIL preflight as FAIL (no SKIP).")
    ap.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = ap.parse_args(argv)

    backends = args.backend or ["gemini", "claude_code", "codex", "kiro", "kimi", "mlx"]

    results: list[BackendResult] = []
    ok = True
    for b in backends:
        r = verify_backend(b, args.prompt, run_on_warn=args.run_on_warn, strict=args.strict)
        results.append(r)
        if r.status == "FAIL":
            ok = False

    if args.json:
        print(
            json.dumps(
                {"ok": ok, "results": [r.__dict__ for r in results]},
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        for r in results:
            if r.status == "SKIP":
                print(f"- {r.backend}: SKIP ({r.reason})")
            elif r.status == "PASS":
                print(f"- {r.backend}: PASS")
            else:
                print(f"- {r.backend}: FAIL ({r.reason})")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
