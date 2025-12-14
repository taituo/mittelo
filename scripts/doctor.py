#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")


@dataclass(frozen=True)
class Check:
    name: str
    argv: list[str]
    help_argv: list[str] | None = None
    required_substrings: list[str] | None = None


def _run(argv: list[str]) -> tuple[int, str]:
    try:
        p = subprocess.run(argv, capture_output=True, text=True, check=False)
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode, out.strip()
    except FileNotFoundError:
        return 127, "not found"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--core", action="store_true", help="Only check core Python/tooling (CI-friendly).")
    args = ap.parse_args(argv)

    if args.core:
        checks = [
            Check("python", [sys.executable, "--version"]),
            Check("mittelo", [sys.executable, "-m", "mittelo", "--help"], required_substrings=["hub", "agent", "swarm"]),
            Check(
                "echo-backend",
                [sys.executable, "-m", "mittelo", "backend-check", "--backend", "echo"],
                required_substrings=["status: ok"],
            ),
        ]
    else:
        checks = [
            Check("codex", ["codex", "--version"], ["codex", "exec", "--help"], ["--full-auto", "--sandbox"]),
            Check("claude", ["claude", "--version"], ["claude", "--help"], ["--print"]),
            Check("kiro-cli", ["kiro-cli", "--version"], ["kiro-cli", "chat", "--help"], ["--no-interactive"]),
            Check("kimi", ["kimi", "--version"], ["kimi", "--help"], ["--print"]),
            Check("npx", ["npx", "--version"]),
        ]

    report: dict[str, object] = {"ok": True, "checks": []}
    for c in checks:
        ok = True
        which = shutil.which(c.argv[0]) if c.argv else None
        code, ver_out = _run(c.argv)
        item: dict[str, object] = {"name": c.name, "which": which, "version_rc": code, "version": ver_out}

        if c.help_argv is not None:
            hrc, hout = _run(c.help_argv)
            item["help_rc"] = hrc
            if c.required_substrings:
                missing = [s for s in c.required_substrings if s not in hout]
                item["missing_flags"] = missing
                if missing:
                    ok = False
        elif c.required_substrings:
            missing = [s for s in c.required_substrings if s not in ver_out]
            item["missing_flags"] = missing
            if missing:
                ok = False
        if code != 0:
            ok = False
        item["ok"] = ok
        if not ok:
            report["ok"] = False
        report["checks"].append(item)

    report["env_model_vars"] = [
        "MITTELO_GEMINI_MODEL",
        "MITTELO_CLAUDE_MODEL",
        "MITTELO_KIRO_MODEL",
        "MITTELO_CODEX_MODEL",
        "MITTELO_KIMI_MODEL",
        "MITTELO_KIRO_TRUST_ALL_TOOLS",
    ]

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("mittelo doctor")
        for item in report["checks"]:  # type: ignore[assignment]
            item = item  # type: ignore[no-redef]
            name = item["name"]
            ok_s = "OK" if item["ok"] else "FAIL"
            print(f"- {name}: {ok_s} ({item.get('which')})")
            if item.get("missing_flags"):
                print(f"  missing flags: {item['missing_flags']}")
        print("model env vars:", ", ".join(report["env_model_vars"]))  # type: ignore[arg-type]

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
