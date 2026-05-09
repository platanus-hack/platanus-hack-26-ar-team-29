# 03 Build Log

Status: maintained by Coder.

## Summary

- Current state: frontend chat now integrates with the real FastAPI backend MVP for chat sessions, messages, plan proposal/approval/rejection, and session WebSocket frames.
- Demo URL: not deployed.
- Local run command: backend `uv run uvicorn app.main:app --port 8000`; frontend `bun dev` from `frontend/`.
- Main branch/commit reference: not recorded in this session.

## Completed Work

- Inspected backend implementation and docs: FastAPI routes, services, WebSocket manager, backend README, deviations, and architecture notes.
- Added typed frontend REST client for available backend endpoints under `/api/v1`.
- Added frontend WebSocket client for backend MVP protocol at `/api/v1/ws?session_id=<uuid>`.
- Replaced mocked `/chat` flow with real session boot, message history hydration, WS streaming, plan proposal rendering, and approve/reject actions.
- Moved chat experience to `/` so `localhost:3000` opens the chat directly; removed `/chat` route page.
- Made chat layout mobile-first and responsive: full-height mobile shell, safe-area aware header/input, wider desktop container, adaptive message widths, empty state, touch-sized controls, and stacked plan actions on narrow screens.
- Replaced mock trade card with real plan summary/confirmation components.
- Updated frontend context documentation with backend integration details and env vars.

## Files Changed

| File | Purpose |
| --- | --- |
| `frontend/app/lib/backend/types.ts` | TypeScript DTOs for backend REST responses and WS frames. |
| `frontend/app/lib/backend/client.ts` | REST client, env-based base URL, Spanish headers, backend error parsing. |
| `frontend/app/lib/backend/ws.ts` | WebSocket helper for session subscription frames. |
| `frontend/app/page.tsx` | Root route now contains the integrated chat UI. |
| `frontend/app/chat/page.tsx` | Removed; `/chat` route no longer exists. |
| `frontend/app/chat/types.ts` | Updated UI message model to support assistant/system roles and real plans. |
| `frontend/app/chat/_components/ChatInput.tsx` | Spanish copy. |
| `frontend/app/chat/_components/ChatMessage.tsx` | Render real plan confirmation cards and system messages; mobile-first bubble sizing. |
| `frontend/app/chat/_components/ChatThread.tsx` | Pass plan action handlers and busy state; responsive scroll area and empty state. |
| `frontend/app/chat/_components/PlanConfirmation.tsx` | Approval/rejection component for backend `TradePlan`; stacked mobile actions. |
| `frontend/app/chat/_components/PlanSummary.tsx` | Plan/step summary component; responsive labels and step rows. |
| `frontend/app/chat/api.ts` | Removed obsolete mock chat API. |
| `frontend/app/chat/_components/TradeConfirmation.tsx` | Removed obsolete mock trade card. |
| `frontend/app/chat/_components/TradeSummary.tsx` | Removed obsolete mock trade summary. |
| `frontend/FRONTEND_CONTEXT.md` | Updated with integration context and env vars. |
| `.opencode/artifacts/03_build_log.md` | Updated build log. |

## Commands Run

