# Current progress

Updated 29 October 2026 (machine local date; inherited release/report names retain 30 October).
Phase 12 research/software evaluation write-up complete with disclosures; no active implementation phase.
p12 / `p12-evaluation-harness`. Deployment (Phase 13) cancelled by owner.
[Final handoff](../phase-12-handoff.md) · [Report](../../docs/evaluation/phase12-evaluation-report.md) ·
[Activation results](../2026-10-30-hosted-560-activation-results.md).
Last full snapshot before condensation: `76d5a92`; use `git show` for prior history.

## Latest change

Hosted research release `p12-research-faqsplit-20261030` is active: 560 chunks/vectors, 39 curriculum links.
Corrected78 superseded and retained as rollback. Staging106.11s/activation121.08s, exits0; exact readbacks,
retrieval target hit and existing-row preservation passed. Bound local artifacts and source states unchanged.
Commits: `acbb0b9` preflight, `0b4aef9` staging, `62ecb96` activation; closure docs follow.

Hosted HTTP smoke: document, prerequisite and Hybrid all answered with citations (51.0/26.7/49.5s,
outer API single observations, excluding startup/browser). Guest browser smoking penalty/source panel passed,
Handbook p.93, 0 console errors/warnings. Backend constructed110.88s, live/ready200.

Backend :8021 uses ignored `p12-hosted-560-activation-20261030/hosted-research-api-config.json`;
frontend :3216 runs from p12; model :18088 is the existing container. Old corrected78/local-documents config
cannot be used after the switch. Restart/rollback commands and exact hashes are in activation results.
.env stays ignored/untracked; no secrets or raw evidence staged. No dependency/model changes.

## Evaluation and limits

Fresh saved-output audit matches report: main v2 38/50 (76%); original C40/50, rerun39/50, A strict3/50,
content8/50; robustness Tagalog19/26, shorthand15/26, broken English2/4. No new benchmark runs.
Historical full merged suite7314pass/1608subtests,6skip/2xfail; related hosted-pin108pass inherited.
Full suite on final code `35629a1`: 7322 pass/1608 subtests, 6 skip/2 xfail, 4 batches exit 0 (30 Oct).
Development reuse, single author/single runs, remaining failures, unmeasured metrics/SUS/UAT, unsupported photos,
deferred PSU sign-in and no institutional validation remain disclosed. Benchmark used local documents;
hosted smoke is not benchmark parity. Undergraduate/source-gap/privacy/unknown-versus-unmet guards remain.

## Hosted query validation (30 Oct)

[Results](../2026-10-30-hosted-query-validation-results.md): prerequisites 44/44 across all 39 curricula; common
document questions 6/10. TOR evidence-ID leak fixed `3206ae1` (multi-line claims; re-asked live). Open: honors
requirements (failed twice), probation (inconsistent), INC removal (selector misses `grade_completion`); fixes would
change selector/prompt behaviour after the frozen report and need an owner decision. Disk: C: filled (local
Supabase analytics 14 GB); cleaned, analytics disabled `01823b9`, Docker disk compacted 47 -> 28.4 GB.

## Document fixes (30 Oct, owner-approved)

`bfdade9` printed section headings in the selector menu (28 Handbook topics); `a0eb42f` a truncated draft retries
once at 1,536 tokens (both test-first; broad 1602 pass). Diagnosis (A/p12-doc-diagnosis-20261030): honors draft now
completes but is refused as `source_gap` (p.54 residence conflict refuses the whole part); INC still selects grade
correction because "3.4 REMOVAL OF INC" is withheld by the defect rule (p.47 deadline conflict); probation misses
are model variation (identical draft request, different reply). Regression on main 50 stopped by Claude Code at
37/50 for low memory: on 29 overlapping cases 23 -> 24 pass (fixed summer-load Taglish, grad-residence en; shift-en
fails only on keyword wording, same clause). Remaining 21 cases not run. Hosted backend still runs pre-fix code.

## Defect-rule change (30 Oct, owner-approved)

