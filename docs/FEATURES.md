# Feature List

This document categorizes the features of the Mittelö project into Real, Mock/Stub, and Partial implementations.

Legend:
- **Real:** implemented and runnable (may still depend on external CLIs being installed/configured).
- **Mock:** deterministic fake used for tests/demos.
- **Alias:** points to another backend/driver (same implementation, different “name”).
- **Stub:** placeholder implementation that still needs real CLI/API details.

## Core Components

| Component | Status | Description |
| :--- | :--- | :--- |
| **Hub** | **Real** | Central orchestrator (`src/orchestrator/server.py`). Handles task queue, dispatch, and state. |
| **Dashboard** | **Real** | TUI for monitoring (`src/utils/dashboard.py`). Connects to Hub via TCP. |
| **Agent Wrapper** | **Real** | Generic wrapper (`src/wrapper/agent.py`) that adapts CLI tools to the Mittelö protocol. |

## Backends (Agents)

| Backend | Status | Description |
| :--- | :--- | :--- |
| **Gemini** | **Real** | Uses `gemini` CLI. Supports `MITTELO_GEMINI_MODEL`. |
| **Claude Code** | **Real** | Uses `claude` CLI. Supports `MITTELO_CLAUDE_MODEL`. |
| **Kiro** | **Real** | Uses `kiro-cli`. Supports `MITTELO_KIRO_MODEL`. |
| **Codex** | **Real** | Uses `codex` CLI. Supports `MITTELO_CODEX_MODEL`. |
| **Kimi** | **Real** | Uses `kimi` CLI. Supports `MITTELO_KIMI_MODEL`. |
| **MLX** | **Real** | Uses `mlx-lm` (Apple Silicon). Supports `MITTELO_MLX_MODEL`. |
| **GLM** | **Alias** | Uses the `claude_code` backend, assuming your `claude` CLI is configured (via env exports) to hit GLM endpoints. |
| **Echo** | **Mock** | Returns the prompt as response. Used for testing. |
| **Fake** | **Mock** | Deterministic responses for contract testing. |
| **GH Copilot** | **Removed** | Previously explored; intentionally removed from this repo to avoid drift. |

## Tooling

| Tool | Status | Description |
| :--- | :--- | :--- |
| **Doctor** | **Real** | `scripts/doctor.py`. Verifies environment and CLI tools. |
| **System Tests** | **Real** | `scripts/run_system_tests.py`. Verifies backend connectivity. |
| **Pair Smoke** | **Real** | `scripts/run_pair_smoke.py`. Verifies Hub-Agent interaction. |
