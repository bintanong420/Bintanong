# Bintanong Implementation Ledger

This file is the authoritative pointer for resuming work. Do not select a phase by file modification time.

## Current State

- Master plan: `plans/master_implementation_plan_original_long.md`
- Active phase: none (Phase 1 software exit complete; source authorization and final benchmark pending)
- Active plan: none; Phase 1 plan metadata is complete
- Active checkpoint: none; Phase 0 and Phase 1 checkpoints are superseded
- Latest final handoff: `plans/phase-01-handoff.md`
- Next permitted phase: `2` (eligibility only); the prepared plan is `phase-02-document-ingestion-plan.md`, and implementation needs the owner's review and a formal start

## Parallel prospectus workstream

- Approved review-only prospectus workstream plan: `plans/2026-09-26-prospectus-phase2-implementation-draft.md`
- Current cross-agent progress: `plans/plan_current_progress/current_progress.md`
- The user authorized JSONification, candidate Prolog work, and human review/correction in parallel with Phase 1 indexing. This workstream does not advance the formal phase ledger or authorize an active institutional release.

## Phase Ledger

| Phase | Name | Status | Plan | Checkpoint | Handoff |
| ---: | --- | --- | --- | --- | --- |
| 0 | Docker and compatibility foundation | complete | `phase-00-docker-compatibility-plan.md` | `phase-00-checkpoint.md` | `phase-00-handoff.md` |
| 1 | Source governance and contracts | complete | `phase-01-source-governance-contracts-plan.md` | `phase-01-checkpoint.md` (superseded) | `phase-01-handoff.md` |
| 2 | Document ingestion | ready (preparation only) | `phase-02-document-ingestion-plan.md` | none | none |

## Resume Order

1. Run `.agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .` when available.
2. Read the active checkpoint and plan.
3. Inspect Git status, recent commits, and referenced verification results.
4. Reconcile repository evidence before continuing the checkpoint's next action.


## Prepared documents (not phase completion)

- Phase 1 plan: [source governance and contracts](phase-01-source-governance-contracts-plan.md), formally started and software exit completed 2026-10-08; see the final handoff for pending source/benchmark gates.
- Phase 2 plan: [document ingestion plan](phase-02-document-ingestion-plan.md).
- Remaining Phase 2 background: [document ingestion preparation](phase-02-document-ingestion-preparation.md). Depends on a complete Phase 1 handoff.
- [Prospectus and whole-Phase-2 workstream status](phase2-workstream-status.md) distinguishes completed A–D, unfinished implementation and human/authority gates.
- [Evaluation protocol](../evaluation/README.md) describes development/final grouping and review rubrics; final verified cases are pending.
