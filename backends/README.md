# Backends

Each backend is a small wrapper that turns:

`stdin prompt → stdout answer`

Put wrappers here:

`backends/<name>/run`

Then run:

```bash
python3 -m mittelo agent --backend <name>
```

This makes it easy for different CLIs (Gemini / Claude Code / Kiro / local OSS LLMs) to edit only their own folder without touching the hub protocol.
