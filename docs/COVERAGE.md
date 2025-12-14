# Test coverage

Mittelö’s CI gate should stay deterministic. Coverage is about measuring **core code paths** (hub/protocol/storage/client), not model output quality.

## Prereqs

Install dev deps (includes `pytest-cov`):

```bash
uv venv
uv pip install -e '.[dev]'
```

## Run coverage (recommended)

```bash
pytest \
  --cov=orchestrator \
  --cov=wrapper \
  --cov=utils \
  --cov-report=term-missing:skip-covered
```

Notes:
- Integration tests may auto-skip if localhost bind is blocked; coverage still works (but won’t cover socket paths).
- For a deterministic-only coverage run, limit to unit tests:

```bash
pytest tests/unit \
  --cov=orchestrator \
  --cov=wrapper \
  --cov=utils \
  --cov-report=term-missing:skip-covered
```

## HTML report (optional)

```bash
pytest \
  --cov=orchestrator \
  --cov=wrapper \
  --cov=utils \
  --cov-report=html:reports/coverage/html
```

`reports/coverage/` is ignored by git.

## What to prioritize

- `src/orchestrator/*` (task lifecycle, leasing, retry, list semantics, REST adapter)
- `src/wrapper/client.py` (protocol correctness)
- `src/wrapper/backends.py` (backend resolution + error paths)
