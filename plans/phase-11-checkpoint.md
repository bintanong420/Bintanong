---
artifact: phase-checkpoint
phase: 11
status: paused
sequence: 16
plan: plans/phase-11-backend-api-plan.md
head_commit: f591416
working_tree: dirty
updated_at: 2026-10-25T00:25:00+08:00
---

# Phase 11 checkpoint — retrieval filter delivered; source expansion in review

Last full oversized snapshot: `f1eafe9:plans/phase-11-checkpoint.md` (recover with git show).
Active plan: [backend API](phase-11-backend-api-plan.md); previous final handoff:
[Phase 10](phase-10-handoff.md). Phase 11 remains active; no final handoff or advancement.

## Completed Tasks

- Backend tasks 1-9 delivered; security/queue/abuse fixes and step-2 E1/E3, 2a-2e/e2, f and h
  delivered. Full task/commit history preserved in f1eafe9 and dated reports, not repeated here.
- h: hosted structured course facts for all 39 curricula (2132 courses), source readings CF1-CF6
  settled in owner ledger. Do not re-extract/review settled facts or route them through RAG.
- g: p.46 full grading table host reply `8c49ad0` (owner chose it after immutable-source blockers).
- g topic filter `8ba6949`: optional JSONB chunk ids before ranking; policy-bound engine and
  PackageStorage parity; HostedReleaseStorage already forwards arguments. Hosted migration applied,
  normalized to file version `20261024112235`. No review/source/release rows changed.
- Supabase MCP now works after prior OAuth login/session restart; authenticated reads verified.

## Current Task

Owner requested a session handoff before `/clear`; implementation paused, no running test jobs.
[Session recovery note](2026-10-25-phase11-session-handoff.md) is the exact resume entry point.
g2 append-only path committed f591416 and full suite passed there. Subsequent root-release identity
and supplementary blank-field changes are uncommitted; latest focused run has one failure (below).
Sources are reviewed under batches1-12 plus standing approval for clear repeated cases; package is
still a draft, not compiled/rehearsed/hosted. Source register and active release remain unchanged.

## Repository State

Worktree p11, `feat/p11-backend-api`, based on dev `cbaa6a7`; nothing pushed. HEAD `f591416`.
Dirty code/tests: runtime research factory; partial/supplementary review loaders; g2 migration;
three focused test files. Documentation is saved in the session handoff commit; preserve dirty code.
No dependency changes/downloads; no frontend work.

## Verification Evidence

- g2: actual missing-RPC RED and missing-client RED; initial GREEN8 +20 subtests. Review bypass RED
  (direct privileged link INSERT accepted a receipt that omitted old fields); corrected trigger GREEN9 +20.
  Two-generation parent-chain and changed replay coverage included in final focused run.
  Migration `20261024114711_phase11_supplementary_source_reviews.sql` remains LOCAL ONLY.

- Full suite at f591416:6628 passed,6 skipped,2 xfailed,+1589 subtests,6 warnings,22m38s;
  full-suite-f591416.log/.exit=0. Does not cover subsequent dirty changes.
- Latest dirty-code regression: four expected RED failures in binding-blank-red.log; attempted GREEN
  gives1 failed,38 passed,+20 subtests in73.77s (binding-blank-green.log). Null blank accepted by
  supplement, rejected by selected-review codec which requires empty-string blank. No current GREEN.
- Topic baseline 48 passed +31 subtests; expected RED observed on real disposable DB/package/engine.
  Final retrieval/runtime selection 157 passed +86 subtests, 53.84 s, `review-green.log`.
  Four isolated mutations caught: engine/package/SQL filter removal and package validation removal.
- Independent review: no new security/compatibility defect; tab/newline validation mismatch reproduced
  and fixed; actual five-chunk SQL crowding/required-neighbor coverage added. No deferred findings.
