import os
import subprocess
import os
from typing import AsyncGenerator, List
from .abstract import AbstractDriver

class KiroCLIDriver(AbstractDriver):
    def __init__(self, binary_path: str = "/Users/tiny/.local/bin/kiro-cli"):
        self.binary_path = binary_path
        self.model = os.environ.get("MITTELO_KIRO_MODEL")
        self.trust_all_tools = os.environ.get("MITTELO_KIRO_TRUST_ALL_TOOLS") == "1"

    async def start(self) -> None:
        try:
            subprocess.run([self.binary_path, "--version"], capture_output=True, check=False)
        except FileNotFoundError:
            raise RuntimeError(f"Binary '{self.binary_path}' not found.")

    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        # Command: kiro-cli chat --no-interactive [--trust-all-tools] [--model <model>] "prompt"
        
        cmd = [self.binary_path, "chat", "--no-interactive"]
        
        if os.environ.get("MITTELO_KIRO_TRUST_ALL_TOOLS") == "1":
            cmd.append("--trust-all-tools")
            
        model = os.environ.get("MITTELO_KIRO_MODEL")
        if model:
            cmd.extend(["--model", model])
            
        cmd.append(content)
        if self.model:
            cmd.extend(["--model", self.model])
        if self.trust_all_tools:
            cmd.append("--trust-all-tools")
        else:
            cmd.append("--trust-tools=")
        cmd.append(content)
        
        try:
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
