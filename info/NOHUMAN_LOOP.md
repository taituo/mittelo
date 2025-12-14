# NOHUMAN_LOOP: The Path to Autonomy

## Vision
The ultimate goal of Mittelö is to reach the **No-Human Loop**: a state where the swarm can iterate, refactor, and extend its own codebase without direct human intervention in the edit-test-commit cycle.

**Current State:** Human-in-the-Loop (MITM).
**Target State:** Recursive Self-Improvement.

## The Bootstrap Paradox
To build Mittelö with Mittelö, the system must be robust enough to not break itself during an update. A broken swarm cannot fix the swarm.

## Roadmap to NOHUMAN

### Phase 1: The Observer (Current)
- Swarm analyzes code and suggests changes.
- Human reviews and applies changes.
- **Risk:** Zero.
- **Telemetry:** Used to train/prompt the agents better.

### Phase 2: The Apprentice (Tool Use)
- Agents are given tools: `read_file`, `write_file` (sandboxed), `run_test`.
- Swarm creates a branch -> applies fix -> runs tests.
- Human only reviews the Pull Request (or merge proposal).
- **Risk:** Low (git revert exists).

### Phase 3: The Engineer (Autonomous CI/CD)
- Swarm detects an issue (via telemetry or self-audit).
- Swarm spins up a ephemeral environment (Docker).
- Swarm fixes the issue, verify with new tests.
- Swarm commits to `main` if confidence > 99%.
- **Risk:** Medium. Requires "Immune System" (Agent that reverts bad commits).

## Technical Requirements for NOHUMAN

1.  **Reliable Backends:** "Mock" agents cannot write code. We need high-IQ models (Claude 3.5, GPT-4, or specialized local CodeLlamas) connected via CLI wrappers.
2.  **Robust Testing Suite:** A change is only valid if `pytest` passes. We need 90%+ coverage before letting the swarm loose.
3.  **Formal Protocol:**
    - `Task: "Fix bug X"`
    - `Agent A (Plan): "Locate bug in file Y."`
    - `Agent B (Act): "Edit file Y."`
    - `Agent C (Verify): "Run test Z."`
4.  **Rollback Mechanism:** If the swarm bricks `hub.py`, an external watchdog (simple script) must restore the last known good state.

## The "Telemetry Loop"
We need to capture not just "result: done", but the **thinking process**.
- Store `stdout` logs of agents.
- Analyze which prompts led to successful code fixes.
- Auto-update `docs/AGENT_PROMPTS.md` with better instructions.

## Danger Zone
- **Infinite Loops:** Agent A creates a bug, Agent B fixes it (badly), Agent A reverts it...
- **Resource Exhaustion:** Spawning infinite sub-agents.

**Constraint:** The "Budget" module. Swarm has a limited token/compute budget per iteration.
