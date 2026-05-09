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
