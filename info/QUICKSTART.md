# Quickstart

Run the smoke test:

```bash
python3 scripts/smoke_test.py
```

Manual run (3 terminals):

Terminal A:

```bash
python3 -m mittelo hub --db mittelo.db --host 127.0.0.1 --port 8765
```

Terminal B:

```bash
python3 -m mittelo agent --host 127.0.0.1 --port 8765 --backend echo
```

Terminal C:

```bash
python3 -m mittelo enqueue --host 127.0.0.1 --port 8765 --jsonl examples/hello.jsonl
python3 -m mittelo status --host 127.0.0.1 --port 8765
```

Run a use-case pack:

```bash
python3 -m mittelo enqueue --host 127.0.0.1 --port 8765 --jsonl examples/use_cases/doc_pack.jsonl
```
