# Bintanong Phase Artifact Contract

## Phase plan

Path: `plans/phase-NN-<slug>-plan.md`

Required frontmatter:

```yaml
artifact: phase-plan
phase: 0
status: ready
master: plans/master_implementation_plan_original_long.md
previous_handoff: null
```

Allowed statuses: `ready`, `in_progress`, `complete`, `blocked`.

The body defines the goal, global constraints, review focus, task checklist, interfaces, verification, and exit gate. Preserve a plan after creation; implementation discoveries go into its checkpoint, decision records, and final handoff.

## Checkpoint

Path: `plans/phase-NN-checkpoint.md`

Required frontmatter:

```yaml
artifact: phase-checkpoint
phase: 0
status: in_progress
sequence: 1
plan: plans/phase-00-<slug>-plan.md
head_commit: abc1234
working_tree: clean
updated_at: 2026-09-20T12:00:00+08:00
```

Allowed statuses: `in_progress`, `paused`, `blocked`, `superseded`.

Required body sections:

- Completed Tasks
- Current Task
- Repository State
- Verification Evidence
- Versions and Digests
- Decisions
- Known Failures or Blockers
- Next Action
- Do Not Repeat

Increment `sequence` for each material update. `head_commit` may be abbreviated if it uniquely prefixes the repository HEAD. If the working tree is dirty, list relevant changed and untracked files.

## Final handoff

Path: `plans/phase-NN-handoff.md`

Required frontmatter:

```yaml
artifact: phase-handoff
phase: 0
status: complete
plan: plans/phase-00-<slug>-plan.md
final_commit: abc1234
next_phase: 1
completed_at: 2026-09-20T13:00:00+08:00
```

Allowed statuses: `complete`, `blocked`.

A complete handoff contains exit-gate evidence, commits, selected versions and digests, compatibility measurements, deviations and rulings, unresolved risks, and next-phase prerequisites. A blocked handoff replaces `next_phase` with `recovery_condition` and cannot authorize advancement.

## Index

`plans/INDEX.md` names the immutable master, active phase, active plan, active checkpoint, latest final handoff, and next permitted phase. Its ledger links every created plan/checkpoint/handoff. It never uses modification time as state.

## Evidence precedence

When artifacts disagree, use this order:

1. Current repository contents and Git history.
2. Fresh verification output.
3. Final handoff.
4. Active checkpoint.
5. Phase plan.
6. Master plan for architectural intent.

