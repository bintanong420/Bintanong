# Current progress

Updated 24 October 2026. Phase 10 complete (owner-approved with disclosures); no active phase.
Branch p10 / `feat/p10-private-files-pipeline` from `ccc3cea`, nothing pushed.
[Plan](../phase-10-private-files-session-plan.md) | [Checkpoint](../phase-10-checkpoint.md) |
[Pre-phase research](../2026-10-23-phase-10-pre-phase-research.md) | [Phase 09 handoff](../phase-09-handoff.md).
Last full snapshot before this replacement: `ccc3cea:plans/plan_current_progress/current_progress.md`.

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

Phase 10 is closed ([final handoff](../phase-10-handoff.md); final suite 6295 passed, 6 skipped, 0 failed). Next: Phase 11 pre-phase research (master 16 + 23.3).
Then the owner summary and go. Then wire `POST /chat`, the cookie, uploads and `DELETE /session` onto the Phase 10
backend.

## Boundaries

Undergraduate scope, read-only advisory, source-gap, privacy, institutional release and one-week improvement
boundaries are unchanged. No grade or conversation persistence. No activation, push, training or DB change.
Dependency change limited to D4. Context consulted 23 Oct: thesis physical 17-19 and 65-66, plus the routing
PNG. No discrepancy.
