# 02 Execution Plan — Decision Addendum: Agent Runtime Model and Backend Hosting

**Status:** Locked 2026-05-09. This addendum amends the canonical execution plan in [`02-1_backend_architechture.md`](./02-1_backend_architechture.md). Sections in this file are written as **patches** to that document — every section here either inserts a new subsection or appends a row to an existing table there, and is referenced by section number from the canonical plan.

**Why a separate file:** the planner-only artifact-write hook in this repo permits writing exactly `.claude/artifacts/02_execution_plan.md`. The canonical plan currently lives under the longer filename for historical reasons; treat this file as the authoritative decision record for the two questions below, and treat `02-1_backend_architechture.md` as the architecture reference it patches into. A future cleanup pass should fold this addendum directly into the canonical plan and rename it.

**Questions answered here:**

1. Should the ChatAgent (and the other agent runtimes) run on Anthropic's Claude Managed Agents, on the self-hosted in-process Python loop the canonical plan §6 already assumes, or on a hybrid?
2. Where does the backend process actually run for the demo?

---

## Table of contents

1. [Decision summary](#1-decision-summary)
2. [Patch — canonical §6.5 "Why not Managed Agents (yet)"](#2-patch--canonical-65-why-not-managed-agents-yet)
3. [Patch — canonical §11 "Locked design decisions" rows 17–18](#3-patch--canonical-11-locked-design-decisions-rows-1718)
4. [Patch — canonical §12 "Tech stack" hosting row](#4-patch--canonical-12-tech-stack-hosting-row)
5. [Patch — canonical §15 "Companion artifacts" cross-reference note](#5-patch--canonical-15-companion-artifacts-cross-reference-note)
6. [Operational notes for the Coder](#6-operational-notes-for-the-coder)
7. [Sources](#7-sources)

---

## 1. Decision summary

**Q1 — Runtime model:** **Self-hosted in-process asyncio loop** as already designed in canonical §6. Reject Managed Agents for v1; reject hybrid. Justification one-liner: the "confirm-once-fire-all" plan-approval handshake in §6.1 needs to *bundle* multiple write `tool_use` blocks into a single user-facing `TradePlan` and gate execution on a single approve/reject, while Managed Agents only exposes **per-tool** confirmation primitives, and its custom-tool callbacks still require our server to round-trip every read tool through Anthropic. We pay extra latency, lose step-through debuggability, and have to bridge SSE → WebSocket — for zero product gain.

**Q2 — Backend hosting v1:** **Local laptop running Uvicorn, exposed via Cloudflare Tunnel.** Fallback: **Fly.io** (Buenos Aires `eze` region, paid plan to disable scale-to-zero). The laptop path is the most hackathon-typical, has zero cold-start risk, gives us native WebSocket support and full filesystem/log access during development, and the Cloudflare Tunnel gives the demo a stable public HTTPS URL that survives a wifi reconnect. Fly.io is the fallback if the laptop dies during the demo block.

**Two-line rationale.** Managed Agents is the wrong abstraction for our handshake — we'd be writing more glue, not less, and demoing through an opaque session ID. Local-laptop + Cloudflare Tunnel beats every free-tier PaaS (Render, Railway, Fly.io free) here because hackathon demos die from cold starts and 15-min idle suspends, not from "my laptop fell over"; we mitigate the latter with a hot Fly.io paid standby and a recorded fallback video (already locked in research brief §7).

**Options weighed for Q2.** Render free / Railway free → rejected: 15-min idle suspend will freeze a multi-minute pitch mid-demo; cold-start re-pull of a Python image is 10–30s. Render / Railway paid → strictly worse than Fly.io paid for our case (Fly.io has a São Paulo `eze`-equivalent region closer to BA than Render's Oregon / Frankfurt; Railway has no SA region). Single VPS (Hetzner / DigitalOcean) → ~30 min of setup we don't need, and Hetzner has no SA region either. Supabase Edge Functions → Deno-only; doesn't fit the Python plan; skipped. Sponsor-provided hosting → research brief §6.5 / §7 confirms no PaaS credit was pre-arranged for this hack (Vercel covers the frontend; the backend is on us). Local laptop + tunnel + Fly.io paid fallback wins.

---

## 2. Patch — canonical §6.5 "Why not Managed Agents (yet)"

> **Insert this subsection in [`02-1_backend_architechture.md`](./02-1_backend_architechture.md) immediately after §6.4 ClassifierAgent and before the `---` separator preceding §7.**

### 6.5 Why not Managed Agents (yet)

Anthropic's [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) (public beta since 2026-04-08, header `managed-agents-2026-04-01`) is a hosted agent harness that owns the loop, retries, and context compaction. Tempting at face value, but the wrong fit for v1 — our agent runtime exists primarily to enforce the "confirm-once-fire-all" plan-approval handshake (§6.1), and that primitive is custom enough that delegating the loop to Anthropic costs us more control than it buys us in scaffolding. The five concrete blockers:

- **No "bundle N writes into one approval" primitive.** Managed Agents exposes `user.tool_confirmation` ([events and streaming docs](https://platform.claude.com/docs/en/managed-agents/events-and-streaming)) which fires **per tool call**, not per plan. Our UX gates on a `TradePlan` aggregate of N steps; replicating that on per-tool confirmations means racing to collect `agent.custom_tool_use` events for writes, force-denying each one, then synthesising our own plan — fighting the hosted loop instead of using it.
- **Custom tools still round-trip our backend.** `agent.custom_tool_use` requires our server to respond with `user.custom_tool_result`, so we already need a public URL — and pay BA → Anthropic → BA latency on **every tool dispatch** on top of model latency. The "managed loop saves you infra" pitch evaporates the moment your tools live on your own server, which all of ours do.
- **Streaming is SSE, our chat transport is WebSocket.** We'd be bridging SSE → WS in the demo critical path, an extra failure mode for zero product gain. The canonical plan §6.1 / §9a is built around a single bidirectional channel.
- **Debuggability and demo reliability.** A self-hosted asyncio loop is a `pdb` / print / log-tail away; a hosted loop is an opaque session ID. The runtime billing is also $0.08 per running session-hour ([Managed Agents 2026 overview](https://blog.laozhang.ai/en/posts/claude-managed-agents)) on top of token cost, and the `managed-agents-2026-04-01` header is explicit that behaviors may change between releases.
- **BA latency budget.** Buenos Aires → Anthropic adds a per-tool-call round-trip that we do not need; with a self-hosted loop, only the model call crosses the WAN.

**Re-evaluate post-MVP** if Anthropic ships a first-class plan-approval primitive or batched tool-confirmation policy that maps onto §6.1 cleanly. The agents/ module already isolates the loop behind the `ToolDispatcher` and `PlanExecutor`, so swapping in is a localized change.

---

## 3. Patch — canonical §11 "Locked design decisions" rows 17–18

> **Append the two rows below to the table at the end of `02-1_backend_architechture.md` §11. The table currently ends at row 16.**

| #  | Decision                  | Choice                                                            | Reason                                                                                                                                                                                       |
|----|---------------------------|-------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 17 | Agent runtime model       | Self-hosted in-process asyncio loop (§6); reject Managed Agents   | Plan-approval handshake (§6.1) needs per-plan, not per-tool, gating; custom tools already require a public URL so the hosted-loop convenience is moot; SSE-vs-WS mismatch; demo debuggability |
| 18 | Backend hosting v1        | Local laptop running Uvicorn + Cloudflare Tunnel                  | Hackathon-typical; zero cold-start; native WebSocket; tunnel gives stable HTTPS public URL with auto-reconnect; full local logs / pdb / hot-reload during the build                            |
| 19 | Backend hosting fallback  | Fly.io (region `eze`, paid plan, no scale-to-zero)                | Closest BA-region PaaS with first-class WebSocket; predictable IP; we pre-deploy a hot standby before demo block, switch DNS if the laptop fails                                              |

---

## 4. Patch — canonical §12 "Tech stack" hosting row

> **Insert a new "Hosting" subsection at the end of the §12 table in `02-1_backend_architechture.md`, after the developer-tooling rows.**

| Component                                       | Default choice                                       | Reason                                                              | Fallback                                                          |
|-------------------------------------------------|------------------------------------------------------|---------------------------------------------------------------------|-------------------------------------------------------------------|
| *— Hosting —*                                   |                                                      |                                                                     |                                                                   |
| Backend runtime host                            | Local laptop, Uvicorn `--host 0.0.0.0 --port 8000`   | Zero cold-start; full WebSocket support; native logs; one cable     | Fly.io paid plan in `eze` region                                  |
| Public URL / TLS                                | Cloudflare Tunnel (`cloudflared`) on a stable hostname under our domain | Free tier; auto-reconnect on wifi blip; survives IP changes; HTTPS handled | ngrok paid (reserved subdomain) if Cloudflare Tunnel breaks       |
| Frontend host                                   | Vercel (already locked in research brief §6.5 / §7) | Sponsor-aligned; zero ops; native Next.js                           | Netlify                                                           |

---

## 5. Patch — canonical §15 "Companion artifacts" cross-reference note

> **Add the following bullet to the §15 list in `02-1_backend_architechture.md`, immediately under the bullet for `02_execution_plan.md`.**

- **Decision addendum:** [`02_execution_plan.md`](./02_execution_plan.md) (this file) — locks the agent-runtime-model and hosting decisions (canonical §6.5, §11 rows 17–19, §12 hosting subsection). Until the canonical doc is renamed and these patches folded in, this is the authoritative record for those four decisions.

---

## 6. Operational notes for the Coder

These are not part of the patched canonical plan — they are practical instructions for the build phase, derived directly from the decisions above.

### 6.1 Cloudflare Tunnel setup (one-time, ~10 minutes)

1. `brew install cloudflared` on the host laptop.
2. `cloudflared tunnel login` (browser-auth into the team Cloudflare account; if no team account, register a free one — a `*.workers.dev` placeholder domain is enough for a demo URL).
3. `cloudflared tunnel create platanus-hack-26` → record the tunnel UUID.
4. Create `~/.cloudflared/config.yml` with one ingress rule pointing the tunnel hostname to `http://localhost:8000`.
5. `cloudflared tunnel route dns platanus-hack-26 demo.<our-domain>` (or use the auto-issued `*.cfargotunnel.com` subdomain — it works fine for a demo).
6. `cloudflared tunnel run platanus-hack-26` runs in a foreground tmux pane; print the public URL to a sticky note before the demo block.

### 6.2 Fly.io fallback (deploy once, leave running)

1. `fly launch --no-deploy --region eze --name platanus-hack-26-fallback`.
2. `fly secrets set` for every env var the laptop has (Anthropic key, Wallbit key, Supabase URL/anon-key, Fernet key — see canonical §11 row 13).
3. Use a vanilla Python Dockerfile; entrypoint is `uvicorn app.main:app --host 0.0.0.0 --port 8080`. Expose port 8080 in `fly.toml`. Set `min_machines_running = 1` (paid plan only — free tier scale-to-zero will kill demo cold-start).
4. `fly deploy` once, then leave it. Re-deploy only on critical fixes — the laptop is the source of truth during the build.
5. Set `FALLBACK_PUBLIC_URL` in our team chat / sticky note. The frontend's WebSocket URL is feature-flagged off an env var so the switch is one Vercel redeploy.

### 6.3 What "self-hosted in-process asyncio loop" actually means in code

The ChatAgent / TradeBotAgent loop is a normal `async def` that calls `anthropic.AsyncAnthropic().messages.create(..., stream=True)`, iterates streaming events, dispatches `tool_use` blocks through our `ToolDispatcher`, and gates writes via our `PlanExecutor` (canonical §6.1, §6.2). No Anthropic-hosted session, no `managed-agents-2026-04-01` header, no environment provisioning. The `ai/` module wraps `anthropic.AsyncAnthropic` only — no managed-agents SDK surface is imported.

### 6.4 What does **not** change

- §4 layered architecture is unchanged.
- §6.1 / §6.2 / §6.3 / §6.4 prose is unchanged.
- §7 background-worker topology is unchanged.
- §11 rows 1–16 are unchanged.
- The `agents/` module structure in §10 is unchanged.

---

## 7. Sources

Public references consulted while making the call. No secrets, tokens, or private URLs were sent to any of these:

- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview) — official beta docs, `managed-agents-2026-04-01` header, four-concept (Agent / Environment / Session / Events) model, SSE streaming, beta status.
- [Claude Managed Agents — sessions API](https://platform.claude.com/docs/en/managed-agents/sessions) — confirms session lifecycle (`idle` / `running` / `rescheduling` / `terminated`) and that custom tool flows still need host-side handling.
- [Claude Managed Agents — events and streaming](https://platform.claude.com/docs/en/managed-agents/events-and-streaming) — full event taxonomy. `user.tool_confirmation` is per-tool. `agent.custom_tool_use` requires `user.custom_tool_result` round-trip. Confirms SSE transport and the absence of any plan-bundle approval primitive.
- [Anthropic engineering — Scaling Managed Agents: decoupling the brain from the harness](https://www.anthropic.com/engineering/managed-agents) — explicit caveat that "if your product depends on a custom loop as a feature rather than as accidental plumbing, Managed Agents can feel too opinionated"; recommends Messages API for custom-loop products.
- [Claude Managed Agents in 2026: when to use it and when not to (LaoZhang AI Blog)](https://blog.laozhang.ai/en/posts/claude-managed-agents) — third-party survey; quotes $0.08/session-hour while running, metered to milliseconds (as of 2026-04-19).
- Canonical execution plan: [`02-1_backend_architechture.md`](./02-1_backend_architechture.md) — §6.1 confirm-once-fire-all, §6.2 tool registry as a port type, §7 background workers, §11 rows 1–16, §12 tech stack.
- Research brief: [`01_research_brief.md`](./01_research_brief.md) — §6.5 / §7 sponsor list (Anthropic, Profound, Supabase, Vercel, ElevenLabs — note: no PaaS hosting credit pre-arranged), §7 backup-demo-video deadline.
