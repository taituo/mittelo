# Backends (Gemini / Claude Code / Kiro / Codex / local OSS LLMs)

Mittelö agents can use any “backend” that turns a **prompt → stdout**.

Preferred way: `backends/<name>/run` wrappers (remix-friendly).

Backend contract:
- read prompt from `stdin`
- print final answer to `stdout`
- avoid interactive UI/banners if possible
- exit `0` on success; non-zero on failure (write details to `stderr`)

Out of the box:
- `echo`: returns `echo:<prompt>`
- `shell`: runs an external command and sends the prompt to stdin

## Shell backend examples

### Kiro CLI (example)

```bash
python3 -m mittelo agent --backend shell --shell-cmd "kiro-cli chat --no-interactive --wrap never"
```

If Kiro times out immediately, check `kiro-cli` settings (example):

```bash
kiro-cli settings api.timeout 300000
```

### Gemini CLI (example)

```bash
python3 -m mittelo agent --backend shell --shell-cmd "npx -y @google/gemini-cli@nightly chat"
```

### Claude Code (example)

Wrap whatever “Claude Code” command you use behind a backend. Example with `shell`:

```bash
python3 -m mittelo agent --backend shell --shell-cmd "claude --print"
```

### Local Ollama (example)

```bash
python3 -m mittelo agent --backend shell --shell-cmd "ollama run llama3.1"
```

## Remix-friendly backend convention

If you want to keep backends as folders (easy to fork/remix), use:

```
backends/<name>/run
```

Where `run` reads the prompt from stdin and prints the result to stdout.

Mittelö will auto-detect these wrappers when you run:

```bash
python3 -m mittelo agent --backend <name>
```

You can also point at another directory with `MITTELO_BACKENDS_DIR=/path/to/backends`.
