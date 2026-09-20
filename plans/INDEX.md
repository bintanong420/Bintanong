# Bintanong Implementation Ledger

This file is the authoritative pointer for resuming work. Do not select a phase by file modification time.

## Current State

- Master plan: `plans/master_implementation_plan_original_long.md`
- Active phase: `0`
- Active plan: `plans/phase-00-docker-compatibility-plan.md`
- Active checkpoint: `plans/phase-00-checkpoint.md`
- Latest final handoff: none
- Next permitted phase: none until Phase 0 has a `complete` handoff

## Phase Ledger

| Phase | Name | Status | Plan | Checkpoint | Handoff |
| ---: | --- | --- | --- | --- | --- |
| 0 | Docker and compatibility foundation | in_progress | `phase-00-docker-compatibility-plan.md` | `phase-00-checkpoint.md` | none |
| 1 | Source governance and contracts | blocked_by_phase_0 | not created | none | none |

## Resume Order

1. Run `.agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .` when available.
2. Read the active checkpoint and plan.
3. Inspect Git status, recent commits, and referenced verification results.
4. Reconcile repository evidence before continuing the checkpoint's next action.

