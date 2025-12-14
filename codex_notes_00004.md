# codex_notes_00004 (coverage + dead code + real features)

Date: 2025-12-14

## What the user asked

- Add a “coverage” section and test coverage guidance.
- Do basic “advanced” code analysis focused on dead/unfinished code.
- Produce a **real feature list** (distinguish real vs mock vs stub).

## What was added/updated

- Coverage how-to: `docs/COVERAGE.md`
  - Uses `pytest-cov` via dev extras (`uv pip install -e '.[dev]'`).
  - Targets `orchestrator`, `wrapper`, `utils` modules (imported from `src/`).
  - Optional HTML report under `reports/coverage/` (gitignored).
- Dead/unfinished map: `docs/DEAD_CODE.md`
  - Highlights `src/utils/rate_limiter.py` as currently unused (but reusable).
  - Clarifies “archived” vs “tooling” vs “actually dead”.
- Features list updated: `docs/FEATURES.md`
  - Adds status legend and corrects GLM to **Alias** and Copilot to **Removed**.
- README links: `README.md` now links to the new docs.

## Known constraints / gotchas

- In some environments localhost bind fails (EPERM): integration + pair smoke will `SKIP`. Unit tests remain deterministic.
- System python may be 3.9, but project targets `>=3.10`; use `.venv/bin/python` for scripts when possible.

## Next “analysis” tasks (if needed)

- Add a lightweight “lint plan” doc (ruff/mypy) without committing a giant lockfile diff.
- Decide whether `src/utils/rate_limiter.py` should be wired into `src/utils/dashboard.py` or removed.
