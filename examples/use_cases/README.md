# Use-case packs

These are ready-to-run prompt packs (JSONL).

Run:

```bash
python3 -m mittelo enqueue --host 127.0.0.1 --port 8765 --jsonl examples/use_cases/doc_pack.jsonl
python3 -m mittelo status --host 127.0.0.1 --port 8765
```

Packs:
- `doc_pack.jsonl`: documentation drafting tasks
- `code_review_pack.jsonl`: checklists and risk mitigation prompts
- `repo_audit_pack.jsonl`: repo audit + CI planning prompts
