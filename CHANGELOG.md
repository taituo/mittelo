# Changelog

This project moves fast and integrates multiple external CLIs; changes are grouped by “what users feel” (core, tooling, integrations, docs).

## 0.1.0 (2025-12-14)

### Added
- Hub REST adapter (optional) alongside the TCP JSONL protocol (`src/orchestrator/rest_api.py`, `docs/REST_API.md`).
- Deterministic test suite scaffold (`tests/`, `pytest.ini`) with localhost-bind auto-skip for integration tests.
- Environment “doctor” to check installed CLIs and required non-interactive flags (`scripts/doctor.py`).
- Artifact-based system runs (`scripts/run_system_tests.py`) and pair-smoke runs (`scripts/run_pair_smoke.py`).
- Integration drivers/wrappers for multiple CLIs (`src/wrapper/drivers/*`, `backends/*`), plus a terminal dashboard (`src/utils/dashboard.py`).
- Documentation set for protocol/backends/version pinning/testing/troubleshooting/coverage/dead-code/feature status:
  - `docs/PROTOCOL.md`, `docs/BACKENDS.md`, `docs/VERSION_LOCK.md`, `docs/TESTING.md`, `docs/TROUBLESHOOTING.md`, `docs/COVERAGE.md`, `docs/DEAD_CODE.md`, `docs/FEATURES.md`.

### Changed
- Repo structure migrated to `src/`-based imports and a single CLI entrypoint (`mittelo/__main__.py`).
- GLM backend clarified as an alias of `claude_code` when Claude is configured via env exports to use GLM endpoints (`backends/glm/run`, `docs/BACKENDS.md`, `docs/FEATURES.md`).

### Fixed
- JSONL `list.limit=0` semantics (“no limit”) now work consistently with docs (`src/orchestrator/server.py`).
- Pair-smoke now always writes artifacts and records `SKIPPED` when localhost socket binding is blocked.

### Removed
- GH Copilot integration (intentionally removed to reduce drift).
- Hypothetical `glm` binary driver (replaced by GLM-as-Claude alias).

### Notes
- Some environments block localhost socket binding (EPERM). Integration tests and pair-smoke runs will skip in those environments; unit tests remain deterministic.
- System Python may be older than the project target; prefer `.venv/bin/python` for scripts that import from `src/`.

