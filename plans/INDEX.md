# Bintanong implementation ledger

## Current state

- Phase11active in p11 / feat/p11-backend-api. Backend/security delivered;frontend
  integration stopped. [Plan](phase-11-backend-api-plan.md) · [Checkpoint](phase-11-checkpoint.md) ·
  [Current progress](plan_current_progress/current_progress.md). No Phase11handoff;
  latest final handoff is [Phase10](phase-10-handoff.md);Phase12not permitted.
- [Reply migration](2026-10-27-english-taglish-migration-results.md),28edea4:
  English/Filipino/Taglish inputs;English/Taglish replies. Saved8/8targets match,
  style prompt95tokens smaller;latency gain unproven. Full6974tests/1595subtests pass.
  [Owner decision](2026-10-27-english-taglish-response-decision.md),master26.
- [Source-bound context](2026-10-27-source-bound-routing-context-results.md),36d5f56:
  [Document follow-ups](2026-10-27-document-follow-up-context-results.md),4ba0f41:full6986/1595subtests pass.
- [TOR answer check](2026-10-27-tor-follow-up-answer-validation-results.md):default
  budget withholds;local complete-context answers abstain on whole-procedure coverage.
- Corrected78research release/39curricula active;expanded465draft inactive and
  predates local corrections. [465bindings/capacity](2026-10-27-expanded-topic-binding-results.md),
  [normalized data](2026-10-27-expanded-context-validation-results.md),
  [hosted draft](2026-10-27-hosted-corpus-staging-results.md).
- [All-nine inclusion](2026-10-27-nine-item-inclusion-results.md)/prior source decisions
  stand;service/image bindings,budgets,release and full answer-quality gates remain.
  No institutional approval,public deployment or executable-rule expansion inferred.
- [Developer pipelines](../docs/development/pipelines.md),[master](master_implementation_plan_original_long.md),
  [two-developer boundary](2026-10-26-phase11-two-developer-workflow.md). Prior phase
  milestones/limitations are in the ledger and linked final handoffs below.

## Resume order

1. Run `python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .`.
2. Read current progress, the Phase 11 plan/checkpoint, Phase 10 handoff; master 16, 23, 24, 26;
   earlier phase files only for a specific dependency/boundary.
3. Compare Git status/log with recorded commits; preserve unrelated owner changes.
4. On phase resume, consult relevant Context thesis pages and the routing PNG.
5. Resume the Phase 11 checkpoint's next action; preserve all inherited release holds.

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
| 11 | Backend API (frontend ready; integration deferred) | in progress; finish pending work first | [Plan](phase-11-backend-api-plan.md) | [Checkpoint](phase-11-checkpoint.md) | none |

## Read only when relevant

- Sources: [locations](dataset-locations.md), [undergraduate scope](undergraduate-scope-policy.md),
  [source gaps](source-gap-policy.md), [service tables](service-table-association-policy.md).
- Architecture: [curriculum/Symbolic direction](2026-10-16-curriculum-symbolic-routing-clarification.md).
- Retrieval: [selected profile](2026-10-16-document-development-profile.md),
  [bounded acceptance](2026-10-16-document-development-acceptance-contract.md),
  [remaining exits](2026-10-16-phase05-remaining-exit-packet.md).
- Phase06: [foundation/readiness](2026-10-17-phase06-foundation.md),
  [Generated review delivery](2026-10-17-phase06-prolog-review-delivery.md),
  [Partial export design](2026-10-17-phase06-partial-review-export-design.md),
  [Reference extension](2026-10-17-phase06-reference-extension.md),
  [translation review03](2026-10-17-phase06-translation-review-03.md),
  [authoring/compiler](../backend/bintanong_symbolic/README.md).
- Ingestion: [supporting index](ingestion/README.md), only for ingestion work.
- Benchmarks: [evaluation protocol](../evaluation/README.md).
- Database integration: [hosted migration gap](2026-10-19-hosted-migration-status.md).
- Settled owner decisions: `AGENTS.md`; consult its linked records for exact evidence.

## History and upkeep
Owner requested compact handoffs on 17 October 2026. These are current snapshots,
not activity logs. Replace stale state;keep durable evidence in dated reports;do not restore bulk history on resume.
Before current index condensation:28edea4. Latest full snapshots:Phase10 checkpoint:`13cf4b5`;Phase09:`e28eb5d`;Phase08:`9606319`;Phase07:`73cf70a`;use `git show <commit>:<path>`.
