# Backends (Gemini / Claude Code / Kiro / Codex / Kimi)

Mittelö agents can use any "backend" that turns a **prompt → stdout**.

## verified Solo Run Commands

Use these commands to verify backends in isolation (no hub required).

### Gemini
```bash
export MITTELO_GEMINI_MODEL="gemini-2.0-flash-exp"
python3 -m mittelo agent --backend gemini --once
# Or raw driver:
# gemini "hello" --model gemini-2.0-flash-exp
```

### Claude Code
```bash
export MITTELO_CLAUDE_MODEL="claude-3-5-sonnet-20241022"
python3 -m mittelo agent --backend claude_code --once
# Raw:
# claude "hello" --print --tools "" --model ...
```

### Kiro CLI
```bash
export MITTELO_KIRO_MODEL="haiku"
python3 -m mittelo agent --backend kiro --once
# Raw:
# kiro-cli chat --no-interactive --model haiku "hello"
```

### Codex CLI
```bash
export MITTELO_CODEX_MODEL="gpt-4o"
python3 -m mittelo agent --backend codex --once
# Raw:
# codex --ask-for-approval never --sandbox workspace-write exec - < input.txt
```

### Kimi CLI (example)

```bash
# Requires MITTELO_KIMI_MODEL env var or defaults to kimi-for-coding
# For Kimi2 models, set MITTELO_KIMI_MODEL=kimi2-preview (or similar)
python3 -m mittelo agent --backend kimi --once
# Raw:
# kimi --model kimi-for-coding --print --query "hello"
```

## Backend Contract
- Read prompt from `stdin` (or argument if safe).
- Print final answer to `stdout`.
- Exit `0` on success.
- Write errors to `stderr`.
