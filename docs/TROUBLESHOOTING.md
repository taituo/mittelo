# Troubleshooting

## Localhost bind fails (EPERM / Operation not permitted)

Some sandboxed environments block listening sockets. Symptoms include:
- Hub cannot start (bind fails)
- Integration tests are skipped
- `scripts/run_pair_smoke.py` records `SKIPPED`

What to do:
- Run unit tests: `pytest` (no sockets)
- Use backend-only artifacts: `python3 scripts/run_system_tests.py --backend <name> --prompt "hello"`
- If you control the environment, allow localhost bind on ephemeral ports (`127.0.0.1:0`).

## Python bytecode cache PermissionError (macOS caches)

Some environments block writes under `~/Library/Caches/com.apple.python`, causing `PermissionError` during compilation.

What to do:
- Prefer the project virtualenv: `.venv/bin/python ...`
- Or disable bytecode: `export PYTHONDONTWRITEBYTECODE=1`

