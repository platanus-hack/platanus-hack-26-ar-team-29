# Pampa Backend

Backend for **Pampa** — a Spanish-first conversational AI agent that lives on top of an account-agnostic personal-finance backend. Built for **Platanus Hack 26 (Buenos Aires)** in the *Agentic Money* track.

The user chats with one agent that can read balances and history across all connected financial accounts (Wallbit today, Ethereum and others later), execute multi-step money-moving plans with one approval gate per plan, and stream every step back over WebSocket. Hexagonal architecture (`api → services → agents/providers/persistence`); see [`docs/architecture.md`](./docs/architecture.md) and [`../.claude/artifacts/`](../.claude/artifacts/) for the locked design.

## Status

**MVP slice running end-to-end.** Chat sessions, message history, real-time streaming, plan-approval ceremony, Wallbit dev API integration, balances + transactions reads. See [`docs/deviations.md`](./docs/deviations.md) for what's intentionally out of scope vs the locked design.

## Prerequisites

- **Python 3.11** (pinned via `.python-version`)
- **[uv](https://docs.astral.sh/uv/)** — `pipx install uv` or [official installer](https://docs.astral.sh/uv/getting-started/installation/)
- **Postgres 14+** reachable on a TCP port. Local Docker is fine; Supabase works too. The async DSN must be `postgresql+asyncpg://...`.

## Quick start

```bash
# 1. From repo root
cd backend

# 2. Install deps + venv
uv sync

# 3. Copy env template
cp .env.example .env
```

Generate a Fernet key (required for credential encryption):

```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Paste the result into `FERNET_KEY` in `.env`. Then fill in `ANTHROPIC_API_KEY` and `WALLBIT_API_KEY` (both optional for read-only smoke testing — see "Without API keys" below).

Bring up Postgres (one-shot Docker option):

```bash
docker run -d --name pampa-pg -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=pampa \
  postgres:16
```

The default `DATABASE_URL` in `.env.example` matches that container.

Apply migrations and boot:

```bash
uv run alembic upgrade head            # creates 6 tables + dev user seed
uv run uvicorn app.main:app --port 8000  # NOT --reload (WS state is in-process)
```

Smoke check:

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok"}
```

## Endpoints (frontend cheat sheet)

All paths under `/api/v1`. Auth is hardcoded to a single dev user (UUID `00000000-0000-0000-0000-000000000001`) — no headers required.

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/chat/sessions` | `{title?}` | `{id, title, created_at, updated_at, ...}` |
| GET | `/chat/sessions` | — | `[{id, title, last_message_preview, updated_at}]` |
| GET | `/chat/sessions/{sid}/messages` | — | `[{id, role, content, created_at}]` (role ∈ user/assistant/system) |
| POST | `/chat/sessions/{sid}/messages` | `{content}` | `202 {message_id, accepted: true}` — agent runs async, results stream over WS |
| POST | `/plans/{pid}/approve` | `{approved?}` | `{ok: true, plan_state: "approved"}` — PlanExecutor runs async |
| POST | `/plans/{pid}/reject` | `{reason?}` | `{ok: true, plan_state: "rejected"}` |
| POST | `/connections/wallbit` | `{label, api_key}` | `{id, connection_type, label, status, capabilities, created_at}` (probes Wallbit to validate) |
| GET | `/connections` | — | List connections (sanity) |
| GET | `/balances` | — | Aggregated checking + stocks (direct Wallbit fetch) |
| GET | `/transactions?limit=N` | — | Transactions feed (direct Wallbit fetch) |
| GET | `/health` | — | `{status: "ok"}` |

### WebSocket

```
ws://localhost:8000/api/v1/ws?session_id=<uuid>&token=<optional, ignored in v1>
```

Subscribe-on-connect (one socket per session). Server → client frames:

```jsonc
{"type": "subscribed",    "session_id": "..."}
{"type": "chat_token",    "session_id": "...", "turn_id": "...", "delta": "..."}
{"type": "chat_message",  "session_id": "...", "message": {"id", "role", "content", "created_at"}}
{"type": "plan_proposed", "session_id": "...", "plan_id": "...", "plan": {"id", "state", "steps": [...]}}
{"type": "plan_update",   "session_id": "...", "plan_id": "...", "step_id": "...", "state": "executing|ok|failed", "ts": "..."}
{"type": "turn_complete", "session_id": "...", "turn_id": "..."}
{"type": "error",         "code": "...", "message_es": "...", "message_en": "..."}
{"type": "pong"}
```

Client → server: `{"type": "ping"}` (server replies `pong`), `{"type": "subscribe_session"}` (noop in v1, single-session per socket).

**Subscribe before sending**: connect the WS, wait for `subscribed`, then `POST /chat/sessions/{sid}/messages`. Frames emitted before subscription are dropped (no replay buffer in v1).

### Demo loop (curl + websocat)

```bash
SID=$(curl -s -X POST http://localhost:8000/api/v1/chat/sessions \
  -H 'Content-Type: application/json' -d '{}' | jq -r '.id')

# Terminal 1: WS subscriber
websocat "ws://localhost:8000/api/v1/ws?session_id=$SID"

# Terminal 2: send a write-intent message
curl -X POST "http://localhost:8000/api/v1/chat/sessions/$SID/messages" \
  -H 'Content-Type: application/json' \
  -d '{"content": "comprá 10 usd de apple"}'

# Terminal 1 streams: chat_token... → plan_proposed (capture plan_id) → turn_complete
PID=<plan_id>

# Approve
curl -X POST "http://localhost:8000/api/v1/plans/$PID/approve" \
  -H 'Content-Type: application/json' -d '{"approved": true}'
# Terminal 1 streams: plan_update (executing → ok) → chat_token (summary) → turn_complete
```

### Without API keys

The agent has a Spanish-keyword heuristic fallback when `ANTHROPIC_API_KEY` is missing — the chat endpoints work, plans get proposed, the demo loop runs. Wallbit endpoints (`/balances`, `/transactions`, `/connections/wallbit`, real plan execution) require `WALLBIT_API_KEY` and a reachable Wallbit dev URL.

## Environment variables

See [`.env.example`](./.env.example). Required at runtime:

| Variable | Purpose | Required |
|---|---|---|
| `DATABASE_URL` | Postgres async DSN, `postgresql+asyncpg://…` | yes |
| `FERNET_KEY` | Symmetric key for credential vault — generate per quick-start above | yes |
| `ANTHROPIC_API_KEY` | Claude API key | optional (heuristic fallback if absent) |
| `ANTHROPIC_MODEL` | Default `claude-haiku-4-5`; override to `claude-sonnet-4-6` for demo | optional |
| `WALLBIT_API_KEY` | Per-user Wallbit dev key (v1 dev shortcut — real auth comes later) | only for live trades + balances |
| `WALLBIT_BASE_URL` | Default `https://api.wallbit.io`; override for dev/sandbox | optional |
| `ETHEREUM_RPC_URL` | EVM JSON-RPC endpoint (Ethereum provider not implemented yet) | no |
| `ENV` | `dev` (console logs) or anything else (JSON logs) | optional |
| `LOG_LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` | optional |
| `CORS_ORIGINS` | Comma-separated allowed origins | optional |

## Common commands

```bash
uv run uvicorn app.main:app --port 8000   # dev server (don't use --reload, breaks WS state)
uv run pytest -q                          # smoke tests (5 currently)
uv run ruff check .                       # lint
uv run ruff format .                      # format
uv run mypy app                           # type-check (non-strict)
uv run alembic revision --autogenerate -m "msg"  # new migration
uv run alembic upgrade head               # apply
uv run alembic downgrade base             # tear down (dev only)
```

All commands run from `backend/`.

## Docker

```bash
docker build -t pampa-backend .
docker run --env-file .env -p 8000:8000 pampa-backend
```

The image is app-only; bring your own Postgres reachable via `DATABASE_URL`.

## Project structure

```
backend/
  app/
    main.py            # FastAPI entrypoint; mounts /api/v1; lifespan boots provider/agent singletons
    config.py          # Pydantic settings (loads .env)
    api/
      rest/            # chat, plans, connections, portfolio routers
      ws/              # ConnectionManager + /ws route
      deps.py          # FastAPI dependencies (dev user, service factories)
    services/          # ChatService, PlanService, ConnectionService, PortfolioService
    agents/            # ChatAgent, PlanExecutor, ToolDispatcher, tool registrations
    ai/                # Anthropic SDK wrapper + Spanish system prompt
    providers/
      base.py          # Provider + Capability ABCs
      registry.py      # ProviderRegistry
      wallbit/         # client.py + adapter.py + capabilities.py + auth.py
    persistence/
      base.py          # SQLAlchemy DeclarativeBase
      session.py       # async engine + get_session() FastAPI dep
      models/          # users, connections, chat, plans
      repositories/    # data-access classes
      crypto.py        # Fernet encrypt/decrypt
    common/
      errors.py        # APIError + standard codes + envelope handler
      logging.py       # structlog setup
  alembic/             # migrations (1 migration: init_mvp)
  docs/                # backend-specific docs (architecture, deviations)
  tests/               # pytest suite (5 smoke tests)
  pyproject.toml
  Dockerfile
```

The full layer responsibilities and import-direction rules live in [`02-1` §10](../.claude/artifacts/02-1_backend_architechture.md) and [`docs/architecture.md`](./docs/architecture.md).

## Documentation

- [`docs/`](./docs/) — backend-specific notes (architecture cheatsheet, deviations log).
- [`../.claude/artifacts/`](../.claude/artifacts/) — locked design contracts:
  - `01_research_brief.md` — track / sponsor / persona context
  - `02-1_backend_architechture.md` — layered architecture (authoritative for backend)
  - `02-2_frontend_design.md` — frontend surface inventory
  - `02-3_api_surface.md` — REST + WebSocket contract (authoritative for endpoint shapes)
  - `02-4_database_schema.md` — Postgres schema (authoritative for migrations)
  - `03_build_log.md` — what shipped, what's open, env vars, decisions

## Team

team-29 — Rubén Bohórquez · Juan Ignacio Medone · Vladimir Kozow · Luca Lazcano · Alen Davies.
