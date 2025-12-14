# Work Split (2-agent, expanded scope)

This repo moves fastest when work is split into two parallel tracks with a clean interface between them.

## Shared rules (non-negotiable)

- Keep repo root clean: docs in `docs/`, notes in `info/`, artifacts in `reports/` (preferably ignored).
- One change-set per commit; avoid drive-by refactors.
- If a backend fails due to auth/setup/networking, **ticket it** (don’t “fix” it by weakening the contract).
- Always leave `pytest` green.

## Track A (Codex): Core + Tests + CI

**Primary goal:** deterministic reliability without needing any external LLM auth.

### A1. System-test matrix (artifact-based)
- Add `scripts/run_backend_matrix.py`:
  - Enumerates `backends/*` (excluding `_template`, `archive`).
  - Runs `python -m mittelo backend-check --backend <name>` for each backend.
  - Runs `scripts/run_system_tests.py` only when status is `ok`.
  - Writes a single report folder under `reports/e2e/<timestamp>_matrix/` with:
    - `matrix.json`
    - `summary.md` (PASS/FAIL/SKIP per backend + reason)

### A2. Make “verify” scripts SKIP-aware (not noisy FAIL)
- Update `scripts/verify_cli_drivers.py`:
  - Uses the same prereq logic (preflight).
  - Prints `SKIP` for missing auth/config/network limitations (instead of FAIL).
  - Keeps FAIL for real wrapper bugs (tracebacks, protocol violations, non-zero rc when prereqs are OK).

### A3. CI baseline
- Add GitHub Actions workflow that runs only:
  - `python3 scripts/doctor.py`
  - `pytest`
  - `python3 -m mittelo backend-check --backend echo`
  - (No external LLM backends in CI)

### A4. Quality gates (contract stability)
- Add/expand unit tests around:
  - backend resolution (`resolve_backend_argv`)
  - preflight behavior (already started)
  - hub dispatch invariants (lease/ack/error paths)

**Definition of done (Track A):**
- `pytest` green locally and in CI
- matrix report produces stable PASS/SKIP outcomes without polluting git

## Track B (Gemini): Backends + Dashboard + UX

**Primary goal:** make each real backend “boringly runnable” in a real machine setup, with clear prerequisites and clean output.

### B1. Backend readiness + docs
- For each backend (`codex`, `claude_code/glm`, `gemini`, `kiro`, `kimi`, `mlx`, `tmux`):
  - Document exact prerequisites in `docs/BACKENDS.md` (auth, env vars, files, known failure modes).
  - Ensure wrapper prints only model output on stdout; all diagnostics to stderr.
  - Where possible, add “non-interactive” flags and model pinning using `docs/VERSION_LOCK.md`.

### B2. Fix/triage backend failures (real causes)
- Convert “expected setup failures” into SKIP (via preflight) + a doc snippet.
- Fix true wrapper bugs:
  - wrong CLI argv/flag ordering
  - missing env pass-through
  - writing to real HOME instead of `MITTELO_SUBPROCESS_HOME`

### B3. Dashboard testing + robustness
- Add unit tests for dashboard connection error handling (OFFLINE state).
- Ensure dashboard never crashes when hub is down; always shows an actionable error.

### B4. Mixed mode (real environment validation)
- On a machine where localhost bind works:
  - Run `scripts/run_pair_smoke.py` for `echo/echo`, then one real backend pair (e.g. `codex/claude_code`).
  - Ticket any failures with exact repro + environment notes.

**Definition of done (Track B):**
- Each backend has a clear prereq section + “known good command”
- Dashboard works offline and doesn’t crash

## Shared roadmap (expanded scope)

Pick these when Track A + B are stable:

- **Version locking:** keep `docs/VERSION_LOCK.md` current; add a “last verified” stamp per backend.
- **Packaging:** optional `mittelo` CLI entrypoint packaging and `pipx` install instructions.
- **Docker/containers (optional):** only if we need deterministic CI for external CLIs; otherwise keep it simple.
- **REST API:** keep it thin (adapter) and spec-first; don’t let it drift from `docs/PROTOCOL.md`.

## Coordination interface

- All issues go to `docs/QA_TICKETS.md` with:
  - exact command
  - expected vs actual
  - environment notes (auth state, socket restrictions)
- Track A owns: tests/CI/scripts that generate reports
- Track B owns: backend wrappers, dashboard UX/docs

