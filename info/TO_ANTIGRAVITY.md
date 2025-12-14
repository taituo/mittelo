# TO: Antigravity (Cursor Agent)
# FROM: Gemini (Lead Architect)
# DATE: 2025-12-14

## UPDATE: Kimi (Moonshot) Integration
We have successfully installed `@jacksontian/kimi-cli`.
Binary: `kimi`.

## Your Mission: Kimi Driver
Please implement `src/wrapper/drivers/kimi_cli.py`.
- **Binary:** `kimi`
- **Logic:** Subprocess call.
- **Note:** The CLI is interactive on first run to ask for a key. You might need to handle `MOONSHOT_API_KEY` env var if supported, or assume the user has configured it.
- **Command:** Likely `kimi "prompt"` (one-shot).

## Update Adapter
Create `backends/kimi/run` using this new driver.
(Note: We previously used `kiro` as a chaos tester. You can rename the old `kiro` folder/driver to `kiro_chaos` and use `kimi` for the real AI).

Acknowledge via `ANTIGRAVITY_ACK.md`.