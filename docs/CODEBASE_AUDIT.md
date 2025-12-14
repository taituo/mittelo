# Codebase Audit & Analysis

**Date:** 2025-12-14
**Scope:** Full directory structure analysis.

## 1. Core Application (`src/`, `mittelo/`)

The heart of the system.

- **`mittelo/`**: The Python package entry point.
  - `__main__.py`: CLI argument parsing and dispatch. **Essential.**
  - `__init__.py`: Package marker. **Essential.**

- **`src/`**: Library code.
  - **`orchestrator/`**: Server-side logic.
    - `server.py`: TCP/JSONL server, connection handling. **Essential.**
    - `storage.py`: SQLite wrapper for task queue. **Essential.**
    - `rest_api.py`: Optional HTTP adapter. **Essential (for future web UI).**
  - **`wrapper/`**: Client/Agent logic.
    - `agent.py`: The worker loop (lease -> run -> ack). **Essential.**
    - `client.py`: TCP client for the hub. **Essential.**
    - `drivers/`: Adapters for different LLM CLIs.
      - `abstract.py`: Base class.
      - `gemini_cli.py`, `claude_cli.py`, `codex_cli.py`, `kiro_cli.py`, `kimi_cli.py`, `mlx_cli.py`: Real drivers. **Essential.**
      - `subprocess_env.py`: Env var helper. **Essential.**
    - `prereqs.py`: Preflight checks for drivers. **Essential.**
    - `backends.py`: Logic to resolve and run `backends/*/run` scripts. **Essential.**
  - **`utils/`**: Shared utilities.
    - `dashboard.py`: Textual TUI. **Essential.**
    - `dashboard_snapshot.py`: Snapshot logic for TUI. **Essential.**
    - `rate_limiter.py`: Token bucket implementation. **Essential.**
  - **`protocol/`**:
    - `__init__.py`: Empty. **Keep** (namespace package).

## 2. Extension Points (`backends/`)

The "Remix" layer. Users add folders here to support new tools.

- **`_template/`**: Boilerplate for new backends. **Keep.**
- **`archive/`**: Old/deprecated backends (`gh_copilot`, `ollama`). **Keep (reference).**
- **Active Backends**:
  - `gemini/`, `claude_code/`, `codex/`, `kiro/`, `kimi/`, `mlx/`: Core supported backends. **Essential.**
  - `echo/`: For testing. **Essential.**
  - `tmux/`: For terminal control. **Essential.**
  - `glm/`: Alias for Claude Code GLM mode. **Essential.**
  - `opencode/`: Placeholder? **Review.**

## 3. Automation & QA (`scripts/`)

Tools for maintaining the repo.

- **Critical QA**:
  - `doctor.py`: Environment health check. **Essential.**
  - `run_system_tests.py`: Single-backend verification. **Essential.**
  - `run_pair_smoke.py`: Multi-agent integration test. **Essential.**
  - `verify_cli_drivers.py`: Driver verification script. **Essential.**
  - `run_backend_matrix.py`: For Track A reporting. **Essential.**

- **Utilities**:
  - `dev_monitor.py`: Watchdog? **Keep.**
  - `img2ansi.py`: Asset generation. **Keep.**
  - `mission_control.sh`: Shell wrapper for dashboard? **Keep.**
  - `smoke_test.py`: Minimal e2e test (used in Quickstart). **Keep.**

- **Archived (`scripts/archive/`)**:
  - `verify_new_structure.py`: **OBSOLETE**. Moved to archive.
  - `debug_codex.py`: Scratchpad. Moved to archive.

## 4. Tests (`tests/`)

The safety net.

- **`unit/`**: Fast, isolated tests.
  - `test_hub_dispatch.py`, `test_taskstore.py`: Core logic tests. **Essential.**
  - `test_backend_*.py`: Driver/resolution tests. **Essential.**
  - `test_dashboard_robustness.py`: Dashboard tests. **Essential.**
- **`integration/`**: Slower, real-socket tests.
  - `test_hub_echo_flow.py`: Basic integration. **Essential.**

## 5. Documentation (`docs/` vs `info/`)

- **`docs/`**: Current, normative documentation.
  - `STRUCTURE.md`, `PROTOCOL.md`, `BACKENDS.md`: Core specs. **Essential.**
  - `DEVELOPING_MITTELO_OUTSIDE_SWARM.md`: Developer guide. **Essential.**
  - `QA_TICKETS.md`, `VERSION_LOCK.md`: Living process docs. **Essential.**
  - `WORKSPLIT.md`: Current plan. **Essential.**
  - `QUICKSTART.md`: Entry point guide. **Essential.**

- **`info/`**: Historical context, plans, logs. **Keep as archive.**

## 6. Experiments (`go/`)

- **`go/`**: Experimental Go port. **Keep** (low maintenance).

## Recommended Actions

1.  **Review** `backends/opencode` (is it needed?).
