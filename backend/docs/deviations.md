# Backend MVP — deviations from the locked design

This MVP implementation intentionally deviates from the locked artifacts in
`.claude/artifacts/02-{1,3,4}_*.md` to fit a sub-day demo budget. Each
deviation below was approved in the implementation plan
(`/home/rpetey317/.claude/plans/let-s-start-implementing-some-tranquil-puppy.md`,
section "Deviations from locked design") and documented here for the reviewer.

## 1. No `idempotency_keys` table; `/plans/{id}/approve` does not enforce idempotency

The locked surface (02-3 §3.5) requires plan-approval to be idempotent via an
`Idempotency-Key` header backed by a dedicated table. We omit the table and
the middleware. The endpoint accepts the header but ignores it; in practice
the demo runner only approves each plan once.

Impact: a duplicate POST to `/approve` while the executor is running could
race a transition. Mitigation: the service rejects approvals when state is no
longer `pending_approval` (412 `PLAN_STALE`), which covers the most common
duplicate-click case.

## 2. No WebSocket `seq` / `since_seq` resume

The locked WS spec (02-3 §6) supports replay-on-reconnect via per-topic
sequence numbers backed by a `ws_topic_sequences` + `ws_frames_buffer`
structure. We omit both. WS clients that reconnect mid-turn lose any frames
emitted while disconnected.

Mitigation: the frontend pulls REST history (`GET /chat/sessions/{id}/messages`
and `GET /plans/{id}`) on reconnect to converge state.

## 3. No `audit_log_entries`

The locked schema (02-4) mandates an immutable audit log of provider-side
side effects. We omit it. Provider responses are stored only in
`trade_plan_steps.result_payload` and structlog output.

## 4. No canonical-ledger cluster (replaced by direct provider fetch)

Locked design (02-4 §canonical_*) builds a provider-agnostic ledger
(`canonical_assets`, `canonical_accounts`, `canonical_balances`,
`canonical_transactions`) populated by a poller. We skip all of it and have
`PortfolioService` fetch the user's Wallbit account directly per request.

Consequences:
- No multi-provider aggregation in the read path (acceptable: only Wallbit ships).
- Every `GET /balances` and `GET /transactions` call is an upstream
  Wallbit request. Rate-limit-sensitive in production; fine for the demo.

## 5. No background workers (`tasks` table, poller, ingest, tradebot runner)

The locked architecture (02-1 §6) ships a `workers/` tree for periodic
polling, ingestion, and tradebot ticks. The MVP runs everything inline in the
FastAPI process (agent task, plan executor task) using `asyncio.create_task`
with a module-level strong-reference `set[asyncio.Task]` to avoid GC.

## 6. No user profile / goals / rules

Locked schema includes profile, goals, and rule tables. We seed a single
hardcoded dev user (`00000000-0000-0000-0000-000000000001`, "Tomás Demo")
in the migration and return it unconditionally from `get_current_user_id`.
No Bearer parsing.

## 7. Anthropic non-streaming for the tool-use loop

Plan §Risks #1 flagged streaming-with-tools as fragile; the MVP uses
non-streaming `messages.create` and synthesizes `chat_token` frames from the
final assistant text so the frontend still gets a streaming UX. Listed
explicitly here because it differs from 02-1's "streaming with tool_use"
description.

## 8. Heuristic plan fallback when `ANTHROPIC_API_KEY` is unset

So the demo loop is exercisable without an API key, `ChatAgent` falls back to
a small Spanish-keyword regex that detects "comprá/vendé N usd de SYMBOL" and
proposes a `place_trade` plan. Not on the production path; remove or guard
once the key is wired.

## 9. Base mainnet allowed in addition to testnets

Locked surface (`02-3` §14 row 28) restricts the custodial Ethereum allowlist
to testnets only. We extend the allowlist with **`base`** (Base mainnet,
chain_id 8453) so the demo can show a real USDC transfer on a low-fee L2.
All other mainnet slugs (`mainnet`, `ethereum`, `polygon`, `arbitrum`,
`optimism`) remain rejected with `400 NETWORK_NOT_ALLOWED`.

Rationale: judges expect a live on-chain artifact; testnet USDC has no
narrative weight. Base was picked over Ethereum L1 / Arbitrum / Polygon for
the lowest per-tx fee.

Risk: the credential vault now holds a key that controls real funds. Mitigations:
- The demo wallet is a single hot wallet funded with a small amount; treat it
  as fully expendable.
- Existing service-layer guard rails (allowlisted networks, USDC-only
  ERC-20 routing on this network, simulate-before-transfer) still apply.
- `private_key` and `mnemonic` are never logged (verified by
  `tests/test_ethereum_credentials.py` and the redaction notes in
  `docs/ethereum_custodial.md`).
- `/export-private-key` is `chat_excluded` and rate-limit TODO already
  tracked; on mainnet that TODO is more urgent — wire the limiter before any
  non-demo use.

USDC contract used on Base mainnet: Circle native
`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (6 decimals).
