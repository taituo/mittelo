# REST API (optional)

Mittelö’s core transport is TCP JSONL (`docs/PROTOCOL.md`). For integrations that prefer HTTP, the hub can also expose a small REST API.

## Enable

Run the hub with `--rest-port`:

```bash
python3 -m mittelo hub --db mittelo.db --host 127.0.0.1 --port 8765 --rest-port 8080 --print-url
```

`--rest-host` is optional (defaults to hub host).

## Endpoints

- `GET /health` → `{ "ok": true }`
- `GET /stats` → `{ "stats": { "queued": 0, "leased": 0, "done": 0, "failed": 0 } }`
- `GET /tasks?status=queued|leased|done|failed&limit=50`
  → `{ "tasks": [...], "stats": {...} }`
- `POST /tasks` body: `{ "prompt": "..." }` → `{ "task_id": 123 }`
- `POST /tasks/retry_failed` → `{ "retried": 3 }`
- `POST /shutdown` → `{ "ok": true }`

Notes:
- `limit <= 0` means “no limit”.
- This REST layer is intentionally minimal and unauthenticated (for localhost/dev). Put auth/reverse-proxy in front if you expose it.
