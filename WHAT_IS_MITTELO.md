# What is Mittelö?

Mittelö is a remix-first **swarm toolkit**: a tiny “task bus” (hub + queue + state) that lets you plug in *any* CLI tool or language model as a worker, run many workers in parallel, and collect results in one place.

It’s deliberately simple at the core and powerful at the edges.

## The elevator pitch

- One **hub** accepts tasks, leases them out, and records results.
- Many **agents** (workers) connect, lease tasks, execute them, and `ack` success/failure.
- Any tool can be a worker if it can do: **stdin prompt → stdout answer**.

That last part is the point: Mittelö doesn’t try to “own” your model choice. You can mix and match Codex/Gemini/Kiro/Claude Code/local LLMs, or even non-LLM tools (linters, scanners, formatters) as long as they can be wrapped.

## Why this is a good idea (and why it scales)

**1) A stable, tiny core**
- The hub is a TCP server with newline-delimited JSON (JSONL/NDJSON) messages and SQLite storage.
- The core semantics are small: `enqueue → lease → ack → list/stats`.

Small cores survive refactors. They’re easier to test, reason about, and keep compatible for remixes.

**2) Tool-agnostic by design**
- You don’t have to commit to one vendor, one SDK, or one “agent framework”.
- Backends are folders (`backends/<name>/run`), so different CLIs can edit only their own backend without touching the hub.

**3) Parallelism is natural**
- You scale by running more agents (even mixed backends).
- Lease-based work distribution is a good default for “many small tasks”.

**4) Remix-friendly collaboration**
- A lot of systems are hard to fork because behavior is scattered across frameworks and SDKs.
- Here, the protocol is readable and reimplementable in any language.

## What Mittelö is *not*

- Not a full orchestration platform (yet): no auth, no multi-tenant permissions, no job DAG scheduler, no cloud deploy story out of the box.
- Not guaranteed “clean model output”: real CLIs differ wildly in interactivity, banners, streaming, and error modes. Wrappers and drivers are where reality is handled.

## The mental model (in one diagram)

```
             enqueue(prompt)
                  │
                  v
        +--------------------+
        |        HUB         |
        |  TCP JSONL + DB    |
        +--------------------+
          ^   ^        ^   ^
          |   |        |   |
       lease ack    list stats
          |   |        |   |
          v   v        v   v
   +-----------+   +-----------+   +-----------+
   |  agent A  |   |  agent B  |   |  agent C  |
   | backend:X |   | backend:Y |   | backend:Z |
   +-----------+   +-----------+   +-----------+
        │                │              │
        v                v              v
   (stdin→stdout)   (stdin→stdout) (stdin→stdout)
```

## Two integration styles

**A) Backend wrappers (preferred)**
- Put a script at `backends/<name>/run`.
- Contract:
  - read prompt from `stdin`
  - print final answer to `stdout`
  - exit `0` on success, non-zero on failure (details to `stderr`)

**B) Shell backend**
- Run any command directly via `--backend shell --shell-cmd "..."`.

## Current state of the repo (honest)

This repository contains:
- A minimal, working implementation under `mittelo/` (hub/client/agent + SQLite store).
- A more structured “next architecture” under `src/` (orchestrator + wrapper drivers + utilities), aimed at “real CLI drivers”.

That split is normal during a transition: the simplest thing keeps working while the structured version catches up.

## What people usually build with it

- “Many-small-tasks” pipelines: code reviews, doc generation, repo audits, checklist generation.
- Mixed-model swarms: cheap model for triage + strong model for hard tasks.
- Sidecar tool swarms: run non-LLM tools (formatters/linters/scanners) as backends too.

## Why it’s worth showing off

Mittelö is one of those projects where the core idea is *embarrassingly practical*:

- simple enough to run locally in minutes,
- flexible enough to integrate whatever your team already uses,
- and structured enough to grow into something serious without rewriting everything.

If you want to contribute, start by adding a backend wrapper or a use-case pack:
- Backends: `backends/<name>/run`
- Packs: `examples/use_cases/*.jsonl`
