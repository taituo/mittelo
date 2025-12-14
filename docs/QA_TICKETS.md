# QA tickets (generated from local test runs)

This file captures actionable follow-ups discovered during “extensive” local testing. It is not a full roadmap.

## P0 — Environment blockers (prevent mixed testing)

- Hub cannot bind localhost (`PermissionError: [Errno 1] Operation not permitted`) when starting `mittelo hub`.
  - Impact: integration tests and mixed swarms cannot run; pair-smoke records `SKIPPED`.
  - Next: confirm whether this is a harness/sandbox restriction; document required OS/network permissions for local dev.

## P1 — Backend/auth usability

- `claude_code`: fails non-interactively without login / valid key (`Invalid API key · Please run /login`).
  - Next: add a short “first-time setup” snippet to `docs/VERSION_LOCK.md` (what env vars or `claude /login` is required).

- `codex`: fails to reach API (`stream disconnected before completion: ... https://api.openai.com/v1/responses`).
  - Next: document required auth env/config; consider adding a clearer “auth missing” classifier in the driver.

- `kiro`: OAuth portal init fails when callback ports are blocked (`kiro-cli login --use-device-flow` suggested).
  - Next: document device-flow login, and/or add a driver option/env to prefer device flow.

- `gemini`: requires auth method or `GEMINI_API_KEY`/Vertex settings; may also require bind permissions in some setups.
  - Next: document exact auth env vars for non-interactive runs; optionally add a doctor-check for GEMINI env.

- `kimi`: fails with `LLM not set` in non-interactive mode.
  - Next: document first-run setup steps and/or required env vars for model/provider selection.

## P2 — MLX local models

- `mlx`: backend fails if `mlx-lm` is not installed in the active Python (`RuntimeError: mlx-lm not available...`).
  - Next: add a short install recipe to `docs/MLX_GUIDE.md` (or reference it from `docs/BACKENDS.md`), and optionally a doctor-check.

## P3 — Tooling / metrics

- Coverage: `pytest-cov` is declared in `pyproject.toml` dev extras, but may not be installed in an existing venv.
  - Next: ensure contributors run `uv pip install -e '.[dev]'` and consider adding a CI job for coverage.

## Hygiene

- Ensure no CLI sandbox home artifacts are ever committed (ignore `reports/verify_cli_drivers/` and keep `reports/e2e/` + `reports/swarm/` ignored).
