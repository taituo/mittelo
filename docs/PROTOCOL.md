# Mittelö protocol (JSONL RPC)

Transport: TCP. Each request/response is one JSON object per line.

Request:

```json
{"id":"<client-id>","method":"<method>","params":{...}}
```

Response:

```json
{"id":"<client-id>","result":{...},"error":null}
```

If error:

```json
{"id":"<client-id>","result":null,"error":{"message":"..."}}
```

## Methods

- `enqueue` params: `{ "prompt": "..." }` → result: `{ "task_id": 123 }`
- `lease` params: `{ "worker_id": "...", "max_tasks": 1, "lease_seconds": 60 }` → result: `{ "tasks": [Task...] }`
- `ack` params: `{ "task_id": 123, "status": "done|failed", "result": "...", "error": "..." }` → result: `{ "ok": true }`
- `list` params: `{ "status": "queued|leased|done|failed"?, "limit": 50 }` → result: `{ "tasks": [...], "stats": {...} }`
- `stats` params: `{}` → result: `{ "stats": {...} }`
- `shutdown` params: `{}` → result: `{ "ok": true }`

Task object fields:

```json
{
  "task_id": 123,
  "prompt": "...",
  "status": "queued|leased|done|failed",
  "created_at": 1730000000.0,
  "updated_at": 1730000001.0,
  "leased_until": 1730000060.0,
  "worker_id": "host-pid-...",
  "result": "...",
  "error": "..."
}
```
