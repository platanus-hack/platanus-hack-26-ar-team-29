# CLAUDE.md — Backend

Guidance for Claude Code when working inside `backend/`.

## Read-before-write rule

**Before making any change to this directory, read:**

1. [`README.md`](./README.md) — overview, setup, conventions, commands.
2. The relevant file(s) in [`docs/`](./docs/) — backend-specific notes that may not yet be reflected in the canonical artifacts.
3. The relevant section(s) of [`../.claude/artifacts/`](../.claude/artifacts/) — these are the **authoritative** design contracts (architecture, API surface, DB schema). They take precedence when `docs/` and an artifact disagree, *unless* `docs/` explicitly notes a deviation that has been approved.

**After completing any change, update [`docs/`](./docs/)** with anything a future agent or human would benefit from knowing — new endpoint behaviors, deviations from the artifacts (with rationale), local conventions, gotchas. Do NOT duplicate artifact content; link to it instead. Keep `docs/` an index plus terse, current notes.

If the change *contradicts* a locked artifact, do not silently diverge. Flag the conflict, propose either an artifact update or a documented deviation in `docs/`, and wait for the user's call.

## Project overview

**Pampa** is a Spanish-first agentic-finance app for Platanus Hack 26 BA (*Agentic Money* track). One conversational agent reads balances across connected accounts (Wallbit, Ethereum, future fintechs), proposes multi-step money-moving plans with one approval gate per plan, runs tradebots within explicit safeguards, ingests / classifies financial documents, and maintains a persistent user financial context.

This `backend/` is the Python / FastAPI service. Frontend is Next.js / React on a separate branch (`front`).

## Tech stack

- **Python 3.11+** (pinned via `.python-version`)
- **FastAPI** on Uvicorn (async)
- **SQLAlchemy 2.x async** + **asyncpg** + **Alembic** for Postgres (Supabase-hosted)
- **Anthropic Claude** via the official SDK (`anthropic`)
- **httpx** for outbound HTTP, **web3.py** for EVM
- **cryptography.Fernet** for the credential vault
- **structlog** for logging
- **pytest** + **pytest-asyncio** for tests, **ruff** for lint+format, **mypy** for types
- **uv** for dependency + virtualenv management

## Architecture (one-paragraph summary)

Hexagonal app with three external surfaces — humans (REST + WebSocket), AI providers (Claude), and finance providers (Wallbit, Ethereum, future). Six layers: `api/` (transport ports — REST, WebSocket, tool registry), `services/` (domain logic), `agents/` (LLM-driven runtimes — chat, tradebots, classifier), `ai/` (Anthropic SDK wrapper), `providers/` (finance-provider adapters via Capability ABCs + a registry), `canonical/` + `persistence/` (provider-agnostic models, async DB). Background work runs in `workers/` (poller, tradebot runner, ingest worker). The chat agent, tradebots, and HTTP endpoints all call the same service layer — "anything in the app must be doable via chat" is enforced as a structural property, not a feature.

**Authoritative source:** [`../.claude/artifacts/02-1_backend_architechture.md`](../.claude/artifacts/02-1_backend_architechture.md). Don't re-derive design decisions; consult that artifact.

## Layout (where things go)

```
app/
  main.py            -> FastAPI entrypoint, mounts /api/v1 router, registers error handlers
  config.py          -> Pydantic Settings (reads .env)
  api/
    rest/            -> REST handlers (one file per resource cluster)
    ws/              -> WebSocket handlers
    tools/           -> Anthropic tool-use registry (siblings to REST endpoints)
  services/          -> domain logic; NO HTTP, NO LLM, NO provider details
  agents/            -> LLM orchestration; chat agent, tradebot agent, classifier, plan executor, tool dispatcher
  ai/                -> Anthropic SDK wrapper (isolated so swapping LLM is one file)
  providers/
    base.py          -> Provider + Capability ABCs
    registry.py      -> ProviderRegistry (find_for_capability dispatch)
    <provider>/      -> client.py + adapter.py + capabilities.py + auth.py per provider
  canonical/         -> CanonicalAccount, CanonicalAsset, CanonicalTransaction, CanonicalBalance
  persistence/
    base.py          -> SQLAlchemy DeclarativeBase
    session.py       -> async engine + session factory + get_session() FastAPI dep
    models/          -> ORM models (one file per cluster from 02-4)
    repositories/    -> data-access classes
    crypto.py        -> Fernet encrypt/decrypt for credential vault
  workers/           -> background process entrypoints
  common/
    errors.py        -> APIError + standard codes + envelope handler (per 02-3 §3.3)
    logging.py       -> structlog setup
```

