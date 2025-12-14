# Mittelö Project TODO

## 0. Stability first (Priority: High)
- [ ] **Backend determinism:** Verify each backend in *solo mode* before mixed swarms (US-B1/B2/B3).
- [ ] **Version lock:** Record known-good CLI versions + non-interactive flags in `docs/VERSION_LOCK.md`.
- [ ] **Protocol drift:** Keep `docs/PROTOCOL.md` aligned with hub methods (`retry_failed` etc).
- [ ] **System runs as artifacts:** Add a system-test runner that writes `reports/e2e/*` instead of flaky pass/fail.

## 1. Cloud Readiness (Priority: Medium)
- [ ] **Dockerization:** Create `Dockerfile` for Hub and Agent images.
- [ ] **Orchestration:** Create `docker-compose.yml` for easy local swarm spinning.
- [ ] **Configuration:** Move hardcoded defaults (ports, hosts) to `.env` file support.
- [ ] **Storage:** Ensure `mittelo.db` location is configurable via env var (for volume mounting).

## 2. Backend Implementations (Priority: High)
- [ ] **Gemini Backend:** Implement `backends/gemini/run` using Google Generative AI SDK.
- [ ] **Codex/OpenAI Backend:** Implement `backends/codex/run` using OpenAI API.
- [ ] **Ollama Backend:** Implement `backends/ollama/run` for local models (Llama 2/3).
- [ ] **Kiro Backend:** Connect `backends/kiro/run` to actual Kiro CLI (if applicable) or robust API.

## 3. Protocol & Capabilities
- [ ] **Tool Use / Function Calling:** Extend protocol to support agents requesting actions (not just text response).
- [ ] **Structured Output:** Enforce JSON schema for agent responses when needed.
- [ ] **Streaming:** Support streaming responses (stdout chunks) back to Hub (currently full buffer).

## 4. CLI & UX Improvements
- [ ] **Dashboard:** Create a simple TUI (Text User Interface) command (e.g., `mittelo dashboard`) using `rich` or `curses`.
- [ ] **Task Management:** Add `cancel` / `delete` commands for tasks.
- [ ] **Logs:** improving logging visibility from agents to hub (currently agents log to stderr, maybe stream to hub?).

## 5. Testing & Quality
- [ ] **Unit Tests:** Add `pytest` suite for `mittelo/` package.
- [ ] **CI/CD:** Setup GitHub Actions for linting (ruff/mypy) and testing.
- [ ] **Load Testing:** Formalize `scripts/stress_test.py` into a repeatable benchmark suite.

## 6. Documentation
- [ ] **Tutorial:** "Zero to Swarm" guide using Docker.
- [ ] **API Reference:** Auto-generated docs for `JsonlClient`.
- [ ] **Feature bundles:** Keep stories + docs + tests together (`docs/FEATURE_BUNDLES.md`).
