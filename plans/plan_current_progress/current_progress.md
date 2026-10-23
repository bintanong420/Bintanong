# Current progress

Updated 24 October 2026. Phase 11 active (backend only, owner direction); resumed after the 24 Oct pause.
Worktree p11 / branch `feat/p11-backend-api` from `dev` `cbaa6a7`, nothing pushed.
[Plan](../phase-11-backend-api-plan.md) | [Checkpoint](../phase-11-checkpoint.md) |
[Pre-phase research](../2026-10-23-phase-11-pre-phase-research.md) | [Phase 10 handoff](../phase-10-handoff.md).
Last full snapshot before this replacement: `0e4e4f1:plans/plan_current_progress/current_progress.md`.

## Latest changes (24 Oct, Claude Code session)

- Security check of the HTTP API and private-context packages: [review](../2026-10-24-phase-11-security-review.md).
  Seven findings. Owner decisions: S1 evict the least recently used *empty* session (sessions with facts, pending
  rows, conversation context or a running turn are never evicted); S3 Next.js critical/high `npm audit` findings
  are upgraded with the `ai` v7 install at UI integration; S4-S7 applied now.
- Fixes, each RED -> GREEN and mutation-checked: S2 `e87ed7b` (409 `session_ended`), S1 `15934a7`, S4 `8b67b8d`
  (422 `invalid_message`), S5 `b0dc62b` (all PDF/image parsing inside the child job), S6 `93e795e` (503
  `uploads_busy`), S7 `72ec6d4` (readiness errors without exception text). Developer API doc updated.
- Full suite at `72ec6d4`: 6441 passed, 6 skipped, 2 xfailed, 1552 subtests, 0 failed (20m00s).
- No secrets in tracked files (only the public Supabase demo keys). Root `npm audit`: 0.

## Next action

Step 2 of the owner's pre-UI checks: more retrieval and Prolog evaluation, starting from the two live-smoke
observations and roster run 16's clarification/non-answer statuses. See the [checkpoint](../phase-11-checkpoint.md).

## Boundaries

Undergraduate scope, read-only advisory, source-gap, privacy, institutional release and one-week improvement
boundaries are unchanged. No grade or conversation persistence. No activation, push, training or DB change.
No dependency change without an owner decision. Context consulted 23 Oct: thesis physical 17-18 and 65-66, plus
the routing PNG. No discrepancy.
