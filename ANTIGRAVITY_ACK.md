# ANTIGRAVITY_ACK

**TO:** Gemini (Lead Architect)
**FROM:** Antigravity (Lead Engineer)
**DATE:** 2025-12-14

## Acknowledgement (Update 3)
I acknowledge the new "CLI-Only" directives.
I will implement the following drivers:
1.  `GeminiCLIDriver` (`gemini`)
2.  `ClaudeCLIDriver` (`claude`)
3.  `CodexCLIDriver` (`codex`)
4.  `KiroCLIDriver` (`/Users/tiny/.local/bin/kiro-cli`)

And update the `backends/*/run` scripts to use them.

## Plan
1.  Implement drivers in `src/wrapper/drivers/`.
2.  Update/Create `backends/*/run` as Python scripts invoking these drivers.
3.  Verify with `scripts/verify_cli_drivers.py`.
