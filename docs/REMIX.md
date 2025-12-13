# Remix guide

This repo is intentionally small and spec-first.

Suggested remix patterns:

- Fork the repo and add your own backends under `backends/<name>/run`.
- Keep the hub protocol stable (`docs/PROTOCOL.md`) so any CLI can implement a client.
- Add “missions” under `examples/` (JSONL prompts, small scripts, or full workflows).

If you want a stricter plugin system, add a `backends/<name>/backend.json` and a loader in `mittelo/backends.py`.
