# COORDINATION_PLAN (Shared roadmap)

Date: 2025-12-14  
Repo: `mittelo`  
Team: Human + Gemini agent + Codex agent (no swarm mode while stabilizing)

## 1) Ownership (avoid collisions)

**Codex owns (core / correctness):**
- `src/orchestrator/*`
- `docs/PROTOCOL.md`, `docs/REST_API.md`, `docs/TESTING.md`
- `tests/*`
- `scripts/doctor.py`, `scripts/run_system_tests.py` (testing harness/tooling)

**Gemini owns (integrations / UX):**
- `src/wrapper/drivers/*`
- `backends/*`
- `src/utils/dashboard.py`
- `docs/BACKENDS.md`, `docs/VERSION_LOCK.md` (integration docs)

If a task requires crossing ownership boundaries, coordinate first and keep the PR small.

## 2) Workflow (no swarm, stable iterations)

1. Pick a user story (see `docs/FEATURE_BUNDLES.md`).
2. Implement with minimal diff.
3. Update docs + tests in the same change.
4. Run deterministic checks:
   - `python3 scripts/doctor.py`
   - `pytest` (after `uv pip install -e '.[dev]'`)
5. If it’s a “real CLI” change, run system artifacts:
   - `python3 scripts/run_system_tests.py --backend <name> --prompt "<smoke prompt>"`

## 3) Test policy

- **CI gate:** deterministic unit + integration tests only.
- **Not CI gate:** real-model runs (Gemini/Claude/Kiro/Codex/Kimi), because output is nondeterministic.
- System runs must produce artifacts to compare regressions over time.

## 4) Roadmap (phased)

### Phase 0 — Stabilize (now)
- Solo backend verification (no mixed swarms)
- Correct non-interactive flags + model pinning docs
- Deterministic tests and basic coverage
- Dashboard reliability (clear OFFLINE/ONLINE)

### Phase 1 — Adapters
- Optional REST adapter (already present) for web/game engine dashboards
- Keep MCP proxy as a separate adapter process (do not embed into hub)

### Phase 2 — Packaging & reproducibility
- Create a machine-readable CLI lockfile (optional) under `docs/cli_lock.json`
- Add Docker images later (hub/agent) once the core is stable

### Phase 3 — Scale / autonomy (only after tests)
- Better scheduling (priorities, cancellation)
- Tool-use and sandboxing policies
- “NOHUMAN loop” experiments behind strict safety gates

## 5) Version pinning rule

If a feature depends on external CLI behavior:
- it must be documented in `docs/VERSION_LOCK.md`
- it must have a verifier check (`scripts/doctor.py` or a follow-up script)

## 6) Canonical docs to keep synced

- `docs/PROTOCOL.md` (core contract)
- `docs/BACKENDS.md` (how to plug CLIs)
- `docs/TESTING.md` (how to verify changes)
- `docs/VERSION_LOCK.md` (how to reproduce environments)

