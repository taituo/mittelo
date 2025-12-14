# Backends (Gemini / Claude Code / Kiro / Codex / Kimi)

Mittelö agents can use any "backend" that turns a **prompt → stdout**.

## verified Solo Run Commands

Use these commands to verify backends in isolation (no hub required).

Tip: run a quick prereq check first:
```bash
python3 -m mittelo backend-check --backend <name>
```

### Gemini
**Prereqs:** `gemini` (or `npx`) available; auth via `GEMINI_API_KEY` or `~/.gemini/settings.json`.
```bash
export MITTELO_GEMINI_MODEL="gemini-2.0-flash-exp"
python3 -m mittelo agent --backend gemini --once
# Or raw driver:
# gemini "hello" --model gemini-2.0-flash-exp
```

### Claude Code
**Prereqs:** `claude` available; logged in (Claude may prompt `/login` on first use).
```bash
export MITTELO_CLAUDE_MODEL="claude-3-5-sonnet-20241022"
python3 -m mittelo agent --backend claude_code --once
# Raw:
# claude "hello" --print --tools "" --model ...
```

### GLM (via Claude Code endpoints)

If your `claude` CLI is configured (via env exports) to talk to GLM-compatible endpoints, you can use the `glm` backend alias:

```bash
# Configure Claude Code to use your GLM endpoints (env exports, per your setup)
python3 -m mittelo agent --backend glm --once
```

### Kiro CLI
**Prereqs:** `kiro-cli` available; may require device-flow login (`kiro-cli login --use-device-flow`).
```bash
export MITTELO_KIRO_MODEL="haiku"
python3 -m mittelo agent --backend kiro --once
# Raw:
# kiro-cli chat --no-interactive --model haiku "hello"
```

### Codex CLI
**Prereqs:** `codex` available; authenticated.
```bash
export MITTELO_CODEX_MODEL="gpt-4o"
python3 -m mittelo agent --backend codex --once
# Raw:
# codex --ask-for-approval never --sandbox workspace-write exec - < input.txt
```

### MLX (Apple Silicon)
**Prereqs:** `mlx-lm` installed in the same Python env used to run the agent.
```bash
# Requires mlx-lm installed
export MITTELO_MLX_MODEL="mlx-community/Qwen2.5-1.5B-Instruct-4bit"
python3 -m mittelo agent --backend mlx --once
```

### Kimi CLI (example)

**Prereqs:** `kimi` available; may require API key/model config (varies by install).
```bash
export MITTELO_KIMI_MODEL="kimi-for-coding"
# For Kimi2 models, set MITTELO_KIMI_MODEL=kimi2-... (per your account/CLI)
python3 -m mittelo agent --backend kimi --once
# Raw:
# kimi --model kimi-for-coding --print --query "hello"
```

## Backend Contract
- Read prompt from `stdin` (or argument if safe).
- Print final answer to `stdout`.
- Exit `0` on success.
- Write errors to `stderr`.
