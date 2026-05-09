# Backend Docs

Backend-specific notes that complement (do not replace) the canonical design artifacts in [`../../.claude/artifacts/`](../../.claude/artifacts/).

## How to use this directory

- **Before making changes** in `backend/`, read the relevant note here *and* the relevant section of the upstream artifact. The artifacts are authoritative; `docs/` captures local additions, deviations (with rationale), gotchas, and runtime tips.
- **After making changes**, update the relevant note here. If a change contradicts an artifact, document the deviation explicitly.
- Keep notes terse. Link out to artifacts rather than duplicate.

## Index

| Doc | Purpose |
|---|---|
| [`architecture.md`](./architecture.md) | Backend module layout summary; import-direction rules; pointers to authoritative design |
| [`deviations.md`](./deviations.md) | What this MVP slice intentionally skips vs the locked design (idempotency, audit log, canonical ledger, workers, etc.) |
| [`wallbit_api.md`](./wallbit_api.md) | Full API surface documentation and schema mappings discovered for Wallbit |

## Canonical design artifacts (upstream — authoritative)

| Artifact | Scope |
|---|---|
| [`01_research_brief.md`](../../.claude/artifacts/01_research_brief.md) | Track, sponsors, persona, problem framing |
| [`02-1_backend_architechture.md`](../../.claude/artifacts/02-1_backend_architechture.md) | **Backend architecture (load-bearing here)** |
| [`02-2_frontend_design.md`](../../.claude/artifacts/02-2_frontend_design.md) | Frontend surface inventory |
| [`02-3_api_surface.md`](../../.claude/artifacts/02-3_api_surface.md) | **REST + WebSocket contract** |
| [`02-4_database_schema.md`](../../.claude/artifacts/02-4_database_schema.md) | **Postgres schema (load-bearing here)** |
| [`03_build_log.md`](../../.claude/artifacts/03_build_log.md) | Coder build log |
| [`04_review_report.md`](../../.claude/artifacts/04_review_report.md) | Reviewer audit |
| [`05_demo_pack.md`](../../.claude/artifacts/05_demo_pack.md) | Final pitch + judge Q&A |
