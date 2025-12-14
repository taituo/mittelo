# GEMINI_PLAN (Backends + Dashboard)

Date: 2025-12-14  
Owner: Gemini agent  
Scope: Backends (`backends/*`, `src/wrapper/drivers/*`) + UX (`src/utils/dashboard.py`) + integration docs  
Mode: No swarm orchestration (verify one backend at a time).

## Goal

Make every backend usable in real life:
- non-interactive runs
- pinned models (no surprise “fallback”)
- clean stdout / clear stderr
- predictable failure modes

And make the dashboard reliable enough to trust (terminal first, web later via adapters).

## Workstreams

### A) Backend reliability (solo-first)

For each backend (`gemini`, `claude_code`, `kiro`, `codex`, `kimi`, `tmux`):

1. **Define a golden smoke prompt**
   - short, safe, comparable across models/tools
   - keep it stable (so runs are comparable over time)

2. **Define required env vars**
   - `MITTELO_GEMINI_MODEL`
   - `MITTELO_CLAUDE_MODEL`
   - `MITTELO_KIRO_MODEL`
   - `MITTELO_CODEX_MODEL`
   - `MITTELO_KIMI_MODEL`
   - `MITTELO_KIRO_TRUST_ALL_TOOLS` (default is trust none)

3. **Verify via wrapper**
   - run through `backends/<name>/run` (stdin → stdout contract)
   - do not rely on interactive sessions or per-machine hidden state

4. **Failure classification**
   - normalize common errors so the hub stores something actionable:
     - binary missing
     - auth missing / token missing
     - interactive prompt detected
     - unsupported model/account (Codex)
     - timeout / rate limit

5. **Record “known good”**
   - update `docs/VERSION_LOCK.md` with the exact CLI version + the exact non-interactive invocation behavior

### B) Dashboard (terminal now, universal later)

1. **Reliability**
   - show ONLINE/OFFLINE and the last error message
   - use short timeouts and avoid freezing the UI
   - only poll hub (`stats` + `list`)—never talk to model CLIs

2. **Portability**
   - keep dashboard as a client; web/game engine UIs can consume the same hub API:
     - TCP JSONL (core)
     - REST adapter (optional)

### C) Docs for operators

1. Update `docs/BACKENDS.md` with real flags (based on actual `--help` output).
2. Add copy/paste “solo run” commands per backend.
3. Keep drift low: every wrapper/driver change that affects usage must update docs.

## Deliverables

- Each backend has:
  - a golden smoke prompt
  - a “solo run” recipe
  - documented env vars and expected output shape
- `docs/VERSION_LOCK.md` reflects current known-good versions and model pins
- Dashboard is usable even when the hub is down (clear OFFLINE state)

## Non-goals (for now)

- Mixed swarms (only after solo stability)
- Changing core protocol / hub internals (coordinate with Codex first)

