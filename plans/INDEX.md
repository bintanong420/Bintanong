# Bintanong implementation ledger

## Current state

- Phase 05 **complete as an owner-approved offline research/software milestone**.
- Phase 06 **complete as an owner-approved offline BSCS research/software milestone**.
- Phase **08 complete: offline candidate orchestration** in p08/feat/p08-orchestration.
  [Plan](phase-08-orchestration-plan.md) · [Superseded checkpoint](phase-08-checkpoint.md) ·
  [Final handoff](phase-08-handoff.md).
  [Developer pipelines](../docs/development/pipelines.md): actual flows/files and boundaries.
- Phase **07 complete as a verified offline software/research milestone**.
  [Completed plan](phase-07-multilingual-routing-plan.md) ·
  [Superseded checkpoint](phase-07-checkpoint.md) · [Final handoff](phase-07-handoff.md) ·
  [Exit mapping/review](2026-10-19-phase07-offline-closeout.md).15/15fresh dev routes/
  effective outcomes,13/15exact reused styles;two Taglish style errors remain.
  [Standing prompt/validation decision](2026-10-19-prompt-engineering-and-validation-decision.md):
  accepted for future phases;one-week improvement cap;no institutional accuracy claim.
- Phase **09 complete (second closeout, 23 Oct, owner direction)** after the hosted Supabase reopening
  ([plan](2026-10-22-hosted-supabase-integration-plan.md)); [Plan](phase-09-generation-validation-plan.md) ·
  [Superseded checkpoint](phase-09-checkpoint.md) · [Final handoff](phase-09-handoff.md). Run 14 PASS.
- Phase **10 complete (23 Oct, owner-approved with disclosures)**: private files and session context.
  [Plan](phase-10-private-files-session-plan.md) · [Superseded checkpoint](phase-10-checkpoint.md) ·
  [Final handoff](phase-10-handoff.md) · [Multi-turn results](2026-10-23-multi-turn-observation-results.md) ·
  [Photo-OCR probe](2026-10-23-photo-ocr-probe-results.md) (photos unsupported).
- Phase **11 active (backend done; security check done 24 Oct ([review](2026-10-24-phase-11-security-review.md)); roster19 compared; corrected78 research release active)** in p11 / `feat/p11-backend-api`: HTTP API, AI SDK v7 stream
  adapter, 24.1 photo rows, 24.2 Taglish style. [Plan](phase-11-backend-api-plan.md) ·
  [Checkpoint](phase-11-checkpoint.md) · [Latest review:BatchBcomplete](2026-10-27-phase11-batch-b-review-results.md) · [Pre-phase research](2026-10-23-phase-11-pre-phase-research.md).
  [Current336candidate overlay](2026-10-26-registration-layout-correction-results.md):BatchA/Bcontent complete;BatchC21of78approved,116approved/220pending;approved Charter services need labelled rebuild,inactive.
  [Hosted80-chunk audit](2026-10-25-hosted-chunk-review.md) complete:72approved/8correction-needed;draft inactive.
  [Corrections](2026-10-26-hosted-chunk-correction-results.md):78chunks/39curricula now research-active;old19retained/old80draft.
  [Runtime check](2026-10-26-corrected-candidate-runtime-results.md):full suite passes;six-query quality gate fails;inactive.
  [Answer fixes/results](2026-10-26-source-field-selection-results.md):6865+1595subtests passed;3/6checked expectations met;inactive.
  [Companion fixes/current results](2026-10-26-companion-context-activation-results.md):6/6selected expectations;6896tests/1595subtests passed;78activation and hosted checks pass. Recovery saved26Oct14:33.
  [Natural grading/coverage triage](2026-10-26-natural-grading-and-source-coverage-results.md):0/2natural answers;omitted student material mapped;new fields unreviewed.
  [Handbook/Charter baseline](2026-10-26-handbook-charter-shared-baseline.md):89groups/8batches bounded review/holds;fork4e99fb6,[two-developer workflow](2026-10-26-phase11-two-developer-workflow.md),isolated ingestion workspace ready;frontend active elsewhere.
  Program prerequisite reviews: [BS Architecture 01](2026-10-22-bsa-prerequisite-review-01.md).[Audit](2026-10-20-runtime-architecture-implementation-audit.md);[master plan](master_implementation_plan_original_long.md) sections 1-22 unchanged except the section 2 "Current pins" table and 16.3 SDK wording (owner, 23 Oct); owner-requested addenda: section 23 (conversational follow-ups, 23 Oct), section 24 (Phase 10 carry-overs: photo OCR, Taglish follow-up style, 24 Oct).
- [Completed plan](phase-05-retrieval-plan.md) · [Superseded checkpoint](phase-05-checkpoint.md) ·
  [Final handoff](phase-05-handoff.md) · [Current progress](plan_current_progress/current_progress.md).
- [Task-first:4/4interpretation,3/4full quality](2026-10-21-task-first-observation-results.md);[checker trial stopped on truncation](2026-10-25-checker-comparison-results.md);[test audit](2026-10-20-test-meaning-audit-results.md).
- [Latency profile 23 Oct](2026-10-23-latency-profile-hosted-39.md) (prompt reuse now default);[conversational follow-up requirement](2026-10-23-conversation-context-requirement.md) (not built).
- [Failed actual-model observation](2026-10-20-question-parts-observation-results.md);[timing contract](2026-10-20-response-time-measurement-contract.md).
- [Per-part generation](2026-10-21-per-part-generation-decision.md) is the default;[actual results](2026-10-21-per-part-observation-results.md):fee fixed;per-language style 4/4 (author reading).
- Scoped/canonical/separate selected;three current correct component answers45.8-49.8s;student end-to-end latency unmeasured.
- Phase06 runtime `49bc993`, checkout fix `a9d8a5d`; Phase05 product `ee7567a`, closure `9a0eea7`.
- Seven reviewed relationships verified;university/institutional runtime/activation holds remain;full-prospectus conversion stays draft.

## Resume order

1. Run `python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .`.
2. Read current progress, the Phase 11 plan/checkpoint, Phase 10 handoff; master 16, 23, 24;
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
Latest full snapshots:Phase10 checkpoint:`13cf4b5`;Phase09:`e28eb5d`;Phase08:`9606319`;Phase07:`73cf70a`;use `git show <commit>:<path>`.
