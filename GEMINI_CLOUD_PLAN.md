# GEMINI_CLOUD_PLAN (Cloud Readiness)

Date: 2025-12-14
Owner: Gemini
Goal: Containerize Mittelö for easy deployment and testing.

## Scope
- `Dockerfile`: Unified image for Hub and Agents.
- `docker-compose.yml`: Orchestration for a local swarm (Hub + 2 Agents).
- `.dockerignore`: Clean builds.

## Steps

1.  **Create `Dockerfile`**
    - Base: `python:3.11-slim` (or similar)
    - Install dependencies (`uv` or `pip`)
    - Copy source code
    - Entrypoint script to choose between `hub` or `agent` mode.

2.  **Create `docker-compose.yml`**
    - Service `hub`: Runs `python -m mittelo hub`
    - Service `agent-1`: Runs `python -m mittelo agent --backend echo`
    - Service `agent-2`: Runs `python -m mittelo agent --backend echo`
    - Network: Internal bridge.

3.  **Verify**
    - `docker-compose up`
    - Check logs to see agents connecting to hub.
    - Run `python -m mittelo client enqueue "hello docker"` from host (mapping port 12345).

## Non-Goals
- Kubernetes (too complex for now).
- Cloud deployment (AWS/GCP) - just local Docker for now.
