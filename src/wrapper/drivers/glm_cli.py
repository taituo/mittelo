import os
import subprocess
from typing import AsyncGenerator, List
from .abstract import AbstractDriver

class GlmCLIDriver(AbstractDriver):
    """
    Driver for GLM CLI.
    Assumes 'glm' binary is available.
    """
    def __init__(self, model: str | None = None):
        self.binary_path = "glm" # Placeholder
        self.model = model

    async def start(self) -> None:
        # Verify binary exists
        pass

    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        # Usage: glm --model <model> --prompt <prompt> (Hypothetical)
        cmd = [self.binary_path, "--non-interactive"]
        
        if self.model:
            cmd.extend(["--model", self.model])
            
        cmd.extend(["--prompt", content])

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode != 0:
                yield f"Error: {process.stderr}"
                return

            yield process.stdout

        except FileNotFoundError:
            yield "Error: GLM binary not found"
        except Exception as e:
            yield f"Error: {e}"

    async def stop(self) -> None:
        pass
