import subprocess
import time
import os
from typing import AsyncGenerator, List, Optional

from .abstract import AbstractDriver

class TmuxDriver(AbstractDriver):
    def __init__(self, session_name: str = "mittelo_default"):
        self.session_name = session_name

    async def start(self) -> None:
        """Ensure the tmux session exists."""
        # Check if session exists
        check = subprocess.run(
            ["tmux", "has-session", "-t", self.session_name], 
            capture_output=True
        )
        if check.returncode != 0:
            # Create it if it doesn't exist
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", self.session_name], 
                check=True
            )

    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        """Send command to tmux and yield output."""
        # Send the command
        subprocess.run(
            ["tmux", "send-keys", "-t", self.session_name, content, "Enter"], 
            check=True
        )
        
        # Wait a bit for output to appear (naive implementation)
        # In a real robust driver, we would poll for a prompt or silence.
        time.sleep(0.5)

        # Capture pane
        result = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", self.session_name], 
            capture_output=True,
            text=True,
            check=True
        )
        
        yield result.stdout

    async def stop(self) -> None:
        """Kill the tmux session."""
        subprocess.run(
            ["tmux", "kill-session", "-t", self.session_name], 
            check=False # Don't error if already gone
        )
