# CLI version lock (practical)

Mittelö is designed to plug in multiple external CLIs (Gemini / Claude Code / Kiro / Codex / Kimi / etc). Most “swarm instability” comes from drift in:
- CLI versions and flags
- default model fallbacks
- interactive behavior (TUI prompts, first-run auth, trust dialogs)

This doc is the single place to record “known-good” versions and how to pin them.

## Principles

- **Pin by command behavior**, not by vibes: record the exact CLI invocation that works.
- Prefer **non-interactive** modes for all backends.
- Keep wrappers stable: `backends/<name>/run` should not require manual “press enter”.

## Runtime model selection (env)

The repo uses env vars so you can force models without editing code:

- `MITTELO_GEMINI_MODEL` (Gemini CLI `--model`)
- `MITTELO_CLAUDE_MODEL` (Claude Code `--model`)
- `MITTELO_KIRO_MODEL` (kiro-cli `--model`)
- `MITTELO_CODEX_MODEL` (codex `--model`)
- `MITTELO_KIMI_MODEL` (kimi `--model`, supports `kimi2-*` models)
- `MITTELO_MLX_MODEL` (mlx-lm `--model`)
- `MITTELO_KIRO_TRUST_ALL_TOOLS=1` to enable `--trust-all-tools` (default is trust none)

## Verified Solo Runs (Dec 2025)

The following commands have been verified to work non-interactively on this machine.

### Gemini
```bash
export MITTELO_GEMINI_MODEL="gemini-2.0-flash-exp"
python3 -m mittelo agent --backend gemini --once
```

### Claude Code
```bash
export MITTELO_CLAUDE_MODEL="claude-3-5-sonnet-20241022"
python3 -m mittelo agent --backend claude_code --once
```

### Kiro CLI
```bash
export MITTELO_KIRO_MODEL="claude-haiku-4.5"
python3 -m mittelo agent --backend kiro --once
```

### Codex CLI
```bash
export MITTELO_CODEX_MODEL="gpt-4o"
python3 -m mittelo agent --backend codex --once
```

### Kimi CLI
```bash
export MITTELO_KIMI_MODEL="kimi-for-coding"
python3 -m mittelo agent --backend kimi --once
```

## Known CLIs (this machine, Dec 2025)

These were observed in this repo/workspace:
- `codex` (`codex-cli 0.72.0`)
- `claude` (`Claude Code 2.0.69`)
- `kiro-cli` (`kiro-cli 1.22.0`)
- `kimi` (`kimi 0.63`)
- Gemini CLI often via `npx -y @google/gemini-cli@nightly` (no stable pin yet)

## Pinning suggestions

- **Codex CLI**
  - Pin via Homebrew and record `codex --version`.
  - Prefer stdin prompts (`codex exec ... -`) to avoid argv length limits.
  - Note: for `codex exec`, prefer `--full-auto` (and `--sandbox ...`) rather than relying on top-level approval flags.
- **Claude Code**
  - Use `--print --tools ""` for non-interactive output.
  - Record a “known good” `claude --version` and any required env configuration (base URL tokens).
- **Gemini**
  - Prefer a pinned npm package version once you find a stable one:
    - `npx -y @google/gemini-cli@<version> ...`
  - Avoid relying on default model fallback (set `MITTELO_GEMINI_MODEL`).
- **Kiro**
  - Use `chat --no-interactive --wrap never` and explicitly set trust mode.
  - Record `kiro-cli settings` that affect timeouts/models.
- **Kimi**
  - First-run config can be interactive; document the exact steps once stabilized.

## “Lockfile” idea (future)

When you want stricter reproducibility, add a machine-readable file (example):

`docs/cli_lock.json`

```json
{
  "codex": {"version": "0.72.0", "install": "brew"},
  "claude": {"version": "2.0.69", "install": "npm -g"},
  "kiro-cli": {"version": "1.22.0", "install": "local"},
  "kimi": {"version": "0.63", "install": "uv tool"}
}
```

Then a verifier can check versions and print a clear “your environment drifted” report.
