# Logbook 00001: CLI Session Wrappers

**Date:** 2025-12-14
**Driver:** Antigravity

## Scope
The goal for today is to enable Mittelö agents to interact with persistent CLI sessions (specifically `tmux`). This allows agents to "live" in a shell environment, execute commands, and see the output, rather than being stateless processes.

## Tasks
1.  **Create Logbook:** Establish this document.
2.  **Design Tmux Wrapper:**
    - Create a backend script `backends/tmux/run`.
    - Implement logic to:
        - Identify target tmux session/pane.
        - Send text/commands to the pane.
        - Capture and return the pane's output.
3.  **Integration:**
    - Ensure `mittelo/agent.py` can utilize this new backend.
4.  **Verification:**
    - Test the wrapper by having an agent control a dummy tmux session.

## Technical Notes
- We will use the existing `backends/` directory structure.
- The wrapper will be a Python script acting as a bridge between the Mittelö protocol (stdin/stdout) and `tmux` commands.
