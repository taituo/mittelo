# Feature Bundles & User Stories

This document tracks the "Feature Bundles" delivered by the Gemini track.

## Bundle B: Backend Reliability

**Goal:** Backends are boring, predictable, and non-interactive.

### US-B1: Non-interactive Execution
**As a** system operator  
**I want** backends to run without user input (stdin only)  
**So that** the swarm can run autonomously.

**Acceptance Criteria:**
- [x] `gemini` driver uses `MITTELO_GEMINI_MODEL` and no interactive flags.
- [x] `claude` driver uses `--print --tools ""`.
- [x] `kiro` driver uses `--no-interactive`.
- [x] `codex` driver uses `--ask-for-approval never`.
- [x] `kimi` driver uses `--print`.

### US-B2: Clean Output
**As a** hub parser  
**I want** backend stdout to contain *only* the model response  
**So that** I don't have to strip ANSI codes or banners.

**Acceptance Criteria:**
- [x] Drivers strip known banners (or use flags to suppress them).
- [x] `verify_cli_drivers.py` confirms output is "clean enough".

## Bundle D: Dashboard Portability

**Goal:** Dashboard is a robust client.

### US-D1: Robust Connection
**As a** user  
**I want** the dashboard to show "OFFLINE" instead of crashing  
**So that** I know when the hub is down.

**Acceptance Criteria:**
- [x] `dashboard.py` catches connection exceptions.
- [x] UI displays red "OFFLINE" status on error.
