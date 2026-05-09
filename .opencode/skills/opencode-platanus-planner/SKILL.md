---
name: opencode-platanus-planner
description: Convert a selected hackathon idea into a concrete 36-hour implementation plan with stack, contracts, tests, and fallback paths.
---

# Platanus Planner Skill

Use this skill with the `planner` agent.

## Procedure

1. Select one idea and state the user, problem, and one-sentence pitch.
2. Define must-haves, should-haves, and explicit non-goals.
3. Choose the smallest stack that supports the demo.
4. Prefer Rust backend when the team can ship it quickly and the SDK fit is acceptable.
5. Include sponsor tools only when they strengthen the product.
6. Define API contracts, data schema, frontend states, AI prompts, and fallback behavior.
7. Break the work into timeboxed milestones.
8. Define acceptance criteria and tests.

## Output

Return Markdown ready for `artifacts/02_execution_plan.md`.

## Guardrails

- May write only `artifacts/02_execution_plan.md`.
- Avoid over-architecture.
- Every feature must serve the demo or core user job.
