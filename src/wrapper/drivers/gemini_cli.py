import os
import shutil
import subprocess
import os
from typing import AsyncGenerator, List
from .abstract import AbstractDriver

class GeminiCLIDriver(AbstractDriver):
    def __init__(self, binary_path: str = "gemini"):
        self.binary_path = binary_path
        self.model = os.environ.get("MITTELO_GEMINI_MODEL")

    async def start(self) -> None:
        # Accept either a native `gemini` binary or an `npx` fallback.
        if shutil.which(self.binary_path):
            subprocess.run([self.binary_path, "--version"], capture_output=True, check=False)
            return
        if not shutil.which("npx"):
            raise RuntimeError("Neither 'gemini' nor 'npx' is available for Gemini CLI.")

    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        try:
            # Assuming basic usage: gemini "prompt" --model <model>
            cmd = [self.binary_path, content]
            
            model = os.environ.get("MITTELO_GEMINI_MODEL")
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
