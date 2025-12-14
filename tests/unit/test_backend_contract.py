import pytest
import asyncio
import os
from src.wrapper.drivers.abstract import AbstractDriver
from typing import AsyncGenerator, List

class FakeDriver(AbstractDriver):
    async def start(self) -> None:
        pass
        
    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        yield f"echo: {content}"
        
    async def stop(self) -> None:
        pass

@pytest.mark.asyncio
async def test_fake_backend_contract():
    driver = FakeDriver()
    await driver.start()
    
    response = []
    async for token in driver.chat("hello", []):
        response.append(token)
        
    await driver.stop()
    
    assert "".join(response) == "echo: hello"
