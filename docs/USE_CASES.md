# Use cases

Mittelö is meant to be used either as:

- a **boilerplate**: fork/remix and add your own backends + missions
- a **toolkit**: keep the protocol stable and plug in any CLI/LLM as a backend wrapper

## Patterns that scale well

- **Queue + lease**: multiple agents pick tasks, you can mix models/tools per backend.
- **Small prompts, many tasks**: split work into many independent tasks instead of one giant prompt.
- **Result aggregation**: write a “collector” script that polls `list` and merges results.

## Example packs

Run any JSONL pack like this:

```bash
python3 -m mittelo enqueue --jsonl examples/hello.jsonl --host 127.0.0.1 --port 8765
```

See `examples/use_cases/` for more:
- `examples/use_cases/doc_pack.jsonl`
- `examples/use_cases/code_review_pack.jsonl`
- `examples/use_cases/repo_audit_pack.jsonl`
