from __future__ import annotations

import os
import subprocess
from typing import AsyncGenerator, List

from .abstract import AbstractDriver
from .subprocess_env import build_env


class CodexCLIDriver(AbstractDriver):
    def __init__(self, binary_path: str = "codex"):
        self.binary_path = binary_path
        self.model = os.environ.get("MITTELO_CODEX_MODEL")

    async def start(self) -> None:
        try:
            subprocess.run([self.binary_path, "--version"], capture_output=True, text=True, check=False, env=build_env())
        except FileNotFoundError:
            raise RuntimeError(f"Codex CLI binary '{self.binary_path}' not found or not working.")


    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        # Usage: codex [GLOBAL_FLAGS] exec "prompt"
        # We need to put flags BEFORE 'exec'
        cmd = [
            self.binary_path,
            "--ask-for-approval", "never",
            "--sandbox", "workspace-write"
        ]
        
        # Use the model from the environment variable if set
        if self.model:
            cmd.extend(["--model", self.model])

        # Add subcommand and prompt
        # Use '-' to read from stdin to avoid argv length limits
        cmd.extend(["exec", "-"])

        process = subprocess.run(
            cmd,
            input=content,
            capture_output=True,
            text=True,
            check=False,
            env=build_env(),
        )
        if process.returncode != 0:
            msg = (process.stderr or process.stdout or "").strip()
            raise RuntimeError(msg or "codex failed")
        yield (process.stdout or "").strip()

    async def stop(self) -> None:
        pass
