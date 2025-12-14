# CODEX_BRIEF (Handover instructions for Codex)

Date: 2025-12-14  
Role: Codex CLI agent (core/tests focus)  
Repo: `mittelo`

## You are (role prompt)

You are a `codex`-CLI-based agent. Your job is to improve **core correctness and testability** of Mittelö with careful, minimal changes (this repo has multiple developers).

## Primary mission

1. Keep the hub/task-bus semantics stable and correct.
2. Increase deterministic test coverage for core behavior.
3. Provide tools/scripts that make environment drift obvious (versions/flags).
4. Avoid touching backend integrations unless explicitly instructed.

## Allowed files (default)

- `src/orchestrator/*`
- `tests/*`
- `scripts/doctor.py`, `scripts/run_system_tests.py`
- `docs/PROTOCOL.md`, `docs/REST_API.md`, `docs/TESTING.md`

## Do NOT touch (unless coordinated)

- `src/wrapper/drivers/*`
- `backends/*`
- `src/utils/dashboard.py`

## Operating constraints (important)

- Some environments may block localhost socket binding (you might see `PermissionError: Operation not permitted` when binding ports). In that case:
  - keep unit tests independent of sockets
  - integration tests must auto-skip if sockets cannot bind

- Python may be unable to write bytecode caches under `~/Library/Caches/com.apple.python`. Prefer:
  - `PYTHONDONTWRITEBYTECODE=1`

## Required “definition of done” for any core change

- Update docs if protocol/semantics change.
- Add/adjust deterministic tests to cover the change.
- Run:
  - `python3 scripts/doctor.py`
  - `pytest` (after `uv pip install -e '.[dev]'`)

## Suggested first tasks

- Close any remaining protocol/doc drift.
- Ensure `limit <= 0` behavior is consistent across JSONL + REST.
- Add unit tests for lease-expiration re-lease and retry semantics.

