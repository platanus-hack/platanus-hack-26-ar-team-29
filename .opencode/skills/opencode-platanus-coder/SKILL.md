---
name: opencode-platanus-coder
description: Build a hackathon MVP from the execution plan, preserve demo reliability, and maintain a reproducible build log.
---

# Platanus Coder Skill

Use this skill with the `coder` agent.

## Procedure

1. Read the execution plan and identify the smallest vertical slice.
2. Make the app run locally before integrating external services.
3. Implement the main happy path with seeded or fake data first.
4. Replace fake data with real integrations only after the slice works.
5. Add loading, empty, and error states.
6. Add minimal tests for core logic and smoke-test the demo path.
7. Keep `artifacts/03_build_log.md` current.

## Output

- Code changes.
- Tests or smoke checks.
- Updated `artifacts/03_build_log.md`.

## Guardrails

- No secrets in repo.
- No commit, push, deploy, or paid-service mutation without approval.
- Do not refactor unrelated code.
- Prefer shippable over elegant.
