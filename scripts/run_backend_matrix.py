#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")


@dataclass(frozen=True)
class Preflight:
    status: str
    problems: list[str]
    warnings: list[str]


def _python() -> str:
    return sys.executable


def _list_backends(backends_dir: Path) -> list[str]:
    names: list[str] = []
    for p in sorted(backends_dir.iterdir(), key=lambda x: x.name):
        if not p.is_dir():
            continue
        if p.name in {"_template", "archive"}:
            continue
        if not (p / "run").exists():
            continue
        names.append(p.name)
    return names


def _run(argv: list[str], *, input_s: str | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        input=input_s,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _preflight(backend: str, env: dict[str, str]) -> Preflight:
    p = _run([_python(), "-m", "mittelo", "backend-check", "--backend", backend, "--json"], env=env)
    if p.returncode not in {0, 1}:
        raise RuntimeError((p.stderr or p.stdout or "").strip() or f"backend-check failed rc={p.returncode}")
    try:
        obj = json.loads((p.stdout or "").strip() or "{}")
    except json.JSONDecodeError:
        raise RuntimeError((p.stderr or "").strip() or "backend-check returned invalid JSON")
    return Preflight(
        status=str(obj.get("status") or "fail"),
        problems=list(obj.get("problems") or []),
        warnings=list(obj.get("warnings") or []),
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", default="Return exactly: mittelo smoke ok")
    ap.add_argument("--out-dir", default=None, help="Default: reports/e2e/<timestamp>_matrix")
    ap.add_argument("--run-on-warn", action="store_true", help="Also run system tests when preflight status=warn")
    ap.add_argument("--include", action="append", default=[], help="Only run these backends (repeatable)")
    ap.add_argument("--exclude", action="append", default=[], help="Skip these backends (repeatable)")
    args = ap.parse_args(argv)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out_dir) if args.out_dir else Path("reports") / "e2e" / f"{ts}_matrix"
    out_dir.mkdir(parents=True, exist_ok=True)

    backends_dir = Path("backends")
    if not backends_dir.exists():
        raise SystemExit("Missing ./backends directory (run from repo root).")

    selected = set(args.include) if args.include else None
    excluded = set(args.exclude)

    matrix: dict[str, object] = {
        "timestamp": ts,
        "cwd": str(Path.cwd()),
        "prompt": args.prompt,
        "run_on_warn": bool(args.run_on_warn),
        "backends": [],
    }

    overall_ok = True
    for name in _list_backends(backends_dir):
        if selected is not None and name not in selected:
            continue
        if name in excluded:
            continue

        item: dict[str, object] = {"backend": name}
        start = time.time()
        backend_out = out_dir / name
        backend_out.mkdir(parents=True, exist_ok=True)

        env = os.environ.copy()
        env["MITTELO_SUBPROCESS_HOME"] = str(backend_out / "home")
        Path(env["MITTELO_SUBPROCESS_HOME"]).mkdir(parents=True, exist_ok=True)
        try:
            pf = _preflight(name, env=env)
            item["preflight"] = {"status": pf.status, "problems": pf.problems, "warnings": pf.warnings}
        except Exception as e:
            item["preflight"] = {"status": "fail", "problems": [str(e)], "warnings": []}
            item["result"] = {"status": "SKIP", "reason": "preflight error"}
            matrix["backends"].append(item)
            overall_ok = False
            continue

        run_allowed = pf.status == "ok" or (args.run_on_warn and pf.status == "warn")
        if not run_allowed:
            item["result"] = {"status": "SKIP", "reason": f"preflight:{pf.status}"}
            matrix["backends"].append(item)
            continue

        p = _run(
            [
                _python(),
                "scripts/run_system_tests.py",
                "--backend",
                name,
                "--prompt",
                args.prompt,
                "--out-dir",
                str(backend_out),
            ],
            env=env,
        )
        item["system_test"] = {
            "rc": p.returncode,
            "out_dir": str(backend_out),
        }
        if p.returncode == 0:
            item["result"] = {"status": "PASS"}
        else:
            item["result"] = {"status": "FAIL"}
            overall_ok = False

        item["elapsed_ms"] = int((time.time() - start) * 1000)
        matrix["backends"].append(item)

    (out_dir / "matrix.json").write_text(json.dumps(matrix, indent=2, ensure_ascii=False), encoding="utf-8")

    lines: list[str] = [f"# Backend matrix ({ts})", "", f"- prompt: `{args.prompt}`", ""]
    for b in matrix["backends"]:  # type: ignore[assignment]
        b = b  # type: ignore[no-redef]
        name = b["backend"]
        result = (b.get("result") or {}).get("status")  # type: ignore[union-attr]
        pf = b.get("preflight") or {}
        pf_status = pf.get("status")
        reason = (b.get("result") or {}).get("reason")  # type: ignore[union-attr]
        msg = f"- {name}: {result} (preflight={pf_status}"
        if reason:
            msg += f", reason={reason}"
        msg += ")"
        lines.append(msg)
    lines.append("")
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
