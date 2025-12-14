from __future__ import annotations

import os
import subprocess
from typing import AsyncGenerator, List

from .abstract import AbstractDriver
from .subprocess_env import build_env


class ClaudeCLIDriver(AbstractDriver):
    def __init__(self, binary_path: str = "claude"):
        self.binary_path = binary_path
        self.model = os.environ.get("MITTELO_CLAUDE_MODEL")

    async def start(self) -> None:
        try:
            subprocess.run([self.binary_path, "--version"], capture_output=True, text=True, check=False, env=build_env())
        except FileNotFoundError:
            raise RuntimeError(f"Binary '{self.binary_path}' not found.")

    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        cmd = [self.binary_path, content, "--print", "--tools", ""]

        model = os.environ.get("MITTELO_CLAUDE_MODEL")
        if model:
            cmd.extend(["--model", model])

        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            env=build_env(),
        )
        if process.returncode != 0:
            msg = (process.stderr or process.stdout or "").strip()
            raise RuntimeError(msg or "claude failed")
        yield process.stdout or ""

    async def stop(self) -> None:
        pass
