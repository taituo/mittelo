# Examples

Run the hub + one agent, then enqueue a pack:

```bash
python3 -m mittelo hub --db mittelo.db --host 127.0.0.1 --port 8765
python3 -m mittelo agent --host 127.0.0.1 --port 8765 --backend echo
python3 -m mittelo enqueue --host 127.0.0.1 --port 8765 --jsonl examples/hello.jsonl
python3 -m mittelo status --host 127.0.0.1 --port 8765
```

Use-case packs live in `examples/use_cases/`.
