# Backend template

Create:

- `backends/<name>/run` (required)

Contract:
- reads prompt from stdin
- prints answer to stdout
- exit 0 on success, non-zero on failure

Environment variables you may use:
- `MITTELO_TASK_ID`
- `MITTELO_WORKER_ID`

Tip: keep wrappers non-interactive if the CLI supports it.
