---
name: bintanong-handoff-reminder
description: Use for every prompt concerning the Bintanong repository, including implementation, fixes, planning, reviews, status requests, and resumed work. Reminds the agent to use the phase handoff skill and maintain plans/plan_current_progress alongside formal plans.
---

# Bintanong Handoff Reminder

At the start of each Bintanong prompt, load [bintanong-phase-handoff](../bintanong-phase-handoff/SKILL.md) and apply the parts relevant to the task. After context rollover, reload it before resuming. This reminder routes to that workflow; it does not replace its artifact contract or phase checks.

- Read `plans/INDEX.md`, `plans/plan_current_progress/current_progress.md`, and the relevant sections of `plans/master_implementation_plan_original_long.md`. Use the active plan, checkpoint, and previous final handoff identified by the handoff workflow. Compare notes with current Git state before acting.
- On every phase start/resume or context rollover, also inspect `Context/`: relevant thesis pages and the runtime routing diagram are architectural evidence. Record which context was consulted and reconcile scope discrepancies before implementation; a new CLI/account must follow the same loop.
- Keep current changes, decisions, verification actually performed, blockers, and the exact next action in `plans/plan_current_progress/current_progress.md`. Update it after material work and before ending a turn, pausing, waiting for approval, or context rollover. For an active numbered phase, also update its checkpoint as required by the handoff skill; the progress log does not replace it. A read-only prompt with no new findings does not require a log edit.
- Keep plans, checkpoints, handoffs, and decision records in the repository's `plans/` and existing decision-record locations. Preserve the original master plan and historical entries; append dated progress instead of overwriting history.
- Read `plans/ingestion/` only when the current task or relevant master-plan section requires ingestion evidence. It is supporting documentation and must not become the sole current progress log or replace the numbered phase ledger. Preserve existing ingestion documents.
- When the owner's stated phase and recorded phase disagree, record both and reconcile the evidence through the handoff skill before claiming formal advancement. Do not fabricate completion evidence or repeat delivered work merely because its handoff is missing. Preserve existing execution and approval boundaries.

This skill provides instructions, not an executable per-prompt hook. Repository `AGENTS.md` supplies the every-prompt routing rule, and automatic skill selection should remain enabled.
