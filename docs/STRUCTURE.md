# Repo structure

Goals:
- Keep the core protocol stable and small.
- Make backends easy to remix as folders.
- Keep “missions” as simple, shareable examples.

Directories:

- `mittelo/`: Python “SwarmKit” core (hub/client/agent).
- `docs/`: protocol + usage docs (start here if you want to reimplement clients in another language).
- `backends/`: backend wrappers (`backends/<name>/run`) to plug in any CLI/LLM.
- `examples/`: shareable task sets (JSONL prompts) and demo flows.
- `scripts/`: smoke tests and local utilities.
- `go/`: optional Go client/CLI skeleton (minimal port).
