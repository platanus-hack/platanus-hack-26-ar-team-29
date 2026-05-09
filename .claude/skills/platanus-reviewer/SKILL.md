---
name: platanus-reviewer
description: Review a hackathon MVP for demo reliability, setup, security, UX, mobile, and pitch alignment.
---

# Platanus Reviewer Skill

Use this skill with the `reviewer` agent.

## Procedure

1. Reproduce setup from the build log.
2. Run available tests and the main smoke path.
3. Test the demo as a judge and as a first-time user.
4. Check missing env vars, API failure behavior, loading states, and empty states.
5. Check secret handling, client/server key boundaries, auth/RLS, and file upload risks.
6. Check mobile responsiveness and obvious accessibility issues.
7. Apply only small low-risk fixes.
8. Write readiness, issues, fixes, and recommendation.

## Output

Create or update `artifacts/04_review_report.md`.

## Guardrails

- Do not destabilize a working demo.
- Prefer documenting risky fixes over making them late.
- No broad refactors without approval.
