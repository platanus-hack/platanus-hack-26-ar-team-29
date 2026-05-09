# 01 - Research Brief: Agentic Money (team-29)

**Hackathon:** Platanus Hack 26 - Buenos Aires
**Track:** Agentic Money
**Dates:** 2026-05-08 to 2026-05-10 (36 hours, in-person)
**Brief written:** 2026-05-09 (the hack is happening NOW; build window is the next ~24-30 hours)
**Team-29:** Ruben Bohorquez (@Rpetey317), Juan Ignacio Medone (@juanimedone), Vladimir Kozow (@vladimirkozow), Luca Lazcano (@lazcanoluca), Alen Davies (@alendavies)

This brief is focused on a **single chosen idea direction**. No alternatives are evaluated. The earlier multi-idea brief at this path has been overwritten.

> **Note on file location:** the user request specified `artifacts/01_research_brief.md` but the agent guardrail only permits writes to `.claude/artifacts/01_research_brief.md`. The team should copy or move this file to the desired final location.

---

## 1. Track Capture

### Exact wording (UNCONFIRMED text)

The team has confirmed via README that the track is **"Agentic Money"** ([README.md](../../README.md)). The official Platanus pages we could fetch ([hack.platan.us](https://hack.platan.us/), [hack.platan.us/26-ar](https://hack.platan.us/26-ar), [hack.platan.us/tour/sponsor](https://hack.platan.us/tour/sponsor)) list event metadata but **the public-facing pages we could reach do not contain the verbatim track description for "Agentic Money."** Track-detail pages (`/26-ar/tracks`, `/26`) returned 404. Treat the literal text below as **inferred, not quoted**:

> Inferred reading (NOT a verbatim quote): the track rewards products where AI agents take real, autonomous action over money - balances, trades, transfers, allocations, or financial decisions - rather than just chat about finance.

Action item for the team on-site: **grab the verbatim track copy from the printed event materials or the in-person Notion/Discord** so the pitch can mirror the language exactly. Label this as confirmed once captured.

### Buenos Aires event facts (confirmed)

- 36-hour in-person hackathon, Buenos Aires, May 8-10, 2026 ([hack.platan.us](https://hack.platan.us/)).
- 120 hackers, teams of 3-5 ([hack.platan.us](https://hack.platan.us/)).
- Buenos Aires prize pool: **3,000 USD in BTC** plus flights to the Santiago stop in November 2026 ([hack.platan.us](https://hack.platan.us/)).
- Headline sponsor: **Anthropic**. Tour sponsors: **Profound, Supabase, Vercel, ElevenLabs** ([hack.platan.us](https://hack.platan.us/)).
- Buenos Aires-specific sponsor relevant to this idea: **Wallbit** (YC W23, Buenos Aires-based neobank with public API). Wallbit's product page literally pitches "connect your finances to AI agents" through their REST API ([Wallbit API home](https://developer.wallbit.io/), [wallbit.io/en, fetched 2026-05-09](https://www.wallbit.io/en)). This makes them the natural data/action sponsor for an Agentic Money build. **UNCONFIRMED that Wallbit is officially listed as a track sponsor** - the tour sponsor page only lists the five global sponsors above. The team should verify on-site.
- Output requirements (carry-over assumption from prior editions): open-source MIT license, deployed publicly ([hack.platan.us/24](https://hack.platan.us/24)).

### Voting & judging mechanics

- **Public voting** on [vote.hack.platan.us](https://vote.hack.platan.us/) is the primary signal. In Platanus Hack 24, 25 submitted projects collected ~2,200 total votes ([sponsor deck](https://hack.platan.us/sponsor-deck)). Each project gets a public page (e.g. `vote.hack.platan.us/projects/<slug>`).
- Past editions also had a **judge panel** (founders from Shinkansen, Plutto, Platanus Ventures) scoring per track ([huss.substack.com](https://huss.substack.com/p/ganamos-la-hackaton-de-platanus)).
- Pitches/demos are **live-streamed** ([hack.platan.us/24](https://hack.platan.us/24)).
- **Implication:** the project must be screenshot-shareable and have a sub-30-second viral hook for social, AND a clear, sober demo for the jury. Both audiences matter.

---

## 2. Platanus Context (only what is load-bearing)

- Platanus is a YC-style accelerator for LatAm. They value **early-stage technical founders, polished demos, real users in 36 hours, and shippable open-source code** ([blog.platan.us](https://blog.platan.us/), [hack.platan.us/24](https://hack.platan.us/24)).
- Past finance-track winner pattern: **Kairos** (Hack 24 at Fintual) won the finance track by parsing credit-card statements with AI and giving humans a clean, friendly summary ([huss.substack.com](https://huss.substack.com/p/ganamos-la-hackaton-de-platanus)). Lesson: **narrow, real, immediately useful, and explainable in 60 seconds.**
- Anthropic just (2026-05-05) announced ten pre-built finance-agent templates for Claude (drafting pitch decks, reviewing financial statements, compliance escalation) ([Bloomberg, 2026-05-05](https://www.bloomberg.com/news/newsletters/2026-05-05/anthropic-announces-new-ai-agents-for-financial-professionals)). The headline sponsor is publicly betting on this exact shape of product **four days before the hack starts.** Mirroring this pattern in the pitch ("personal finance analyst as an agent") is on-brand for Anthropic's judges.
- Tone: Spanish-first, LatAm pain points, demo-driven. The `platanus-hack-project.json` requires Spanish project name and description ([platanus-hack-project.json](../../platanus-hack-project.json)).

---

## 3. Sponsor Deep-Dive: Wallbit API

**Source of truth:** [developer.wallbit.io](https://developer.wallbit.io/), [developer.wallbit.io/docs/quickstart](https://developer.wallbit.io/docs/quickstart), and the dump at [developer.wallbit.io/docs/llms.txt](https://developer.wallbit.io/docs/llms.txt). All endpoints below are taken from these docs. Anything not in those docs is labeled **(unconfirmed)**.

### What Wallbit is

- LatAm-focused neobank for global remote workers (founded in Buenos Aires, YC W23) ([ycombinator.com/companies/wallbit](https://www.ycombinator.com/companies/wallbit)).
- Their pitch: "the world's first neobank with a public API" ([developer.wallbit.io](https://developer.wallbit.io/)).
- A single Wallbit account exposes: USD checking, US-stock/ETF investment account, Visa card, USDT/USDC/BTC/ETH crypto deposit addresses, transfers, robo-advisor, fees, FX rates ([wallbit.io/en](https://www.wallbit.io/en), [llms.txt endpoint dump](https://developer.wallbit.io/docs/llms.txt)).
- Operates in 90+ countries; supports USD and ARS as core fiat ([help.wallbit.io](https://help.wallbit.io/en/articles/8059439-what-is-wallbit)).
- Brokerage backend is Alpaca Securities; investment advisory is W2B (SEC-registered) per the Markets product page ([markets.wallbit.io](https://markets.wallbit.io/)).

### Auth & base URL (confirmed)

- Base URL: `https://api.wallbit.io` ([quickstart](https://developer.wallbit.io/docs/quickstart)).
- Endpoints live under the `/api/public/v1/...` prefix (e.g. `GET /api/public/v1/balance/checking`) ([quickstart](https://developer.wallbit.io/docs/quickstart)).
- Auth header: `X-API-Key: <key>` ([quickstart](https://developer.wallbit.io/docs/quickstart)).
- Keys are created in the Wallbit Dashboard under **Agents** (suggesting the product itself is built around the agent persona). Two scopes:
  - `read` - balances, transactions, assets, FX rates, fee config.
  - `trade` - execute buy/sell, change card status, robo-advisor actions ([quickstart](https://developer.wallbit.io/docs/quickstart), [llms.txt](https://developer.wallbit.io/docs/llms.txt)).
- Key shown ONCE on creation. Store securely. Revocable via `/api-key/revoke` ([llms.txt](https://developer.wallbit.io/docs/llms.txt)).

### Rate limiting (confirmed shape, unconfirmed numbers)

Headers returned on every response ([api-reference summary fetched 2026-05-09](https://developer.wallbit.io/docs/llms.txt)):

- `X-RateLimit-Limit` - requests per minute (exact number **not stated in the public docs**, treat as unknown).
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset` (unix ts)
- `Retry-After` on 429.

**Hackathon mitigation:** cache balances client-side; refresh on-demand only; debounce.

### Endpoint catalog

All paths below come from [developer.wallbit.io/docs/llms.txt](https://developer.wallbit.io/docs/llms.txt) as fetched 2026-05-09. Methods/scopes are as documented; verbs marked unconfirmed should be verified before wiring.

| Endpoint | Method | Scope | Returns / does |
|---|---|---|---|
| `/balance/checking` | GET | read | Available balances in DEFAULT account by currency. Only positive balances. |
| `/balance/stocks` | GET | read | Stocks/ETFs held with share counts and USD value. Only positive. |
| `/transactions` | GET | read | Paginated, filterable transaction history. |
| `/assets` | GET | read | Paginated catalog of stocks/ETFs/etc. Filter by `category`, `symbol`, `name`. |
| `/assets/{symbol}` | GET | read | Asset detail: price, sector, market cap, dividends, description, CEO. |
| `/wallets` | GET | read | Crypto deposit addresses for **USDT, USDC, BTC, ETH** across networks. Optional filters `currency`, `network`. |
| `/rates/{source}/{dest}` | GET | read | Stored FX rate. Returns 1.0 if same currency. |
| `/fees/{type}` | GET | read | Fee config + investment subscription tier. |
| `/account/details` | GET | read | Bank-account-level details (ACH-US, SEPA-EU). |
| `/cards` | GET | read | List of active/SUSPENDED cards. |
| `/cards/{id}/status` | PATCH/POST (verb unconfirmed) | trade | Toggle card ACTIVE/SUSPENDED. |
| `/trades` | POST | trade | BUY/SELL stocks/ETFs. MARKET or LIMIT. Amount in USD or shares (not both). |
| `/operations/internal` | POST | trade | Move funds between DEFAULT (checking) and INVESTMENT accounts. Requires KYC complete. |
| `/roboadvisor/balance` | GET | read | Risk-profile portfolios with allocation, performance, positions. |
| `/roboadvisor/deposit` | POST | trade | Deposit into robo-advisor (min $10 USD; async). |
| `/roboadvisor/withdraw` | POST | trade | Withdraw from robo-advisor. One pending withdrawal at a time. Auto-liquidates positions. |
| `/api-key/revoke` | POST | (none) | Revokes the key in the request header. |

### What Wallbit gives us that's hackathon-gold

1. **Real action surface, not just read.** With a `trade`-scoped key the agent can actually execute trades, move money between checking and investment, deposit into the robo-advisor, and freeze a card. This is the core "agentic" credibility - the agent **does**, not just suggests.
2. **Multi-asset in one account.** USD cash + US stocks/ETFs + USDT/USDC/BTC/ETH in one API. The "consolidated view" demo is trivial vs. having to integrate Binance + IOL + Lemon + Coinbase separately.
3. **Robo-advisor primitive.** `/roboadvisor/deposit` with $10 minimum is a perfect "agent puts your spare cash to work" demo moment.
4. **Card freeze/unfreeze.** Subtle but powerful "agent took action" demo - "Claude saw a duplicate charge and suspended the card."
5. **Wallbit dashboard literally calls these things 'Agents'** ([quickstart](https://developer.wallbit.io/docs/quickstart)). The vendor mental model is already aligned.

### What Wallbit does NOT give us (gaps & mitigations)

- **No data aggregation outside Wallbit.** Wallbit only sees Wallbit. To talk about "all your money in Argentina," you would have to integrate other rails (Lemon, Binance, MercadoPago, IOL) separately. **Mitigation:** explicitly position the product as Wallbit-native ("the agent that lives inside your Wallbit account"), not a multi-bank aggregator. This is a feature, not a bug - it scopes the demo cleanly.
- **No historical price series, charts, or technical indicators in the docs we found** (the `/assets/{symbol}` endpoint exposes a single price snapshot per the llms.txt summary). **Mitigation:** if charts are needed, pull from a free public source (e.g. CoinGecko for crypto, Yahoo Finance unofficial endpoints for stocks) and render client-side. **Do not advertise this as a Wallbit feature.**
- **No webhooks documented** in the docs we read. The agent will have to **poll** for new transactions / balance changes. **Mitigation:** poll `/transactions` every 30-60s during demo; for the live demo, scripted nudges work better than waiting for real events.
- **Sandbox / test mode not explicitly documented** in the pages we read ([quickstart](https://developer.wallbit.io/docs/quickstart) is silent on this). **(Unconfirmed - ask Wallbit reps on-site.)** If no sandbox: use a real account with small balances, plus a synthetic-data fallback for the demo (record a smooth happy-path walkthrough as backup video).
- **Rate-limit numbers not published** ([api-reference index](https://developer.wallbit.io/docs/llms.txt) names the headers but not the limit). **(Unconfirmed.)** Be defensive: cache + debounce.
- **KYC required for `/operations/internal`** ([llms.txt](https://developer.wallbit.io/docs/llms.txt)). For the demo account, complete KYC ahead of time or skip that endpoint entirely.
- **Not in docs we found:** crypto SEND / withdraw (only deposit-address read). The agent cannot push BTC/USDT *out*. **(Unconfirmed - verify; this might be intentional.)** **Mitigation:** position crypto as observe-only, fiat/stocks as full-action.
- **DeFi / on-chain transactions:** Wallbit appears centralized-only (no signing of arbitrary chain txs). DO NOT pitch this as a DeFi agent.

### Hackathon-day operations advice

1. **Day 1, hour 1:** Each team member with a Wallbit account creates an `Agents` API key with `read` only first; wire up `/balance/checking` end-to-end. This is the unblocking step.
2. Get a single `trade`-scoped key on a shared demo account. Lock it down; rotate via `/api-key/revoke` if anyone screenshots it accidentally.
3. Pre-fund the demo account with USD + one stock position + one stablecoin balance so the demo has texture.
4. Record a backup demo video early Sunday morning, in case of API hiccups during pitches.

### 3.8 API-key capability summary (Q&A)

**Both answers verified against live Wallbit docs on 2026-05-09. Every claim below cites the URL it came from. Confidence labels: CONFIRMED = explicitly in the cited doc; PARTIAL = listed but verb/path needs on-site verification; ABSENCE CONFIRMED = the docs we fetched do not document the capability; UNCONFIRMED = inferred or asked-but-not-verified.**

#### Q1: Can you read balances using only an API key? **YES (CONFIRMED).**

- `GET /api/public/v1/balance/checking` - scope `read` - USD/ARS checking balances ([llms.txt](https://developer.wallbit.io/docs/llms.txt)). CONFIRMED.
- `GET /api/public/v1/balance/stocks` - scope `read` - stocks/ETFs with share counts and USD value ([llms.txt](https://developer.wallbit.io/docs/llms.txt)). CONFIRMED.
- `GET /api/public/v1/wallets` - scope `read` - crypto deposit addresses (USDT/USDC/BTC/ETH) ([llms.txt](https://developer.wallbit.io/docs/llms.txt)). CONFIRMED.
- `GET /api/public/v1/roboadvisor/balance` - scope `read` - robo-advisor portfolio + positions ([llms.txt](https://developer.wallbit.io/docs/llms.txt)). CONFIRMED.
- Auth header: `X-API-Key: <key>`. No OAuth, no per-request session ([quickstart](https://developer.wallbit.io/docs/quickstart)). CONFIRMED.
- **Account scoping (CONFIRMED):** the key is created by the Wallbit user themselves in Dashboard -> Agents -> Create agent. Reads only that user's own account. **No documented OAuth or third-party / multi-user onboarding flow.** Each user must paste their own key; an external app cannot onboard *other* Wallbit users via API. (Confirmed by absence in [quickstart](https://developer.wallbit.io/docs/quickstart) and [developer.wallbit.io](https://developer.wallbit.io/); no OAuth/partner endpoints in [llms.txt](https://developer.wallbit.io/docs/llms.txt).) ABSENCE CONFIRMED for OAuth/partner flow.

#### Q2: Can you execute transactions using only an API key? **YES, partial scope (CONFIRMED).**

All write endpoints require scope `trade` and only the `X-API-Key` header. **No 2FA, OTP, email confirmation, or idempotency-key requirement is mentioned in the public docs we fetched.** (ABSENCE CONFIRMED in public docs; double-check with Wallbit reps on-site.)

- `POST /api/public/v1/trades` - BUY/SELL stocks/ETFs (MARKET/LIMIT/STOP/STOP_LIMIT) - requires complete investment KYC (returns 412 if not) ([trades/create](https://developer.wallbit.io/docs/api-reference/trades/create)). CONFIRMED.
- `POST /api/public/v1/operations/internal` - DEFAULT <-> INVESTMENT internal transfers - requires complete investment KYC (412 if not) ([operations/internal](https://developer.wallbit.io/docs/api-reference/operations/internal)). CONFIRMED.
- `POST /api/public/v1/roboadvisor/deposit` - min 10 USD, async ([roboadvisor/deposit](https://developer.wallbit.io/docs/api-reference/roboadvisor/deposit)). CONFIRMED.
- `POST /api/public/v1/roboadvisor/withdraw` - one pending withdrawal per user ([roboadvisor/withdraw](https://developer.wallbit.io/docs/api-reference/roboadvisor/withdraw)). CONFIRMED.
- Card status toggle (ACTIVE/SUSPENDED): listed in [llms.txt](https://developer.wallbit.io/docs/llms.txt) as "Update Card Status"; **exact verb/path is partial - verify on-site.** PARTIAL.
- **Crypto SEND / wallet withdraw is NOT in public docs.** `/wallets` exposes deposit addresses only; no documented endpoint to push BTC/USDT/USDC/ETH out of Wallbit. (Confirmed by absence in [llms.txt](https://developer.wallbit.io/docs/llms.txt).) ABSENCE CONFIRMED.

#### Demo blockers (must address before demo)

- **KYC gate on `/trades` and `/operations/internal`:** complete investment KYC on the demo account in hour 1 or these tools fail with 412 mid-pitch ([trades/create](https://developer.wallbit.io/docs/api-reference/trades/create), [operations/internal](https://developer.wallbit.io/docs/api-reference/operations/internal)). CONFIRMED.
- **No public sandbox documented:** demo runs on real money. Use a small pre-funded account. (Absence unconfirmed - verify with Wallbit on-site; not documented in [quickstart](https://developer.wallbit.io/docs/quickstart) or [llms.txt](https://developer.wallbit.io/docs/llms.txt).) UNCONFIRMED.
- **Single-user key model:** judges/audience cannot try the agent on their *own* balances live. The demo is bound to the team's account ([quickstart](https://developer.wallbit.io/docs/quickstart)). CONFIRMED.
- **No documented 2FA / email-confirm on writes:** the agent *can* fire transactions inside a 30-second demo window. (Absence confirmed in public docs at [trades/create](https://developer.wallbit.io/docs/api-reference/trades/create), [operations/internal](https://developer.wallbit.io/docs/api-reference/operations/internal), [roboadvisor/deposit](https://developer.wallbit.io/docs/api-reference/roboadvisor/deposit), [roboadvisor/withdraw](https://developer.wallbit.io/docs/api-reference/roboadvisor/withdraw); double-check with Wallbit on-site to be safe.) ABSENCE CONFIRMED.
- **No crypto-send capability:** if the "money shot" depends on pushing BTC/USDT out of Wallbit, redesign around fiat + stocks + robo-advisor ([llms.txt](https://developer.wallbit.io/docs/llms.txt)). CONFIRMED via absence.

### 3.9 Investable catalog: what you can actually buy via Wallbit's API

**Purpose:** definitive enumeration of every product class Wallbit's public API actually lets the agent *acquire/invest in*, with confidence labels. Compiled 2026-05-09 from [developer.wallbit.io/docs/llms.txt](https://developer.wallbit.io/docs/llms.txt) plus per-endpoint pages cited inline.

| Product class | Endpoint | Order types | Asset universe (per docs) | KYC? | Limits / notes | Confidence |
|---|---|---|---|---|---|---|
| **US stocks & ETFs** | `POST /api/public/v1/trades` | MARKET, LIMIT, STOP, STOP_LIMIT (all four; per [trades/create](https://developer.wallbit.io/docs/api-reference/trades/create)) | Symbols served by `GET /assets`, paginated catalog. 12 categories: `MOST_POPULAR`, `ETF`, `DIVIDENDS`, `TECHNOLOGY`, `HEALTH`, `CONSUMER_GOODS`, `ENERGY_AND_WATER`, `FINANCE`, `REAL_ESTATE`, `TREASURY_BILLS`, `VIDEOGAMES`, `ARGENTINA_ADR` ([assets/list](https://developer.wallbit.io/docs/api-reference/assets/list)). Asset fields include `asset_type`, `exchange`, `sector`, `country`, `market_cap_m`, dividends. Total count not stated in docs (markets.wallbit.io marketing claims "4,000+" - verify on-site). | YES (412 if not) | Amount in USD or shares (not both). | CONFIRMED |
| **Treasury bills** | Same `POST /trades` (filter `category=TREASURY_BILLS` in `/assets` to discover) | MARKET/LIMIT (assumed same) | One of the 12 `/assets` categories ([assets/list](https://developer.wallbit.io/docs/api-reference/assets/list)). Specific tickers not enumerated in docs. | YES (same `/trades` KYC gate) | Verify ticker liquidity before demo. | PARTIAL (category exists; specific tickers not enumerated in public docs - verify on-site) |
| **Argentine ADRs (CEDEAR-like exposure)** | Same `POST /trades` (filter `category=ARGENTINA_ADR`) | MARKET/LIMIT (assumed same) | Per-page filter in `/assets` ([assets/list](https://developer.wallbit.io/docs/api-reference/assets/list)). Note: these are US-listed ADRs of Argentine names, not local-market CEDEARs (Wallbit settles via Alpaca per [markets.wallbit.io](https://markets.wallbit.io/)). | YES | Useful Argentine narrative hook ("compra ADR de YPF") even though settlement is USD/Alpaca. | CONFIRMED (category) / PARTIAL (semantics) |
| **Robo-advisor portfolios (Conservative / Moderate / Aggressive)** | `POST /api/public/v1/roboadvisor/deposit` | n/a (deposit, not order) | Three risk tiers: `risk_level: 1` (Conservative), `2` (Moderate), `3` (Aggressive). Holdings are sample-shown as VTI/BND in docs but actual basket is not explicitly enumerated; `/roboadvisor/balance` returns `Cash` vs `Securities` % split per portfolio ([roboadvisor/balance](https://developer.wallbit.io/docs/api-reference/roboadvisor/balance)). "Chest" portfolios also referenced as a separate type. | YES (investment KYC implied; same as `/operations/internal`) | **$10 USD minimum**. Async settlement. One pending withdrawal at a time on `/roboadvisor/withdraw`. | CONFIRMED (tiers, min, async) / PARTIAL (exact tickers in basket not in public docs) |
| **Crypto BUY from USD/ARS balance** | **NO ENDPOINT** | n/a | n/a | n/a | **Confirmed via absence in [llms.txt](https://developer.wallbit.io/docs/llms.txt)**: only `GET /wallets` exists for crypto, and it returns *deposit addresses only* (currencies USDT/USDC, networks: ethereum, arbitrum, solana, polygon, tron). No `/crypto/buy`, `/swap`, `/exchange`, or `/wallets/buy` endpoint exists. To get crypto INTO Wallbit, the user must deposit from an external wallet to the Wallbit-issued address. **The agent cannot acquire crypto.** | n/a | ABSENCE CONFIRMED |
| **Crypto SELL / off-ramp** | **NO ENDPOINT** | n/a | n/a | n/a | Same absence confirmed. The agent cannot push BTC/USDT/USDC/ETH *out* of Wallbit either. | n/a | ABSENCE CONFIRMED |
| **Internal account transfer (DEFAULT <-> INVESTMENT)** | `POST /api/public/v1/operations/internal` | n/a | The `from`/`to` parameters accept **only two enum values**: `DEFAULT` and `INVESTMENT` ([operations/internal](https://developer.wallbit.io/docs/api-reference/operations/internal)). | YES (412 if not) | **No P2P between Wallbit users**; no path to/from a "crypto" account-type via this endpoint. | CONFIRMED |
| **P2P transfers between Wallbit users** | **NO ENDPOINT** | n/a | n/a | n/a | Confirmed via absence in [llms.txt](https://developer.wallbit.io/docs/llms.txt) and [operations/internal](https://developer.wallbit.io/docs/api-reference/operations/internal) (which only supports DEFAULT/INVESTMENT enum values). | n/a | ABSENCE CONFIRMED |
| **Fiat OFF-ramp (push USD/ARS to external bank)** | **NO ENDPOINT** | n/a | n/a | n/a | `GET /account` returns the user's *inbound* deposit instructions (ACH-US, SEPA-EU) - i.e. the rails for receiving money INTO Wallbit, not for sending OUT ([llms.txt](https://developer.wallbit.io/docs/llms.txt)). No `/withdrawals`, `/payouts`, `/transfers/external`, or wire-out endpoint in public docs. | n/a | ABSENCE CONFIRMED |
| **Card management** | `GET /cards`, `PATCH /cards/{id}/status` | n/a | Toggle card status between `ACTIVE` and `SUSPENDED` ([llms.txt](https://developer.wallbit.io/docs/llms.txt)). | n/a | **Only status toggle.** No documented endpoints for setting limits, ATM PIN, ordering a new card, freezing-vs-suspending distinction, or replacing a lost card. | CONFIRMED (status toggle) / ABSENCE CONFIRMED (everything else) |
| **FX / currency conversion** | `GET /api/public/v1/rates/{source}/{dest}` (read-only quote) | n/a | Returns stored FX rate ([llms.txt](https://developer.wallbit.io/docs/llms.txt)). **Read-only**: no `POST /fx/convert` or `/exchange` endpoint to actually swap USD for ARS programmatically. | n/a | The rate endpoint is for *display*; it does not convert balances. | ABSENCE CONFIRMED for execute-side |
| **Subscriptions / recurring rules** | **NO ENDPOINT** | n/a | n/a | n/a | No documented cron/recurring-deposit/standing-order endpoint ([llms.txt](https://developer.wallbit.io/docs/llms.txt)). The agent must implement standing rules in its own backend. | n/a | ABSENCE CONFIRMED |

**Summary of what the agent can ACQUIRE on the user's behalf (the actual investable catalog):**

1. **US-listed stocks & ETFs** across 12 themed categories from `/assets`, executed via `/trades` with MARKET/LIMIT/STOP/STOP_LIMIT order types. CONFIRMED.
2. **Treasury bills** as a sub-category. CONFIRMED (category) / PARTIAL (specific tickers).
3. **Argentina ADRs** as a sub-category - the only natively LatAm-flavored asset in the catalog. CONFIRMED (category).
4. **Robo-advisor portfolio shares** in three risk tiers, $10 minimum, async, via `/roboadvisor/deposit`. CONFIRMED.
5. **That's the entire investable catalog.** Crypto is observe-only (deposit-address-read). Fiat moves are limited to the DEFAULT<->INVESTMENT internal swap. There is **no P2P, no fiat off-ramp, no crypto buy/sell, no FX execution, no card-limit / new-card-issue, no recurring-rule** endpoint.

**Pitch-design implication:** the demo's "money shot" must live within the four-product loop above. The cleanest agent narrative is: *paycheck arrives in DEFAULT -> agent proposes split -> agent (a) moves a slice to INVESTMENT via `/operations/internal`, (b) buys a stock/ETF via `/trades`, (c) deposits to robo-advisor via `/roboadvisor/deposit`, (d) leaves the rest in DEFAULT.* That is the entire investable surface and it is more than enough for a winning 30-second clip. **Do not promise crypto trading, P2P, or fiat off-ramp in the pitch** - they are not in the public API as of 2026-05-09.

### 3.10 End-to-end read/write flow: fetching assets and executing a trade

**Purpose:** definitive, step-by-step walkthrough of the agent loop a Pampa-style chat agent runs for a single "the user wants to invest some money" interaction. Every endpoint, request shape, response shape, and error code below is cited to the public Wallbit docs as fetched 2026-05-09. Anything not in those docs is labeled. The planner and coder lift this into the execution plan as-is.

#### Step 1 - Authenticate

- Header: `X-API-Key: <key>` ([quickstart](https://developer.wallbit.io/docs/quickstart)). No OAuth, no per-request signing nonce, no secret. CONFIRMED.
- Scopes: `read` (balances/transactions/assets/rates/fees) and `trade` (writes). The same key carries both if granted at creation in Dashboard -> Agents ([quickstart](https://developer.wallbit.io/docs/quickstart)). CONFIRMED.
- 401 means **missing or invalid API Key** (verbatim string from [trades/create](https://developer.wallbit.io/docs/api-reference/trades/create) and [balance/checking](https://developer.wallbit.io/docs/api-reference/balance/checking)). Surface to user as: "Tu API key esta mal o vencida - revocala y crea una nueva."
- 403 means **insufficient permissions** for the called scope (e.g. `read`-only key calling `/trades`). Verbatim string from same docs. Surface to user as: "Esta key no puede operar - tenes que crear una con permiso de `trade`."
- The agent must NEVER log the key. Encrypt at rest in Supabase (per §6 plan).

#### Step 2 - Read user state ("available investable USD")

Call in this order, in parallel where possible:

1. `GET /api/public/v1/balance/checking` -> `{ data: [{ currency: "USD", balance: 1000.5 }, ...] }`. Only positive balances are returned ([balance/checking](https://developer.wallbit.io/docs/api-reference/balance/checking)). CONFIRMED.
2. `GET /api/public/v1/balance/stocks` -> `{ data: [{ symbol: "AAPL", shares: 10.5 }, ...] }`. Note: the **public spec does NOT include a per-position USD market value**; only `symbol` and `shares` ([balance/stocks](https://developer.wallbit.io/docs/api-reference/balance/stocks)). To compute USD value, the agent must cross-reference each symbol with `/assets/{symbol}` for current price. (Field name `value` was inferred in earlier brief notes - **verify on-site; the public schema we read only documents `symbol` and `shares`.**)
3. `GET /api/public/v1/roboadvisor/balance` -> portfolios array with `balance`, `portfolio_value`, `cash`, `cash_available_withdrawal`, `risk_profile.risk_level` (1-3), `assets[]` with `symbol/shares/market_value/price`, `allocation.{cash,securities}` percentages, `has_pending_transactions` boolean ([roboadvisor/balance](https://developer.wallbit.io/docs/api-reference/roboadvisor/balance)). CONFIRMED.
4. `GET /api/public/v1/wallets` -> crypto deposit addresses (USDT/USDC/BTC/ETH) ([llms.txt](https://developer.wallbit.io/docs/llms.txt)). CONFIRMED. Crypto is observe-only - the agent CANNOT use these to compute "investable USD" for an action.

**Computing "available investable USD":**

```
investable_usd = (USD entry of /balance/checking) + (DEFAULT->INVESTMENT slack)
```

Note: **`/balance/checking` returns the DEFAULT account balance**. To buy stocks/ETFs the funds must already be in `INVESTMENT`. If the user has only DEFAULT cash, the agent must FIRST call `/operations/internal { from: DEFAULT, to: INVESTMENT, amount, currency: "USD" }` ([operations/internal](https://developer.wallbit.io/docs/api-reference/operations/internal)) BEFORE calling `/trades`. There is no documented "investment cash" balance endpoint distinct from `/balance/checking`; the planner must treat investment-side cash as derived from prior operations or accept a 422 "Insufficient funds" from `/trades` and recover. **(Field for "investment cash" not enumerated in public docs - verify on-site.)**

#### Step 3 - Read product catalog

`GET /api/public/v1/assets?category=ETF&search=SPY&page=1&limit=10` ([assets/list](https://developer.wallbit.io/docs/api-reference/assets/list)).

Query params (CONFIRMED): `category` (one of 12 enumerated values: `MOST_POPULAR`, `ETF`, `DIVIDENDS`, `TECHNOLOGY`, `HEALTH`, `CONSUMER_GOODS`, `ENERGY_AND_WATER`, `FINANCE`, `REAL_ESTATE`, `TREASURY_BILLS`, `VIDEOGAMES`, `ARGENTINA_ADR`); `search` (max 100 chars - matches symbol, name, or keywords); `page` (>=1, default 1); `limit` (1-50, default 10).

Response shape (CONFIRMED):
```json
{
  "data": [{
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "price": 175.5,
    "asset_type": "Stock",
    "exchange": "NASDAQ",
    "sector": "Technology",
    "market_cap_m": "2750000",
    "logo_url": "https://static.atomicvest.com/AAPL.svg"
  }],
  "pages": 15,
  "current_page": 1,
  "count": 150
}
```

**Filtering by country/sector/dividend** is NOT a documented top-level query parameter. `country`, `sector`, `dividend` are response *fields*, not filterable inputs - the agent must paginate and filter client-side, OR use the `category` enum (e.g. `category=DIVIDENDS` instead of `dividend>0`). ABSENCE CONFIRMED for fine-grained filters in [assets/list](https://developer.wallbit.io/docs/api-reference/assets/list).

`GET /api/public/v1/assets/{symbol}` returns the same fields plus `description`, `description_es`, `country`, `ceo`, `employees`, and a nullable `dividend` object ([assets/get](https://developer.wallbit.io/docs/api-reference/assets/get)). CONFIRMED.

#### Step 4 - Quote / market data

There is **no separate quote/quotes endpoint in the public docs**. The `price` field on `/assets` and `/assets/{symbol}` is a **single numeric value with no timestamp** ([assets/get](https://developer.wallbit.io/docs/api-reference/assets/get)). ABSENCE CONFIRMED for an `as_of` field.

**Staleness risk:** the agent treats `/assets/{symbol}.price` as the canonical pre-trade price for a MARKET order's USD-amount sizing, but **must not present it as a guaranteed execution price**. For MARKET orders, the actual fill price is whatever the brokerage backend (Alpaca, per [markets.wallbit.io](https://markets.wallbit.io/)) returns post-fill. For LIMIT orders, the agent uses `/assets/{symbol}.price` to derive a sensible `limit_price` (e.g. price + 0.5%) but the user (or the agent's standing rule) must explicitly set the limit.

#### Step 5 - Validate preconditions

- **KYC complete?** No documented `/account/kyc` or `/me` endpoint that returns a structured KYC status. The agent must **attempt-and-handle**: a 412 from `/trades` or `/operations/internal` with body string `"You must complete your investment account verification before performing this operation"` is the canonical KYC-incomplete signal ([trades/create](https://developer.wallbit.io/docs/api-reference/trades/create), [operations/internal](https://developer.wallbit.io/docs/api-reference/operations/internal)). CONFIRMED. **(A pre-flight KYC endpoint is ABSENT in public docs - verify on-site.)** Mitigation: complete KYC on the demo account before the hack.
- **Market open?** The public docs do NOT expose market-hours metadata. ABSENCE CONFIRMED. The agent attempts the order; on rejection (likely 422 with a validation message - **exact wording for after-hours rejection is not in public docs**), the agent surfaces "el mercado esta cerrado, queda guardado para cuando abra?" or queues a LIMIT order with `time_in_force: GTC`.
- **Min order size, lot constraints?** Not enumerated in [trades/create](https://developer.wallbit.io/docs/api-reference/trades/create). Note: `/trades` accepts `amount` (USD) OR `shares` (float), so fractional shares appear supported (response example shows `shares: 0.5847953`). The robo-advisor has an explicit $10 minimum on `/roboadvisor/deposit` ([roboadvisor/deposit](https://developer.wallbit.io/docs/api-reference/roboadvisor/deposit)). CONFIRMED.
- **Internal-transfer limits:** `/operations/internal` documents `amount` range 1-999,999 USD ([operations/internal](https://developer.wallbit.io/docs/api-reference/operations/internal)). CONFIRMED.

#### Step 6 - Build the order body

`POST /api/public/v1/trades` request body fields ([trades/create](https://developer.wallbit.io/docs/api-reference/trades/create)) - **all CONFIRMED**:

| Field | Required | Type | Allowed values | Notes |
|---|---|---|---|---|
| `symbol` | yes | string | e.g. `AAPL`, `SPY` | Same symbols served by `/assets` |
| `direction` | yes | enum | `BUY`, `SELL` | (Note: field name is `direction`, not `side`.) |
| `currency` | yes | string | `USD` only | "Currency (only USD supported)" - quoted from spec |
| `order_type` | yes | enum | `MARKET`, `LIMIT`, `STOP`, `STOP_LIMIT` | All four supported |
| `amount` | conditional | float | USD notional | Specify `amount` OR `shares`, NOT both |
| `shares` | conditional | float | fractional supported | Specify `amount` OR `shares`, NOT both |
| `limit_price` | conditional | float | required for `LIMIT` and `STOP_LIMIT` | |
| `stop_price` | conditional | float | required for `STOP` and `STOP_LIMIT` | |
| `time_in_force` | conditional | enum | `DAY`, `GTC` | "required for LIMIT" per spec |

**MARKET BUY of $500 of SPY** (concrete JSON):
```json
{
  "symbol": "SPY",
  "direction": "BUY",
  "currency": "USD",
  "order_type": "MARKET",
  "amount": 500
}
```

**LIMIT BUY of 1.5 shares of SPY at <= $350** (concrete JSON):
```json
{
  "symbol": "SPY",
  "direction": "BUY",
  "currency": "USD",
  "order_type": "LIMIT",
  "shares": 1.5,
  "limit_price": 350.00,
  "time_in_force": "GTC"
}
```

**STOP SELL** (sell when price drops to $340):
```json
{
  "symbol": "SPY",
  "direction": "SELL",
  "currency": "USD",
  "order_type": "STOP",
  "shares": 1.5,
  "stop_price": 340.00
}
```

CONFIRMED via [trades/create](https://developer.wallbit.io/docs/api-reference/trades/create).

**Order types in plain Spanish (for the agent's user-facing copy):**
- MARKET = "compra ya, al precio que el mercado de"
- LIMIT = "compra solo si el precio es <= X" (BUY) / "vende solo si el precio es >= X" (SELL)
- STOP = "cuando el precio toque X, dispara una orden a mercado" (typically protective stop-loss)
- STOP_LIMIT = combo: cuando llegue a stop_price, dispara una LIMIT con limit_price

#### Step 7 - POST the order

Request:
```
POST https://api.wallbit.io/api/public/v1/trades
Headers:
  X-API-Key: <key with trade scope>
  Content-Type: application/json
Body: <JSON from Step 6>
```

Success response (200) - **CONFIRMED via [trades/create](https://developer.wallbit.io/docs/api-reference/trades/create)**:
```json
{
  "data": {
    "symbol": "AAPL",
    "direction": "BUY",
    "amount": 100,
    "shares": 0.5847953,
    "status": "REQUESTED",
    "order_type": "MARKET",
    "limit_price": null,
    "stop_price": null,
    "time_in_force": null,
    "created_at": "2024-01-15T10:30:00.000000Z",
    "updated_at": "2024-01-15T10:30:00.000000Z"
  }
}
```

**Initial status is `REQUESTED`**, not PENDING/ACCEPTED/FILLED. The response shape does NOT include an explicit `id` or `uuid` field at this surface - **the public spec example only documents the fields above. ABSENCE CONFIRMED for an `id`/`uuid` on the trades response (verify on-site).** This is a critical gap because there is no documented `GET /trades/{id}` endpoint either (we attempted to fetch [api-reference/trades/get](https://developer.wallbit.io/docs/api-reference/trades/get) on 2026-05-09 and got 404 - it does not exist publicly). Status tracking goes through `/transactions` instead (see Step 9).

#### Step 8 - Handle errors

Documented error codes for `/trades` ([trades/create](https://developer.wallbit.io/docs/api-reference/trades/create)) - **CONFIRMED**:

| HTTP | Verbatim message | Agent's user-facing copy (Spanish) |
|---|---|---|
| 400 | "Insufficient funds to complete the operation" | "No te alcanza la plata - tenes X USD en cuenta de inversion" |
| 401 | "Missing or invalid API Key" | "Tu API key vencio - generate una nueva" |
| 403 | "Insufficient permissions" | "Esta key no puede operar - necesita scope `trade`" |
| 412 | "You must complete your investment account verification before performing this operation" | "Falta completar tu KYC de inversion - te paso el link" |
| 422 | Validation errors with field-specific messages | "Pedido invalido: <field>: <reason>" |
| 429 | Rate limit exceeded; body includes `retry_after` (seconds) | "Estoy yendo muy rapido, espera <N>s y reintento" |

Note on 5xx: the public docs we fetched do NOT enumerate 500/502/503 ([trades/create](https://developer.wallbit.io/docs/api-reference/trades/create) lists 400/401/403/412/422/429 only). ABSENCE CONFIRMED. The agent must still handle network/5xx defensively (retry with exponential backoff capped at 3 attempts; never auto-retry a successful POST that returned 200 - see Idempotency below).

`/operations/internal` adds a 412 case for **"Account locked"** and **"account migrating"** in addition to KYC ([operations/internal](https://developer.wallbit.io/docs/api-reference/operations/internal)). CONFIRMED.

`/roboadvisor/deposit` adds a documented 404 case: **"No query results for model [UserRoboAdvisor]"** when `robo_advisor_id` is unknown ([roboadvisor/deposit](https://developer.wallbit.io/docs/api-reference/roboadvisor/deposit)). CONFIRMED.

#### Step 9 - Poll for fill / read order status

There is **no `GET /trades/{id}` endpoint in public docs** ([api-reference/trades/get](https://developer.wallbit.io/docs/api-reference/trades/get) returned 404 on 2026-05-09). ABSENCE CONFIRMED.

There are **no documented webhooks** in [llms.txt](https://developer.wallbit.io/docs/llms.txt). ABSENCE CONFIRMED.

The canonical status path is `GET /api/public/v1/transactions` ([transactions/list](https://developer.wallbit.io/docs/api-reference/transactions/list)) with filters:
- `type=TRADE` (filter to trade-shaped transactions)
- `from_date=YYYY-MM-DD` (today)
- `limit=10`, `page=1`

Response (CONFIRMED):
```json
{
  "data": [{
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "type": "TRADE",
    "source_currency": {"code": "USD"},
    "dest_currency": {"code": "USD"},
    "source_amount": 500,
    "dest_amount": 1.4205,
    "status": "COMPLETED",
    "created_at": "2026-05-09T10:30:00.000000Z",
    "comment": null
  }],
  "pages": 1, "current_page": 1, "count": 1
}
```

The public docs explicitly enumerate `"COMPLETED"` as the example status string but do NOT publish the full status state machine ([transactions/list](https://developer.wallbit.io/docs/api-reference/transactions/list)). The trades endpoint emits initial status `REQUESTED` ([trades/create](https://developer.wallbit.io/docs/api-reference/trades/create)) and the robo-advisor deposit emits initial `PENDING` ([roboadvisor/deposit](https://developer.wallbit.io/docs/api-reference/roboadvisor/deposit)) - **the full transition path is NOT documented**. Plausible terminal states by inference: `COMPLETED`, `FAILED`, `CANCELLED`. Treat unknown statuses as "still in flight; keep polling."

**Polling strategy for the agent (to avoid hammering rate limits):**

1. After POSTing `/trades`, wait 2-3 seconds.
2. `GET /transactions?type=TRADE&from_date=<today>&limit=10` and look for the most recent transaction matching the order's symbol + direction + source_amount.
3. If status is `COMPLETED` -> success. If still `REQUESTED`/`PENDING` -> wait 3-5 more seconds, retry. Cap at ~30 seconds, then surface "esta tardando, te aviso cuando confirme" and persist the polling task in Supabase to continue in the background.
4. **Matching the trades response to a transactions row is fragile** because the trades response (per public docs) does not return a UUID. The agent's matching key has to be `(symbol, direction, source_amount, created_at within +/- 5s)`. **(Verify on-site whether `/trades` actually returns a UUID - the public spec example omits it.)**

#### Step 10 - Re-read balances / positions

After the transaction status flips to `COMPLETED`, the agent re-reads:
- `GET /balance/checking` -> USD reduced by ~`source_amount` (less the fill price diff).
- `GET /balance/stocks` -> `shares` for the bought symbol increased by `dest_amount` (or appears as a new position row).
- (Optional) `GET /assets/{symbol}` -> current price, to compute the position's current USD value for display.

#### Step 11 - Surface to user

Natural-language confirmation, Argentine register:

> "Listo. Compre 1.4205 acciones de SPY por 500 USD. Tu posicion ahora es 1.4205 acciones (~498 USD). Te quedan 4,000 USD en checking."

Persist a row in Supabase `audit_log` with: tool name, request body, response body, status, timestamp, user-facing message. This is the trust ceremony.

#### Cross-cutting gotchas

**Idempotency.** The public docs do **NOT mention an `Idempotency-Key` header or a client-side dedup token** for `/trades`, `/operations/internal`, or `/roboadvisor/deposit` ([trades/create](https://developer.wallbit.io/docs/api-reference/trades/create), [operations/internal](https://developer.wallbit.io/docs/api-reference/operations/internal), [roboadvisor/deposit](https://developer.wallbit.io/docs/api-reference/roboadvisor/deposit)). ABSENCE CONFIRMED. **Strategy:** the agent maintains an in-flight order ledger in Supabase keyed by `(user_id, tool_call_id)` (Anthropic's tool-use API gives each tool invocation a stable `tool_use_id`). Before sending a `/trades` POST, the agent (a) checks the ledger - if a recent in-flight entry exists for this `tool_use_id`, abort and poll `/transactions` instead; (b) writes a `PENDING` row to the ledger; (c) sends the POST; (d) on 200 OK, marks the ledger row with the response payload; (e) on network timeout, **never blindly retries** - polls `/transactions?type=TRADE&from_date=today` to determine whether the order actually landed before deciding to retry. This is the only safe pattern given Wallbit's lack of an idempotency primitive.

**Async vs sync.** `/trades` returns immediately with `status: REQUESTED` - settlement is asynchronous, even for MARKET orders ([trades/create](https://developer.wallbit.io/docs/api-reference/trades/create)). The agent always polls `/transactions`. `/roboadvisor/deposit` is **explicitly documented as async** with initial `status: PENDING` and the docs say *"the transaction is processed asynchronously and its status can be checked via the transactions endpoint"* ([roboadvisor/deposit](https://developer.wallbit.io/docs/api-reference/roboadvisor/deposit)). CONFIRMED. `/operations/internal` returns a Transaction object on success but the docs do NOT explicitly document it as async; the agent should still poll `/transactions` to confirm `COMPLETED`.

**Quantity vs notional.** Wallbit's `/trades` accepts EITHER `amount` (USD) OR `shares` (float, fractional supported) - not both ([trades/create](https://developer.wallbit.io/docs/api-reference/trades/create)). CONFIRMED. **Agents should default to `amount`** because users speak in dollars ("compra 500 de SPY"). Conversion logic (`qty = floor(notional / price)`) is unnecessary - Wallbit accepts notional natively. The example response shows fractional shares like `0.5847953`, so leftover-cash handling is internal to the brokerage.

**Rate limits.** Headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` (unix ts) are returned on every response; 429 includes `retry_after` (seconds) ([balance/checking](https://developer.wallbit.io/docs/api-reference/balance/checking), [trades/create](https://developer.wallbit.io/docs/api-reference/trades/create)). CONFIRMED for header presence; **specific numbers (requests-per-minute) are NOT published** - we attempted [docs/rate-limiting](https://developer.wallbit.io/docs/rate-limiting) and got 404. ABSENCE CONFIRMED. **Back-off:** on 429, sleep for `retry_after` seconds, then exponential back-off capped at 30s for further failures. Cache `/balance/checking` and `/assets` responses in-memory for 30-60s; never call them more than once per Claude tool invocation.

**KYC pre-check.** No endpoint documented. ABSENCE CONFIRMED. Mitigation: the demo account completes KYC on Day 1, hour 1. The agent's defensive code path: catch 412, surface "necesitas completar el KYC de inversion antes de operar - te paso el link de Wallbit," and end the action gracefully.

**Single-user model.** One key reads only one user's account ([quickstart](https://developer.wallbit.io/docs/quickstart)). The Pampa app stores keys per user in Supabase encrypted at rest; the agent's tool layer reads the current user's key from session, never from a global env var.

#### LLM-agent translation (Anthropic tool-use shape)

The chat agent is a Claude session with the following tool definitions (names match §6 plan; descriptions are the "spec" the LLM sees):

```python
tools = [
  {
    "name": "read_balances",
    "description": "Returns the user's full Wallbit balance snapshot: DEFAULT checking by currency, stocks/ETFs held, robo-advisor portfolios, and crypto deposit addresses. Read-only, fast (~3 parallel calls).",
    "input_schema": {"type": "object", "properties": {}, "required": []}
  },
  {
    "name": "search_assets",
    "description": "Search the Wallbit catalog of investable stocks/ETFs. Returns symbol, name, price, sector, exchange, market_cap. PRICE IS NOT REAL-TIME-STAMPED - use only for sizing, not as guaranteed execution price.",
    "input_schema": {
      "type": "object",
      "properties": {
        "category": {"type": "string", "enum": ["MOST_POPULAR","ETF","DIVIDENDS","TECHNOLOGY","HEALTH","CONSUMER_GOODS","ENERGY_AND_WATER","FINANCE","REAL_ESTATE","TREASURY_BILLS","VIDEOGAMES","ARGENTINA_ADR"]},
        "search": {"type": "string", "description": "Free-text search by symbol/name/keyword (max 100 chars)"},
        "limit": {"type": "integer", "default": 10, "maximum": 50}
      },
      "required": []
    }
  },
  {
    "name": "get_asset_quote",
    "description": "Get full detail for a single symbol. NOTE: Wallbit does not expose a separate real-time quote endpoint - this returns the same `price` field as search_assets, no timestamp. Treat as 'most recent known price', not real-time.",
    "input_schema": {"type":"object","properties":{"symbol":{"type":"string"}}, "required":["symbol"]}
  },
  {
    "name": "transfer_internal",
    "description": "Move USD between DEFAULT (checking) and INVESTMENT accounts. Required before buying stocks if cash is in DEFAULT. Requires investment KYC complete (412 if not). Range 1-999,999 USD.",
    "input_schema": {
      "type":"object",
      "properties":{
        "from":{"type":"string","enum":["DEFAULT","INVESTMENT"]},
        "to":{"type":"string","enum":["DEFAULT","INVESTMENT"]},
        "amount":{"type":"number","minimum":1,"maximum":999999},
        "currency":{"type":"string","enum":["USD"]}
      },
      "required":["from","to","amount","currency"]
    }
  },
  {
    "name": "place_trade",
    "description": "Place a stock/ETF order. Returns initial status REQUESTED; settle is async, must be confirmed via get_order_status. Requires investment KYC (412 if not). Specify amount OR shares, not both.",
    "input_schema": {
      "type":"object",
      "properties":{
        "symbol":{"type":"string"},
        "direction":{"type":"string","enum":["BUY","SELL"]},
        "currency":{"type":"string","enum":["USD"]},
        "order_type":{"type":"string","enum":["MARKET","LIMIT","STOP","STOP_LIMIT"]},
        "amount":{"type":"number","description":"USD notional"},
        "shares":{"type":"number","description":"Fractional shares allowed"},
        "limit_price":{"type":"number"},
        "stop_price":{"type":"number"},
        "time_in_force":{"type":"string","enum":["DAY","GTC"]}
      },
      "required":["symbol","direction","currency","order_type"]
    }
  },
  {
    "name": "get_order_status",
    "description": "Poll Wallbit /transactions filtered by type=TRADE, from_date=today. Returns the most recent matching transaction with its current status. Use after place_trade to know when an order moves from REQUESTED to COMPLETED.",
    "input_schema": {
      "type":"object",
      "properties":{
        "symbol":{"type":"string"},
        "direction":{"type":"string","enum":["BUY","SELL"]},
        "approx_amount":{"type":"number"}
      },
      "required":["symbol","direction"]
    }
  },
  {
    "name": "deposit_roboadvisor",
    "description": "Deposit USD into a robo-advisor portfolio (min $10, async). Status starts PENDING, confirm via get_order_status / transactions.",
    "input_schema": {
      "type":"object",
      "properties":{
        "robo_advisor_id":{"type":"integer"},
        "amount":{"type":"number","minimum":10},
        "from":{"type":"string","enum":["DEFAULT","INVESTMENT"]}
      },
      "required":["robo_advisor_id","amount","from"]
    }
  }
]
```

Each tool wraps the corresponding endpoint plus the two-step confirm gate (§6 MVP item 3): the agent calls the tool, the UI surfaces "Aprobar / Modificar / Saltar," and only after the user clicks Aprobar does the actual HTTP POST fire.

#### Simulated agent transcript: "comprame 500 dolares de SPY"

```
USER: comprame 500 dolares de SPY

AGENT (thinking, no tool yet):
  Plan: (1) check user has >= 500 USD investable, (2) confirm SPY is a real symbol & get price, (3) propose, (4) on approval place MARKET BUY of 500.

AGENT -> tool: read_balances({})
TOOL RESULT:
  {
    "checking": [{"currency":"USD","balance":4500}],
    "stocks": [{"symbol":"AAPL","shares":2}],
    "roboadvisor": [{"id":1,"balance":1500,"risk_profile":{"risk_level":3}}]
  }

AGENT -> tool: search_assets({"search":"SPY","limit":3})
TOOL RESULT:
  { "data": [{"symbol":"SPY","name":"SPDR S&P 500 ETF","price":352.10,"asset_type":"ETF"}], "count": 1 }

AGENT (thinking):
  4500 USD checking is in DEFAULT. To buy SPY I need INVESTMENT cash.
  I'll plan: transfer_internal 500 DEFAULT->INVESTMENT, then place_trade.

AGENT -> user (proposal, awaiting approval):
  "Te quedan 4,500 USD en checking. Para comprar 500 USD de SPY (precio actual ~352 USD/accion = ~1.42 acciones) primero muevo 500 de DEFAULT a INVESTMENT, despues mando la orden a mercado. Aprobas?"

USER clicks Aprobar.

AGENT -> tool: transfer_internal({"from":"DEFAULT","to":"INVESTMENT","amount":500,"currency":"USD"})
TOOL RESULT: { "uuid":"...","status":"COMPLETED","source_amount":500,"dest_amount":500 }

AGENT -> tool: place_trade({"symbol":"SPY","direction":"BUY","currency":"USD","order_type":"MARKET","amount":500})
TOOL RESULT: { "data":{"symbol":"SPY","direction":"BUY","amount":500,"shares":1.4205,"status":"REQUESTED","order_type":"MARKET","created_at":"2026-05-09T15:30:00Z"} }

AGENT -> tool: get_order_status({"symbol":"SPY","direction":"BUY","approx_amount":500})
  (after 3s delay)
TOOL RESULT: { "data":[{"uuid":"...","type":"TRADE","source_amount":500,"dest_amount":1.4205,"status":"COMPLETED","created_at":"2026-05-09T15:30:02Z"}] }

AGENT -> user (final):
  "Listo. Compre 1.4205 acciones de SPY por 500 USD a un precio promedio de ~352.10. Tu posicion total en SPY ahora es 1.4205 acciones (~500 USD). Te quedan 4,000 USD en checking."
```

The audit log gets four rows: `read_balances`, `search_assets`, `transfer_internal`, `place_trade` (each with timestamps, args, and responses). The user can scroll the chat thread to replay the exact ceremony.

#### What's NOT in the public docs (verify on-site)

1. Does `/trades` response include an `id` or `uuid`? Public spec example doesn't show one. **High priority to verify** because order-to-transaction matching depends on it.
2. Full status state machine (REQUESTED -> ? -> COMPLETED). Only terminal example is `COMPLETED`.
3. Specific rate-limit numbers (X requests per minute). Headers exist; numbers absent.
4. Sandbox / test mode. Not documented.
5. After-hours order rejection wording (likely 422 but exact message not shown).
6. KYC pre-check endpoint. Not documented.
7. 5xx error response shapes. Not enumerated for `/trades`.
8. Whether `/balance/stocks` ever returns a USD `value` field (some prior summaries imply it; the public schema we read shows only `symbol` + `shares`).

These are the issues to ask Wallbit reps about in the first hour on-site.

---

## 4. Reference Deep-Dive: wallsync.cc

**Sources:** [wallsync.cc](https://wallsync.cc) (the public site returned 403 to our automated fetcher; positioning is paraphrased from indexed search snippets fetched 2026-05-09).

### What wallsync.cc is (positioning)

- Tagline: "AI-Powered Financial Intelligence & Wealth Management" ([wallsync.cc title tag](https://wallsync.cc)).
- Positioning paragraph (paraphrased from search snippets, not a direct quote): a "complete financial operating system built for clarity, speed, and intelligence" that tracks 4,000+ assets (stocks, ETFs, crypto, commodities) with live data, allocation charts, top movers, and real-time risk exposure.
- Core mechanism: "orchestrates specialized AI agents that monitor, analyze, and optimize your finances. Each agent watches a different part of your money - your portfolio, spending, the markets - and tells you what's happening, what to do, and why."
- Trading: market and limit orders directly from the dashboard, one click. Strongly suggests they're using a brokerage backend - **most likely Wallbit/Alpaca**, given the asset count and stock/ETF/bond/crypto mix matches Wallbit Markets exactly ([markets.wallbit.io](https://markets.wallbit.io/)). **(Unconfirmed but high-likelihood inference.)**
- Other features mentioned: unified checking + investment view, transaction history fully searchable, dividend/fee tracking, allocation rebalancing suggestions.

### What we'd do differently / better

| wallsync.cc | Our wedge |
|---|---|
| English-first, generic global wealth-management aesthetic. | **Spanish-first, Argentine-context aware** (CCL, MEP, blue-vs-oficial dollar mental models, USDT-as-savings-vehicle, ARS volatility). |
| Multi-agent dashboard - presents agents as side panels / cards. The user still has to read and interpret. | **Single conversational agent** with explicit, named tools. The user *talks* and the agent *acts*. The agent is the UI. |
| "Tells you what to do" - recommendation surface. | "Does it for you, with a confirmation step" - **action surface**. Approve, Decline, Snooze. |
| Continuous-monitoring framing implies you check the app. | **Push-driven**: the agent reaches out only when something matters (new income, anomalous spending, a stock crossed a threshold, a stablecoin opportunity). |
| No clear LatAm-specific use case (inflation, FX, dollar-denominated savings). | LatAm-specific moments: "today the agent moved 200 USD from your stale checking balance into the robo-advisor, locking in inflation protection - is that ok?" |
| Closed product, not a hackathon-grade demo target. | **36-hour, open-source, hosted demo. Easy to clone, easy to remix.** |

### What wallsync.cc is missing that we can claim

- No conversational chat front-and-center - they have agent panels, not a chat agent.
- No clear voice-mode story (ElevenLabs angle, see Section 6).
- No LatAm pesos / USDT mental model.
- No visible "agent took an action and you can audit it" log - the trust ceremony.

---

### 4.5 Wallbit API ecosystem: who else consumes it

**Compiled 2026-05-09. Confidence labels: CONFIRMED = explicit on the cited page; PARTIAL = inferred or paraphrased from indexed snippet; UNCONFIRMED = no evidence either way; ABSENCE CONFIRMED = checked, not present.**

The ecosystem of public Wallbit-API consumers is **very small and Wallbit-controlled**. We found 3 confirmed first-party tools, 1 confirmed third-party product (wallsync.cc), and zero independent SDKs / hackathon projects / community apps. This is a finding: as of 2026-05-09 the public Wallbit-API ecosystem appears to be days/weeks old.

**Confirmed consumers:**

- **wallsync.cc** - "AI-Powered Financial Intelligence & Wealth Management." Tracks 4,000+ assets (stocks, ETFs, crypto, commodities), live allocation/risk views, one-click market+limit orders, multi-agent dashboard. **CONFIRMED** as Wallbit consumer: indexed snippet of [wallsync.cc](https://wallsync.cc) reads "wallsync is built in collaboration with Wallbit and is powered by Wallbit's global financial API" (the live page returned 403 to our fetcher, but Google search cache surfaced this exact phrasing on 2026-05-09). Endpoints inferred from feature surface: `/balance/checking`, `/balance/stocks`, `/assets`, `/trades` (read+trade scope, both order types). LatAm relevance: English-first global wealth-management aesthetic; not specifically Argentine. **Direct competitor to our pitch: yes - closest analog by far. Strong tagline overlap on "AI-powered" + "wealth management". Differentiator below.**
- **wallbit-mcp** ([github.com/Wallbit/wallbit-mcp](https://github.com/Wallbit/wallbit-mcp)) - **First-party** MCP server "that lets AI agents interact with the Wallbit API using their own API keys." Exposes 5 tools: `get_checking_balance`, `get_stocks_balance`, `list_transactions`, `get_asset`, `create_trade`. Stdio + HTTP/SSE deployment modes. **CONFIRMED** by the org owning the repo (Wallbit). Endpoints: `/balance/checking`, `/balance/stocks`, `/transactions`, `/assets/{symbol}`, `/trades`. **Not a competitor - it's a tool we can directly fork or use as the wiring layer for our agent. This is hackathon-gold.**
- **wallbit-skills** ([github.com/Wallbit/wallbit-skills](https://github.com/Wallbit/wallbit-skills), also indexed at [smithery.ai/skills/wallbit/wallbit-skills](https://smithery.ai/skills/wallbit/wallbit-skills)) - **First-party** Claude/Cursor skill that teaches the AI assistant how to write correct Wallbit-API code. Covers 9 endpoints (balances, transactions, trades, assets, wallets, account, operations). PHP/Laravel + JS Fetch + Python Requests examples. **CONFIRMED** first-party. Not a runtime consumer - it's a code-generation aid. **Not a competitor - it's another tool we should pre-load into Claude Code on Day 1.**
- **markets.wallbit.io** ([markets.wallbit.io](https://markets.wallbit.io/)) - Wallbit's own market-explorer surface. **PARTIAL**: clearly a Wallbit-built UI on top of the same Alpaca/W2B brokerage backend, but the page does not explicitly say "consumes the public API"; it might use private internal endpoints. Endpoints likely overlap with `/assets`, `/assets/{symbol}`. Not a competitor.
- **Wallbit core mobile/web app** ([app.wallbit.io](https://app.wallbit.io/), Google Play, App Store) - The Wallbit consumer app itself. **PARTIAL** that it "consumes the public API" specifically; more likely consumes private internal endpoints. Not a competitor.

**Searched and ABSENCE CONFIRMED:**

- **Independent SDKs / npm / PyPI packages**: searched npm + PyPI + GitHub for "wallbit", "api.wallbit.io", "X-API-Key wallbit". Result: **zero** community SDKs found ([github.com/Wallbit](https://github.com/Wallbit) shows only the 2 first-party repos above; the only other "wallbit" repo is [goncy/wallbit-challenge](https://github.com/goncy/wallbit-challenge), an unrelated frontend interview test that uses the Fake Store API, not the Wallbit API). ABSENCE CONFIRMED.
- **Past Platanus Hack projects on Wallbit**: [vote.hack.platan.us](https://vote.hack.platan.us/) project list (Hack 25) shows 26 projects; **none** mention Wallbit. Wallbit is **not** listed as a sponsor on [hack.platan.us/tour/sponsor](https://hack.platan.us/tour/sponsor) for Hack 24, 25, or 26. ABSENCE CONFIRMED for prior-hack precedent.
- **Product Hunt / Devpost**: no Wallbit-API consumers found (searches returned only Wallbit's own page and unrelated "walbit"/"wallbot" products). ABSENCE CONFIRMED.
- **Reddit / dev.to / Medium / Hacker News chatter**: no posts mentioning building on the Wallbit API surfaced in our searches on 2026-05-09. ABSENCE CONFIRMED.
- **Conversational/chat agent on top of Wallbit**: zero direct consumers found. ABSENCE CONFIRMED.

**Bucketed competitive map:**

- **(a) Wallbit's own products consuming the API**: `wallbit-mcp`, `wallbit-skills` (first-party, code-gen + tool-use scaffolding); `markets.wallbit.io` and Wallbit core app (partial, likely internal-API but on same data).
- **(b) Direct competitors to our pitch (chat/AI agent over personal finance)**: **wallsync.cc - the only one**. They ship a multi-agent **dashboard**, not a single conversational chat. We are differentiated by being chat-first / Spanish-first / LatAm-first; they are dashboard-first / English-first / global-wealth aesthetic. ([wallsync.cc](https://wallsync.cc)).
- **(c) Tangential consumers (read-only dashboards, trading bots, MCP wrappers)**: only the first-party `wallbit-mcp` exists. No third-party trading bots, dashboards, or analytics tools. ABSENCE CONFIRMED.
- **(d) White space we can claim**: (i) **First conversational-chat agent over Wallbit** (wallsync is dashboard, not chat). (ii) **First Spanish/LatAm-first product** on Wallbit (wallsync is English-first). (iii) **First voice-mode product** on Wallbit (no ElevenLabs / voice consumers found). (iv) **First open-source / hackathon-grade demo** on Wallbit (no community projects found).

**Defensibility verdict:** **Not crowded.** The Wallbit-API ecosystem is essentially: Wallbit + wallsync.cc. Wallsync is the only meaningful third-party consumer, and it occupies the "dashboard" lane, not the "chat agent" lane. We are walking into a near-empty room with one neighbor whose UX framing differs from ours. **Caveat**: wallsync exists, is polished, ships trading, and explicitly partners with Wallbit - we should expect Wallbit reps at the hack to know wallsync well. We must position **alongside** wallsync, not against it.

**Pitch implications:**

- **DO NOT claim** "the first product built on Wallbit's API" - wallsync.cc beat us to that and Wallbit will know.
- **DO NOT claim** "the first AI-powered Wallbit consumer" - same reason.
- **DO claim** "the first **conversational** AI agent on Wallbit" (wallsync ships a multi-agent dashboard, not a chat). PARTIAL on first-ness; safer phrasing: "an LLM-native, chat-first companion to the Wallbit account."
- **DO claim** "Spanish-first / Argentine-context / voice-mode" - all three are uncontested white space on Wallbit per our scan on 2026-05-09.
- **Safer framing**: "if wallsync.cc is the Bloomberg terminal for your Wallbit, we are the WhatsApp chat with your Wallbit." Position as a complement, not a competitor.

---

## 5. Reference Deep-Dive: LemonGPT & the conversational-finance pattern

**Honest disclosure:** Our public-web searches on 2026-05-09 returned **no indexed product called "LemonGPT" from Lemon Cash**. Searches for "LemonGPT," "Lemon GPT," "Lemon Cash AI chatbot," and Spanish equivalents returned only generic Lemon Cash company info plus generic AI-finance content. The team has direct knowledge of this product; we treat its existence/spirit as **team-confirmed but not externally citable**. **(Unconfirmed in public sources - team to provide a direct link if the pitch needs to name-drop it.)** Safer pitch posture: invoke the *pattern* ("a Lemon-style chat over your money"), not the specific brand name.

### Lemon Cash context (confirmed)

- Argentina-founded crypto/fiat wallet; ~5M LatAm users by late 2025; $20M Series B in October 2025 ([lemon.me/en/blog/serie-b-20-m](https://lemon.me/en/blog/serie-b-20-m), [Crunchbase](https://www.crunchbase.com/organization/lemon-cash)).
- Argentine retail uses Lemon as a USDT/USDC + ARS hybrid wallet, often as inflation hedge.
- The Lemon brand owns the conversational-finance concept in the Argentine retail mind.

### Why the conversational-finance pattern is hot now

- Anthropic publicly shipped 10 finance-agent templates on 2026-05-05, four days before this hack ([Bloomberg, 2026-05-05](https://www.bloomberg.com/news/newsletters/2026-05-05/anthropic-announces-new-ai-agents-for-financial-professionals)).
- Wallbit redesigned its API surface around an "Agents" concept ([quickstart](https://developer.wallbit.io/docs/quickstart)).
- Wallsync went to market on the AI-agent-orchestrator framing.
- All three signals say: **2026 is the year a normal person starts trusting an AI to touch their money.** The Agentic Money track is Platanus betting on the same trend.

### The pattern, distilled

A user **chats** with a single agent. The agent has **named tools** (Get Balance, Move Money, Buy Stock, Suspend Card, ...). The agent maintains **memory** of what the user wants (goals, risk tolerance, recurring rules). When something happens, the agent **proactively reaches out** with a proposed action; the user **approves, modifies, or rejects** in the same chat thread. The chat thread is the audit log.

This is what we are building.

---

## 6. The Chosen Idea

> **A standalone, Spanish-first, conversational AI agent that lives on top of a Wallbit account and actually moves your money - safely, with confirmation, with memory.**
> Inspired by the Lemon-style chat-over-finance pattern in spirit, going head-to-head with wallsync.cc on the agentic-finance positioning, but narrower, sharper, more LatAm-native, and demo-able in 36 hours.

### Name candidates (team picks one)

1. **Pampa** - Argentine-resonant, short, brandable. "Tu Pampa financiera: vasto, calmo, todo a la vista." Domain `pampa.money` / `pampa.ai` likely available - **(unverified, team to check on Sunday morning).**
2. **Plata** - "Plata" is colloquial Argentine for money. Direct, memorable. Risk: generic, harder to SEO.
3. **Cuy** - The agent is "your cuy" (Andean reference: a small, alert, ever-watching companion). Memorable, weird, demo-friendly. Best for going viral on the public vote.

**Recommendation:** **Pampa**. Calm, dignified, speaks Argentine without being a meme, easy to draw a logo for in 30 minutes (a horizon line + a sun).

### One-liners

- **English:** "Pampa is the AI agent that runs your Wallbit account so you don't have to."
- **Spanish (for `platanus-hack-project.json`):** "Pampa es el agente de IA que maneja tu cuenta Wallbit por vos: te avisa, te sugiere, y mueve la plata cuando se lo permitis."

Keep the Spanish version casual, "vos"-form, Argentine. Avoid neutral Spanish.

### Target user (concrete persona)

**"Tomas, 29, Buenos Aires, software developer."**

- Receives 4,500 USD/month via Wallbit (remote contract, US client).
- Spends ~1,800 USD/month on rent + life via the Wallbit Visa.
- Holds 8,000 USDT-equivalent in his Wallbit checking as savings, scared of ARS inflation but doesn't actively manage it.
- Owns ~3,000 USD in fractional US stocks via Wallbit (bought once, never rebalances).
- Hates logging into Wallbit. Forgets dividends. Doesn't know his runway. Doesn't know if his cash is "working."
- Wants someone to **just handle it** - but with audit and consent, not blind autopilot.

This persona is exactly Wallbit's existing user base ([wallbit.io/en](https://www.wallbit.io/en) pitches "remote workers, freelancers, developers, digital creators"). Pampa is a **wrapper that makes Wallbit accounts feel managed** without leaving Wallbit.

### Core wedge (what makes us 10x better than wallsync.cc or a generic dashboard)

1. **The agent is the UI.** No dashboard-first, agent-second. A chat thread is the entire product. wallsync.cc is a dashboard with agent side-cards; we are an agent with a balance card.
2. **Action, not advice.** Every agent message ends with an actionable button (Approve / Modify / Skip). The agent calls Wallbit's `trade`-scoped endpoints when approved. This is the **Agentic Money** core.
3. **Spanish-first, Argentine-context aware.** The agent knows what "el dolar blue," "MEP," "plazo fijo," and "USDT" mean in their specific cultural register. wallsync.cc does not.
4. **Memory and rules.** The agent stores standing rules ("siempre dejame 500 USD liquido," "si entra mas de 3000, mande 30% al robo-advisor automaticamente, pero pregunta primero"). Stored in Supabase ([Supabase is a tour sponsor](https://hack.platan.us/)).
5. **Voice mode (stretch).** Press-to-talk via ElevenLabs. "Pampa, cuanto tengo en dolares?" Voice answers in natural Argentine Spanish. **ElevenLabs is a tour sponsor** ([hack.platan.us](https://hack.platan.us/)) - free credit angle.
6. **Audit trail.** Every action has a chat message + a row in Supabase. The user can scroll and see "Pampa moved 200 USD on Friday at 3pm because you approved it." Trust ceremony built in.

### Demo-day money shot (the 30-second moment that wins votes)

**Set-up (10s):** "Tomas just got paid - 4,500 USD landed in his Wallbit checking." Show real Wallbit `/balance/checking` updating live (or trigger the demo by sending the team treasurer a small USD transfer right before walking on stage).

**The shot (15s):** Pampa's chat window pops a notification: *"Hola Tomas, te entraron 4,500 USD. Segun tu regla, propongo: dejar 1,800 para gastos, mover 800 al robo-advisor, comprar 300 USD de SPY, y dejar 1,600 en stablecoin. Te aviso?"*

User taps **Aprobar**. Four animated chips light up in sequence, each calling a real Wallbit endpoint. Live API responses. The balance card on the side updates in real time.

**The kicker (5s):** Tomas now does press-to-hold voice: *"Pampa, cuando es mi proximo dividendo?"* ElevenLabs voice answers in natural Argentine Spanish: *"Eh, el 15 de mayo cobras 12 dolares de Coca-Cola."*

That's the vote-winning clip. Record it. Tweet it. Done.

### MVP scope for 36 hours (golden path only)

The MVP is *only* this flow:

1. **API-key entry:** user pastes Wallbit `read`+`trade` API key on first load. Stored encrypted in Supabase per user. (No third-party OAuth; manual key paste matches Wallbit's actual flow.)
2. **Read tools wired:** `getBalanceChecking`, `getBalanceStocks`, `getTransactions`, `getWallets`, `getRoboadvisorBalance`. Each is a Claude tool exposed via tool-use.
3. **Action tools wired:** `createTrade(symbol, side, amount)`, `roboadvisorDeposit(amount)`, `internalOperation(direction, amount)`. Each tool call is wrapped in a **two-step confirm**: agent proposes -> user clicks Aprobar -> tool fires -> result returned to agent -> agent confirms in chat.
4. **Single chat UI** (Next.js / Vercel AI SDK / v0-generated components). Streaming Claude responses. Action chips inline. (Vercel + Anthropic are sponsors; this is a clean fit.)
5. **One standing rule UI:** user can write a free-text rule ("dejame siempre 500 liquido") that gets injected into the system prompt. No rule-engine, no cron, no background jobs - just system-prompt augmentation. Cheap, demoable, honest.
6. **Audit log view:** simple Supabase-backed list of all tool calls with timestamp, args, response. Read-only.
7. **Spanish system prompt and tone tuned to Argentine register.** Tested by a native team member (Ruben/Juan/Vladimir/Luca/Alen all qualify - free advantage).

**Out of scope for MVP** (do NOT touch in the first 24 hours):
- Background polling / cron rules.
- Multi-account aggregation (only Wallbit).
- Voice mode.
- Charts.
- Mobile.
- DeFi / on-chain.
- Card management.
- Multi-language (English).
- Full RBAC.

### Stretch features (only after the MVP demo runs end-to-end)

In rough priority order:

1. **Voice mode** - press-to-talk, ElevenLabs TTS in Argentine Spanish, browser STT. Sponsor angle: ElevenLabs.
2. **Proactive notifications** - a Supabase scheduled function polls `/transactions` every 60s; new transaction triggers a chat message from Pampa. Real "agentic" feel.
3. **Rule engine** - parse natural-language rules into structured triggers (Claude does this in one call) and persist them.
4. **Card actions** - "Pampa, freezame la tarjeta" calls `/cards/{id}/status` with SUSPENDED.
5. **Anomaly detection** - "este gasto de 800 USD no parece tuyo, queres que freeze la tarjeta?" - using transaction history.
6. **Goal mode** - "quiero juntar 10k para un viaje en diciembre" - the agent splits paychecks toward the goal.

### Risks and mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Wallbit API rate-limits or 5xx during the live demo. | High demo risk. | (a) Backup pre-recorded demo video. (b) Cache last-good responses; show cached state if API fails. (c) Demo at low-traffic hours. |
| Wallbit `trade` scope requires KYC the demo account doesn't have. | High dev risk. | Complete KYC on the demo account on Day 1, hour 1. If blocked, swap that demo step for `/roboadvisor/deposit` (also `trade`-scoped, lower KYC bar - **unconfirmed; verify on-site**). |
| No Wallbit sandbox - real money in demo. | Medium. | Use a tiny demo account, $20-50. Don't pre-fund with real savings. |
| Claude tool-use mis-parses or loops. | Medium. | Keep tool count small (8-10 tools max). Use Anthropic's documented tool-use patterns. Add a hard "stop after 3 tool calls per user message" guard. |
| Public vote viability - 25+ projects, attention is scarce. | High to win. | (a) Ship a deployed link, not a localhost demo. (b) Record the 30s money shot Saturday night and tweet it Sunday morning. (c) Argentine voice angle = native shareable. |
| Argentine Spanish tone goes off (sounds Mexican / neutral / chatbot-y). | Medium. | Native team members review every system prompt and example. Use "vos," "che," "boludo" sparingly but present. Avoid "tu". |
| Sensitive data in API keys. | Low (no real users at demo) but sponsor-perception high. | Encrypt at rest in Supabase. Don't log keys. Make security visible in the pitch ("revocable in 1 click via `/api-key/revoke`"). |
| Wallbit isn't formally a track sponsor and we lean on them too hard. | Medium narrative risk. | Pitch the product as Wallbit-API-powered, but frame Wallbit as "the rails." If they ARE a sponsor, lean in publicly. **(Confirm on-site before the pitch.)** |
| Anthropic / Claude not locked in as the LLM (some teams may use OpenAI). | Low. | Anthropic is the headline sponsor. Use **Claude (Sonnet 4 or Opus 4)** with tool use, period. This is on-brand for the headline-sponsor judges. Mention "Claude" by name in the pitch. |

### Why this fits Agentic Money specifically

The "Agentic" word is doing real work in the track name. A chat-over-balances product is **not** agentic - it's a chatbot. We pass the agentic test on three counts:

1. **The agent has tools that move money.** `/trades`, `/operations/internal`, `/roboadvisor/deposit` - real action endpoints, called by the LLM in tool-use mode, not by a button the user pressed manually.
2. **The agent has goals and memory.** Standing rules ("dejame 500 liquido siempre") are persistent state that constrain future agent decisions. This is the difference between a chat and an agent.
3. **The agent has autonomy with consent.** It proposes; the user approves once; the agent executes a multi-step plan. The user is in the loop, but each step is not micromanaged.

The "Money" part is on the nose: real USD, real stocks, real stablecoins, real movements via Wallbit. Not synthetic. Not paper trading. (Demo account is small, but it is real money on real rails.)

This framing - **"agentic" = tools + memory + autonomy with consent**, **"money" = real Wallbit movements** - is the line we open the pitch with.

---

## 7. Open Questions (team must decide before planner)

Resolve these in the first 60 minutes on-site:

1. **Confirm Wallbit is on the BA sponsor wall.** If yes, lean in (free credits, possible bonus prize). If no, proceed but de-emphasize sponsor language. ([hack.platan.us/tour/sponsor](https://hack.platan.us/tour/sponsor) only lists 5 global sponsors as of fetch.)
2. **Confirm the verbatim "Agentic Money" track copy.** Update the pitch deck to mirror the language exactly.
3. **Wallbit demo account ownership:** who on the team has a Wallbit account with KYC complete? That person is the demo-account custodian. (Recommendation: Juan or Ruben, picked by 2026-05-09 18:00 ART.)
4. **LLM decision:** Claude Sonnet 4 vs Opus 4? **Recommendation: Sonnet for speed during dev; Opus for the demo flight** if cost allows (sponsor credits help). Tool-use works on both.
5. **Frontend stack:** **Next.js + Vercel AI SDK + v0-generated components**, deployed on Vercel. Sponsor-aligned, fastest path. Alternative: Streamlit (faster but less impressive). **Recommendation: Next.js.**
6. **Auth model:** API-key paste vs full Wallbit OAuth. **Recommendation: API-key paste.** Wallbit's docs do not mention OAuth ([quickstart](https://developer.wallbit.io/docs/quickstart)); building OAuth from nothing in 36h is suicide. Paste-the-key is honest and demo-able.
7. **Persistence:** Supabase. (Sponsor.) Use `auth.users` for user accounts, one table for `agent_rules`, one table for `audit_log`, one table (encrypted column) for `wallbit_keys`.
8. **Voice mode commitment:** stretch, only if MVP is locked by 2026-05-09 23:59 ART (Saturday night).
9. **What chains for crypto observation?** Wallbit's `/wallets` returns USDT/USDC/BTC/ETH addresses across networks. **Recommendation: don't try to query on-chain balances ourselves.** Just show the addresses Wallbit returns and let `/transactions` track flows. Stay inside Wallbit's data model.
10. **Project name:** Pampa / Plata / Cuy. **Recommendation: Pampa.** Decide by 2026-05-09 19:00 ART so logo + Spanish copy can be finalized.
11. **`platanus-hack-project.json` Spanish copy:** lock the Spanish one-liner by 2026-05-09 19:00 ART. Suggested above.
12. **Open-source license:** MIT (Platanus past requirement; carry-over). ([hack.platan.us/24](https://hack.platan.us/24))
13. **Backup demo video:** committed by 2026-05-09 23:59 ART. No exceptions.

---

## 8. Explicit Unknowns and Assumptions

### Unknowns (label as unknown in any artifact downstream)

- Verbatim "Agentic Money" track description text. **Unknown** - must capture on-site.
- Whether Wallbit is officially a Buenos Aires track sponsor. **Unknown.**
- Wallbit free-tier / hackathon credit details. **Unknown** - the public docs do not state pricing; they state two scopes and an API-key ceremony.
- Wallbit rate-limit numerical values. **Unknown** - headers exist, numbers not in public docs.
- Wallbit sandbox / test mode. **Unknown** - not documented in the pages we read.
- Existence of "LemonGPT" as a public Lemon Cash product. **Unknown publicly** - team has direct knowledge; we treat it as inspiration only, not a public reference. The pitch should NOT claim "we are like LemonGPT" externally without a citable source.
- Exact judging criteria for Agentic Money track (jury vs. public vote weighting). **Unknown.** Past editions used both ([huss.substack.com](https://huss.substack.com/p/ganamos-la-hackaton-de-platanus), [vote.hack.platan.us](https://vote.hack.platan.us/)). Assume both matter.

### Assumptions (carrying these forward)

- **A1.** "Agentic Money" rewards tool-using LLM agents that take real action on real financial accounts. (Inferred from track name + sponsor mix + 2026 industry signals.)
- **A2.** Public voting is meaningful (~2k+ votes split across ~25 projects). Shareable demo clip matters.
- **A3.** Anthropic's Claude is the on-brand LLM choice (headline sponsor + finance-agents launch 4 days before hack).
- **A4.** Vercel + Supabase + ElevenLabs are tour sponsors and using them does not hurt. ([hack.platan.us](https://hack.platan.us/))
- **A5.** A demo on a small real Wallbit account (not synthetic data) is feasible and significantly more impressive than any mock.
- **A6.** Spanish-first Argentine register is a competitive advantage at a Buenos Aires venue.
- **A7.** Open-source MIT and a deployed public URL are required (carried over from past Platanus editions).

---

## Source index

Primary sources cited in this brief:

- [hack.platan.us](https://hack.platan.us/) - event metadata, sponsors, prize, dates
- [hack.platan.us/tour/sponsor](https://hack.platan.us/tour/sponsor) - sponsor list
- [hack.platan.us/sponsor-deck](https://hack.platan.us/sponsor-deck) - prior format, voting, sponsorship tiers
- [hack.platan.us/24](https://hack.platan.us/24) - prior edition rules (open source, MIT, deployed)
- [vote.hack.platan.us](https://vote.hack.platan.us/) - public voting platform
- [blog.platan.us](https://blog.platan.us/) - context on Platanus events
- [huss.substack.com - Ganamos la hackaton de Platanus en Fintual](https://huss.substack.com/p/ganamos-la-hackaton-de-platanus) - winner pattern, judging, demo strategy
- [developer.wallbit.io](https://developer.wallbit.io/) - Wallbit API home
- [developer.wallbit.io/docs/quickstart](https://developer.wallbit.io/docs/quickstart) - auth, base URL, first call
- [developer.wallbit.io/docs/llms.txt](https://developer.wallbit.io/docs/llms.txt) - endpoint catalog (canonical)
- [wallbit.io/en](https://www.wallbit.io/en) - product positioning
- [help.wallbit.io/en/articles/8059439-what-is-wallbit](https://help.wallbit.io/en/articles/8059439-what-is-wallbit) - countries, ARS/USD support
- [markets.wallbit.io](https://markets.wallbit.io/) - asset coverage, brokerage backend (Alpaca)
- [ycombinator.com/companies/wallbit](https://www.ycombinator.com/companies/wallbit) - Wallbit YC profile (W23)
- [wallsync.cc](https://wallsync.cc) - competitor positioning (snippets; fetch returned 403)
- [Bloomberg, 2026-05-05 - Anthropic Finance Agents](https://www.bloomberg.com/news/newsletters/2026-05-05/anthropic-announces-new-ai-agents-for-financial-professionals) - Anthropic finance agents launch (fetch 403, summary via search snippet)
- [lemon.me/en/blog/serie-b-20-m](https://lemon.me/en/blog/serie-b-20-m) - Lemon Cash Series B / scale
- [Crunchbase: Lemon Cash](https://www.crunchbase.com/organization/lemon-cash) - Lemon Cash company facts
- [README.md](../../README.md) - team-29 track confirmation
- [platanus-hack-project.json](../../platanus-hack-project.json) - submission template (Spanish required)

---

## 9. Appendix: Alternative APIs considered (API-key fintech landscape)

**Brief written:** 2026-05-09. Compiled to (a) defend Wallbit vs. judges asking "why not X?" and (b) identify a Plan B if Wallbit's API breaks during the demo. Hard requirements imposed: static credential auth (API key, or API key + secret HMAC - **no OAuth, no per-user consent flow, no browser-session SDK**), programmatic balance read, programmatic execution of at least one money-moving action, public docs reachable today, and free tier or sandbox usable inside a hackathon.

**Confidence labels:** CONFIRMED = explicitly in cited doc; PARTIAL = in docs but a sub-detail (sandbox/limits/etc.) is missing; UNCONFIRMED = inferred or not in docs we reached; ABSENCE CONFIRMED = the cited doc explicitly contradicts or omits the capability.

### 9.1 Comparison table

| API | Auth | Read balances | Execute (write) | LatAm? | Hackathon-ready? | Source |
|---|---|---|---|---|---|---|
| **Wallbit (chosen)** | `X-API-Key` header (single static key, two scopes `read`/`trade`) - CONFIRMED | USD/ARS checking, US stocks/ETFs, USDT/USDC/BTC/ETH addresses, robo-advisor - CONFIRMED | BUY/SELL stocks, internal DEFAULT<->INVESTMENT, robo-advisor deposit/withdraw, card freeze - CONFIRMED. NO crypto-send (ABSENCE CONFIRMED). | Yes - BA-based, USD+ARS - CONFIRMED | Single user only (each user pastes own key). No documented sandbox - UNCONFIRMED. KYC needed for trades. | [developer.wallbit.io/docs/quickstart](https://developer.wallbit.io/docs/quickstart), [llms.txt](https://developer.wallbit.io/docs/llms.txt) |
| **Alpaca** | `APCA-API-KEY-ID` + `APCA-API-SECRET-KEY` headers OR HTTP Basic - CONFIRMED. (OAuth exists but is optional.) | Account, positions, activities - CONFIRMED | Place orders, ACH funding, journals (transfers) - CONFIRMED | No (US brokerage). - CONFIRMED via Alpaca being US broker-dealer | Paper-trading account is **global, free, instant by email**, $100k simulated, IEX data - CONFIRMED | [docs.alpaca.markets/docs/authentication](https://docs.alpaca.markets/docs/authentication), [docs.alpaca.markets/docs/paper-trading](https://docs.alpaca.markets/docs/paper-trading) |
| **Bitso** | API key + nonce + HMAC-SHA256, header `Authorization: Bitso [key]:[nonce]:[signature]` - CONFIRMED | `GET /v3/balance` (account balance) - CONFIRMED | `POST /v3/orders` market+limit BUY/SELL, `POST /v3/withdrawals` for ARS bank transfer (CVU/CBU) and crypto - CONFIRMED | Yes - **Argentina, Mexico, Brazil, Colombia, Chile, Peru** core markets - CONFIRMED. ARS pairs (USDT/ARS, USD/ARS, BTC/ARS) traded on Bitso Alpha - CONFIRMED | Sandbox documented (`api-stage.bitso.com`); requires testing-account creation + funding - CONFIRMED | [docs.bitso.com/.../api-overview](https://docs.bitso.com/bitso-api/docs/api-overview), [signing](https://docs.bitso.com/bitso-api/docs/create-signed-requests), [withdrawing-ars](https://docs.bitso.com/bitso-payouts-funding/docs/withdrawing-ars) |
| **Binance** | API key + secret, HMAC / RSA / Ed25519 - CONFIRMED | `/api/v3/account` - CONFIRMED | `/api/v3/order` BUY/SELL, withdraw via Wallet API - CONFIRMED | Yes - Binance has historically served LatAm including USDT/ARS pairs (separate from Binance.US) - CONFIRMED via search | Free testnet at `testnet.binance.vision` - CONFIRMED | [developers.binance.com/.../rest-api](https://developers.binance.com/docs/binance-spot-api-docs/rest-api) |
| **Coinbase Advanced Trade** | API key + secret + passphrase, HMAC-SHA256, headers `CB-ACCESS-KEY`, `CB-ACCESS-SIGN`, `CB-ACCESS-TIMESTAMP` - CONFIRMED | Accounts/balances - CONFIRMED | Place/cancel orders - CONFIRMED | Limited LatAm; Coinbase is US-first - PARTIAL | No public sandbox documented for retail Advanced Trade (Coinbase Exchange has sandbox separately) - UNCONFIRMED | [docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/overview](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/overview) |
| **Kraken (Spot REST)** | `API-Key` + `API-Sign` (HMAC-SHA512 over URI + SHA256(nonce+POST)) + nonce - CONFIRMED | Account balance - CONFIRMED | Add order, withdraw - CONFIRMED | Limited LatAm; global US-style exchange - PARTIAL | No public retail sandbox; live-only with small balances - UNCONFIRMED | [docs.kraken.com/api](https://docs.kraken.com/api/), [spot-rest-auth](https://docs.kraken.com/api/docs/guides/spot-rest-auth) |
| **IOL InvertirOnline** (Argentina broker) | OAuth2 password grant + bearer token (15-min expiry) + refresh token - CONFIRMED. NOT a static API key. | Portfolio, account state, quotes - CONFIRMED | Buy/sell Argentine stocks, CEDEARs, bonds, dollar MEP - CONFIRMED | Yes - Argentina-native broker - CONFIRMED. ARS-denominated. | Sandbox exists, free testing environment ("ambiente seguro y aislado del mercado") - CONFIRMED. Requires existing IOL investment account + manual API activation request via internal messaging. - PARTIAL | [invertironline.com/api](https://www.invertironline.com/api), [api.invertironline.com](https://api.invertironline.com/) |
| **Cocos Capital** (Argentina broker) | **No official public API** - only unofficial reverse-engineered Python clients (`pyCocos`, `cocos_capital_client`) using email/password + TOTP - ABSENCE CONFIRMED | Via unofficial library only | Via unofficial library only | Yes - Argentina | UNSAFE for hackathon: unofficial, can break any time, ToS risk | [github.com/nacho-herrera/pyCocos](https://github.com/nacho-herrera/pyCocos) |
| **Bull Market**, **Buenbit**, **Ripio**, **Belo** (Argentina) | No public developer API found - ABSENCE CONFIRMED in our 2026-05-09 searches | n/a | n/a | Yes (consumer-only, no API) | Not viable | search results above |
| **Lemon Cash** (Argentina) | No public consumer-facing developer API - ABSENCE CONFIRMED. (`lemon.markets` is an unrelated **invite-only** German brokerage infrastructure platform - do NOT confuse.) | n/a | n/a | Yes (consumer-only) | Not viable | search 2026-05-09 |
| **Tradier** (US broker) | OAuth2 + access tokens; sandbox tokens available - PARTIAL | Yes | Yes | No | UNCONFIRMED if hackathon-ready (docs page returned 404 in our fetch) | search results |
| **Interactive Brokers Client Portal API** | **Session-based via local Java Gateway with manual login + 2FA**, OR OAuth2 for enterprise. NOT a static API key. - CONFIRMED | Yes | Yes | Limited | **Disqualified**: requires browser session login or enterprise OAuth flow - violates the "static credential" hard requirement | [interactivebrokers.com/.../cpapi-v1](https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/) |
| **Mercury** (US business banking) | API key as HTTP Basic username (or `Authorization: Bearer`) - CONFIRMED. Three scopes: ReadOnly, Read+Write, Custom (e.g. `RequestSendMoney`). | All accounts + transaction history - CONFIRMED | ACH transfers, book transfers between Mercury accounts, payments - CONFIRMED | No (US-only, business banking) - CONFIRMED | Sandbox exists - CONFIRMED. **But Mercury is business-only**: needs a registered US business + Mercury approval. NOT hackathon-spawnable. | [docs.mercury.com/docs/getting-started](https://docs.mercury.com/docs/getting-started), [mercury.com/api](https://mercury.com/api) |
| **Brex** (US business banking) | Bearer token (user token, expires after 90d unused) OR OAuth for partners - PARTIAL | Yes | ACH, wire, book transfers, payments - CONFIRMED | No (US business only) | Same Brex-account-required problem as Mercury | [developer.brex.com/guides/authentication](https://developer.brex.com/guides/authentication) |
| **Mercado Pago** | OAuth2 + Access Token; "money transfer API" is **gated behind a commercial-advisor approval** and not generally enabled - PARTIAL/ABSENCE CONFIRMED for write | `/v1/payments/...` reads - CONFIRMED | Standard API supports collecting payments (selling), NOT general wallet-to-wallet personal transfers - ABSENCE CONFIRMED | Yes - Argentina/Brazil/Mexico - CONFIRMED | Standard API is hackathon-feasible **for accepting** payments, not for **moving** a user's money around. Wrong shape for an "agent moves my money" pitch. | [mercadopago.com.ar/developers/en/reference](https://www.mercadopago.com.ar/developers/en/reference), [google groups thread on inter-account transfer](https://groups.google.com/g/mercadopago-developers/c/s0gztUHgQ4w) |
| **Belvo** (LatAm "Plaid") | OAuth-style + secret keys; uses **Belvo Connect Widget** for end-user consent - PARTIAL. Not a static-key flow for cross-bank read; per-user link required. | Banking, employment, fiscal - CONFIRMED for Brazil, Mexico, Colombia | Payment Initiation in **Brazil, Mexico** (Pix Automatico, etc.) - CONFIRMED. **Not in Argentina** in publicly-documented coverage as of 2026-05-09 - PARTIAL | LatAm aggregator HQ MX/SP/Bogota; **Argentina coverage not publicly documented** as of our 2026-05-09 fetch - PARTIAL/ABSENCE CONFIRMED for AR | Hackathon-feasible for read in BR/MX, but **wrong country and OAuth-style consent per user** - not API-key-only | [developers.belvo.com/docs/integration-overview](https://developers.belvo.com/docs/integration-overview), [belvo.com/solutions/aggregation/](https://belvo.com/solutions/aggregation/) |
| **Plaid** | OAuth-style per-user Link flow, then access tokens. Read-only in most products. | Yes | No payment-init in most regions for retail flows - ABSENCE CONFIRMED for our use-case | US/CA/EU primary | **Disqualified**: per-user OAuth, not static API key | (well-known) |
| **Hyperliquid / dYdX** (DeFi perps) | **Wallet private key signing** (EIP-712 / Msgpack on L1). Hyperliquid: "no API keys", you generate an "API wallet" private key and sign every action. - CONFIRMED | Yes | Trades, transfers, withdrawals - CONFIRMED | Global (DeFi) | Technically automatable, but private-key-signing is a different primitive from a static API-key header (key material is more dangerous; wallet must be funded with crypto). Probably out-of-scope for the chosen pitch's "consumer agent on a fiat+stocks+crypto neobank" frame. | [hyperliquid.gitbook.io/.../api](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api) |
| **OKX, Bybit, KuCoin** | All use API key + secret HMAC schemes similar to Binance/Bitso - PARTIAL (not individually verified for this brief) | Yes | Yes | Some LatAm exposure but not LatAm-native; CEX-of-CEX | Most have testnets; viable Plan-D if exotic crypto pair needed - UNCONFIRMED | (not fetched - flagged as low-priority overlap) |

### 9.2 Top 3-5 ranked alternatives that meet hard requirements

In rank order of "best plan-B" for the chosen pitch (Wallbit-based Spanish-first conversational personal-finance agent):

1. **Bitso** - the strongest LatAm-aligned plan B. API key + HMAC-SHA256 ([signing docs](https://docs.bitso.com/bitso-api/docs/create-signed-requests)). Reads balances, places market/limit orders ([place-order](https://docs.bitso.com/bitso-api/docs/place-an-order)), and pushes ARS to Argentine bank accounts via CVU/CBU through `POST /v3/withdrawals` ([withdrawing-ars](https://docs.bitso.com/bitso-payouts-funding/docs/withdrawing-ars)). Sandbox at `api-stage.bitso.com` is documented. **Pitch line if Wallbit dies:** "the agent reads your Bitso balances and rotates pesos into USDT (or vice versa) when the blue rate moves." Different surface than Wallbit (no US stocks, no robo-advisor) but the LatAm/ARS angle survives. CONFIRMED hackathon-feasible.
2. **Alpaca (paper-trading mode)** - the **literal substrate Wallbit sits on top of** ([markets.wallbit.io](https://markets.wallbit.io/) confirms "Brokerage services are provided by Alpaca Securities LLC"). API-key-only auth ([Alpaca authentication](https://docs.alpaca.markets/docs/authentication)), instant global signup, $100k simulated capital ([paper-trading](https://docs.alpaca.markets/docs/paper-trading)). **Use as Plan B for the stock-trading half of the demo only**: if `POST /trades` on Wallbit 412s due to KYC mid-pitch, swap in Alpaca paper for that one tool call - the user-facing chat still says "compre 300 USD de SPY", just the backend differs. Loses Wallbit's multi-asset bundle (no ARS, no fiat checking, no crypto, no card, no LatAm angle), so it is a fallback rail, not a replacement product.
3. **Binance (testnet)** - solid free-tier crypto plan B for the stablecoin half. API key + HMAC, free testnet at `testnet.binance.vision`. Loses LatAm framing entirely; only useful if the pitch needs a recoverable "crypto trade" tool call when Wallbit's `/wallets` is fine but a different stablecoin demo is wanted.
4. **IOL InvertirOnline** - the Argentine broker option. NOT a static API key (OAuth2 password + 15-min bearer + refresh per [api.invertironline.com](https://api.invertironline.com/)) so it technically violates our "API-key-only" hard requirement, but the bearer-token-after-login model is hackathon-tractable (one curl to log in, then bearer in headers). Sandbox is real and documented. **The only realistic way to put Argentine peso securities (CEDEARs, dollar MEP) in front of judges.** Not a Wallbit replacement - a *complement* if a stretch goal is "agent that talks about your CEDEARs."
5. **Coinbase Advanced Trade** - works the same as Binance/Bitso (API key + HMAC-SHA256), but no clear public sandbox for retail Advanced Trade and weaker LatAm story. Use only if the team already has a funded Coinbase account and Wallbit's crypto-balance read endpoint is the failing piece.

Out-of-bracket but worth knowing exist: Kraken, OKX/Bybit/KuCoin (technically qualify, weak LatAm fit), Mercury/Brex (great APIs, US-business-only, can't spawn an account in 36h), Hyperliquid/dYdX (private-key-signing, not static-API-key, and not on-brand for a consumer fiat-first agent pitch).

### 9.3 The Wallbit-uniqueness verdict

**Wallbit is genuinely unusual** in bundling, behind a single static `X-API-Key` header, all of: USD checking + ARS support, US stocks/ETFs (via Alpaca, [markets.wallbit.io](https://markets.wallbit.io/)), USDT/USDC/BTC/ETH deposit addresses, a robo-advisor with $10 minimum, an internal DEFAULT<->INVESTMENT transfer primitive, and a card-status toggle - all in one account, with **no OAuth, no per-user partner flow, no signing nonce ceremony**. We could not find a single competitor that matches all five facets simultaneously:

- **Bitso** has fiat (ARS, USD, BRL, MXN) + crypto + recently stocks ([bitso.com](https://bitso.com/)), but **HMAC-signs every request**, not a single header, and lacks a robo-advisor primitive in its public API.
- **Alpaca** has stocks/ETFs/options/crypto and is API-key + secret, but **no fiat banking, no LatAm fiat, no robo-advisor**.
- **Mercury / Brex** have API-key fiat banking (US business) but **no stocks, no crypto, no robo-advisor, no LatAm**.
- **IOL InvertirOnline** has Argentine securities + dollar MEP but is **OAuth2 bearer**, not static API key, and no crypto.
- **Lemon / Buenbit / Ripio / Belo / Cocos / Bull Market** have no public developer API at all in our 2026-05-09 search.
- **Mercado Pago** is API-key-ish but **its money-movement API is commercial-advisor-gated**, not retail-self-serve.
- **Belvo** is OAuth/widget-flow per user, not Argentina-covered for payments, and primarily read-only.

So when a judge asks "why Wallbit and not X," the defensible answers are:

1. "API-key-only auth means the demo skips OAuth scaffolding entirely - we built a real action surface in the 36 hours we had." (Bitso, Coinbase, Kraken, Binance all force HMAC-signing every request - solvable, but extra time.)
2. "Wallbit is the only neobank-shaped API where one key sees fiat + stocks + crypto + robo-advisor in one account. Everywhere else we'd be stitching three or four backends." (Cite: [developer.wallbit.io/docs/llms.txt](https://developer.wallbit.io/docs/llms.txt) endpoint catalog vs. Bitso/Alpaca/Mercury split.)
3. "Wallbit's brokerage backend is Alpaca ([markets.wallbit.io](https://markets.wallbit.io/)). If we'd used Alpaca directly we'd have lost ARS, lost fiat checking, lost the crypto wallet bundle, and lost the LatAm framing - the very things that make this a Buenos Aires hackathon pitch." (This is the cleanest defense: Wallbit is not a layer over Alpaca, it is **Alpaca + USD checking + ARS + crypto + card + robo-advisor + LatAm UX**, all behind one key.)

**Plan B if Wallbit blows up on demo day:**

- **Tier 1 (single-tool swap):** if only `/trades` fails (KYC 412), reroute that one tool to **Alpaca paper-trading** (instant global signup, $100k fake capital). User chat still says "compro SPY"; backend is different. Pre-wire this swap before stage time.
- **Tier 2 (full pivot, LatAm-preserving):** if Wallbit is fully down, pivot the demo narrative to **Bitso**: agent reads ARS+USDT balances, executes BUY USDT against ARS, withdraws ARS to a CVU. Loses stocks and robo-advisor, keeps the LatAm/inflation-hedge story.
- **Tier 3 (last resort):** play the **pre-recorded backup video** committed by 2026-05-09 23:59 ART (per Section 7, item 13) and pitch live without live API calls.

Pre-wire all three tiers before pitch time. Have Alpaca paper keys and a Bitso sandbox key sitting in environment variables on the deployed Vercel build, gated by a feature-flag query param so a switch is one click.

### 9.4 Caveats and open questions

- We did **not** individually verify OKX/Bybit/KuCoin docs in this pass (UNCONFIRMED). They are functionally equivalent to Binance/Bitso for the API-key+HMAC pattern; if a non-Binance crypto-only Plan B is needed, sweep these.
- **Bitso sandbox account opening time** is not documented in the pages we reached - UNCONFIRMED whether it's instant-by-email like Alpaca or whether a Bitso testing-environment account requires KYC/manual approval. Practical advice: have a team member start the Bitso testing-environment signup *now* in parallel, before committing to it as Plan B.
- **IOL "ambiente de pruebas"** requires an existing live IOL investment account plus a manual activation request via internal messaging - PARTIAL. The team would need at least one member with an IOL account already to use it as a hackathon backup.
- **lemon.markets** (the German brokerage infrastructure at [lemon.markets](https://www.lemon.markets/)) is **NOT** Lemon Cash and is **invite-only**. Do not confuse them in the pitch or in the appendix; we have seen this conflation in search results.
- **Belvo Argentina coverage** as of 2026-05-09 is unclear. Public docs and 2025 press releases position the product in BR/MX/CO with stated *interest* in AR/CL/PE, but no concrete AR institution catalog was reachable in our search - PARTIAL.
- This appendix is a comparison of API surfaces only. **No new product directions are proposed** - the team has chosen the Wallbit-based agent (per Section 6) and this appendix exists to harden that choice, not to revisit it.

### 9.5 Discovery + execution APIs (full agent loop)

**Why this exists:** the Agentic Money pitch requires APIs where one auth surface lets the agent (1) *discover* a financial product (catalog/listing endpoint with metadata: ticker, type, fees, min size, current price), (2) *reason* over user balance + catalog, and (3) *execute* on a product from the same catalog. Trading-only APIs with a real listing endpoint count. Read-only data APIs (Polygon, Finnhub, Alpha Vantage) and read-only aggregators (Plaid Investments) do **not** count - they break the loop at step 3.

**Confidence labels:** CONFIRMED = both endpoints documented and demonstrably under one auth model; PARTIAL = both exist but a sub-detail (sandbox, scope, asset count) is missing or auth has caveats; UNCONFIRMED = inferred / docs page not reachable in our 2026-05-09 fetch.

#### 9.5.1 Comparison table

| API | Auth model | Catalog endpoint | Execution endpoint | Asset universe | LatAm relevance | Hackathon-feasible (24h)? | Confidence | Source |
|---|---|---|---|---|---|---|---|---|
| **Wallbit** | `X-API-Key` static header, two scopes `read`/`trade` | `GET /api/public/v1/assets` (12 categories incl. ETF, TREASURY_BILLS, ARGENTINA_ADR) + `GET /assets/{symbol}` for detail | `POST /api/public/v1/trades` (MARKET/LIMIT/STOP/STOP_LIMIT) + `POST /roboadvisor/deposit` + `POST /operations/internal` | US stocks/ETFs/treasuries/Argentina-ADRs + robo-advisor + USD/ARS internal moves; crypto observe-only | **High** - BA-based, USD+ARS native | **YES** - one header, no signing, no sandbox needed if using small real account; KYC required for `/trades` | CONFIRMED | [assets/list](https://developer.wallbit.io/docs/api-reference/assets/list), [trades/create](https://developer.wallbit.io/docs/api-reference/trades/create), [quickstart](https://developer.wallbit.io/docs/quickstart) |
| **Alpaca** | `APCA-API-KEY-ID` + `APCA-API-SECRET-KEY` headers (one auth setup covers data + trade) | `GET /v2/assets` (filterable by `asset_class=us_equity` or `asset_class=crypto`; status, exchange filters) | `POST /v2/orders` (same key) | **US stocks + ETFs + 20+ crypto assets across 56 pairs (BTC/USD, ETH/USD, etc.) + options.** Same `/v2/assets` and `/v2/orders` cover crypto via `asset_class=crypto` filter | Low (US broker; international jurisdictions vary) | **YES** - paper-trading is global, free, instant by email, $100k simulated capital | CONFIRMED | [Alpaca authentication](https://docs.alpaca.markets/docs/authentication), [crypto-trading](https://docs.alpaca.markets/docs/crypto-trading), [paper-trading](https://docs.alpaca.markets/docs/paper-trading) |
| **Bitso** | API key + nonce + HMAC-SHA256 per request | `GET /v3/available_books` (returns crypto pairs with min/max amount, tick size, fees) | `POST /v3/orders` (uses same `book` codes from `/available_books`) | **Crypto pairs only** (btc_mxn, eth_btc, etc.; ARS pairs on Bitso Alpha per [docs.bitso.com](https://docs.bitso.com/bitso-api/docs/api-overview)). No stocks via API. | **High** - Argentina/Mexico/Brazil/Colombia/Chile/Peru, ARS+MXN+BRL fiat books | YES (HMAC adds 1-2h of dev) | CONFIRMED | [available_books](https://docs.bitso.com/bitso-api/docs/list-available-books), [place-an-order](https://docs.bitso.com/bitso-api/docs/place-an-order) |
| **Binance** | API key + secret HMAC (also supports RSA, Ed25519) | `GET /api/v3/exchangeInfo` (symbols, base/quote, order types, filters, status) | `POST /api/v3/order` (uses `symbol` from exchangeInfo) | **Crypto-only** (spot pairs ETHBTC, BTCUSDT, etc.) | Medium (USDT/ARS pairs exist on Binance; Binance.US separate) | YES - free testnet at `testnet.binance.vision` | CONFIRMED | [Binance REST](https://developers.binance.com/docs/binance-spot-api-docs/rest-api), [exchangeInfo](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/general-endpoints) |
| **Coinbase Advanced Trade** | `CB-ACCESS-KEY` + signed-by-secret + timestamp HMAC | `GET /api/v3/brokerage/products` | `POST /api/v3/brokerage/orders` | **Crypto-only** | Low (US-first) | PARTIAL - no clear public retail sandbox | PARTIAL | [Coinbase Advanced Trade overview](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/overview) |
| **Kraken (Spot REST)** | `API-Key` + `API-Sign` HMAC-SHA512 + nonce | `GET /0/public/AssetPairs` | `POST /0/private/AddOrder` (uses pair codes from AssetPairs) | **Crypto-only** spot pairs | Low | PARTIAL - no public retail sandbox; live-only with small balances | PARTIAL | [Kraken API](https://docs.kraken.com/api/), [tradable-asset-pairs](https://docs.kraken.com/api/docs/rest-api/get-tradable-asset-pairs) |
| **Tradier** | OAuth2 OR static API token (Production / Sandbox tokens via account settings) | `GET /v1/markets/lookup` (Search/Lookup Symbol per [getting-started](https://docs.tradier.com/docs/getting-started)) | `POST /v1/accounts/{id}/orders` (stocks, ETFs, options strategies, stop-loss, bracket) | **US stocks + ETFs + options.** No crypto. | None | YES - sandbox token instantly | PARTIAL (sandbox account approval cadence not in docs) | [Tradier getting-started](https://docs.tradier.com/docs/getting-started) |
| **IOL InvertirOnline** | OAuth2 password grant + 15-min bearer + refresh ([api.invertironline.com](https://api.invertironline.com/)) | Yes (per docs - asset/quote endpoints; specific endpoint not enumerated in docs we reached) | Yes (buy/sell/cancel orders) | **Argentine stocks, CEDEARs, bonds, dollar MEP** | **Highest** - native Argentine broker | NO without prep - requires existing IOL account + manual API activation request, plus OAuth bearer plumbing | PARTIAL | [api.invertironline.com](https://api.invertironline.com/), [invertironline.com/api](https://www.invertironline.com/api) |
| **Interactive Brokers Client Portal API** | **Session-auth via local Java Gateway with manual login + 2FA** OR enterprise OAuth2 | Yes | Yes | US + global multi-asset | Limited | **DISQUALIFIED** for the loop: local-gateway session is not a clean static-auth model and 2FA login breaks agent automation | n/a | [interactivebrokers.com cpapi-v1](https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/) |
| **Mercado Pago** | OAuth2 + access token | Read endpoints exist | Money-movement (wallet-to-wallet) is **commercial-advisor-gated**, not generally enabled per [Mercado Pago developer reference](https://www.mercadopago.com.ar/developers/en/reference) | Payments, not investments | Yes (AR/BR/MX) | NO - the execute side for moving a user's own money is not retail-self-serve | ABSENCE CONFIRMED for the loop | [Mercado Pago developers](https://www.mercadopago.com.ar/developers/en/reference) |
| **Lemon Cash / Buenbit / Ripio / Belo / Cocos / Bull Market** | No public developer API | n/a | n/a | n/a | High (would-be-LatAm) | NO - no public API in our 2026-05-09 search; Cocos has only unofficial reverse-engineered Python client | ABSENCE CONFIRMED | search 2026-05-09 |
| **Hyperliquid** | Wallet private-key signing (EIP-712); generate "API wallet" key, sign every action - "no API keys" | `GET https://api.hyperliquid.xyz/info` (perps metadata) | Trade/transfer/withdraw via signed L1 actions from same wallet | DeFi perps (crypto only) | Global / off-brand for fiat consumer pitch | YES technically; off-brand for our consumer-fiat pitch and key material is more dangerous than an API key | CONFIRMED (loop exists) / off-brand | [Hyperliquid docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api) |
| **dYdX** | Wallet signing (EVM/Cosmos depending on chain version); same wallet auth covers both info read and order placement | Yes (markets/perps endpoint) | Yes (place-order via signed message) | DeFi perps (crypto only) | Global / off-brand | YES technically; same off-brand caveat as Hyperliquid | CONFIRMED (loop exists) / off-brand | [docs.dydx.xyz](https://docs.dydx.xyz/) |

#### 9.5.2 Top 3 ranked for "full agent loop, usable in 24h"

1. **Wallbit** - the only API in this list that bundles **fiat checking + stocks/ETFs + treasuries + Argentina-ADR + robo-advisor + crypto observation + card status** behind a single `X-API-Key` static header. Catalog (`/assets`) and execution (`/trades`, `/operations/internal`, `/roboadvisor/deposit`) are explicitly cross-referenced - the symbol you discover is the symbol you trade. **Why this for our agent:** narrowest auth surface (no HMAC, no OAuth, no signing nonce), broadest investable bundle, plus native USD+ARS context that maps to the Buenos Aires audience.
2. **Alpaca** - the gold-standard discover+execute loop in pure brokerage form: `GET /v2/assets?asset_class=us_equity` and `?asset_class=crypto` both feed the same `POST /v2/orders` under one `APCA-API-KEY-ID + SECRET` pair. Paper-trading is instant, free, and global. **Why this for our agent:** strongest Plan-B for the stock-trading half of the demo if Wallbit `/trades` 412s on KYC mid-pitch; same chat narrative ("compre 300 USD de SPY"), Alpaca paper backend swapped in. Loses Wallbit's ARS/robo-advisor/card bundle, so it's a fallback rail not a replacement product.
3. **Bitso** - the strongest LatAm-aligned crypto-only discover+execute. `/v3/available_books` -> `/v3/orders` is a clean loop, ARS pairs are native (Bitso Alpha), and the sandbox at `api-stage.bitso.com` is documented. **Why this for our agent:** Plan-B if Wallbit fails entirely and the team needs to keep the LatAm/inflation-hedge narrative; agent reads ARS+USDT balances and rotates pesos to USDT (or vice versa) when blue rate moves. HMAC adds ~1-2h of plumbing.

Honorable mentions: **Tradier** (cleanest US-stock+options loop with a real static token, but no LatAm angle), **IOL InvertirOnline** (only realistic way to put real CEDEARs and dollar MEP in front of judges, but OAuth + manual API-activation gate kills it as a Plan B in 24h), **Hyperliquid/dYdX** (technically perfect loop, but wallet-signing is a different primitive and off-brand for a consumer fiat-first pitch).

#### 9.5.3 Verdict on Wallbit's uniqueness for the full agent loop

Among API-key-authed products that satisfy the full discover-reason-execute loop, **Wallbit is the only one that bundles fiat (USD + ARS) + US stocks/ETFs + treasuries + an Argentina-themed sub-category + a robo-advisor primitive in a single catalog/execute pair**. Every other contender either drops a major asset class or splits across multiple auth surfaces:

- Alpaca has stocks + crypto but **no fiat banking, no ARS, no robo-advisor primitive**, and no Argentine framing.
- Bitso has crypto + ARS fiat but **no US stocks, no ETFs, no robo-advisor**, and HMAC-signs every request.
- Binance, Coinbase, Kraken are crypto-only.
- Tradier is US-stocks-and-options-only with no LatAm hook.
- IOL is the only Argentine securities API but requires OAuth + manual activation and has no crypto.
- Mercury/Brex are US-business-banking-only with no investment catalog.
- Mercado Pago is gated on the execute side.
- Lemon/Buenbit/Ripio/Cocos/Belo/Bull Market have no public developer API.

So when judges ask "could you have done this with [API]?" the cleanest defensive answer remains the one in §9.3: Wallbit is functionally Alpaca + USD/ARS checking + crypto observation + card + robo-advisor + LatAm UX behind one static key. Nothing else lets a 36-hour team ship a multi-asset agentic-money product without stitching three separate auth flows. **For the demo, this means: keep the pitch tightly framed as "the agent that lives inside your Wallbit account," not "a multi-broker aggregator," because the multi-broker aggregator pitch would require multiple auth surfaces and lose the 24-hour feasibility argument.**