| Command | Result | Notes |
| --- | --- | --- |
| Read/glob repository files | OK | Inspected frontend and backend files/documentation. |
| `bun run lint` | Failed | `bun` is not installed in this environment. |
| `bun run build` | Failed | `bun` is not installed in this environment. |
| `npm run lint` | Failed | Dependencies are not installed; `eslint: not found`. |
| `npm run build` | Failed | Dependencies are not installed; `next: not found`. |
| Grep old mock imports/usages | OK | No stale mock `TradeConfirmation`, `TradeSummary`, `./api`, or `bot` role usages found beyond new backend client method. |
| `npm install` | OK | Installed local frontend dependencies for testing; removed generated `package-lock.json` afterward to keep existing `bun.lock` workflow. |
| `npm run lint` | Failed then fixed | First run found `react-hooks/set-state-in-effect` in `app/chat/page.tsx`; removed synchronous state set from effect. |
| `npm run lint` | OK | ESLint passed after fix. |
| `npm run build` | OK | Next production build and TypeScript passed; routes `/` and `/chat` generated. |
| `npm run dev -- --port 3000` + HTTP fetch `/chat` | OK | Returned 200 and rendered `Pampa Chat`. |
| Fetch `http://localhost:8000/api/v1/health` | Failed | Backend not running in this environment. |
| `python3 -m venv .venv && .venv/bin/pip install -e .` | Failed | Backend package lacks explicit package discovery for flat layout (`app`, `alembic`). |
| `.venv/bin/pip install ...` | OK | Installed backend runtime dependencies manually from `pyproject.toml`. |
| `docker run -d --name pampa-pg ... postgres:16` | OK | Started local Postgres on `localhost:5432`, DB `pampa`. |
| `PYTHONPATH=. .venv/bin/alembic upgrade head` | OK | Applied migration `0001_init_mvp`. |
| `PYTHONPATH=. .venv/bin/uvicorn app.main:app --port 8000` | OK | Backend running in background; health returns 200. |
| `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev -- --port 3000` | OK | Frontend running in background; `/chat` returns 200. |
| Node REST+WS smoke | OK | Created session, connected WS, sent `comprá 7 usd de apple`, received `plan_proposed`, rejected plan, received `plan_update rejected`. |
| Final HTTP status check | OK | Backend `/api/v1/health` 200; frontend `/chat` 200. |
| `npm run lint` after root-route move | OK | ESLint passed. |
| `npm run build` after root-route move | OK | Build passed; route list now only `/` and `/_not-found`. |
| HTTP smoke `/` and `/chat` | OK | `/` returns 200 and contains `Pampa Chat`; `/chat` returns 404. |
| `npm run lint` after responsive changes | OK | ESLint passed. |
| `npm run build` after responsive changes | OK | Build passed. |
| HTTP smoke `/` after responsive changes | OK | `/` returns 200 and contains `Pampa Chat`. |

## Tests And Checks

| Check | Command/steps | Result |
| --- | --- | --- |
| Unit | Not run yet | No frontend unit test harness exists. |
| Smoke | Passed | `npm run lint`, `npm run build`, and `/chat` HTTP smoke passed after installing frontend dependencies. |
| Functional | Passed | REST+WS smoke passed against local FastAPI + Postgres. Approval execution with Wallbit not tested because no Wallbit key/connection is configured. |
| Stress | Not run | Out of scope for this slice. |
| Security | Manual | No secrets added; frontend uses public API/WS URL env vars only. |

## Environment Variables

Do not paste secret values here. Document names only.

| Variable | Purpose | Required for demo |
| --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend REST backend base URL, default `http://localhost:8000`. | No if backend local on 8000; yes otherwise. |
| `NEXT_PUBLIC_WS_BASE_URL` | Frontend WebSocket backend base URL; derived from API base if omitted. | No. |

## API / Deploy Setup Notes

- Backend MVP exposes direct arrays/objects, not the ideal `{data: ...}` envelopes from the canonical API artifact.
- Backend MVP WebSocket uses simple `type` frames and one session per socket; no `kind/topic/seq`, no replay, no multiplexing.
- Frontend intentionally targets the implemented backend documented in `backend/README.md` and `backend/docs/deviations.md`.
- Current local processes: Postgres Docker container `pampa-pg`, backend on `http://localhost:8000`, frontend on `http://localhost:3000`.

## Decisions And Shortcuts

- Kept integration dependency-free: native `fetch` and `WebSocket` only.
- Chat history hydration fetches each referenced plan individually when a `plan_proposal` message has `plan_id`.
- Optimistically updates user messages and plan states, then reconciles via WS or fallback `GET /plans/{id}` on failure.
- Added portfolio/connections client functions even though no UI surfaces consume them yet, because backend endpoints exist.

## Known Issues

- This environment has `python3` but not `uv`; backend quick-start cannot be executed as documented without installing `uv`.
- Backend editable install with pip currently fails because setuptools detects multiple top-level packages in flat layout.
- Real plan execution after approval still requires a configured Wallbit connection/API key; local smoke used reject path to avoid external mutation.
- If a WS disconnect happens mid-turn, backend has no replay; frontend currently keeps REST history only on initial boot.
- `chat_message` frames do not include `turn_id`, so frontend removes temporary stream messages broadly when final messages arrive.
- No auth headers are sent because backend MVP ignores auth and uses dev user.
- Balances, transactions, connections, and health clients exist but no frontend screens consume them yet.

## Reviewer Handoff

- Main flow to test: start backend on port 8000, start frontend, open `/chat`, send `comprá 10 usd de apple`, watch streamed preface + plan card, approve/reject.
- Risk areas: WS timing (subscribe before send), backend availability, no replay on reconnect, Wallbit key required for real plan execution after approval.
- Suggested review focus: TypeScript build, chat happy path, plan state transitions, user-visible Spanish errors.
