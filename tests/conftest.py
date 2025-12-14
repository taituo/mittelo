from __future__ import annotations

import os
import socket
import sys
from pathlib import Path


project_root = Path(__file__).resolve().parents[1]
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.path.insert(0, str(project_root / "src"))


def can_bind_localhost() -> bool:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", 0))
            return True
        finally:
            s.close()
    except Exception:
        return False
