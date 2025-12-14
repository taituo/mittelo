import subprocess
import os
import re
import sys # <-- Added this import
from typing import AsyncGenerator, List
from .abstract import AbstractDriver

class CodexCLIDriver(AbstractDriver):
    def __init__(self, binary_path: str = "codex"):
        self.binary_path = binary_path
        self.model = os.environ.get("MITTELO_CODEX_MODEL")

    async def start(self) -> None:
        try:
            subprocess.run([self.binary_path, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
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

        try:
            process = subprocess.run(
                cmd,
                input=content,  # Pass content via stdin
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode != 0:
                yield f"Error: {(process.stderr or process.stdout).strip()}"
            else:
                yield process.stdout.strip()

        except Exception as e:
            yield f"Exception running Codex: {e}"

    async def stop(self) -> None:
        pass
