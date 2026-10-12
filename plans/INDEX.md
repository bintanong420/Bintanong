# Bintanong Implementation Ledger

This file is the authoritative pointer for resuming work. Do not select a phase by file modification time.

## Current State

- Master plan: `plans/master_implementation_plan_original_long.md`
- Active phase: `5` (blocked on extraction/field/source review and approved runtime retrieval; verified candidate execution delivered)
- Active plan: `phase-05-retrieval-plan.md`
- Active checkpoint: `phase-05-checkpoint.md`; Phase 04 checkpoint superseded
- Latest handoff: `plans/phase-05-handoff.md` (blocked recovery handoff; does not authorize advancement)
- Previous complete final handoff: `plans/phase-04-handoff.md` (corrective closure preserved)
- Next permitted phase: `5` (active); Phase 06 requires a complete Phase 05 final handoff
- Corrective review: [Phase 04 security verification](phase-04-security-review-2026-10-12.md)
- Phase05 latest candidate delivery: [27-question balanced college practice exam](phase-05-practice-exam-report.md), code `317bf54`; nine colleges, three cases each; original12-case version preserved. Source/answer approval and real retrieval scoring pending.
- Real retrieval status: [actual original-corpus/model execution](phase-05-real-retrieval-readiness.md);39 verified bundles,33audit errors/6warnings/336chunks,336real document vectors/27query diagnostics. Actual spans near27/28regions,3chunk-linked regions.4906tests/107subtests pass; independent final review clear. Only3exam cases have emitted chunks; source/field review and approved runtime scoring remain open.
- Source location and planned relocation: [dataset location guide](dataset-locations.md); owner-approved expansion is 27 dev questions, three per each of nine college folders.

## Parallel prospectus workstream

- Approved review-only prospectus workstream plan: `plans/2026-09-26-prospectus-phase2-implementation-draft.md`
- Current ingestion plans and delivery: [repository documentation index](ingestion/README.md) and [current status](ingestion/CURRENT_STATUS.md)
- Candidate ingestion pipelines and rule preparations delivered in dev branch. Ingestion outputs remain candidate text and review bundles.

## Phase Ledger

| Phase | Name | Status | Plan | Checkpoint | Handoff |
| ---: | --- | --- | --- | --- | --- |
| 0 | Docker and compatibility foundation | complete | `phase-00-docker-compatibility-plan.md` | `phase-00-checkpoint.md` | `phase-00-handoff.md` |
| 1 | Source governance and contracts | complete | `phase-01-source-governance-contracts-plan.md` | `phase-01-checkpoint.md` (superseded) | `phase-01-handoff.md` |
| 2 | Document ingestion | complete | `phase-02-document-ingestion-plan.md` | none | `phase-02-handoff.md` |
| 3 | Embedding generation | complete | `phase-03-embedding-generation-plan.md` | `phase-03-checkpoint.md` (superseded) | `phase-03-handoff.md` |
| 4 | Supabase vector and relational storage | complete after security remediation | `phase-04-supabase-storage-plan.md` | `phase-04-checkpoint.md` (superseded) | `phase-04-handoff.md` (complete) |
| 5 | Retrieval | blocked formal exit; software candidate verified | `phase-05-retrieval-plan.md` | `phase-05-checkpoint.md` (active) | `phase-05-handoff.md` (blocked) |

## Resume Order

1. Run `.agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .` when available.
2. Read the active checkpoint and plan.
3. Inspect Git status, recent commits, and referenced verification results.
4. Reconcile repository evidence before continuing the checkpoint's next action.


## Prepared documents (not phase completion)

- Phase 1 plan: [source governance and contracts](phase-01-source-governance-contracts-plan.md), formally started and software exit completed 2026-10-08; see the final handoff for pending source/benchmark gates.
- Phase 2 plan: [document ingestion plan](phase-02-document-ingestion-plan.md).
- Phase 4 plan: [Supabase vector and relational storage plan](phase-04-supabase-storage-plan.md).
- Remaining Phase 2 background: [document ingestion preparation](phase-02-document-ingestion-preparation.md). Depends on a complete Phase 1 handoff.
- [Prospectus and whole-Phase-2 workstream status](phase2-workstream-status.md) distinguishes completed A–D, unfinished implementation and human/authority gates.
- [Evaluation protocol](../evaluation/README.md) describes development/final grouping and review rubrics; final verified cases are pending.
