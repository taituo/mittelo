from __future__ import annotations

import json
import threading
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Protocol
from urllib.parse import parse_qs, urlparse

class _State(Protocol):
    store: Any
    def request_shutdown(self) -> None: ...


def _json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")


class _RestHandler(BaseHTTPRequestHandler):
    server_version = "mittelo-rest/0.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        # Keep REST quiet by default (hub already has enough output).
        return

    def _send(self, status: int, payload: Any) -> None:
        body = _json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    @property
    def state(self) -> _State:
        return self.server.state  # type: ignore[attr-defined]

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send(200, {"ok": True})
            return

        if parsed.path == "/stats":
            self._send(200, {"stats": self.state.store.stats()})
            return

        if parsed.path == "/tasks":
            qs = parse_qs(parsed.query or "")
            status = (qs.get("status") or [None])[0]
            limit_s = (qs.get("limit") or [None])[0]
            try:
                limit = int(limit_s) if limit_s is not None else 50
            except ValueError:
                self._send(400, {"error": "invalid limit"})
                return

            tasks = self.state.store.list(status=status, limit=limit)
            self._send(200, {"tasks": [asdict(t) for t in tasks], "stats": self.state.store.stats()})
            return

        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            body = self._read_json()
        except Exception:
            self._send(400, {"error": "invalid json"})
            return

        if parsed.path == "/tasks":
            prompt = body.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip():
                self._send(400, {"error": "missing prompt"})
                return
            task_id = self.state.store.enqueue(prompt)
            self._send(200, {"task_id": task_id})
            return

        if parsed.path == "/tasks/retry_failed":
            retried = self.state.store.retry_all_failed()
            self._send(200, {"retried": retried})
            return

        if parsed.path == "/shutdown":
            self.state.request_shutdown()
            self._send(200, {"ok": True})
            return

        self._send(404, {"error": "not found"})


class RestApiServer:
    def __init__(self, host: str, port: int, state: _State):
        self.host = host
        self.port = port
        self.state = state
        self._srv = ThreadingHTTPServer((host, port), _RestHandler)
        self._srv.state = state  # type: ignore[attr-defined]
        self._thread = threading.Thread(target=self._srv.serve_forever, name="mittelo-rest", daemon=True)

    @property
    def address(self) -> tuple[str, int]:
        h, p = self._srv.server_address
        return str(h), int(p)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        try:
            self._srv.shutdown()
        finally:
            try:
                self._srv.server_close()
            except Exception:
                pass
