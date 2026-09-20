---
name: bintanong-phase-handoff
description: Use when starting, pausing, resuming, checkpointing, or completing a Bintanong implementation phase, especially after context rollover or when deciding whether the next phase may begin.
---

# Bintanong Phase Handoff

Keep phase progress recoverable without treating notes as proof. Repository state and fresh verification outrank checkpoints; only a complete final handoff permits phase advancement.

## Start or Resume

1. Run `python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .`.
2. Read `plans/INDEX.md`, the active checkpoint and plan, the previous final handoff, and only the relevant master-plan sections.
3. Compare checkpoint `head_commit` and working-tree claims with `git status --short`, recent commits, diffs, and named test results.
4. Preserve dirty changes. Repair stale checkpoint metadata before new implementation work.
5. Resume the checkpoint's exact next action. Do not repeat completed tasks unless repository evidence invalidates them.

## Checkpoint

Update the active `plans/phase-NN-checkpoint.md` after each verified task or commit, after a material ruling, and before a pause, approval wait, long operation, or expected context rollover. Record completed tasks and commits, active step, Git state, concise verification evidence, decisions, failures, next action, and work not to repeat.

A checkpoint is recoverable state, never completion evidence.

## Complete or Advance

1. Run the phase's full exit-gate verification and read every result.
2. Create a final handoff with exact versions, digests, commits, commands, results, deviations, risks, and next-phase prerequisites.
3. Mark the checkpoint `superseded` and update `plans/INDEX.md`.
4. Run `phase_state.py validate`, then `phase_state.py can-advance`.
5. Create the next numbered phase plan only when `can-advance` succeeds.

If the exit gate cannot pass, keep the same phase active or write a blocked handoff with its recovery condition. Never infer completion from checkboxes, elapsed effort, or a context boundary.

## Artifact Rules

Read [references/artifact-contract.md](references/artifact-contract.md) whenever creating or changing a plan, checkpoint, handoff, or index. Treat master-plan dependency versions as historical: each phase resolves current stable compatible versions from official sources and records what it pins.

## Common Mistakes

| Mistake | Required response |
| --- | --- |
| Selecting the newest file by timestamp | Use frontmatter and `plans/INDEX.md`. |
| Checkpoint disagrees with Git | Reconcile; Git and tests win. |
| Dirty tree after context loss | Inspect and preserve it; never reset it away. |
| Phase looks finished but lacks a handoff | It remains active. |
| Handoff is blocked | Do not increment the phase. |

