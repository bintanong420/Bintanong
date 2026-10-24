---
artifact: phase-checkpoint
phase: 11
status: in_progress
sequence: 13
plan: plans/phase-11-backend-api-plan.md
head_commit: 8ba6949
working_tree: dirty
updated_at: 2026-10-24T19:39:13+08:00
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

Finish item g roster19 comparison, then g2 supplementary-review path/source expansion.
[Topic filter execution](2026-10-24-topic-filtered-retrieval.md) has RED/GREEN, review and hosted evidence.
[Supplementary plan](2026-10-24-supplementary-source-review-plan.md) is prepared; no g2 production code yet.
Owner chose database path/new research release; do not ask again. Source batches 1-3 approved:
[actual readings and limits](2026-10-24-partial-topics-source-review.md). More rows/Charter still need review.
Machine date 24 Oct; inherited handoff/owner notes said 25 Oct. Retain historical dates as recorded.

## Repository State

Worktree p11, `feat/p11-backend-api`, based on dev `cbaa6a7`; nothing pushed. HEAD `8ba6949`.
Dirty documentation: topic execution report, owner ledger, this checkpoint, current progress,
new source-review report and supplementary plan. Preserve the pre-existing current-progress changes.
No dependency changes/downloads; no frontend work.

## Verification Evidence

- Last recorded full suite: `01d8db2` (prior agent, no failures). Earlier full at `874f0c9`:
  6478 passed, 6 skipped, 2 strict photo xfails; current full suite not yet rerun.
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
  is running (tool session 37068), results.jsonl and roster19-retry.log in that same evidence folder.
  Do not run another roster concurrently. Roster18 baseline: audit-evidence/p11-20261023/roster18.

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

Two simple grading router misses remain. Full suite/roster comparison pending. g2 remaining source
rows/Charter need actual owner replies. Hybrid next-step part without topic and vague clarifications
remain. Photos unsupported (strict xfails); 6 register-only Taglish style misses; no browser/UI exit,
SDK parser contract test or installed linter. Next/sharp/source-map-js advisories deferred to UI by owner.

## Next Action

Complete running roster19, compare all 63 cases against18, explain every status/decision/text change.
Then follow supplementary plan with RED on disposable DB before production changes. Remaining order:
g2 reviewed topic completion; g6/router follow-ups; Hybrid no-topic partial answer, bare clarifications,
Nursing negative claim mode; owner's multilingual simple-query battery; full suite and final review.
UI/auth/SDK install needs co-worker design and approval of exact dependency pins. Phase12 not authorized.

## Context Consulted

24 Oct Codex resume: thesis physical17-18 and routing PNG inspected; consistent scope/routing, no
new discrepancy. Existing master3/10 and owner ledger reviewed; source/scope/gap/service policies apply.
Earlier context/architecture evidence is preserved in the prior checkpoint snapshot.

## Do Not Repeat

Backend tasks1-9, prior security/abuse/capacity runs, source CF1-CF6, existing benchmark wording
acceptances, completed course-fact extraction, failed query expansion, source chunks for grading alone
(owner chose host reply), environment/model setup, prior photo/style experiments. Do not infer any
institutional release permission, source-gap resolution or phase advancement from candidate delivery.
