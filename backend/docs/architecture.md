# Backend Architecture (Local Summary)

Authoritative design lives in [`../../.claude/artifacts/02-1_backend_architechture.md`](../../.claude/artifacts/02-1_backend_architechture.md). This note is a quick-reference for "where do I put new code." When in doubt, the artifact wins.

## Six layers

| Layer | Path | Responsibility | What goes here |
|---|---|---|---|
| Transport ports | `app/api/` | Translate external shape → service-method calls | REST handlers (`rest/`), WebSocket handler (`ws/`), Anthropic tool-use registry (`tools/`) |
| Domain services | `app/services/` | Business logic — the only layer with rules | One file per resource cluster (`chat`, `portfolio`, `tradebot`, `ingestion`, `context`, `auth`) |
| Agent runtimes | `app/agents/` | LLM-driven orchestration | Chat agent loop, tradebot agent loop, classifier (batch), plan executor, tool dispatcher |
| AI provider | `app/ai/` | Wraps the Anthropic SDK | `anthropic.py`, prompt templates, streaming helpers |
| Finance providers | `app/providers/` | External-API knowledge | One package per provider with `client.py` + `adapter.py` + `capabilities.py` + `auth.py` |
| Canonical + persistence | `app/canonical/`, `app/persistence/` | Provider-agnostic data shapes; dumb storage | Canonical models, ORM models, repositories, Fernet vault |

Background workers (`app/workers/`) are separate process entrypoints that import the service layer.

## Import-direction rules (lint-enforced eventually)

- `api/` → `services/`, `agents/` (only for chat-agent invocation)
- `services/` → `providers/`, `canonical/`, `persistence/`, `agents/`. **Must NOT import `ai/` directly** — all LLM calls go through `agents/`.
- `agents/` → `ai/`, `providers/` (via registry), `canonical/`, `services/`
- `providers/` imports nothing from `services/`, `agents/`, `api/`. **One-way flow into providers.**
- `canonical/`, `persistence/` import only from each other and stdlib.
- `workers/` are entrypoints; nothing imports from `workers/`.

## Where to add code (recipes)

| Task | Where |
|---|---|
| New REST endpoint | `app/api/rest/<resource>.py` → register on `app.api.api_router` |
| New WebSocket frame | `app/api/ws/chat.py` (and `02-3` §6 for the frame catalog) |
| New tool exposed to Claude | `app/api/tools/<resource>_tools.py` — must be paired with a service method (per `02-3` §13) |
| New domain rule | `app/services/<resource>.py` |
| New LLM behavior | `app/agents/<agent>.py` (and prompt template under `app/ai/prompts/`) |
| New finance provider | `app/providers/<name>/` package; subclass `Provider`; implement relevant `Capability` ABCs; register at startup |
| New canonical field | `app/canonical/models.py` + the ORM mirror in `app/persistence/models/` |
| New ORM model | `app/persistence/models/<cluster>.py` — **also import in `models/__init__.py`** so Alembic autogenerate finds it |
| New error code | Add a constant in `app/common/errors.py` and a row in [`02-3` §3.3](../../.claude/artifacts/02-3_api_surface.md) |
| New background job | `app/workers/<job>.py` — own `__main__`, imports services |

## Locked decisions (cheat sheet — full table in [`02-1` §11](../../.claude/artifacts/02-1_backend_architechture.md))

- Python 3.11+ on FastAPI / Uvicorn
- Hosted Postgres (Supabase) — async SQLAlchemy + Alembic
- Anthropic Claude (Sonnet for dev, Opus for demo)
- Confirm-once-fire-all plan executor; stop-on-first-error default
- Pure asyncio; no OS threads
- Postgres-backed task queue (no Redis / Celery)
- `cryptography.Fernet` credential vault, key in env
- Combined web + workers in one process for v1; architecture allows split with no code change

## Current scope (MVP slice)

Implemented: chat sessions/messages, plan approve/reject, Wallbit connection, balances + transactions reads, `/api/v1/ws` WebSocket, ChatAgent + PlanExecutor + ToolDispatcher, WallbitProvider with read/trade capabilities. ORM models for `users`, `provider_connections`, `chat_sessions`, `chat_messages`, `trade_plans`, `trade_plan_steps`. Migration `0001_init_mvp` creates them plus `pgcrypto` and the `set_updated_at()` trigger.

Deferred (with rationale in [`./deviations.md`](./deviations.md)):
- Auth flow (hardcoded dev user UUID for v1)
- Idempotency keys table + middleware
- Audit log entries
- Canonical ledger cluster (replaced by direct provider fetch)
- Background workers (`tasks` table, poller, ingest, tradebot runner)
- User profile / goals / rules
- WebSocket sequence/replay
- Tradebots, document ingestion, Ethereum provider

When implementing one of these, update this file's recipe table if the path or pattern shifts in any way from what's documented above, and remove the corresponding deferred entry from [`./deviations.md`](./deviations.md).
