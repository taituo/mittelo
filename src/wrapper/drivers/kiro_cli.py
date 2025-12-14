from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import AsyncGenerator, List

from .abstract import AbstractDriver
from .subprocess_env import build_env


class KiroCLIDriver(AbstractDriver):
    def __init__(self, binary_path: str = "/Users/tiny/.local/bin/kiro-cli"):
        self.binary_path = binary_path
        self.model = os.environ.get("MITTELO_KIRO_MODEL")
        self.trust_all_tools = os.environ.get("MITTELO_KIRO_TRUST_ALL_TOOLS") == "1"

    async def start(self) -> None:
        try:
            subprocess.run([self.binary_path, "--version"], capture_output=True, text=True, check=False, env=build_env())
        except FileNotFoundError:
            raise RuntimeError(f"Binary '{self.binary_path}' not found.")

    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        cmd = [self.binary_path, "chat", "--no-interactive", "--wrap", "never"]
        if self.model:
            cmd.extend(["--model", self.model])

        work_dir = os.environ.get("MITTELO_SUBPROCESS_WORKDIR")
        if not work_dir and self.trust_all_tools:
            # When tools are auto-approved, prevent accidental writes to the repo root by default.
            work_dir = str(Path.cwd() / ".mittelo" / "work" / "kiro")
        if work_dir:
            Path(work_dir).mkdir(parents=True, exist_ok=True)
            cmd.extend(["--work-dir", work_dir])

        if self.trust_all_tools:
            cmd.append("--trust-all-tools")
        else:
            # Per `kiro-cli chat --help`: trust no tools via an empty value.
            cmd.append("--trust-tools=")

        cmd.append(content)

        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            env=build_env(),
            cwd=work_dir,
        )
        if process.returncode != 0:
            msg = (process.stderr or process.stdout or "").strip()
            raise RuntimeError(msg or "kiro-cli failed")
        yield process.stdout or ""

    async def stop(self) -> None:
        pass
