## 30–60 min coding session (Gemini)

Goal: improve real-life integration stability (solo + pair) while keeping CI deterministic.

### 0) Prep (5 min)
- Pull latest `main`, verify clean working tree.
- Run `python3 scripts/doctor.py --json` and paste output into the session notes (versions/flags).
- Decide the target pair to validate first: `claude_code + kiro` or `kiro + kimi` (keep `echo+echo` as fallback).

### 1) Pair smoke hardening (15–20 min)
- Run: `python3 scripts/run_pair_smoke.py --backend-a echo --backend-b echo`.
- If it succeeds on your machine: add a second run with real backends:
  - Example: `python3 scripts/run_pair_smoke.py --backend-a kiro --backend-b kimi --tasks 4 --timeout-s 60`
- Ensure artifacts always exist:
  - `reports/swarm/<run>*/run.json`
  - `reports/swarm/<run>*/result.json`
  - `reports/swarm/<run>*/summary.md`
- Confirm `run.json` records `doctor` output and model env vars.

Acceptance:
- Script exits `0` on success, `1` on failure, `0` on localhost-bind SKIP.
- No interactive prompts in agents during the run (if there are, treat as a backend bug).

### 2) Solo-run “known good” capture (15–20 min)
- For each backend you have configured locally, run one artifact:
  - `python3 scripts/run_system_tests.py --backend <name> --prompt "Say hello"`
- Update `docs/VERSION_LOCK.md` with:
  - exact CLI version
  - exact “raw” non-interactive invocation
  - required env vars and how to pin the model

Acceptance:
- `docs/VERSION_LOCK.md` contains copy/paste recipes that actually run on your machine.

### 3) GLM decision + stub (10–15 min)
- Decide what “GLM” means here (binary name + command format).
- If you know the CLI:
  - Add `backends/glm/run` and `src/wrapper/drivers/glm_cli.py`.
  - Add env `MITTELO_GLM_MODEL` and document it.
  - Extend `scripts/doctor.py` to check the GLM binary and required non-interactive flags (if possible).

Acceptance:
- `python3 scripts/run_system_tests.py --backend glm --prompt "hello"` produces artifacts (even if it fails with a clear error).

### 4) Wrap-up (5 min)
- Run `pytest`.
- Commit with a tight message:
  - `integrations: ...` for backend/driver changes
  - `docs: ...` if only doc/version lock changes

Notes:
- CI should stay deterministic; do not add “real model” expectations to `tests/`.
- If you hit localhost bind EPERM in your environment, keep pair-smoke SKIP behavior and rely on solo-run artifacts.
