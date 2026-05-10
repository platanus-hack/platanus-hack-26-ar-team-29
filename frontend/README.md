# Atajo Frontend

Frontend for **Atajo** — a Spanish-first conversational AI agent that lives on top of an account-agnostic personal-finance backend. Built for **Platanus Hack 26 (Buenos Aires)** in the *Agentic Money* track.

## Status

**MVP chat interface running.** Integrates with the backend REST and WebSocket APIs to support real-time conversational agent interactions and plan approvals.

## Prerequisites

- **Bun** — `curl -fsSL https://bun.sh/install | bash`
- Node.js (v18+)

## Quick start

```bash
# 1. From repo root
cd frontend

# 2. Install dependencies
bun install

# 3. Start development server
bun dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

### Environment variables

The frontend requires the backend (FastAPI) to be running. Configure these variables (they default to localhost if not defined, but it's good practice to have them explicitly):

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
```

## Common commands

```bash
bun dev          # Start development server
bun run build    # Build for production
bun run lint     # Run ESLint
```

All commands run from `frontend/`.

## Documentation

- [`CLAUDE.md`](./CLAUDE.md) — frontend-specific guidelines, architecture, and context.
- [`AGENTS.md`](./AGENTS.md) — Next.js 15 specific instructions for LLMs.
- [`../.opencode/artifacts/`](../.opencode/artifacts/) — locked design contracts:
  - `02-2_frontend_design.md` — frontend surface inventory
  - `02-3_api_surface.md` — REST + WebSocket contract (authoritative for endpoint shapes)