- Hosted body MD5 `8e2c1fa7114220707e169d224829531f` matches local. One 9-argument STABLE invoker
  RPC, anon/authenticated execute, service_role denied. Active release unchanged, 19 chunks/39 links.
  Security: owner-accepted leaked-password WARN only. Performance: existing FK +19 unused-index INFOs.
- Live grading/fee battery 8/10 answered correctly within limits. Passing English/Filipino, 4.0,
  85, full grading, INC+completion partial and both fees work. Taglish passing selected no topic;
  uppercase percentage got no route. Duplicate evidence header not reproduced. These router misses
  remain separate from retrieval. Logs: workspace audit-evidence/p11-topic-filter-20261024/.
- Roster19 initial startup failed reading curriculum_ledgers: hosted SQL statement timeout. No cases
  ran. Activity check showed no lock pressure; bounded log query returned no matching event. Retry
  completed63/63 with0 exceptions.62 status/decision pairs unchanged; Architecture Filipino recovered an
  expected ineligible result from prior timeout. No previously answered status/decision lost. Eleven text
  changes explained by prior host/referral/currentness commits; language matches21/21 en,21/21 fil,
  15/21 Taglish unchanged. Roster18 baseline: audit-evidence/p11-20261023/roster18.

## Versions and Digests

Shared venv Python 3.13.7; FastAPI 0.141.1, SWI-Prolog 10.1.15, PostgreSQL 17.6, pgvector 0.8.2.
Installed Supabase CLI 2.117.0 (help consulted; no upgrade). Model/embedding identities unchanged;
MODELS_DIR=C:/Coding-projects/bintanong_workspace/MODELS. No weights copied/rehashed/downloaded.
Handbook SHA-256 and source decisions are in the source-review report. Models not altered/trained.

## Decisions

- Reuse approved requirements/plan. Topic filter narrows trusted model-selected topics; it does not
  replace semantic routing, waive threshold/scope/review binding or decide curricular eligibility.
- g2 approved database route: append-only supplementary receipts, NEW research release preserving
  old 19 chunks and 39 ledger links; rollback current release. No published source/receipt rewriting.
- Human review remains exact original regions/short inline batches. Weapon exception is malformed
  in original: approved retention with unresolved gap, never invented interpretation or rule.
- Carry standing prompt-engineering/no-training and one-week improvement boundaries. Source approvals
  are provisional undergraduate research evidence, not university approval or currentness.

## Known Failures or Blockers

One focused blank-field compatibility regression remains; current dirty changes need correction,
negative blank tests, relevant runtime/legacy regressions and fresh full-suite verification. Package
compiler/rehearsal/hosted g2 migration are not done. Two simple grading router misses, Hybrid next-step
without topic, vague clarifications and Nursing negative claim mode remain. Photos unsupported;
6 register-only Taglish misses; no browser/UI exit, SDK parser contract test or installed linter.

## Next Action

After owner resumes, read the [session handoff](2026-10-25-phase11-session-handoff.md), inspect the
preserved dirty diff and fix the null-vs-empty-string blank contract using existing codec semantics.
Run focused/legacy checks before committing behavior; then compile and locally rehearse the new
source package. Authority report must be frozen before its hash is used. No hosted g2 changes yet.
UI/auth/SDK install awaits design and exact-pin approval; Phase12 remains unauthorized.

## Context Consulted

24 Oct Codex resume: thesis physical17-18 and routing PNG inspected; consistent scope/routing, no
new discrepancy. Existing master3/10 and owner ledger reviewed; source/scope/gap/service policies apply.
Earlier context/architecture evidence is preserved in the prior checkpoint snapshot.

## Do Not Repeat

Backend tasks1-9, prior security/abuse/capacity runs, source CF1-CF6, existing benchmark wording
acceptances, completed course-fact extraction, failed query expansion, source chunks for grading alone
(owner chose host reply), environment/model setup, prior photo/style experiments. Do not infer any
institutional release permission, source-gap resolution or phase advancement from candidate delivery.
