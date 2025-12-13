# Contributing

Mittelö is designed to be edited by many different “agent CLIs” (Gemini, Claude Code, Kiro, Codex, local OSS LLMs, etc). The main rule is: keep the **protocol stable** and keep additions **remix-friendly**.

## Add a backend (preferred)

Create a wrapper at:

`backends/<name>/run`

Contract:
- Read the full prompt from `stdin`
- Write the final answer to `stdout`
- Avoid banners/progress UI if possible
- Exit `0` on success; non‑zero on failure (write details to `stderr`)

Then run it:

```bash
python3 -m mittelo agent --backend <name>
```

If your backends live elsewhere:

```bash
export MITTELO_BACKENDS_DIR=/path/to/backends
python3 -m mittelo agent --backend <name>
```

## Add a use-case pack

Put shareable prompts in JSONL:

`examples/use_cases/<pack>.jsonl`

Each line is:

```json
{"prompt":"..."}
```

Add a short README next to it if the pack needs extra context:

`examples/use_cases/<pack>.md`

## Add another-language client

Keep the reference in `docs/PROTOCOL.md`. A client only needs:
- Open TCP connection
- Send `{id, method, params}\n`
- Read one response line

If you add a new port (Go/Rust/etc), keep it minimal and document it in `docs/`.
