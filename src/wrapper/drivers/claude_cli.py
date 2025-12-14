import os
import subprocess
import os
from typing import AsyncGenerator, List
from .abstract import AbstractDriver

class ClaudeCLIDriver(AbstractDriver):
    def __init__(self, binary_path: str = "claude"):
        self.binary_path = binary_path
        self.model = os.environ.get("MITTELO_CLAUDE_MODEL")

    async def start(self) -> None:
        try:
            subprocess.run([self.binary_path, "--version"], capture_output=True, check=False)
        except FileNotFoundError:
            raise RuntimeError(f"Binary '{self.binary_path}' not found.")

    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        try:
            # Usage: claude "prompt" --print --tools ""
            cmd = [self.binary_path, content, "--print", "--tools", ""]
            
            model = os.environ.get("MITTELO_CLAUDE_MODEL")
            if model:
                cmd.extend(["--model", model])

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            if process.returncode != 0:
                yield f"Error: {(process.stderr or process.stdout).strip()}"
            else:
                yield process.stdout
        except Exception as e:
            yield f"Exception: {e}"

    async def stop(self) -> None:
        pass
