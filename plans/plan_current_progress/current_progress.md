# Current progress

Updated 28 October 2026. Phase 11 active; p11 / `feat/p11-fullstack-integration` (owner 28 Oct: branched from
`feat/p11-backend-api` f0889c3; frontend-integration and charter-layouts lanes pushed to origin; this branch local only).
[Plan](../phase-11-backend-api-plan.md) · [Checkpoint](../phase-11-checkpoint.md) ·
[Session handoff](../2026-10-28-phase11-session-handoff.md).
Last full snapshot before condensation: `7be3e1c` (earlier ba7d8b4, 40a35f9, f635ccc, d32aa18); use `git show`.

## Latest change

Topic families batch 1 (owner 28 Oct: F1-F4 and "separate" approved; F4 "b perhaps" provisional) and printed
openings, `a4f33f7` test-first (RED 9 fail -> GREEN 9 pass; related 558 pass). 88 unlabelled Handbook topics show a
verbatim 100-char opening (defects withhold it); one family member brings its siblings (<=8). Real selector prompt
3409 -> 5625 tokens. Live 12 affected cases (run-a4f33f7-families): 3 newly pass (refund en/Taglish, transfer fee).
Selector now right for drop (FAQ), probation (standing), honors; remaining are router claim/detail picks.
Gate case req-transfer-en now expects a clarification (F4). Then `72f6ab6` (whole request naming only not-stated
facts answers the printed procedure; diploma en/Taglish now pass) and `e2cbc62` router v25 (meeting a printed rule
-> specific; honors residence en/Taglish now pass; probation still `whole`, not retried under the stop rule).
Owner chose A for drop: split FAQ 7 (drop) from FAQ 8 (shift) as a new derived package (chunk-level
required_neighbor_chunk_ids + one shared claim force citing the shift continuation; package sealed). Earlier today: simple-question gate run 2 67/91
([results](../2026-10-28-simple-question-gate-results.md)); router v24, detail split, owner year-level limit.

Verification: full suite on `72f6ab6` 7215 pass / 1608 subtests, 6 skip / 2 xfail, exit 0 (1370.39 s;
A/p11-fullsuite-20261028d); a4f33f7 7212. e2cbc62 (at 3eb31ae): 4 sequential batches after a memory-pressure stop,
7216 pass / 1608 subtests, 6 skip / 2 xfail, all exit 0 (A/p11-fullsuite-20261028e, 286 files once each).

## Lane status (owner 28 Oct)

- [Workstream split](../2026-10-28-phase11-model-workstream-split.md): Codex lanes idle, all merged.
  A: Charter layouts 41/44 (e574d67). B: frontend, PSU auth, account-bound sessions (307a2bd, df3811a),
  guest mode (04e6d38; [results](../2026-10-28-guest-mode-results.md); [review](../2026-10-28-guest-mode-review.md)).
- Guest mode: full features incl. temporary PDF upload, login kept (master 25.1 amended). Real PSU sign-in
  verification owner-deferred; no authenticated HTTP smoke claim. P3s: delete the superseded guest session on
  mode switch; cross-tab early-auth race (not reproduced).
- No program given -> ask program and curriculum (216/1093 codes repeat; BSIT/BSCS share 20; BSCS has 2
  versions); the frontend ScopePanel asks up front. "CS6 (title)" mentions are covered by prompting guidance.

## Open gate failures (diagnosed 28 Oct, run-e193093 call artifacts)

1. Selector topic: fixed for drop/probation/honors/refund by a4f33f7; certification fee still -> charter_tor_copy
   (charter_certifications has no label: held). k-NN only searches the selected topic's chunks.
2. Router claim/detail: drop (en/Taglish), diploma, DAC, overdue pick a not-stated claim; probation and honors
   ask `whole` over multi-chunk topics -> repair_exhausted; grad residence answers max-residence clause.
3. F4 clarify (leaving vs transferring in) not built; Law scope notice; Taglish second-year empty clarify.
Families combine selection only; one part still answers from one subject (multi-source answers not built).

## Package state and boundaries

559 package inactive (559 vectors / 145 subjects / 240 reviews); active corrected78 / 39 curricula unchanged.
Original PDFs, the base package and the active pin are unchanged. No hosted writes, dependency or model changes,
institutional approval, Phase 11 exit or Phase 12 advance.

## Next action

Owner-approved order: F4 leaving/transferring-in clarify and Law scope notice (code, test-first), then the FAQ
split package (show the owner the exact split text first), then full 91-case gate rerun.
Mark `LIVE RUN` here while using the model.
