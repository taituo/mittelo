# Dead code & “unfinished” code map

This is a pragmatic inventory of code that is currently **unused at runtime**, **archived**, or **unfinished**, plus guidance on whether it should be revived or removed.

## How to audit (repeatable)

1) Fast grep signals:

```bash
rg -n "import .*<name>|from .*<name>" src
```

2) Optional tooling (best-effort, may include false positives):

```bash
python -m pip install vulture
vulture src mittelo scripts --min-confidence 80
```

## Findings (current)

### `src/utils/rate_limiter.py`

- **Status:** likely unused (no imports found in `src/`).
- **Can we use it?** yes.
- **Suggested use:** rate-limit dashboard polling and/or backend calls (if wrappers start doing retries/backoff).
- **Action:** keep for now; if unused after dashboard stabilization, consider deleting or moving to `docs/` as reference.

### `backends/archive/*`

- **Status:** archived backends (intentionally not in the default set).
- **Can we use it?** yes, as reference or for resurrecting older backends.
- **Action:** keep under `backends/archive/` to avoid confusion in main backends list.

### Developer scripts (`scripts/verify_*.py`, `scripts/debug_codex.py`, `scripts/img2ansi.py`)

- **Status:** “tooling code” (not used by hub/agent runtime).
- **Can we use it?** yes; these are intentionally runnable utilities.
- **Action:** keep, but document the intended audience (human/dev) vs CI.

## What is NOT considered dead code

- Drivers under `src/wrapper/drivers/*` that are invoked by `backends/<name>/run`.
- Docs and example JSONL under `docs/` and `examples/` (they exist to be remixed, not imported).