**Import direction (per [`02-1` §10.1](../.claude/artifacts/02-1_backend_architechture.md#101-import-direction-rules-enforced-by-lint)):**

- `api/` → `services/`, `agents/` (only for chat-agent invocation)
- `services/` → `providers/`, `canonical/`, `persistence/`, `agents/`. **Must NOT import `ai/` directly** — all LLM calls go through `agents/`.
- `agents/` → `ai/`, `providers/` (via registry), `canonical/`, `services/`
- `providers/` imports nothing from `services/`, `agents/`, `api/`. **One-way flow into providers.**
- `canonical/` and `persistence/` import only from each other and stdlib.
- `workers/` are entrypoints; nothing imports from `workers/`.

## Common commands

| Action | Command |
|---|---|
| Install deps | `uv sync` |
| Run dev server | `uv run uvicorn app.main:app --reload --port 8000` |
| Run tests | `uv run pytest -q` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| Type-check | `uv run mypy app` |
| New migration | `uv run alembic revision --autogenerate -m "msg"` |
| Apply migrations | `uv run alembic upgrade head` |
| List migration heads (offline) | `uv run alembic heads` |
| Build container | `docker build -t pampa-backend .` |

All commands run from `backend/`.

## Conventions

- **JSON casing:** `snake_case` everywhere (per [`02-3` §3.1](../.claude/artifacts/02-3_api_surface.md)).
- **IDs:** UUIDv4 lowercase strings.
- **Times:** TIMESTAMPTZ in DB, ISO 8601 UTC with `Z` in JSON.
- **Money:** `NUMERIC(28, 10)` in DB, JSON numbers in API (precision caveat noted in `02-3`).
- **Errors:** every non-2xx response uses the [`02-3` §3.3](../.claude/artifacts/02-3_api_surface.md) envelope — raise `app.common.errors.APIError(...)`; the registered handler emits the envelope automatically.
- **Spanish-first messages:** user-visible strings (errors, agent prompts) default to Argentine-register Spanish (`message_es`); `message_en` is fallback.
- **Async everywhere:** the web tier is pure asyncio. **No OS threads.** No `asyncio.run` inside request handlers. No blocking I/O in handlers (use `httpx`, not `requests`).
- **Idempotency:** state-changing endpoints accept an optional `Idempotency-Key` header; plan-approval requires it (per [`02-3` §3.5](../.claude/artifacts/02-3_api_surface.md)).
- **Tool registry parity:** every public service method either has a tool registration in `app.api.tools` or is annotated `@chat_excluded`. The "anything via chat" property is a hard rule.
- **Adding a new provider:** drop a package into `app/providers/<name>/` with `client.py` + `adapter.py` + `capabilities.py` + `auth.py`; register in `ProviderRegistry`. **Zero changes to services, agents, or transport.**
- **Adding a new ORM model:** put it under `app/persistence/models/<cluster>.py`, import it in `app/persistence/models/__init__.py` so Alembic autogenerate sees it, then `alembic revision --autogenerate`.

## Code style

- No emojis in code, comments, or docstrings unless the user explicitly asks.
- Comments only when *why* is non-obvious. Don't restate what the code does.
- No README/docs for individual modules unless the user asks.
- Prefer editing existing files to creating new ones.
- Don't add error handling, fallbacks, or validation for cases that can't happen. Trust internal code.
- Don't add backwards-compat shims, removed-code stubs, or "for future use" abstractions. Three similar lines beat a premature abstraction.

## Out of scope right now (do not implement until prompted)

- Auth flow (use the dev token shape `Bearer dev-<user_id>` if you must, per `02-3` §3.2)
- Tool registry contents (anchor exists; tools land per-feature)
- ORM models (add per-cluster as features land)
- WebSocket handler implementation (port stub exists; protocol per `02-3` §4)
- Provider adapters
- Background workers (entrypoints exist; logic lands later)

## Footguns

- The Alembic `env.py` imports `app.persistence.models` so autogenerate sees every model. **When you add a new model file under `models/`, also import it in `models/__init__.py`** — otherwise autogenerate will silently miss it and the migration will be empty.
- `app.providers.base.Capability` is intentionally an empty ABC (marker class for type-based dispatch). The `# noqa: B024` is intentional; don't "fix" it by adding a method.
- `get_settings()` is `@lru_cache`d — tests that mutate env should clear the cache or pass an override. There's no fixture for that yet; add one when first needed.
- The Fernet vault helper raises `RuntimeError` if `FERNET_KEY` is empty. Don't catch it — fix the env.
