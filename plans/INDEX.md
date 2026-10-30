# Bintanong implementation ledger

## Current state

- Phase 12 research/software evaluation write-up complete with disclosures; no active implementation phase.
  [Plan](phase-12-evaluation-writeup-plan.md), [superseded checkpoint](phase-12-checkpoint.md),
  [latest final handoff](phase-12-handoff.md), [report](../docs/evaluation/phase12-evaluation-report.md).
- Hosted research560 active; corrected78 retained as rollback. [Activation results](2026-10-30-hosted-560-activation-results.md).
  This is not institutional approval or public deployment. Phase 13 deployment cancelled by owner.
- Post-Phase-12 accuracy work: [eight-failures handoff](2026-10-30-eight-failures-handoff.md) (open).
- Test-suite audit/consolidation complete, ready for external Claude review: [plan](2026-10-30-test-suite-audit-plan.md),
  [results and verification](2026-10-30-test-suite-audit-results.md).
- Worktree p12 / `p12-evaluation-harness`; [current progress](plan_current_progress/current_progress.md).
  Immutable master: [master plan](master_implementation_plan_original_long.md).
  Structural next_phase13 is cancelled; no next implementation phase authorized.

## Resume order

1. Run `python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .`.
2. Read current progress, Phase12 handoff and relevant master sections; compare with fresh Git evidence.
3. For recovery, use activation results and [Claude's executor handoff](2026-10-30-hosted-560-codex-handoff.md).
   Do not rerun staging/activation or regenerate bound review artifacts.
4. Consult relevant Context thesis pages/routing PNG on phase resume; preserve undergraduate/release boundaries.

## Phase ledger

Historical labels are retained. The [Phase 1–2 claims audit](2026-10-12-phase12-progress-claims-audit.md) records unmet
real-source exits; ledger validity alone does not prove source readiness.

| Phase | Name | Recorded status | Plan | Checkpoint | Handoff |
| ---: | --- | --- | --- | --- | --- |
| 0 | Docker and compatibility | complete | [Plan](phase-00-docker-compatibility-plan.md) | [Checkpoint](phase-00-checkpoint.md) | [Handoff](phase-00-handoff.md) |
| 1 | Source governance and contracts | complete; source gates qualified above | [Plan](phase-01-source-governance-contracts-plan.md) | [Superseded](phase-01-checkpoint.md) | [Handoff](phase-01-handoff.md) |
| 2 | Document ingestion | historical complete; audit applies | [Plan](phase-02-document-ingestion-plan.md) | none | [Handoff](phase-02-handoff.md) |
| 3 | Embedding generation | complete | [Plan](phase-03-embedding-generation-plan.md) | [Superseded](phase-03-checkpoint.md) | [Handoff](phase-03-handoff.md) |
| 4 | Vector and relational storage | complete after security remediation | [Plan](phase-04-supabase-storage-plan.md) | [Superseded](phase-04-checkpoint.md) | [Handoff](phase-04-handoff.md) |
| 5 | Retrieval | complete offline research/software; institutional release gated | [Plan](phase-05-retrieval-plan.md) | [Superseded](phase-05-checkpoint.md) | [Complete](phase-05-handoff.md) |
| 6 | Structured knowledge | complete offline BSCS research/software; institutional release gated | [Plan](phase-06-structured-knowledge-plan.md) | [Superseded](phase-06-checkpoint.md) | [Complete](phase-06-handoff.md) |
| 7 | Multilingual NLP and LLM routing | complete offline software/research;two style errors disclosed;institutional release held | [Plan](phase-07-multilingual-routing-plan.md) | [Superseded](phase-07-checkpoint.md) | [Complete](phase-07-handoff.md) |
| 8 | Orchestration | complete offline candidate software; institutional execution held | [Plan](phase-08-orchestration-plan.md) | [Superseded](phase-08-checkpoint.md) | [Complete](phase-08-handoff.md) |
| 9 | Generation/validation | complete offline research/software on hosted 39-curriculum release; eight limitations disclosed; institutional release held | [Plan](phase-09-generation-validation-plan.md) | [Superseded](phase-09-checkpoint.md) | [Complete](phase-09-handoff.md) |
| 10 | Private files and session context | complete offline research/software; photos unsupported; HTTP wiring in Phase 11; institutional release held | [Plan](phase-10-private-files-session-plan.md) | [Superseded](phase-10-checkpoint.md) | [Complete](phase-10-handoff.md) |
| 11 | Backend API, frontend integration, answer accuracy | complete with disclosures (photos unsupported, 24.2 rerun not done, hosted 560 activation deferred) | [Plan](phase-11-backend-api-plan.md) | [Superseded](phase-11-checkpoint.md) | [Complete](phase-11-handoff.md) |
| 12 | Evaluation write-up | complete with disclosed research gaps | [Plan](phase-12-evaluation-writeup-plan.md) | [Superseded](phase-12-checkpoint.md) | [Complete](phase-12-handoff.md) |

## Read only when relevant

- [Scope](undergraduate-scope-policy.md), [source gaps](source-gap-policy.md),
  [source locations](dataset-locations.md), [service associations](service-table-association-policy.md).
- [Owner decisions](owner-decisions-ledger.md), [English/Taglish replies](2026-10-27-english-taglish-response-decision.md),
  [curriculum/Symbolic architecture](2026-10-16-curriculum-symbolic-routing-clarification.md).
- [Benchmark results](2026-10-29-phase12-benchmark-results.md),
  [questions](../docs/evaluation/benchmark-questions.md), [evaluation protocol](../evaluation/README.md).
- [Developer pipelines](../docs/development/pipelines.md), [ingestion index](ingestion/README.md) only when needed.
- Historical expanded corpus/review/capacity findings remain in prior snapshots and dated reports;
  use final handoffs/current activation evidence for delivered state. Source gaps and answer failures remain.

## History and upkeep

Compact snapshots follow owner17Oct direction; exact decisions/history remain in dated records and Git.
Last full index before this condensation: `62ecb96`; full progress snapshot: `76d5a92`.
Earlier full checkpoints: Phase10 `13cf4b5`; Phase09 `e28eb5d`; Phase08 `9606319`; Phase07 `73cf70a`.
