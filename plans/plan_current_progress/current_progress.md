# Current progress

Updated 28 October 2026. Phase 11 active; p11 / `feat/p11-fullstack-integration` (owner 28 Oct: branched from
`feat/p11-backend-api` f0889c3; frontend-integration and charter-layouts lanes pushed to origin; this branch local only).
[Plan](../phase-11-backend-api-plan.md) · [Checkpoint](../phase-11-checkpoint.md) ·
[Session handoff](../2026-10-28-phase11-session-handoff.md).
Last full snapshot before condensation: `7be3e1c` (earlier ba7d8b4, 40a35f9, f635ccc, d32aa18); use `git show`.

## Latest change

Simple-question gate ([results](../2026-10-28-simple-question-gate-results.md), 91 owner-accepted cases):
run 1 58/91 (61 adjusted), run 2 `e193093` 67/91 (70 adjusted). Fixes, all test-first:
- `289cf4b` router v24: not yet passed / not taken = failed claim (Taglish eligibility 7/7 fixed).
- `84ef585` detail answers split within claim limits, phase headings kept (TOR time, admission fee fixed).
- `a6bc52a` single-detail parts skip whole-procedure coverage (substitution deadline passes en/Taglish).
- `2189faf` owner-resolved source limits: year-level overlap shown as printed, no note (owner 28 Oct).
- `2112d62` `specific` detail and no clarify for missing personal details (second-year en passes).
Earlier today: answer only the asked detail (5ed4c98/6961e64), all-of wording guard d49aa27, shifting
option A 04e913f/12ac411 ([clarify results](../2026-10-28-clarify-and-condition-wording-results.md)).

Verification: full suite on `f0889c3` (includes a6bc52a/2189faf/2112d62) 7203 pass / 1608 subtests,
6 skip / 2 xfail, exit 0 (1376.65 s; A/p11-fullsuite-20261028b). Prior 04e6d38 run 7198 pass.

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

1. Selector topic: Handbook menu entries are ID-only (no printed heading), so drop -> handbook_dac_policy,
   refund -> handbook clause, transfer -> handbook_transfer_credentials, certification fee -> charter_tor_copy,
   Taglish probation -> discipline. k-NN only searches the selected topic's chunks.
2. Router claim: diploma/DAC/overdue pick a not-stated claim; two-topic picks choose the wrong one
   (honors residence, English probation, grad residence).
3. Law admission not routed to the undergraduate-scope notice. Taglish second-year: empty clarify (stop rule).
Proposed to owner: printed Handbook headings in the selector menu; optional owner-reviewed "topic families"
(overlapping topics selected and answered together; clarify only when the answer materially differs).

## Package state and boundaries

559 package inactive (559 vectors / 145 subjects / 240 reviews); active corrected78 / 39 curricula unchanged.
Original PDFs, the base package and the active pin are unchanged. No hosted writes, dependency or model changes,
institutional approval, Phase 11 exit or Phase 12 advance.

## Next action

Await owner answer on topic families; then fix 1 (selector headings) test-first, fixes 2-3, full gate rerun.
Mark `LIVE RUN` here while using the model.
