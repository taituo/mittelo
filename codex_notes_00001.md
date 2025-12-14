# Codex notes 00001 (read-only review)

Date: 2025-12-14  
Repo: `/Users/tiny/Documents/projects3/mittelo`

These notes are based on reading the codebase only (no functional changes applied).

## What Mittelö is (as implemented)

- A small TCP hub that speaks newline-delimited JSON (JSONL/NDJSON) RPC and stores tasks in SQLite.
- Agents repeatedly `lease` tasks, run a backend wrapper (stdin → stdout), then `ack` with `done|failed`.

Core protocol + flow:
- Spec: `docs/PROTOCOL.md`
- Hub implementation: `mittelo/hub.py`
- Task storage: `mittelo/storage.py`
- Agent loop: `mittelo/agent.py`
- Client helper: `mittelo/client.py`

## Protocol surface (current code)

Implemented hub methods (`mittelo/hub.py`):
- `enqueue`, `lease`, `ack`, `list`, `stats`, `retry_failed`, `shutdown`

Note:
- `retry_failed` exists in code but is missing from `docs/PROTOCOL.md` (doc drift).

## Storage (SQLite)

SQLite DB schema (`mittelo/storage.py`) tracks:
- `prompt`, `status` (`queued|leased|done|failed`)
- leasing: `leased_until`, `worker_id`
- outputs: `result`, `error`

Repo currently contains local DB files (`mittelo.db`, `mittelo_v2.db`, `stress.db` + WAL/SHM). These should stay uncommitted (they are covered by `.gitignore`).

## Backends / wrappers

Backend mechanism:
- Preferred: `backends/<name>/run` auto-detected via `mittelo/backends.py:resolve_backend_argv`.
- Or `--backend shell --shell-cmd "..."` (runs a bash command).
- Optional override: `MITTELO_BACKENDS_DIR`.

Important reality check:
- `backends/gemini/run` is an example using `npx ... gemini-cli`.
- `backends/claude_code/run` is an example wrapper calling `claude --print` (assumes CLI exists).
- `backends/opencode/run` is a placeholder that exits non-zero.
- `backends/codex/run` and `backends/kiro/run` look like “dev persona simulators”, not real model integrations.

## CLI surface

Python CLI entrypoints live in `mittelo/__main__.py`:
- `hub`, `enqueue`, `status`, `stats`, `retry`, `agent`, `swarm`, `shutdown`

Note:
- `mittelo/__main__.py` currently prints `DEBUG: main() started` to stderr every run. If this is unintentional, it will add noise for wrappers and tests.

## Docs & “multi-agent dev” posture

Onboarding checklist: `docs/SHARE_THIS.md`  
Backend contract + examples: `docs/BACKENDS.md` + `backends/_template/`  
Multi-agent “role prompts”: `docs/AGENT_PROMPTS.md`

Repo also includes narrative/vision docs:
- `NOHUMAN_LOOP.md`, `DEVELOPING_mittelo_human_loop.md`, `doing_mittelo_now.md`
- `HLD_finnish.md` describes a more elaborate architecture (drivers/orchestrator/protocol enums) than what’s currently in `mittelo/`.

Recommendation for 3-dev safety:
- Treat `docs/PROTOCOL.md` and `mittelo/` as “stable core”.
- Encourage new contributors/agents to add/modify only `backends/<name>/` and `examples/use_cases/` unless explicitly coordinating changes.

## Suggested low-risk next steps (for the team to decide)

- Fix doc drift: add `retry_failed` to `docs/PROTOCOL.md`.
- Remove or gate the `DEBUG: main() started` print (if not needed).
- Decide whether `backends/codex` + `backends/kiro` should be real integrations or clearly labeled as simulators.
- Add a tiny “collector” example script that polls `list` and writes `results.jsonl` (helps demonstrate end-to-end workflow).

## Open questions

- Is “Subshell Swarm / tmux injection” (`backends/tmux/run`) intended as a first-class mode, or just experimentation?
- Do we want a version field in the protocol (to allow evolution without breaking remixes)?
