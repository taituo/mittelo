#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wrapper.drivers.tmux import TmuxDriver

async def main():
    print("Verifying New Structure & Tmux Driver...")
    
    driver = TmuxDriver(session_name="new_structure_test")
    
    print("1. Starting Driver (Creating Session)...")
    await driver.start()
    
    print("2. Sending Command...")
    async for chunk in driver.chat("echo 'Hello from new structure'", []):
        print("--- Output Chunk ---")
        print(chunk)
        if "Hello from new structure" in chunk:
            print("PASS: Output verified.")
        else:
            print("FAIL: Output mismatch.")
            
    print("3. Stopping Driver...")
    await driver.stop()

if __name__ == "__main__":
    asyncio.run(main())
