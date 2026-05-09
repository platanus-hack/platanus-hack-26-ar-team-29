# 03 Build Log

## Summary

- Current state: backend MVP feature-complete; demo loop runs end-to-end.
  Chat → agent → plan proposal → approve → real Wallbit dev API call → completion summary.
- Demo URL: local only. `uv run uvicorn app.main:app --port 8000` (NOT --reload).
- Local run command: see `## Reproduce locally`.
- Main branch/commit reference: `main`. Implementation work uncommitted at handoff time.

## Completed Work

- 9 REST endpoints + 1 WebSocket route per the plan, mounted under `/api/v1`.
- 6-table Postgres schema with `pgcrypto`, `set_updated_at()` trigger, dev user seed.
- Hexagonal layering preserved: `api/` → `services/` → `agents/`/`providers/`/`persistence/`.
- ConnectionManager + WS frame taxonomy: `subscribed`, `chat_token`, `chat_message`,
  `plan_proposed`, `plan_update`, `turn_complete`, `error`, `pong`.
- Real Wallbit dev API client (`X-API-Key` auth, `/api/public/v1/...` routes) plus
  capability adapter that tolerates undocumented response shapes.
- Confirm-once-fire-all PlanExecutor with stop-on-first-error, broadcasting
  `plan_update` frames per step.
- Anthropic-backed ChatAgent (non-streaming `messages.create` + synthesized
  token streaming for UX). Heuristic Spanish-keyword fallback when no API key.
- Smoke tests (5) passing; ruff clean.

## Files Changed

| File | Purpose |
| --- | --- |
| `backend/app/persistence/models/users.py` | User ORM model (new) |
| `backend/app/persistence/models/connections.py` | ProviderConnection ORM model (new) |
| `backend/app/persistence/models/chat.py` | ChatSession + ChatMessage models (new) |
| `backend/app/persistence/models/plans.py` | TradePlan + TradePlanStep models (new) |
| `backend/app/persistence/models/__init__.py` | Eager imports for Alembic autogen (new) |
| `backend/app/persistence/repositories/users.py` | User repository (new) |
| `backend/app/persistence/repositories/chat.py` | Chat repo (sessions + messages) (new) |
| `backend/app/persistence/repositories/plans.py` | Plan repo with selectinload of steps (new) |
| `backend/app/persistence/repositories/connections.py` | Connection repo (new) |
| `backend/app/persistence/session.py` | Added `reset_engine()` for test isolation |
| `backend/app/api/deps.py` | Dev user dep + service factories (new) |
| `backend/app/api/__init__.py` | Mount REST + WS routers under `/api/v1` |
| `backend/app/api/rest/chat.py` | Sessions + messages endpoints (new) |
| `backend/app/api/rest/plans.py` | Plan get/approve/reject (new) |
| `backend/app/api/rest/connections.py` | Wallbit connect + list (new) |
| `backend/app/api/rest/portfolio.py` | Balances + transactions (direct Wallbit) (new) |
| `backend/app/api/ws/manager.py` | In-process ConnectionManager (new) |
| `backend/app/api/ws/chat.py` | `/api/v1/ws` route + ping/pong loop (new) |
| `backend/app/services/chat.py` | ChatService + agent task spawn (strong-ref set) (new) |
| `backend/app/services/plans.py` | PlanService with state-transition validation (new) |
| `backend/app/services/connections.py` | ConnectionService (probe + encrypt + store) (new) |
| `backend/app/services/portfolio.py` | PortfolioService (direct Wallbit) (new) |
| `backend/app/providers/wallbit/__init__.py` | Package init (new) |
| `backend/app/providers/wallbit/auth.py` | WallbitCredentials + Fernet blob helpers (new) |
| `backend/app/providers/wallbit/client.py` | httpx-based Wallbit REST client (new) |
| `backend/app/providers/wallbit/adapter.py` | Response-shape adapters (new) |
| `backend/app/providers/wallbit/capabilities.py` | WallbitProvider implements Provider (new) |
| `backend/app/ai/anthropic.py` | Anthropic SDK wrapper (new) |
| `backend/app/ai/prompts/chat_system.py` | Spanish-first system prompt (new) |
| `backend/app/ai/prompts/__init__.py` | Package init (new) |
| `backend/app/agents/__init__.py` | Tool registrations (read_balances/read_transactions/propose_trade) |
| `backend/app/agents/tool_dispatcher.py` | ToolDispatcher + ToolContext (new) |
| `backend/app/agents/chat_agent.py` | ChatAgent.run_turn + plan-proposal emit (new) |
| `backend/app/agents/plan_executor.py` | PlanExecutor.execute (new) |
| `backend/app/main.py` | Lifespan with singletons, agent_tasks set, engine reset on shutdown |
| `backend/app/config.py` | Added `wallbit_base_url` and `anthropic_model` settings |
| `backend/.env.example` | Added new env entries |
| `backend/.env` | Local dev values (gitignored, NOT committed) |
| `backend/alembic/versions/0001_init_mvp.py` | Initial migration with pgcrypto, trigger, dev user seed (new) |
| `backend/tests/conftest.py` | Session-scoped TestClient fixture |
| `backend/tests/test_chat_smoke.py` | Sessions REST shape (new) |
| `backend/tests/test_plan_smoke.py` | Plan reject + 412 stale (new) |
| `backend/tests/test_ws_smoke.py` | WS subscribe + ping/pong + plan flow (new) |
| `backend/pyproject.toml` | Lint ignore list (B008, SIM105) |
| `backend/docs/deviations.md` | Six approved deviations from locked design (new) |

