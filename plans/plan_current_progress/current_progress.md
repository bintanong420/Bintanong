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

## Next action

Owner decision: INC (router claim choice + ungrouped deadline-conflict quoting) and honors (disjunction guard vs
printed honors list). Phase 13 remains cancelled. Preserve existing evaluations, bound artifacts and corrected78 rollback.
