# Mittelö (SwarmKit)

Mittelö (“mittelo”) is a small, remix-friendly swarm toolkit: a **hub** queues tasks and multiple **agents** (Codex, Gemini, Kiro, local OSS LLMs, or anything that can read/write stdin/stdout) lease tasks, produce results, and ack them back.

## Quick start (no LLM, just echo)

Terminal A:

```bash
python3 -m mittelo hub --db mittelo.db --host 127.0.0.1 --port 8765
```

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
- `docs/REMIX.md` (how to remix the repo)
- `docs/QUICKSTART.md` (copy-paste commands)
- `docs/STRUCTURE.md` (repo layout)
- `docs/USE_CASES.md` (example patterns)
- `docs/GAIA_REMIX.md` (composition recipe)
- `docs/GO_PORT.md` (Go skeleton client)
- `docs/REST_API.md` (optional REST adapter)
- `docs/VERSION_LOCK.md` (pin CLI flags/versions)
- `docs/FEATURE_BUNDLES.md` (ship features as stories+docs+tests)
- `docs/TESTING.md` (unit/integration/system tests)
- `docs/SHARE_THIS.md` (onboarding checklist)
- `docs/AGENT_PROMPTS.md` (multi-agent dev prompts)

## Contributing

See `CONTRIBUTING.md`.
