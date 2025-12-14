# Kiro CLI Notes 00001

**Date:** 2025-12-14
**Agent:** Kiro (AWS AI Assistant)
**Context:** Mittelö SwarmKit Development

## Observations

### Codebase Structure
- **Hub:** TCP server (JSONL RPC), SQLite task queue, thread-safe TaskStore
- **Agent:** Leases tasks, runs backend, acks results
- **Backend:** stdin → stdout process (echo, shell, or custom)
- **Protocol:** Newline-delimited JSON, methods: enqueue, lease, ack, list, stats, retry_failed, shutdown

### Today's Development (2025-12-14)
1. **Tmux Backend** (`backends/tmux/run`): Bridge between Mittelö and persistent shell sessions
   - Sends commands to tmux pane
   - Captures output via `tmux capture-pane`
   - Assumes session exists or creates it
   - Dirty timing: 0.5s sleep (needs refinement)

2. **Dev Monitor** (`scripts/dev_monitor.py`): Observability tool
   - Lists active tmux sessions
   - Tracks running mittelo processes
   - Basic telemetry for swarm health

3. **Architecture Documents:**
   - `NOHUMAN_LOOP.md`: Vision for autonomous self-improvement (Phase 1→3)
   - `HLD_finnish.md`: Detailed LLD spec (v1.4) with asyncio, mmap, hybrid cloud
   - `doing_mittelo_now.md`: Current MITM phase (human-in-the-loop)

### Key Insights
- **Bootstrap Problem:** System must be robust enough to not break itself during updates
- **Mmap Strategy:** 40 agents can share single 5GB model via OS page cache (17GB total RAM)
- **Hybrid Cloud:** Entry-tier VPS (4vCPU/16GB) can run ~25 agents at <1€/agent/month
- **Telemetry Loop:** Capture agent thinking process, not just results

### Current Bottlenecks
1. **Tmux Timing:** 0.5s sleep is arbitrary; needs prompt detection or better signaling
2. **Mock Backends:** Kiro backend simulates 20% failure rate (for testing)
3. **No Tool Use Yet:** Agents cannot read/write files or run tests (Phase 2 requirement)
4. **Streaming:** Protocol doesn't support streaming responses (full buffer only)

### Next Steps (Inferred)
1. Refine tmux backend: Replace sleep with prompt detection or event-based signaling
2. Implement real backends: Gemini, Codex, Ollama (currently mocked or CLI wrappers)
3. Add tool use: `read_file`, `write_file`, `run_test` (sandboxed)
4. Implement CI/CD: GitHub Actions for linting, testing, load testing
5. Docker readiness: Compose file, env var support, volume mounting

### Technical Debt
- `backends/kiro/run`: Simulates failures; needs real Kiro CLI integration
- `backends/gemini/run`, `backends/codex/run`: Placeholder scripts
- No pytest suite yet
- No dashboard/TUI for monitoring

### Collaboration Notes
- 3 developers in this repo (careful, minimal changes)
- Gemini is lead; Kiro is stress tester; Codex verifies structure
- Human is MITM filter (ensures clean, actionable outputs)

## Questions for Next Session
1. Should tmux backend use event-based signaling (e.g., inotify) instead of sleep?
2. What is the priority: real backend implementations vs. tool use infrastructure?
3. Should we add a "Budget" module to prevent infinite loops in autonomous phase?
4. How to handle agent hallucinations (repeated tokens/lines)?

## Code Snippets to Remember
- **Lease Logic:** `TaskStore.lease()` marks tasks as "leased" with timeout, allows re-lease if expired
- **Backend Resolution:** `resolve_backend_argv()` searches `MITTELO_BACKENDS_DIR`, cwd, and package dir
- **Agent Loop:** `run_agent()` leases, runs backend, acks; `--once` flag for single task
- **Asyncio Pattern:** `asyncio.gather(network_loop, driver.start())` for concurrent I/O and subprocess

## Reminders
- Always use `--once` flag when testing single tasks
- Check `mittelo.db-wal` for active transactions
- Monitor `pgrep -fl "python3.*mittelo"` for stuck processes
- Use `python3 -m mittelo status` to inspect task queue
