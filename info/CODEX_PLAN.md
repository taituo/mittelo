# CODEX_PLAN (Core + Tests)

Date: 2025-12-14  
Owner: Codex agent  
Scope: Core hub/protocol/storage + deterministic tests + system-run artifacts tooling  
Mode: No swarm orchestration; keep changes small and reviewable.

## Goal

Make the core “boringly correct”:
- protocol and docs match
- task semantics are stable
- unit/integration tests are deterministic
- system runs produce artifacts (not flaky pass/fail)

## Workstreams

### A) Core correctness

1. **Protocol parity**
   - keep `docs/PROTOCOL.md` aligned with hub methods and semantics
   - lock down semantics like `limit <= 0` meaning “no limit”

2. **Storage semantics**
   - ensure task lifecycle is well-defined:
     - `queued → leased → done|failed`
     - expired lease can be re-leased
     - retry resets failed tasks cleanly

### B) Deterministic tests (CI gate)

1. Unit tests (`tests/unit/*`)
   - `TaskStore` behavior, including retry and lease expiry
   - hub dispatch semantics without requiring sockets

2. Integration tests (`tests/integration/*`)
   - end-to-end hub + `echo` agent
   - auto-skip if localhost sockets are blocked

3. Coverage targets
   - prioritize core modules (`src/orchestrator/*`, protocol dispatch) over drivers

### C) System runs (artifacts, not CI gate)

- A runner that executes one backend wrapper and writes:
  - `reports/e2e/<run>/run.json`
  - `reports/e2e/<run>/result.json`
  - `reports/e2e/<run>/summary.md`

### D) Environment reproducibility

- A `doctor` tool that checks:
  - CLI presence + versions
  - required non-interactive flags exist
  - reminds about model env vars

## Deliverables

- `docs/TESTING.md` and a repeatable dev setup (`uv pip install -e '.[dev]'`)
- Deterministic tests runnable locally and in CI
- System-run artifacts tooling
- Protocol/doc drift minimized

## Non-goals (for now)

- Major refactor of `src/` structure
- Implementing real model quality scoring in CI

