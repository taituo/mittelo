# Developing Mittelö Outside Swarm

This guide is for working on Mittelö **without running a multi-agent swarm** (single developer / single CLI / local tests).

## Start Here (15 minutes)

1. Read:
   - `README.md`
   - `docs/STRUCTURE.md`
   - `info/QUICKSTART.md` (archived)
   - `docs/TESTING.md`
   - `docs/VERSION_LOCK.md`
2. Sanity-check your environment:
   - `python3 scripts/doctor.py`
   - `pytest`

## Repo Hygiene (important)

- Don’t add random files to repo root.
  - Public docs → `docs/`
  - Scratch notes / “agent logs” → `info/` (or don’t commit them)
  - Generated artifacts → `reports/` (preferably ignored)
- Make small, surgical changes (there are multiple humans working in the same folder).
- One topic per commit; avoid drive-by refactors.

## Quick Local Run (no LLM)

In 3 terminals:

Terminal A (hub):
```bash
python3 -m mittelo hub --host 127.0.0.1 --port 8765
```

Terminal B (agent, echo backend):
```bash
python3 -m mittelo agent --host 127.0.0.1 --port 8765 --backend echo
```

Terminal C (enqueue + status):
```bash
python3 -m mittelo enqueue --host 127.0.0.1 --port 8765 --prompt "hello swarm"
python3 -m mittelo status --host 127.0.0.1 --port 8765
```

Notes:
- Hub DB default is `.mittelo/mittelo.db` (override via `--db` or `MITTELO_DB`).
- If hub start fails with `PermissionError: Operation not permitted` when binding, your environment blocks localhost sockets.
  In that case, use unit tests + backend system tests (below) and run swarm/hub on a machine that allows binding.

## Backend Development (outside swarm)

Backends are scripts under `backends/<name>/run`.

Recommended workflow:
1. Add/update the backend script.
2. Verify it produces “clean stdout” (no banners, no ANSI) for simple prompts.
3. Run a prereq check (best-effort):
   ```bash
   python3 -m mittelo backend-check --backend <name>
   ```
4. Run the backend system test:
   ```bash
   python3 scripts/run_system_tests.py --backend <name> --prompt "Return exactly: mittelo smoke ok"
   ```

If your backend wraps an external CLI (Claude/Codex/Gemini/Kiro/Kimi/MLX):
- Expect auth/config failures until the CLI is logged in and environment variables are set.
- Prefer to ticket missing auth/config as “setup prerequisites”, not “code bugs”.

## Testing Strategy

Use the closest test that catches your change:

- Unit tests (fast, deterministic):
  - `pytest`
- Contract tests (protocol/dispatch invariants):
  - `pytest -q` (included in suite)
- System tests (one backend wrapper at a time):
  - `python3 scripts/run_system_tests.py --backend echo --prompt "Return exactly: ok"`
- Pair smoke (end-to-end hub+agents):
  - `python3 scripts/run_pair_smoke.py --backend-a echo --backend-b echo --tasks 6 --timeout-s 15`
  - May `SKIP` if localhost bind is blocked (environment constraint).

Coverage:
- See `docs/COVERAGE.md`

## Where to Put New Work

- Core protocol, hub, orchestration: `src/` and `mittelo/`
- Backend wrappers: `backends/` and `src/wrapper/`
- Scripts: `scripts/`
- Tests: `tests/`
- Public documentation: `docs/`

## “If Something Breaks” Checklist

1. Re-run: `python3 scripts/doctor.py`
2. Re-run: `pytest`
3. If it’s a backend CLI issue:
   - Check `docs/TROUBLESHOOTING.md`
   - Check `docs/VERSION_LOCK.md` (flags changed upstream?)
   - Confirm auth/login for that CLI
4. If it’s networking (`EPERM` bind):
   - Don’t patch around it in code; ticket it as environment limitation and run e2e on a host that allows binding.

## Ticketing (how we keep velocity)

When you hit a failure:
- Create/append a short ticket in `docs/QA_TICKETS.md`:
  - Symptom (exact error)
  - Repro command
  - Expected vs actual
  - Environment notes (OS, restrictions, auth state)
  - Proposed fix owner (“code”, “docs”, “setup”, “CI”)
