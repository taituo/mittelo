# Mittelö (SwarmKit)

Mittelö (“mittelo”) is a small, remix-friendly swarm toolkit: a **hub** queues tasks and multiple **agents** (Codex, Gemini, Kiro, local OSS LLMs, or anything that can read/write stdin/stdout) lease tasks, produce results, and ack them back.

## Quick start (no LLM, just echo)

Terminal A:

```bash
python3 -m mittelo hub --host 127.0.0.1 --port 8765
```

By default, the hub stores its DB in `.mittelo/mittelo.db` (override via `--db` or `MITTELO_DB`).

Terminal B:

```bash
python3 -m mittelo agent --host 127.0.0.1 --port 8765 --backend echo
```

Terminal C:

```bash
python3 -m mittelo enqueue --host 127.0.0.1 --port 8765 --prompt "hello swarm"
python3 -m mittelo status --host 127.0.0.1 --port 8765
```

## Mixed swarms

Run a small local swarm with mixed backends:

```bash
python3 -m mittelo swarm --host 127.0.0.1 --port 8765 --agent echo=2 --agent kiro=1
```

## Backends as folders (remix-friendly)

Drop a script at `backends/<name>/run` and then run:

```bash
python3 -m mittelo agent --backend <name>
```

If you want to keep backends elsewhere, set `MITTELO_BACKENDS_DIR=/path/to/backends`.

## Docs

- `docs/PROTOCOL.md` (JSONL RPC protocol)
- `docs/BACKENDS.md` (how to plug in Codex/Gemini/Kiro/local)
- `docs/QUICKSTART.md` (copy-paste commands)
- `docs/REMIX.md` (how to remix the repo)
- `docs/GAIA_REMIX.md` (composition recipe)
- `docs/GO_PORT.md` (Go skeleton client)
- `docs/MLX_GUIDE.md` (Apple Silicon setup)
- `docs/STRUCTURE.md` (repo layout)
- `docs/USE_CASES.md` (example patterns)
- `docs/REST_API.md` (optional REST adapter)
- `docs/VERSION_LOCK.md` (pin CLI flags/versions)
- `docs/FEATURE_BUNDLES.md` (ship features as stories+docs+tests)
- `docs/FEATURES.md` (real vs mock/stub features)
- `docs/TESTING.md` (unit/integration/system tests)
- `docs/COVERAGE.md` (test coverage how-to)
- `docs/DEAD_CODE.md` (unused/unfinished code map)
- `docs/TROUBLESHOOTING.md` (common issues)
- `docs/SHARE_THIS.md` (onboarding checklist)
- `docs/AGENT_PROMPTS.md` (multi-agent dev prompts)

## Verification (recommended)

```bash
python3 scripts/doctor.py
pytest
python3 scripts/run_pair_smoke.py --backend-a echo --backend-b echo --tasks 6 --timeout-s 15
```

Pair smoke writes artifacts under `reports/swarm/...` and may record `SKIPPED` if localhost socket binding is blocked.

## Contributing

See `CONTRIBUTING.md`.
