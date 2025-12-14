from abc import ABC, abstractmethod
from typing import AsyncGenerator, List

class AbstractDriver(ABC):
    @abstractmethod
    async def start(self) -> None:
        """Start the underlying process or session."""
        pass

    @abstractmethod
    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        """Send content and stream response."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the underlying process or session."""
        pass
