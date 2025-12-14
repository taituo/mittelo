# Doing Mittelö Now: The Man-in-the-Middle Phase

## 1. The Concept
We are currently in the **Man-in-the-Middle (MITM)** phase of development.
- **Who is in the middle?** The Human Developer, the Prime Agent (Gemini), and Antigravity (Dev Assistant).
- **What are we doing?** We are manually wiring the "nervous system" of the swarm.
- **Why?** Before Mittelö can "develop itself" (Recursive Self-Improvement), the agents must first have reliable, verified inputs and outputs.

## 2. Integration Strategy (The "Wiring")
Right now, our job is to replace the "mock" wrappers with real "sensory" wrappers.

### Current Flow:
`Hub -> [stdin] -> Mock Script (Sleep/Print) -> [stdout] -> Hub`

### Target Flow (Integration):
`Hub -> [stdin] -> API Client (OpenAI/Gemini/Ollama) -> [stdout] -> Hub`

**Crucial MITM Task:**
We must verify that the **text** coming out of the API is clean, structured, and actionable. We are the filter ensuring no garbage enters the system loop.

## 3. The Path to Self-Improvement (The "Singularity" Step)
Once the integration is stable, we enable **Tool Use**.

1.  **Read Code:** Agents get a tool to read `mittelo/*.py`.
2.  **Write Code:** Agents get a tool to write/patch files.
3.  **Test Code:** Agents get a tool to run `pytest`.

**When this happens:**
- You (Human) step out of the middle.
- You enqueue a task: *"Refactor hub.py to use PostgreSQL."*
- The Swarm reads the code, plans the change, edits the file, runs the test, and reports back.

## 4. Immediate Protocol for Agents (Codex/Kiro)
- **Codex:** Your job is to verify structural integrity. Watch the `stats`. If `failed` count rises, alert the Prime Agent.
- **Kiro:** You are the stress tester. Run loops. Break things. If you crash, we learn.

## 5. Summary
We are building the ladder. Once the ladder is built, we climb up and kick it away. The swarm takes over.
