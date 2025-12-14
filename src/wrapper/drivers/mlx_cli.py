from __future__ import annotations

import subprocess
import sys
from typing import AsyncGenerator, List, Optional

from .abstract import AbstractDriver


class MlxCLIDriver(AbstractDriver):
    """
    Driver for Apple MLX (mlx-lm).

    Runs `python -m mlx_lm.generate ...` and returns the output.
    """

    def __init__(self, model: Optional[str] = None, python_path: Optional[str] = None):
        self.python_path = python_path or sys.executable
        self.model = model or "mlx-community/Qwen2.5-1.5B-Instruct-4bit"

    async def start(self) -> None:
        p = subprocess.run(
            [self.python_path, "-c", "import mlx_lm"],
            capture_output=True,
            text=True,
            check=False,
        )
        if p.returncode != 0:
            raise RuntimeError(
                "mlx-lm not available in this Python environment; install `mlx-lm` (and run via your venv python)."
            )

    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        cmd = [
            self.python_path,
            "-m",
            "mlx_lm.generate",
            "--model",
            self.model,
            "--prompt",
            content,
            "--max-tokens",
            "1024",
            "--temp",
            "0.7",
        ]

        p = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if p.returncode != 0:
            msg = (p.stderr or p.stdout or "").strip()
            yield f"Error: {msg}"
            return
        yield p.stdout

    async def stop(self) -> None:
        return
