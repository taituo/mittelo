from __future__ import annotations

import os
import shutil
import subprocess
from typing import AsyncGenerator, List

from .abstract import AbstractDriver
from .subprocess_env import build_env


class GeminiCLIDriver(AbstractDriver):
    def __init__(self, binary_path: str = "gemini"):
        self.binary_path = binary_path
        self.model = os.environ.get("MITTELO_GEMINI_MODEL")

    async def start(self) -> None:
        # Accept either a native `gemini` binary or an `npx` fallback.
        if shutil.which(self.binary_path):
            subprocess.run([self.binary_path, "--version"], capture_output=True, text=True, check=False, env=build_env())
            return
        if not shutil.which("npx"):
            raise RuntimeError("Neither 'gemini' nor 'npx' is available for Gemini CLI.")

    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        cmd = [self.binary_path, content]

        model = os.environ.get("MITTELO_GEMINI_MODEL")
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
            raise RuntimeError(msg or "gemini failed")
        yield process.stdout or ""

    async def stop(self) -> None:
        pass