Owner: "we should still show ... note the limitation and ask them to refer to the appropriate university office".
`abbaf58` printed headings stay in the topic menu despite a defect elsewhere in the chunk (trailing possibly-cut
heading and openings withheld). `9f1b9ac` a claim citing an unresolved malformed_source_condition record becomes an
exact quotation + recorded limitation + office referral (never interpreted; fidelity-checked; oversized -> source_gap).
Test-first; generation/routing/runtime/orchestration/API 1656 pass. Full suite not yet run on `9f1b9ac`.
Pre-change regression (`a0eb42f`): 40/50; on 40 cases shared with the 38/50 run 28 -> 31. New code (`9f1b9ac`,
42 + 8 batches after a low-memory stop): 41/50; shared 40: 28 -> 32. Diagnosis on new code: probation answered
(quotes the p.41 held record with limitation); honors no longer source_gap but both drafts rejected by the existing
introduced_disjunction guard ("..., or Cum Laude"), abstained; INC selector now picks grade_completion but the router
requests the timing claim (menu source_context shows only timing text), so 3.4/3.5 removal text is never retrieved;
those records carry ungrouped conflicting_deadlines, which deadline_conflict_reply still turns into source_gap.
Full suite on `9f1b9ac`: batches 7172 pass/6 skip/2 xfail; 17 DB files failed only because the local Supabase DB
was stopped, rerun with DB up 182 pass/842 subtests. Hosted backend :8021 (81.8 s) and frontend :3216 (next dev)
restarted on new code; live probation 200 answered 52.2 s (outer API, single observation).
Both were then stopped by Claude Code's low-memory reaper; the owner now runs them in their own terminals
(same commands), outside the reaper. Rechecked: frontend health ready, live probation 200 answered 46.0 s.

## INC/honors follow-up (30 Oct, owner-approved)

`1f2f9db` ungrouped conflicting_deadlines records are quoted with their limitation (incomplete groups stay
source_gap); `880c733` router menu lists each fact's printed headings (`fact_headings`). Honors: owner chose to keep
the introduced_disjunction guard (disclosed limitation). Related tests 1661 pass. Regression on `880c733`: 42/50
(prev 41; drop-subject-tagalog regained, no losses); shared 40: 28 -> 32. INC still fails: the router received
fact_headings (fact 1 = "3.4 REMOVAL OF INC") but Gemma still chose the timing fact; stopped after this bounded
attempt. Honors abstains (guard), probation passes. Two runs hit intermittent DNS failures to hosted Supabase and
were rerun (`*-headings-b2`, `*-headings` diag dirs have no cases). Hosted servers stopped by owner for the run.

## INC second attempt (30 Oct)

