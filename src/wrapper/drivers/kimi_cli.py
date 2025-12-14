from __future__ import annotations

import os
import subprocess
from typing import AsyncGenerator, List
from .abstract import AbstractDriver
from .subprocess_env import build_env


class KimiCLIDriver(AbstractDriver):
    def __init__(self, binary_path: str = "/Users/tiny/.local/bin/kimi"):
        self.binary_path = binary_path
        self.api_key = os.environ.get("KIMI_API_KEY") 

    async def start(self) -> None:
        if not os.path.exists(self.binary_path):
            # Fallback to checking PATH
            try:
                subprocess.run(["which", "kimi"], check=True, capture_output=True)
                self.binary_path = "kimi"
            except subprocess.CalledProcessError:
                raise RuntimeError(f"Kimi binary not found at {self.binary_path}")

        # Ensure API Key is available
        if not self.api_key:
            try:
                key_path = os.path.expanduser("~/.ssh/kimi.token")
                if os.path.exists(key_path):
                    with open(key_path, "r") as f:
                        self.api_key = f.read().strip()
            except Exception:
                pass

    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        """Run kimi with content."""
        
        env = build_env()
        if self.api_key:
            env["KIMI_API_KEY"] = self.api_key # Some CLIs use this
            # Also try MOONSHOT_API_KEY as generic fallback
            env["MOONSHOT_API_KEY"] = self.api_key

        # Command structure based on what we learned:
        # kimi --model <model> --print --query "PROMPT"
        model = os.environ.get("MITTELO_KIMI_MODEL", "kimi-for-coding")
        
        cmd = [
            self.binary_path,
            "--model", model,
            "--print",
            "--query", content
        ]
        
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                check=False
            )
            
            if process.returncode != 0:
                err_msg = (process.stderr or process.stdout or "").strip()
                raise RuntimeError(err_msg or "kimi failed")
            yield process.stdout or ""

        except Exception:
            raise

    async def stop(self) -> None:
        pass
