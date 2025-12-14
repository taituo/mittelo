from __future__ import annotations

import os
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

        if self.trust_all_tools:
            cmd.append("--trust-all-tools")
        else:
            cmd.extend(["--trust-tools", ""])

        cmd.append(content)

        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            env=build_env(),
        )
        if process.returncode != 0:
            msg = (process.stderr or process.stdout or "").strip()
            raise RuntimeError(msg or "kiro-cli failed")
        yield process.stdout or ""

    async def stop(self) -> None:
        pass
