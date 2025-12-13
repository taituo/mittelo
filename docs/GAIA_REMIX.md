# “GAIA remix” composition idea

The simplest way to “compose toolchains” is to treat Mittelö as the **common task bus**:

- One hub (queue + DB)
- Many agents (different backends)
- Extra tools as “sidecars” (linters, repo scanners, formatters) wrapped as backends too

## Practical recipe

1. Keep Mittelö protocol stable (`docs/PROTOCOL.md`).
2. Put each tool/LLM CLI behind a wrapper:
   - `backends/gemini/run`
   - `backends/claude_code/run`
   - `backends/kiro/run`
   - `backends/ollama/run`
3. Create “mission packs” as JSONL under `examples/use_cases/`.
4. Run a small swarm with mixed agents:

```bash
python3 -m mittelo swarm --host 127.0.0.1 --port 8765 --agent gemini=2 --agent kiro=1
```

Now any upstream remix (“gaia-remix”) can:
- add/replace backends without touching core
- add new mission packs without touching backends
- reimplement clients in another language without touching either
