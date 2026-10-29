# Current progress

Updated 30 October 2026. Phase 11 closed, Phase 12 prepared; p11 / `feat/p11-fullstack-integration` (owner 28 Oct: branched from
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
Then `19d762f` F4 host clarify (leaving vs transferring in; req-transfer-en passes) and `4221d26` excluded-program
scope notice (law-scope passes); both phrase lists owner-approved 28 Oct (ledger). Owner chose A for drop: split FAQ 7 (drop) from FAQ 8 (shift) as a new derived package (chunk-level
required_neighbor_chunk_ids + one shared claim force citing the shift continuation; package sealed). Earlier today: simple-question gate run 2 67/91
([results](../2026-10-28-simple-question-gate-results.md)); router v24, detail split, owner year-level limit.

Verification: full suite on `72f6ab6` 7215 pass / 1608 subtests, 6 skip / 2 xfail, exit 0 (1370.39 s;
A/p11-fullsuite-20261028d); a4f33f7 7212. e2cbc62 (at 3eb31ae): 4 sequential batches after a memory-pressure stop,
7216 pass / 1608 subtests, 6 skip / 2 xfail, all exit 0 (A/p11-fullsuite-20261028e, 286 files once each).
19d762f batched 7226 pass / 1608, exit 0 (…-20261028f); e4a676b (4221d26 + docs) batched 7233 pass / 1608,
exit 0 (…-20261028g).

Owner-approved FAQ 7/8 split built as inactive 560 package (A/p11-faq-split-20261028: 557 vectors reused,
3 encoded offline 40 s, 155 storage probes, drop claim = 1 record); drop en/Taglish and shifting en/Taglish pass.
Gate run 3 (0dfef59, split package): 73/91 (76 adjusted) vs run 2 67/91, but 8 run-2 passes regressed: router
v25 labelled eligibility parts specific/topic -> reverted `682fe7b`; `9553ed9` drops a stray topic on a course-
check part (test-first, related 1303 pass). Still failing after fixes: cc5-en (router omitted course mentions),
crim-1-1-taglish (selector ambiguous). Gate 4 (29 Oct, code 9553ed9): **77/91**, exit 0 (+6 fixed vs run 3,
honors en/Taglish regressed as expected after the v25 revert; [results](../2026-10-28-simple-question-gate-results.md)).
Batched full suite at 75ec50f: 7232 pass / 1608 subtests, 6 skip / 2 xfail, 4 batches exit 0 (A/p11-fullsuite-20261029a).

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

## Owner decisions 29 Oct (ledger)

Finish by 30 Oct. Phase 13 deployment cancelled. Replies English/Taglish only; pure-Tagalog input kept only while
free. Keep upload if doable. Phase 12: 50 common English/Taglish queries across enrollment procedures, prerequisite
eligibility, grade policies and academic standing, disciplinary policies. Honors/probation: option A (Handbook policy sections).

## Website on local 560 package (owner option A, 29 Oct)

`f235319` Handbook policy sections answer from the cited clause (honors/probation en+Taglish pass live).
`d1a2d53` local-documents pin: the website backend serves the gate-tested 560 package with the gate composition
(it had searched hosted 78 chunks without topic selection). Live HTTP: document, structured, hybrid, upload ->
confirm -> follow-up, deletion all work ([results](../2026-10-29-local-documents-website-results.md)).
Config: A/p11-local-documents-20261029/research-api-config.json (old 78 config unchanged). Hosted activation deferred.

## Phase 12 benchmark and final suite (29 Oct)

Benchmark (50 en/Taglish, four owner categories; 40 development cases disclosed): full system 40/50 at `7f8c02b`
(disciplinary 2/10 -> 7/10 via `38ccb83` printed row names and `7f8c02b` exact penalty quotes; no regressions);
plain Gemma 3/50 strict, 8/50 content ([results](../2026-10-29-phase12-benchmark-results.md),
[questions](../../docs/evaluation/benchmark-questions.md)). `37688aa` hides "(e2)" aliases in student text.
Batched full suite at `e50e18a`: 7247 pass / 1608 subtests, 6 skip / 2 xfail, 4 batches exit 0 (A/p11-fullsuite-20261029b).

## Phase 11 closed (29 Oct)

Browser check passed (Playwright guest run, 0 console errors); owner approved closing with disclosures:
[Phase 11 handoff](../phase-11-handoff.md). Next permitted phase: 12.

## After closing (29 Oct, owner)

`f770169`: student answers drop the "Candidate preview" line; the reply-language guidance sentence travels as
data-answer `notice` and shows small and muted under the answer (backend RED 6 -> API 151 pass; frontend RED 1 ->
66/66, typecheck 0). Browser-checked (smoking penalty, exact quotes). `npm ci` in p11/frontend (owner): 89 packages,
0 vulnerabilities, lockfile unchanged; the site now runs from this worktree.

## Late 29 Oct (owner decisions in ledger)

- `d5e638a` course title-initial abbreviations (963 approved, e.g. DSA = CC 4/L), any case, curriculum-scoped;
  `159d1f3`/`9820734` a mention fitting two courses lists each with printed code, title, year/semester, units.
- `cb82c53` reviewed Filipino shorthand expansion (`backend/bintanong_routing/shorthand.py`); probe 8/26 -> 15/26
  (normal spelling 20/26; list built after seeing the probe: disclosed). Docs: `docs/evaluation/accepted-input-forms.md`
  (forms, probe questions, research basis).
- Benchmark layout (owner): main 50 = 24 English / 16 Taglish / 10 pure Tagalog (`p12-benchmark-20261029/benchmark-cases-v2.json`);
  shorthand Taglish (26) and broken English (4, `loose/`) are separate robustness results.
- Runs at cb82c53 (A/p12-benchmark-20261029): shorthand2 done; condition-c4 (original 50), tagalog (26), loose (4)
  queued/running in this session and stop if the CLI closes. Restart with the commands in the exit/log files' scripts:
  `run_condition_c.py` (GATE_SUFFIX=-condition-c-cb82c53), `tagalog/run_tagalog.py`, `loose/run_loose.py`,
  each with GATE_PACKAGE=p11-faq-split-20261028/runtime-package; check for existing run-* folders first.
- No full suite yet on d5e638a..cb82c53 (related tests 1546 pass).

## Next action

Runs finished and recorded (`5fe66cc`): main 50 v2 = 38/50; regression check 39/50; Tagalog 19/26; shorthand 15/26;
broken English 2/4. absence-taglish diagnosed (30 Oct): identical selector request, one-off server non-determinism
(8/8 replays correct); recorded in the benchmark results. Phase 12 [plan](../phase-12-evaluation-writeup-plan.md)
prepared with [pre-phase research](../2026-10-30-phase-12-pre-phase-research.md) (`f2b00dc`); paired stats done
(C 40/50 Wilson [0.67,0.89] vs A 3/50, exact McNemar 37/0, p≈1.5e-11). Batched full suite running at `0d6ebac`
(A/p11-fullsuite-20261030a). Owner decided single runs (disclosed) and write-up before hosted 560 activation (ledger).
Report written (`36ae881`); Phase 12 started (`a6363c3`, checkpoint seq 1).

**Hosted 560 activation in progress (p12 worktree, branch `p12-evaluation-harness`).** Hosted read 30 Oct: active
corrected78; 5 versions partially_reviewed. The 257 re-authored records had no chunk-level validation; owner chose to
record the 29 Oct activation directive as it (ledger, no per-chunk human approval). Receipts built and passing the
Python validators (A/p12-hosted-560-activation-20261030: 4 cumulative supplementary receipts, 26 event envelopes,
selected review scope 17e11149…). Local-DB rehearsal running. Next: rehearsal result -> hosted stage -> activate ->
readback/smoke (rollback to corrected78 on any failure); then report section 8 and the Phase 12 handoff.
