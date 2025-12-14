from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .backends import resolve_backend_argv


PreflightStatus = Literal["ok", "warn", "fail"]


@dataclass(frozen=True)
class PreflightResult:
    backend: str
    problems: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def status(self) -> PreflightStatus:
        if self.problems:
            return "fail"
        if self.warnings:
            return "warn"
        return "ok"

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def _which_any(*bins: str) -> str | None:
    for b in bins:
        p = shutil.which(b)
        if p:
            return p
    return None


def _home_candidates() -> list[Path]:
    candidates: list[Path] = []
    sp_home = os.environ.get("MITTELO_SUBPROCESS_HOME")
    if sp_home:
        # When we intentionally sandbox subprocess HOME, treat it as authoritative.
        # This makes preflight checks match the environment the external CLI will see.
        return [Path(sp_home)]
    home = os.environ.get("HOME")
    if home:
        candidates.append(Path(home))
    return candidates


def preflight_backend(backend: str) -> PreflightResult:
    backend = backend.strip().lower()
    problems: list[str] = []
    warnings: list[str] = []

    if backend in {"echo", "shell"}:
        return PreflightResult(backend=backend)

    if resolve_backend_argv(backend) is None:
        problems.append(f"backend '{backend}' not found (expected backends/{backend}/run or MITTELO_BACKENDS_DIR).")
        return PreflightResult(backend=backend, problems=tuple(problems), warnings=tuple(warnings))

    if backend == "opencode":
        problems.append("backend 'opencode' is a placeholder (backends/opencode/run exits with 'not configured').")
        return PreflightResult(backend=backend, problems=tuple(problems), warnings=tuple(warnings))

    # External CLIs (best-effort checks)
    if backend == "gemini":
        if not _which_any("gemini", "npx"):
            problems.append("Gemini CLI not found (need `gemini` or `npx`).")

        has_auth = bool(os.environ.get("GEMINI_API_KEY"))
        has_settings = any((h / ".gemini" / "settings.json").exists() for h in _home_candidates())
        if not (has_auth or has_settings):
            warnings.append("Gemini auth not detected (set GEMINI_API_KEY or configure ~/.gemini/settings.json).")

    elif backend in {"claude_code", "glm"}:
        if not _which_any("claude"):
            problems.append("Claude CLI not found (need `claude`).")
        warnings.append("Claude may require login (`claude` can say 'Please run /login').")

    elif backend == "codex":
        if not _which_any("codex"):
            problems.append("Codex CLI not found (need `codex`).")
        if not os.environ.get("OPENAI_API_KEY"):
            warnings.append("OPENAI_API_KEY is not set (Codex may still work if already authenticated).")

    elif backend == "kiro":
        if not _which_any("kiro-cli"):
            problems.append("Kiro CLI not found (need `kiro-cli`).")
        warnings.append("Kiro may require device-flow login (`kiro-cli login --use-device-flow`).")

    elif backend == "kimi":
        if not _which_any("kimi"):
            problems.append("Kimi CLI not found (need `kimi`).")
        has_key = bool(os.environ.get("KIMI_API_KEY"))
        token_found = any((h / ".ssh" / "kimi.token").exists() for h in _home_candidates())
        if not has_key and not token_found:
            warnings.append("KIMI_API_KEY not set and ~/.ssh/kimi.token not found (Kimi may fail to run).")

    elif backend == "tmux":
        if not _which_any("tmux"):
            problems.append("tmux not found (need `tmux`).")
        if not os.environ.get("MITTELO_TMUX_SESSION"):
            warnings.append("MITTELO_TMUX_SESSION not set (defaults to 'mittelo_default').")

    elif backend == "mlx":
        # MLX driver checks python env for mlx_lm at runtime; keep this as a warning unless strict mode is used.
        warnings.append("MLX requires `mlx-lm` installed in the same Python env as the agent.")

    return PreflightResult(backend=backend, problems=tuple(problems), warnings=tuple(warnings))