`5904e09` router guard: a fact whose printed heading names >=2 of the part's words replaces a choice whose headings
name none (adding both exceeded grade_completion's 3,072-token budget: timing 1,520 + 3.4 group 1,959); offline only
INC changes across 53 recorded outputs. `1cbc68b` conflicting records outside a real conflict group (singleton or
mixed package groups) are quoted alone. Live INC now retrieves 3.1-3.7, drafts a correct answer, passes host checks
and all six support verdicts, but the Gemma reviewer returns does_not_answer (likely the reviewer rule on a cited
claim_not_stated limit, 3.1 "colleges ... not named"). A reviewer instruction (`3430b67`) did not change it and was
reverted (`6b7d2a7`). Regression (owner-run in their own PowerShell after Claude Code's memory reaper stopped
two attempts; `run-ddf2338-owner-b1..3`, backend = 6b7d2a7): 42/50, identical cases to `880c733`, no exceptions.

Reviewer replays (recorded INC call-5): removing the claim_not_stated limit kept does_not_answer; removing the
leading limitation notice, or moving it after the quote, gave answers. `91fa3c0` quotes now lead with the printed
text ("The printed source states (quoted exactly): ... Source note: ...; please confirm ... office"). Live INC:
answered/validated, 49.6 s, Handbook p.46-47 3.1-3.7 cited. Open cosmetic: two model claims end "(e5)" (short
reference label leak; pre-existing class). Honors remains a disclosed limitation (guard kept, owner).

## Eight failures (30 Oct)

Plagiarism EN/Taglish root cause: `prefer_printed_procedure` replaced a not-stated-only choice with all 39 printed
academic_misconduct claims (> 8 part bound) -> ValidationError -> invalid_reference clarify. `8e75428` narrows a
large topic to printed claims naming the part's words (II.7b); test-first, related 2286 pass (4 local-DB storage
tests not run: container stopped). `6efe5cf` after a settled single-topic selection, an empty router clarify answers
that topic's printed claims (second-year Taglish x3, cheating/shift short replay to RAG). `1dc5adb` an operation
target naming a reviewed course alias (CC5 short form) keeps the Symbolic check (only cc5-en changes in recorded
outputs). `648c4b5` fixes a 6efe5cf flaw ("ano" named "another", adding II.7g). Related suites 2281 pass.
Not host-fixable safely: uniform Taglish (model picked II.13; a one-word label rule would wrongly move smoking
Taglish to II.24 "campus"), grad-residence Taglish (selector/model chose handbook_residence over graduation),
summer-load EN (same evidence as passing Taglish; EN draft dropped the 12-unit Dean exception: replay needed).
Owner `-owner2` run (b1 31064fb, b2 1dc5adb, b3 648c4b5): 44/50 (prev 42); fixed plagiarism x2, second-year Taglish;
lost disc-smoking-en ("campus" also kept II.24 littering -> abstained). `070438f` ignores generic institutional
words (campus/university/premises/school/student) when matching; 310 recorded outputs: only smoking-en and
smoking-taglish-short change. `a29f23d` owner decision (a): Taglish claims keep printed source wording in English,
Filipino connectors only (ledger 30 Oct). Live on a29f23d (`run-a29f23d-live3`): cc5-failed-cc4-en (ineligible,
CC 4/L), disc-smoking-en, leave-length-taglish ("one (1) academic year") all PASS. Related suites 2283 pass.
Remaining: uniform Taglish, grad-residence Taglish (model choice), summer-load EN (drafting omission).

## Hosted-parity regression (30 Oct, owner-approved plan)

The 50-case runner read documents from the local 559-chunk package (curricula hosted). New ignored runner
`audit-evidence/p12-hosted-regression-20261030/run_hosted_regression.py` composes exactly as `load_research_app`
(hosted pin/seal, 560 chunks, `ResearchProvider` hosted pin check per case); old runner unchanged for comparison.
Full owner run `-hosted2` on 63b9653: **47/50 on hosted** (no exceptions; `-hosted1` void: Docker Desktop stopped).
Gained vs local `-owner2` 44/50: cc5-en, smoking-en, leave-length-taglish; nothing lost. Remaining: summer-load-en
(missing Dean), grad-residence-taglish, disc-uniform-taglish. [Results](../2026-10-30-hosted-regression-results.md).

## Test-suite audit (30 Oct)

Read-only audit of the inherited tests (Hawksprey420: 105 files, 4,646 of 7,365): no dataset/.env/absolute-path
dependency; contracts family fragmented across fix-pass files; redundancy unmeasured (no coverage tool installed).
[Plan](../2026-10-30-test-suite-audit-plan.md) execution started by Codex at `3ad52e5`:
7,365 collected; local Supabase DB started/healthy; all four full-suite baseline batches exit 0:
7,357 passed / 6 skipped / 2 xfailed / 1,608 subtests (no test changes yet).
Owner approved coverage + pytest-cov in evaluation venv only after baseline; no dependency/lockfile edits.
[Execution checkpoint](../2026-10-30-test-suite-audit-results.md). No tests changed or removed yet.

## Next action

Install approved coverage tools and measure task 2 (105 inherited files / 4,646 tests reconciled).
Earlier accuracy follow-ups remain deferred; tool retirement requires the owner's task 6 decision.
Phase 13 remains cancelled. Preserve evaluations, bound artifacts, corrected78.