## Commands Run

| Command | Result | Notes |
| --- | --- | --- |
| `docker run -d --name openfi-pg -p 5433:5432 ... postgres:16-alpine` | OK | Local Postgres for dev |
| `uv sync` | OK | Used pre-existing lock; no new deps |
| `uv run alembic revision --autogenerate -m "init mvp"` | OK | Generated `0001_init_mvp.py`; hand-edited for pgcrypto + trigger + seed |
| `uv run alembic upgrade head` | OK | 6 tables created; `users` seed verified |
| `uv run uvicorn app.main:app --port 8000` | OK | Server boots cleanly |
| Manual curl + websocket smoke against running server | OK | Demo loop works end-to-end |
| `uv run pytest -q` | 5 passed | All smoke tests pass |
| `uv run ruff check app tests` | All checks passed | After enabling B008/SIM105 ignores |

## Tests And Checks

| Check | Command/steps | Result |
| --- | --- | --- |
| Unit | n/a — smoke level only for MVP | n/a |
| Smoke | `uv run pytest -q tests/` | 5 passed (chat shape, plan reject + 412, ws subscribe/ping/pong, ws plan-flow, health) |
| Functional | Manual curl loop in §Reproduce locally | Verified plan create/approve/reject paths + WS frames |
| Stress | not run | Hackathon scope |
| Security | Manual: secrets gitignored, Fernet vault wraps Wallbit creds | OK |

## Environment Variables

