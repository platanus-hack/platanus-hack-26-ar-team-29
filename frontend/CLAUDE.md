# CLAUDE.md — Frontend

Guidance for Claude Code when working inside `frontend/`.

## Read-before-write rule

**Before making any change to this directory, read:**

1. [`README.md`](./README.md) — overview, setup, conventions, commands.
2. [`AGENTS.md`](./AGENTS.md) — crucial warnings about Next.js 15 breaking changes. Do not assume compatibility with previous Next.js knowledge. Before writing code that depends on Next.js specific APIs/conventions, review the relevant guide in `node_modules/next/dist/docs/`.
3. The relevant section(s) of [`../.opencode/artifacts/`](../.opencode/artifacts/) — these are the **authoritative** design contracts (architecture, API surface, frontend design). If there is a conflict between the current prototype and the artifacts, treat the prototype as a temporary implementation and the artifacts as product direction, unless the team decides otherwise.

**After completing any change, update this file** with anything a future agent or human would benefit from knowing.

## Project overview

**Atajo** is a Spanish-first agentic-finance app for Platanus Hack 26 BA (*Agentic Money* track). The frontend is the primary surface where the user interacts with the conversational agent to query, plan, and approve actions involving money.

Currently, the implementation shows a real chat integrated with the backend directly in `/`. The agent and layout occasionally refer to the name "Pampa", but the official product name is **Atajo**.

The frontend is a Next.js App Router application written in TypeScript, using React 19 and Tailwind CSS v4.

## Tech stack

- **Framework:** Next.js 15 (`next@16.3.0-canary.17` / App Router)
- **Runtime UI:** React 19 (`react@19.2.6`, `react-dom@19.2.6`)
- **Language:** TypeScript 5 (`strict: true`)
- **Styles:** Tailwind CSS 4 via `@tailwindcss/postcss`
- **Lint:** ESLint 9 (`eslint-config-next/core-web-vitals`, `eslint-config-next/typescript`)
- **Package Manager:** Bun

## Architecture (one-paragraph summary)

The target frontend is not just a chat; it is a chat application with connected financial lenses. Chat is the universal surface and control plane. Tabs are state projections: they read directly, but sensitive writes pass through the agent and a plan approval ceremony. Plans are first-class entities, not ephemeral modals. The app relies on real-time data via WebSocket, not client-side polling. The UI must be provider-aware but without hardcoding specific providers (like Wallbit/Ethereum) into general components.

**Authoritative sources:** [`../.opencode/artifacts/02-2_frontend_design.md`](../.opencode/artifacts/02-2_frontend_design.md) (design) and [`../.opencode/artifacts/02-3_api_surface.md`](../.opencode/artifacts/02-3_api_surface.md) (REST/WebSocket contract).

## Layout (where things go)

```text
frontend/
  app/
    globals.css        -> Global Tailwind imports and CSS variables
    layout.tsx         -> Root layout, font setup (Geist)
    page.tsx           -> Main product screen (chat integration)
    chat/              -> Chat-related logic and components
      page.tsx         -> Chat UI and state management
      types.ts         -> UI models (Message, TradePlan, etc.)
      api.ts           -> API helpers for chat sessions
      _components/     -> Chat Input, Thread, Message bubbles, Trade confirmations
    lib/
      backend/         -> Typed REST and WebSocket clients
  public/              -> Static assets
  AGENTS.md            -> Next.js 15 specific LLM guidance
  CLAUDE.md            -> This file (Frontend context and rules)
  README.md            -> Setup and quick start
```

## Common commands

| Action | Command |
|---|---|
| Install deps | `bun install` |
| Run dev server | `bun dev` |
| Build for prod | `bun run build` |
| Lint | `bun run lint` |

All commands run from `frontend/`.

## Conventions

- **Environment variables:** Use `NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_WS_BASE_URL`. Do not store secrets in the repo. Currently, no auth token is sent because the MVP backend uses a hardcoded dev user.
- **Language & Locale:** The product is Spanish-first with an Argentine register (`es-AR`). API requests should send `Accept-Language: es-AR`.
- **Writes:**
  - Reads: REST snapshot per tab.
  - Updates: WebSocket with deltas per topic.
  - Sensitive writes: Mediated by chat/agent and plan approval.
  - Direct writes: Allowed for metadata or low-risk idempotent actions. Financial actions should never be executed directly from a button calling a trade endpoint.
- **API Errors:** The backend returns an envelope `{ error: { code, message_es, ... } }`. `app/lib/backend/client.ts` parses this and throws a `BackendApiError`.
- **WebSocket:** Use `wss://<host>/api/v1/ws`. One socket per app, multiplexing topics. The client must support `subscribe`, `unsubscribe`, `ack`, `error`, `ping`, `pong`, and `resync`.

## Code style

- Prefer editing existing files to creating new ones.
- Keep components provider-aware but generic (avoid hardcoded provider logic unless in specific connection forms).
- Avoid client-side polling in tabs; use WebSocket or documented manual refresh.
- Separate mock types from target API types to avoid coupling the prototype to an incomplete contract.

## Implementation Status & Gaps (Out of scope right now)

- **UI/UX & Copy:** The UI is currently mostly in English; the target is `es-AR` with no i18n system yet. Metadata, title, and `lang` still show generic "Create Next App" / `en` and need updating to Atajo / `es-AR`.
- **Routing & Navigation:** There is no routing for the 11 target surfaces (Home, Balances, Holdings, Activity, etc.) and no persistent app layout (navigation, sidebar).
- **State & Data Management:** There is no auth/session management, nor a global state/cache strategy for REST snapshots + WS deltas.
- **Plans & Trade Steps:** The current trade is an embedded object inside a message; the target is a first-class `TradePlan` with steps and states when real approval is implemented.
- **Testing:** No tests are implemented.

## Footguns

- **Next.js 15 / React 19:** Introduces breaking changes (e.g., async server components handling, form actions). See `AGENTS.md` before making assumptions.
- **Styling:** The `body` in `globals.css` currently forces `font-family: Arial...` which competes with the configured Geist fonts.
- **WebSockets:** Wait for WS `subscribed` frame before sending messages over REST; frames emitted before subscription are dropped in the v1 backend.