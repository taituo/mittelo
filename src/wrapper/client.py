from __future__ import annotations

import json
import socket
import uuid
from typing import Any


class JsonlClient:
    def __init__(self, host: str, port: int, timeout_s: float = 30.0):
        self.host = host
        self.port = port
        self.timeout_s = timeout_s
        self._sock: socket.socket | None = None
        self._fp = None

    def __enter__(self) -> "JsonlClient":
        self._sock = socket.create_connection((self.host, self.port), timeout=self.timeout_s)
        self._fp = self._sock.makefile("rwb")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if self._fp is not None:
                self._fp.close()
        finally:
            if self._sock is not None:
                self._sock.close()
        self._sock = None
        self._fp = None

    def call(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if self._fp is None:
            raise RuntimeError("Client not connected")
        req_id = uuid.uuid4().hex
        req = {"id": req_id, "method": method, "params": params}
        self._fp.write((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))
        self._fp.flush()
        line = self._fp.readline()
        if not line:
            raise ConnectionError("Hub closed connection")
        resp = json.loads(line.decode("utf-8"))
        if resp.get("id") != req_id:
            raise RuntimeError("Mismatched response id")
        if "error" in resp and resp["error"] is not None:
            raise RuntimeError(resp["error"].get("message", "Unknown error"))
        return resp["result"]