| Variable | Purpose | Required for demo |
| --- | --- | --- |
| `DATABASE_URL` | Postgres async URL (`postgresql+asyncpg://...`) | Yes |
| `FERNET_KEY` | Vault key (generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`) | Yes |
| `ANTHROPIC_API_KEY` | Anthropic Claude key | Yes for full LLM demo. Without it, agent uses heuristic fallback. |
| `ANTHROPIC_MODEL` | Override LLM model. Default `claude-haiku-4-5` | No |
| `WALLBIT_API_KEY` | Demo-account Wallbit key (only needed if you also wire the env-config probe; in MVP, the user POSTs the key via `/connections/wallbit`) | Optional |
| `WALLBIT_BASE_URL` | Wallbit base URL. Default `https://api.wallbit.io` | No |
| `CORS_ORIGINS` | Comma-separated allowed origins. Default `http://localhost:3000` | Yes for frontend |
| `ENV` / `LOG_LEVEL` | Runtime + log level | No |

## API / Deploy Setup Notes

- The migration runs cleanly on a fresh Postgres 16 DB. The first op enables
  `pgcrypto` for `gen_random_uuid()` server defaults.
- A `set_updated_at()` trigger function is created and attached to all five
  tables that have `updated_at` columns.
- The dev user (`00000000-0000-0000-0000-000000000001`, "Tomás Demo") is
  seeded inside the migration. Auth deps return this UUID unconditionally.
- The lifespan hook fail-fasts on a missing `FERNET_KEY` by encrypting a
  byte string at startup.
- WS resume / `since_seq` is intentionally NOT implemented; clients that
  reconnect mid-turn must refetch `/messages` and `/plans/{id}` to converge.

## Decisions And Shortcuts

- **Non-streaming Anthropic for tool use**. Per plan §Risks #1, streaming with
  `tool_use` is brittle. We call `messages.create` non-streaming, parse the
  response server-side, and synthesize `chat_token` deltas after the fact so
  the frontend still gets streaming UX. (Documented in `backend/docs/deviations.md`.)
- **Heuristic Spanish-keyword fallback** when `ANTHROPIC_API_KEY` is unset.
  Detects "comprá/vendé <N> usd de <SYMBOL>" and proposes a single-step
  `place_trade` plan. This makes the WS demo loop exercisable without an
  Anthropic key. Remove once a key is wired.
- **Direct Wallbit fetch** for `/balances` and `/transactions` — no canonical
  ledger, no poller. Acceptable because only Wallbit ships in the MVP.
- **Tool registry**: three tools — `read_balances` (read), `read_transactions`
  (read), `propose_trade` (write). Write tools never execute during the chat
  turn; they're queued as `trade_plan_steps` and only run after `/approve`.
- **In-process `agent_tasks: set[asyncio.Task]`** with `add_done_callback(set.discard)`
  to keep spawned tasks alive against GC. Stored on `app.state.agent_tasks`.
- **WS frame race**: `asyncio.sleep(0.05)` at start of agent task to let the
  frontend subscribe before frames start arriving.
- **Engine reset on lifespan shutdown** so re-using the same FastAPI app across
  multiple TestClient lifecycles in pytest doesn't cause asyncpg's "another
  operation in progress" errors. See `app/persistence/session.py:reset_engine`.
- **Tests are session-scoped TestClient** so we only enter lifespan once per
  test session.

## Known Issues

- **Wallbit response shapes** are still an inferred best-guess. The adapter
  in `app/providers/wallbit/adapter.py` accepts several common payload keys
  (`balances|data|items|results` etc.) but has not been validated against a
  real `/balance/checking` response. On first live call the raw payload is
  logged at INFO; iterate the adapter mapping if shapes don't match.
- **Anthropic streaming not implemented**. We non-streaming + synth-stream.
  If real streaming is required, swap `AnthropicClient.messages_create` for
  `messages.stream` and refactor the agent's hop loop.
- **Wallbit settlement polling not implemented**. We mark steps `ok` on the
  first 2xx from `POST /trades`, even though Wallbit returns `REQUESTED`
  initially. Production would need a follow-up poller.
- **No retry / circuit-breaker** on Wallbit calls. The hackathon mitigation is
  to surface upstream errors as `PROVIDER_UNAVAILABLE` (502) and stop the plan.
- **`ChatService.list_sessions` does N+1 DB calls** to compute previews
  (one per session). Fine for the demo (you'll have <10 sessions), needs a
  CTE for production.
- **Lifespan tasks are cancelled but the FastAPI shutdown gathers them with
  `return_exceptions=True`**, which means a slow trade call on shutdown is
  cancelled mid-flight. Acceptable for the demo; production would want a
  graceful drain timeout.

## Reproduce locally

```bash
cd /home/rpetey317/facu/platanus-hack-26-ar-team-29/backend
docker run -d --name openfi-pg -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=openfi -p 5433:5432 postgres:16-alpine

# Generate a Fernet key:
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Create .env (copy from .env.example, fill in DATABASE_URL, FERNET_KEY, ANTHROPIC_API_KEY)
cp .env.example .env

uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --port 8000   # NOT --reload (per plan §Risks #6)

# In another shell:
curl http://localhost:8000/api/v1/health
# {"status":"ok"}

SID=$(curl -s -X POST http://localhost:8000/api/v1/chat/sessions \
  -H 'Content-Type: application/json' -d '{}' | jq -r .id)

# Connect WS in one terminal:
websocat "ws://localhost:8000/api/v1/ws?session_id=$SID"

# Trigger a buy intent in another:
curl -X POST "http://localhost:8000/api/v1/chat/sessions/$SID/messages" \
  -H 'Content-Type: application/json' -d '{"content":"comprá 10 usd de apple"}'

# WS streams: chat_token deltas → chat_message → plan_proposed → turn_complete
# Capture plan_id from plan_proposed; then approve:
curl -X POST "http://localhost:8000/api/v1/plans/$PID/approve"
# WS streams: plan_update (executing → ok|failed) → chat_token (summary) → chat_message → turn_complete
```

## Reviewer Handoff

- **Main flow to test**:
  1. POST `/api/v1/chat/sessions` → save `session_id`.
  2. Connect WS at `/api/v1/ws?session_id=<id>`.
  3. POST `/api/v1/chat/sessions/{id}/messages` with content "comprá 10 usd de apple".
  4. Capture plan_id from `plan_proposed` frame.
  5. POST `/api/v1/connections/wallbit` (REQUIRED before approve, otherwise step fails fast).
  6. POST `/api/v1/plans/{plan_id}/approve` → expect `plan_update` frames + summary chat message.
- **Risk areas** (in priority order):
  1. Wallbit response shape adapter — first live call should be inspected to
     verify the adapter mapping; raw payloads are logged.
  2. Agent task lifecycle on uvicorn `--reload`: don't use `--reload` for the
     demo. Tasks survive proper shutdown via lifespan hook.
  3. Plan timeout: plans expire 5 minutes after creation. Approving a stale
     plan returns 412 PLAN_STALE.
- **Suggested review focus**:
  - `backend/app/agents/chat_agent.py` — the load-bearing `_run_turn_inner` hop loop and `_emit_plan_proposal`.
  - `backend/app/agents/plan_executor.py` — DB-session-per-step pattern + WS broadcasts + stop-on-first-error.
  - `backend/app/api/ws/manager.py` + `app/api/ws/chat.py` — connection lifecycle.
  - `backend/alembic/versions/0001_init_mvp.py` — verify against fresh DB.
- **Next steps for Reviewer**:
  - Add a real Anthropic key (`ANTHROPIC_API_KEY`) to `.env` and re-run
    `comprá 10 usd de apple` — agent should now use the LLM rather than the heuristic.
  - Ship a real Wallbit dev API key via `POST /api/v1/connections/wallbit`
    (the validation probe will fire and reject bad keys).
  - Inspect first `wallbit_response` log lines and tune
    `app/providers/wallbit/adapter.py` if the row keys don't line up.
  - Optional: swap to streaming Anthropic if `tool_use` partial-JSON parsing is
    desired; non-streaming is the safer default per the plan.

---

## 2026-05-09 — Phase 1: custodial Ethereum endpoints

### What shipped

Six new REST endpoints landing the wallet-management + on-chain-transfer + private-key-export surface from `02-3` §5.13.1, §5.13.2, §5.13.5. Spec compliance follows the locked decisions in §14 rows 28–31 (testnets only, manual gas funding, custodial encryption, export = `chat_excluded`).

| Method | Path | Notes |
|---|---|---|
| `POST` | `/api/v1/connections/ethereum-custodial/import` | Accepts hex (with or without `0x`) **or** 12/24-word BIP-39 mnemonic. Shape detection in `_normalize_private_key_input`. |
| `POST` | `/api/v1/connections/ethereum-custodial/create` | Returns mnemonic + address **once**; only the encrypted private key is persisted. |
| `GET` | `/api/v1/connections/{id}/onchain/gas` | Three-tier (slow/standard/fast) suggestion with multipliers `0.85 / 1.0 / 1.25`. |
| `POST` | `/api/v1/connections/{id}/onchain/simulate` | `eth_call` + `estimate_gas` dry-run; raw revert text never leaks to the client. |
| `POST` | `/api/v1/connections/{id}/onchain/transfer` | ETH and ERC-20 (USDC where supported). Response shape per artifact: `tx_hash`, `status:"pending"`, `block_explorer_url`, `gas_estimate_gwei`, `fee_estimate_eth`. |
| `POST` | `/api/v1/connections/{id}/export-private-key` | `Cache-Control: no-store, private`; non-custodial connections return `400 NOT_EXPORTABLE`. **Not** registered as a Claude tool. |

### Files Changed

| File | Purpose |
| --- | --- |
| `backend/app/config.py` | Replaced single `ethereum_rpc_url` with five per-network env vars (Sepolia, Holesky, Polygon Amoy, Arb Sepolia, Base Sepolia). Exposes `ethereum_rpc_urls` dict. |
| `backend/.env.example` | Added the five `ETHEREUM_RPC_URL_*` entries. |
| `backend/app/common/errors.py` | New codes `NETWORK_NOT_ALLOWED`, `NOT_EXPORTABLE`, `INVALID_ADDRESS`, `ASSET_NOT_SUPPORTED`. |
| `backend/app/persistence/models/connections.py` | CHECK constraints extended: `connection_type` + `'ethereum_custodial'`, `auth_kind` + `'private_key'`. |
| `backend/alembic/versions/0002_ethereum_custodial_constraints.py` | Migration for the constraint widen. Hand-written (autogenerate would not pick up CHECK-constraint string changes). **Not applied** — local DB unreachable in this pass. |
| `backend/app/persistence/repositories/connections.py` | Added `create_ethereum_custodial`, `get_active_ethereum_custodial`. |
| `backend/app/providers/ethereum/__init__.py` | Package init (new). |
| `backend/app/providers/ethereum/auth.py` | `EthereumCustodialCredentials` dataclass with `to_blob()` / `from_blob()` (mirrors `WallbitCredentials`). |
| `backend/app/providers/ethereum/networks.py` | Network registry: `chain_id`, explorer URL template, ERC-20 contract map. Includes `MAINNET_NETWORK_SLUGS` for the rejection allow-list. |
| `backend/app/providers/ethereum/abi.py` | Minimal ERC-20 ABI. |
| `backend/app/providers/ethereum/client.py` | `EthereumClient` — sync web3.py wrapped via `asyncio.to_thread`. ETH + ERC-20 reads, gas, simulate, send, receipt. |
| `backend/app/providers/ethereum/capabilities.py` | `EthereumCustodialProvider(Provider)` with Phase 1 capabilities (`read_balance`, `read_transactions`, `send_onchain`). |
| `backend/app/providers/ethereum/adapter.py` | Placeholder for Phase 2. |
| `backend/app/services/connections.py` | New methods: `import_ethereum_custodial`, `create_ethereum_custodial`, `export_private_key`, `get_active_ethereum_custodial`. Calls `Account.enable_unaudited_hdwallet_features()` once at module load. |
| `backend/app/services/onchain.py` | New `OnchainService` — gas, simulate, transfer. Insufficient-balance reverts surface as `400 INSUFFICIENT_FUNDS` (not raw text). |
| `backend/app/api/rest/connections.py` | Added the three connection-management routes + the export endpoint. |
| `backend/app/api/rest/onchain.py` | New file with `/connections/{id}/onchain/{gas,simulate,transfer}`. |
| `backend/app/api/__init__.py` | Mounted the onchain router under `/connections`. |
| `backend/app/api/deps.py` | New `get_onchain_service` factory. |
| `backend/app/main.py` | Registers `EthereumCustodialProvider` in the lifespan, exposes it on `app.state.ethereum_provider`. |
| `backend/tests/test_ethereum_credentials.py` | 8 pure-unit tests: round-trip encrypt/decrypt, hex/mnemonic shape detection, canonical mnemonic vector, malformed-input rejection. |
| `backend/tests/test_connections_ethereum_custodial.py` | 7 REST-shape tests gated on a reachable Postgres + `FERNET_KEY`. |
| `backend/docs/README.md` | Index entries for the two new docs. |
| `backend/docs/ethereum_custodial.md` | Backend-side endpoint index + file map + audit-log notes. |
| `backend/docs/testing.md` | What runs vs. what skips; manual-test recipe for live testnet flows. |

### Commands Run

| Command | Result |
| --- | --- |
| `uv sync` | OK (no new deps; `web3` and `cryptography` were already in `pyproject.toml`). |
| `uv run alembic revision -m "ethereum custodial constraints"` | Generated stub; renamed to `0002_ethereum_custodial_constraints.py` and filled the up/down migration by hand. |
| `uv run ruff check . --fix` then `uv run ruff format .` | Clean (75 files unchanged after format). |
| `uv run mypy app` | Success: no issues found in 64 source files. Six narrow `# type: ignore[arg-type]` comments added in `client.py` for web3.py's overly-strict TxParams typing — limited to the call sites. |
| `uv run pytest tests/test_ethereum_credentials.py -q` | 8 passed. |
| `uv run pytest tests/test_connections_ethereum_custodial.py -q` | 7 skipped (no DB / no Fernet key in this environment). Will execute once the user runs them with a configured `.env`. |
| `uv run alembic upgrade head` | **NOT run** — no Postgres reachable on the dev machine for this pass. The migration file is staged for the user to apply. |

### Tests And Checks

| Check | Result |
| --- | --- |
| `uv run ruff check .` | All checks passed. |
| `uv run ruff format --check .` | 75 files already formatted. |
| `uv run mypy app` | Success: no issues found in 64 source files. |
| `uv run pytest tests/test_ethereum_credentials.py -q` | 8 passed. |
| `uv run pytest -q` (full suite) | Pre-existing 4 errors are unchanged from baseline (chat / plan / ws smoke require Postgres + `FERNET_KEY`, neither of which is set up on this machine). New custodial Ethereum tests skip gracefully under the same condition. |

### Environment Variables (new / changed)

| Variable | Purpose | Default |
| --- | --- | --- |
| `ETHEREUM_RPC_URL_SEPOLIA` | RPC endpoint for Sepolia | `https://ethereum-sepolia-rpc.publicnode.com` |
| `ETHEREUM_RPC_URL_HOLESKY` | RPC endpoint for Holesky | `https://ethereum-holesky-rpc.publicnode.com` |
| `ETHEREUM_RPC_URL_POLYGON_AMOY` | RPC endpoint for Polygon Amoy | `https://polygon-amoy-bor-rpc.publicnode.com` |
| `ETHEREUM_RPC_URL_ARBITRUM_SEPOLIA` | RPC endpoint for Arbitrum Sepolia | `https://arbitrum-sepolia-rpc.publicnode.com` |
| `ETHEREUM_RPC_URL_BASE_SEPOLIA` | RPC endpoint for Base Sepolia | `https://base-sepolia-rpc.publicnode.com` |

The previous single `ETHEREUM_RPC_URL` is **removed**. `Settings.extra="ignore"` means leaving it in `.env` won't break anything but it's no longer read.

### Decisions And Shortcuts

- **Custodial encryption pattern.** Mirrors `WallbitCredentials` exactly: a `@dataclass(slots=True)` with `to_blob()` / `from_blob()` going through `app.persistence.crypto`. Address is **not** stored in the encrypted blob; it lives in `connection_metadata` (JSONB column) for fast list-without-decrypt reads.
- **Async wrapping of web3.py.** `web3>=7` ships an `AsyncWeb3` but its providers and contract API are still maturing; for hackathon-grade reliability we use the sync `Web3` and wrap each call in `asyncio.to_thread`. Cached one `Web3` per network so HTTP keep-alive sticks.
- **Gas tier multipliers** (`0.85` / `1.0` / `1.25`) are deliberately simple — the artifact doesn't pin them and testnets don't have the volatility that justifies a richer model. Easy to swap for an EIP-1559 fee-history call later.
- **ERC-20 simulate path** hand-encodes the `transfer(address,uint256)` call (selector `0xa9059cbb`) instead of pulling another helper, avoiding a `build_transaction` that needs a nonce just for a dry-run.
- **Shape-detection precedence.** Hex-key regex runs first because a 64-char hex string with valid characters is unambiguous; mnemonic detection accepts 12 / 15 / 18 / 21 / 24 word counts (BIP-39's full set).
- **`Account.enable_unaudited_hdwallet_features()`** called once at the import of `app.services.connections`. Idempotent in eth-account; documented as the official opt-in for mnemonic support.
- **Insufficient-balance handling** uses a substring heuristic (`"insufficient"` or `"exceeds balance"` in the lowered raw error) to map to a structured `400 INSUFFICIENT_FUNDS`. Other errors return `502 PROVIDER_UNAVAILABLE` with the Spanish-first user-facing message; raw revert strings are never surfaced.
- **mypy ignores** are limited to six call sites in `client.py` where web3.py's `TxParams` requires `TypedDict` literal kwargs that conflict with our generic `dict[str, Any]` flow. All other code is strict-clean.
- **Connection list shape.** `GET /api/v1/connections` now surfaces `address`, `network`, `chain_id`, and `primary_asset_hint` for `ethereum_custodial` rows by reading `connection_metadata`. Other connection types still return the lean shape (no behavior change for Wallbit).

### What's deferred (NOT in this pass)

- **DeFi (`§5.13.3`, `§5.13.4`)** — Aave V3 + Morpho Blue. The provider package is structured so adding Phase 2 means a new `defi/` subpackage (markets, positions, supply/withdraw, capability extensions). No refactor of Phase 1 needed.
- **Re-auth / 2FA on `/export-private-key`** (`§16 q17`).
- **Rate-limit on `/export-private-key`** (5/hour, `§5.13.5`). `TODO(phase-1.1)` marker in `app/api/rest/connections.py`.
- **WebSocket transfer status** on `connection.<id>` (`§5.13.2`). Topic doesn't exist yet; `TODO(phase-1.1)` marker in `app/services/onchain.py`.
- **Idempotency middleware** (deferred globally per `§16 q3`).
- **Audit-log entries** — no `audit_log_entries` table in MVP yet; when it lands, the export endpoint must redact `private_key`.

### Known Issues / Gaps

- **Holesky has no USDC.** Calling `/onchain/transfer` with `asset: "USDC"` on Holesky returns `400 ASSET_NOT_SUPPORTED`. Documented in `backend/docs/ethereum_custodial.md`.
- **USDT not shipped.** Testnet USDT is inconsistent across chains; we explicitly don't include any USDT contracts. Returns `400 ASSET_NOT_SUPPORTED`.
- **Tests for connections REST shape skip** without a reachable Postgres + `FERNET_KEY`. Bring up the existing docker-compose Postgres + generate a Fernet key per `backend/README.md`, then `uv run alembic upgrade head` to apply both `0001_init_mvp` and `0002_ethereum_custodial_constraints` before re-running the test file.
- **`docker_ps` was unreachable** in this pass; the migration was generated and inspected but **not applied**. Reviewer should run `uv run alembic upgrade head` against a fresh DB and confirm the constraint update succeeds without rewriting existing rows.

### Conflicts found vs. the artifact

- **None substantive.** One minor wording note: the artifact's import response example (`§5.13.1`) shows the connection `id` as `"conn_..."` but the rest of the surface uses unprefixed UUIDv4 strings (per `02-3` §3.1). I returned a UUID v4 string (`str(conn.id)`) to match the existing Wallbit pattern. Flag for the spec author if a `conn_` prefix is actually wanted.
- **Capabilities list** in the §5.13.1 example includes `supply_defi` / `withdraw_defi`. Phase 1 advertises `["read_balance", "read_transactions", "send_onchain"]` only; the DeFi capabilities will be added when §5.13.3 ships. Documented in `backend/docs/ethereum_custodial.md`.

### Reviewer next steps

1. `uv run alembic upgrade head` on a reachable Postgres so `0002_ethereum_custodial_constraints` actually applies.
2. With `FERNET_KEY` set and Postgres running, `uv run pytest -q` should now show 7 additional passes from `tests/test_connections_ethereum_custodial.py` (15 new + the existing suite). The 4 pre-existing chat/plan/ws errors should also resolve — they're DB-related, not custodial-related.
3. Run the manual recipe in `backend/docs/testing.md` against Sepolia using a faucet-funded wallet to validate gas / simulate / transfer end-to-end.
4. Spot-check the structlog output during a transfer to confirm no `private_key` or `mnemonic` appears in any log line.
