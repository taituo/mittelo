# Testing

Mittelö uses multiple test “layers”:

## 1) Unit tests (deterministic)

Run:

```bash
uv venv
uv pip install -e '.[dev]'
pytest
```

Note: Mittelö targets Python `>=3.10` (see `pyproject.toml`). If your system `python3` is older, `uv venv` will install a compatible Python for the virtualenv.

Unit tests should not require any external CLIs.

If you see `PermissionError` related to Python bytecode caches under `~/Library/Caches/com.apple.python`, run with:

```bash
export PYTHONDONTWRITEBYTECODE=1
```

## 2) Integration tests (deterministic, but may need localhost sockets)

Integration tests try to start the hub and an `echo` agent.

If your environment cannot bind localhost sockets, these tests will be skipped.

## 3) System runs (non-deterministic, artifact-based)

System runs are for real CLIs (Gemini/Claude/Kiro/Codex/etc). They produce artifacts under `reports/e2e/...` rather than being strict CI gates.

Example:

```bash
python3 scripts/run_system_tests.py --backend gemini --prompt "Say hello"
```
