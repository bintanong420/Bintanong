# Current progress

Updated 24 October 2026. Phase 10 complete (owner-approved with disclosures); no active phase.
Branch p10 / `feat/p10-private-files-pipeline` from `ccc3cea`, nothing pushed.
[Plan](../phase-10-private-files-session-plan.md) | [Checkpoint](../phase-10-checkpoint.md) |
[Pre-phase research](../2026-10-23-phase-10-pre-phase-research.md) | [Phase 09 handoff](../phase-09-handoff.md).
Last full snapshot before this replacement: `ccc3cea:plans/plan_current_progress/current_progress.md`.

## Approved frontend implementation - 23 October 2026

Owner approved the bounded [desktop preview plan/delivery](../2026-10-23-approved-frontend-delivery.md).
Live Figma approval/status/annotations rechecked; interactive synthetic home page,
metadata-only local attachments, no backend/API changes or formal phase advancement.
Interaction RED6failures/GREEN8tests; next: Tailwind/shadcn foundation, local assets
and health-route preservation. Existing untracked model directory is untouched.

## Frontend synchronization - 23 October 2026

Owner requested another history-preserving merge: dev cbaa6a7 into frontend9723fa7.
Retained dev's current phase status and the frontend design brief/index pointer;
resolved only this progress-file conflict. Application code matches dev. Prior
frontend history is preserved; no phase advancement or deployment is part of sync.
Verification: staged whitespace clean;10 documentation hygiene tests pass; phase ledger valid.
Application/build suites are not rerun for the documentation-only difference to dev.

## Latest changes (23 Oct, Claude Code session)

- Phase 10 started on the owner's go (new `p10` worktree). can-advance: yes.
- Owner decisions: D3 cookie credential with 30 min idle, memory only; D1 (OCR engine/Docling pin) and D2
  (Gemma vision) deferred to step 5; D4 add the locked pypdfium2 5.13.0 and Pillow 12.3.0 to the `api` extra.
  The research had missed that the `api` image lacks them. Uploads use a raw body, so python-multipart is not added.
- Worktree environment verified complete: the ignored `.env`, datasets, `supabase/.temp` and `.superpowers` match
  main. `.claude/settings.local.json` copied from p09.
- Multi-turn: the owner accepted F1-F7/F4b and asked for document follow-ups (D1-D4). Owner: most messages are
  not follow-ups, so stored context never binds an unrelated question. Prechecks found and fixed 5 issues.
- Task 5: the photo-OCR probe (onnxruntime CPU) found silent row misalignment on tilted photos, so photos
  stay unsupported. Exit: isolation tests, a bounded child parser job and the fact cap were added before closing.
- Lockfile churn from Orca's post-create `npm install` (npm 11.19 dropped 4 `"peer": true` metadata lines;
  no version change) was restored. The external Orca setup script now uses `npm ci`.

## Next action

Phase 10 is closed ([final handoff](../phase-10-handoff.md); final suite 6295 passed, 6 skipped, 0 failed).
Open owner questions (asked 24 Oct, not yet answered; ask again before starting):
- The owner wants all backend finished while the frontend design is pending. Proposed: start Phase 11
  backend-first (pre-phase research, then `POST /chat` with the cookie session and conversation capture,
  `POST /uploads` plus the confirm step, `DELETE /uploads/{id}`, `DELETE /session`, `GET /sources/{id}`, and the
  AI SDK 6 streaming adapter, all with API tests). Frontend tasks wait for the co-worker's design.
- Photo OCR has no owning phase (it is not in master 16). Proposed: a backend task for deskewed row grouping,
  refusal when uncertain, and a grade-row Q11-style scorer on simulated photos. A "supported" claim needs real
  phone photos (owner to provide, kept private).
- The conversational function is built and live-tested in the backend but not yet reachable over HTTP.

## Boundaries

Undergraduate scope, read-only advisory, source-gap, privacy, institutional release and one-week improvement
boundaries are unchanged. No grade or conversation persistence. No activation, push, training or DB change.
Dependency change limited to D4. Context consulted 23 Oct: thesis physical 17-19 and 65-66, plus the routing
PNG. No discrepancy.
