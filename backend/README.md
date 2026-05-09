# Pampa Backend

Backend for **Pampa** — a Spanish-first conversational AI agent that lives on top of an account-agnostic personal-finance backend. Built for **Platanus Hack 26 (Buenos Aires)** in the *Agentic Money* track.

The user chats with one agent that can read balances and history across all connected financial accounts (Wallbit, Ethereum, future fintechs), execute multi-step money-moving plans with one approval gate per plan, run autonomous tradebots within explicit safeguards, classify ingested documents, and maintain a persistent user financial context that grounds every conversation.

This service is a Python / FastAPI app with hosted Postgres, the Anthropic Claude SDK, async SQLAlchemy, and a layered hexagonal architecture (transport → services → agents → finance providers + canonical model + persistence). See [`docs/architecture.md`](./docs/architecture.md) for the design summary and [`../.claude/artifacts/`](../.claude/artifacts/) for the locked design contracts.

## Status

Scaffold-only. The package layout from [`02-1` §10](../.claude/artifacts/02-1_backend_architechture.md) exists, settings + logging + error-envelope plumbing is wired, Alembic is configured, and a `GET /api/v1/health` smoke endpoint boots clean. Endpoints, services, agents, providers, and ORM models land in subsequent prompts.

## Prerequisites

- **Python 3.11** (pinned via `.python-version`)
- **[uv](https://docs.astral.sh/uv/)** — package + virtualenv manager. Install via `pipx install uv` (recommended) or the official installer.
- **Postgres** — hosted Supabase for prod; any reachable Postgres works for dev. The async driver string is `postgresql+asyncpg://...`.

## Setup

```bash
cd backend
uv sync                    # creates .venv and installs runtime + dev deps
cp .env.example .env       # then fill in the values
```

Generate a Fernet key for credential encryption:

```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Paste the result into `FERNET_KEY` in `.env`.

## Running

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The app boots on `http://localhost:8000`. Smoke-check:

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok"}
```

## Testing, lint, type-check

```bash
uv run pytest -q              # tests (currently: health smoke test)
uv run ruff check .           # lint
uv run ruff format .          # format
uv run mypy app               # type-check (non-strict for now)
```

## Database migrations

Migrations are managed by Alembic. The first real migration will enable `pgcrypto` (per [`02-4` §4](../.claude/artifacts/02-4_database_schema.md)) and create the canonical-model tables. The scaffold ships zero migrations.

```bash
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
uv run alembic current        # requires a reachable DB
uv run alembic heads          # lists head revisions; works offline
```

## Docker

```bash
docker build -t pampa-backend .
docker run --env-file .env -p 8000:8000 pampa-backend
```

The image is app-only; the database is expected to be Supabase (or any reachable Postgres reachable via `DATABASE_URL`).

## Project structure

```
backend/
  app/
    main.py            # FastAPI entrypoint; mounts /api/v1 router and /health
    config.py          # Pydantic settings (loads .env)
    api/               # transport ports — REST, WebSocket, tool registry
    services/          # domain logic (no HTTP, no LLM, no provider details)
    agents/            # LLM-driven runtimes (chat, tradebots, classifier)
    ai/                # Anthropic SDK wrapper
    providers/         # finance-provider adapters (Wallbit, Ethereum, …)
    canonical/         # provider-agnostic data shapes
    persistence/       # async SQLAlchemy engine, models, repositories, Fernet vault
    workers/           # background processes (poller, tradebot runner, ingest)
    common/            # cross-cutting: logging, error envelope, audit, rate limit
  alembic/             # migrations (currently empty)
  docs/                # backend-specific docs (links to canonical artifacts)
  tests/               # pytest suite
  pyproject.toml       # uv-managed deps + tool config
  Dockerfile
```

The full layer responsibilities and import-direction rules live in [`02-1` §10](../.claude/artifacts/02-1_backend_architechture.md).

## Environment variables

See `.env.example` for the full list. Required at runtime:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres async DSN, `postgresql+asyncpg://…` |
| `ANTHROPIC_API_KEY` | Claude API key |
| `WALLBIT_API_KEY` | Wallbit account API key (per-user — dev shortcut for now) |
| `ETHEREUM_RPC_URL` | EVM JSON-RPC endpoint |
| `FERNET_KEY` | Symmetric key for credential vault encryption |
| `ENV` | `dev` (console logs) or anything else (JSON logs) |
| `LOG_LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `CORS_ORIGINS` | Comma-separated allowed origins |

## Documentation

- [`docs/`](./docs/) — backend-specific notes; consult before making changes and update after.
- [`../.claude/artifacts/`](../.claude/artifacts/) — locked design contracts:
  - `01_research_brief.md` — track / sponsor / persona context
  - `02-1_backend_architechture.md` — layered architecture (authoritative for backend)
  - `02-2_frontend_design.md` — frontend surface inventory
  - `02-3_api_surface.md` — REST + WebSocket contract (authoritative for endpoint shapes)
  - `02-4_database_schema.md` — Postgres schema (authoritative for migrations)

## Team

team-29 — Rubén Bohórquez · Juan Ignacio Medone · Vladimir Kozow · Luca Lazcano · Alen Davies.
