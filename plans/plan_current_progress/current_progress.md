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
Gate case req-transfer-en now expects a clarification (F4). Earlier today: simple-question gate run 2 67/91
([results](../2026-10-28-simple-question-gate-results.md)); router v24, detail split, owner year-level limit.

Verification: full suite on `a4f33f7` 7212 pass / 1608 subtests, 6 skip / 2 xfail, exit 0 (1378.87 s;
A/p11-fullsuite-20261028c). Prior f0889c3 7203 pass.

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

Fix 2 test-first (router: printed fields over not-stated for how-to; `specific` over `whole` for one rule), then
F4 clarify and Law scope, then full gate rerun.
Mark `LIVE RUN` here while using the model.
