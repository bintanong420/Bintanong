---
artifact: phase-checkpoint
phase: 11
status: in_progress
sequence: 20
plan: plans/phase-11-backend-api-plan.md
head_commit: fb4e1e8
working_tree: dirty
updated_at: 2026-10-25T01:31:00+08:00
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

Owner resumed25 Oct; frontend ready, integration deferred until pending work is finished.
Docker restored via installed CLI; actual-DB blank-codec failure reproduced and corrected under TDD.
[Session recovery note](2026-10-25-phase11-session-handoff.md) is the exact resume entry point.
g2 append-only path committed f591416 and full suite passed there. Subsequent root-release identity
and supplementary blank-field changes committed febd6c1/5440368; focused42 +26 subtests GREEN, review clean.
Full suite on5440368 passed6635 +1595 subtests.5dbc706 run stopped as obsolete at94%; new claim
filter fb4e1e8 passes79 focused +31 subtests and actual DB8 +22; final suite running (session51777).
All61 records compiled with8 limitations and exact token checks; Charter
atomic context exceeds2048; owner delegated4096 for pre_enrollment only. Exact compiled group3816 fits.
Source append and full release/39-links/activate/rollback/reactivation rehearsal passed.61 embeddings
computed;19 old embedding records retained byte-for-byte. Hosted g2 migration/staging delivered;
80-chunk/39-link draft inactive, original19-chunk release active. Live checks/switch remain.
[Resume evidence](2026-10-25-phase11-resume-verification.md) supersedes the failing stopping point.

## Repository State

Worktree p11, `feat/p11-backend-api`, based on dev `cbaa6a7`; nothing pushed. HEAD `fb4e1e8`.
Blank correction febd6c1, snapshot binding5440368, scoped context/menu bounds5dbc706 committed after
focused GREEN/review; claim filtering fb4e1e8 preserves ambiguity/negative/unknown guards. Only docs
remain dirty; fresh final suite uses fb4e1e8 production/tests.
No dependency changes/downloads; no frontend work.

## Verification Evidence

- g2: actual missing-RPC RED and missing-client RED; initial GREEN8 +20 subtests. Review bypass RED
  (direct privileged link INSERT accepted a receipt that omitted old fields); corrected trigger GREEN9 +20.
  Two-generation parent-chain and changed replay coverage included in final focused run.
  Migration `20261024114711_phase11_supplementary_source_reviews.sql` remains LOCAL ONLY.

- Full suite at f591416:6628 passed,6 skipped,2 xfailed,+1589 subtests,6 warnings,22m38s;
  full-suite-f591416.log/.exit=0. Does not cover subsequent dirty changes.
- Resume RED reproduced codec failure; corrected blank contract after4 expected focused failures.
  Final focused42 passed +26 subtests,94.10s (`resume-contract-green2.log`); independent review clean.
  Core full suite completed6635 +1595 subtests; latest tree still needs its fresh final result.
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

Final fb4e1e8 suite running (`claim-final-full-suite.log`). Claim filtering resolved10/60 same-topic
component refusals to60/60; review P2 edition/curriculum hiding fixed by RED/GREEN. Both review fixes
covered; no deferred findings. Hosted schema/staging read back; live quality/latency and switch remain.
Two grading router misses, Hybrid next-step
without topic, vague clarifications and Nursing negative claim mode remain. Photos unsupported;
6 register-only Taglish misses; no browser/UI exit, SDK parser contract test or installed linter.

## Next Action

Finish sealed package/pin controls while final suite runs. After successful final checks, run bounded
live candidate quality/latency, then coordinated hosted active-release/local-pin switch and roster
comparison. Current hosted draft stays inactive; preserve old package/release rollback.
UI ready; integrate after pending work. Auth/SDK installation retains applicable pin approvals; Phase12 unauthorized.

## Context Consulted

25 Oct Codex resume: thesis physical17-18,39-44 and routing PNG inspected; consistent scope/routing, no
new discrepancy. Existing master3/10 and owner ledger reviewed; source/scope/gap/service policies apply.
Earlier context/architecture evidence is preserved in the prior checkpoint snapshot.

## Do Not Repeat

Backend tasks1-9, prior security/abuse/capacity runs, source CF1-CF6, existing benchmark wording
acceptances, completed course-fact extraction, failed query expansion, source chunks for grading alone
(owner chose host reply), environment/model setup, prior photo/style experiments. Do not infer any
institutional release permission, source-gap resolution or phase advancement from candidate delivery.
