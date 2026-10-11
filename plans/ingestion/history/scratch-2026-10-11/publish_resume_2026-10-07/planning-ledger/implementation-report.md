# Prepared phase ledger verification

Worktree: C:\Users\Hawksprey\source\repos\Bintanong-wt\formal-plans
Branch: docs/phase-1-2-preparation-20261007
Base HEAD: 3227ac8a801396a06b0d593c975df313e7f67c84
Interpreter: Python 3.13.12; pytest 9.0.3.

## Scope and ruling

Preparation-only phase plans use explicit boolean preparation_only: true, permitted only for status: ready on phase-plan artifacts. Ordinary ready plans remain active when the flag is omitted or false. Prepared plans remain in duplicate/sequence checks, but do not replace the active/current phase or its final handoff gate. A prepared Phase 1 after a complete Phase 0 handoff has no active phase and next permitted phase 1. A handoff attached to the still-prepared phase cannot authorize Phase 2.

Separate adjacent ruling from the root: starting Phase 1 must preserve superseded Phase 0 history. Only superseded cross-phase checkpoints are excluded from active-plan mismatch errors; foreign in_progress, paused and blocked checkpoints remain invalid. Start by removing the preparation flag (or setting false), marking the plan in_progress, creating its checkpoint and updating index active pointers. Phase 2 requires the Phase 1 complete handoff.

No INDEX parser, dependency installation, checkpoint migration or runtime changes. No commit, stage, push, dev movement or owner-checkout writes. No institutional source authorization or approval was inferred; owner authorization evidence and institution approval remain pending.

## Authentic TDD evidence

Tests were written before production code. Distinct red runs were recorded before either fix.

Preparation red: 7 selected test methods; pytest reported 10 failed (including subtests), 3 passed, 12 deselected; exit 1. Expected selection/gate/flag validation assertions failed.
Start transition red: 1 failed, 1 passed, 17 deselected; exit 1. Preserved superseded Phase 0 checkpoint was rejected during Phase 1 start.
Preparation green: 7 passed, 12 deselected; exit 0.
Start transition green: 2 passed, 17 deselected; exit 0.
Full skill test module: 19 passed in 14.35 seconds; exit 0.

All commands ran directly in PowerShell from the worktree. PYTHONDONTWRITEBYTECODE=1. No pytest cache provider. All pytest basetemp paths outside the worktree.

Exact pytest commands (each piped through Tee-Object to the corresponding log, followed by LASTEXITCODE capture and exit):

py -3.13 -m pytest .agents/skills/bintanong-phase-handoff/tests/test_phase_state.py -p no:cacheprovider --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\planning-ledger\pytest-red-preparation" -k 'prepared or preparation or ordinary_ready'
py -3.13 -m pytest .agents/skills/bintanong-phase-handoff/tests/test_phase_state.py -p no:cacheprovider --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\planning-ledger\pytest-red-start" -k 'started_phase'
py -3.13 -m pytest .agents/skills/bintanong-phase-handoff/tests/test_phase_state.py -p no:cacheprovider --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\planning-ledger\pytest-green-preparation" -k 'prepared or preparation or ordinary_ready'
py -3.13 -m pytest .agents/skills/bintanong-phase-handoff/tests/test_phase_state.py -p no:cacheprovider --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\planning-ledger\pytest-green-start" -k 'started_phase'
py -3.13 -m pytest .agents/skills/bintanong-phase-handoff/tests/test_phase_state.py -p no:cacheprovider --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\planning-ledger\pytest-green-full"

Logs: red-preparation.txt, red-start-transition.txt, green-preparation.txt, green-start-transition.txt, green-full.txt.

## Frozen files

.agents/skills/bintanong-phase-handoff/scripts/phase_state.py:32 (flag), :100 (validation), :134 (active selection), :150 (checkpoint history), :178 (current handoff selection).
.agents/skills/bintanong-phase-handoff/tests/test_phase_state.py:213 (preparation regressions), :283 (start transition), :303 (unfinished checkpoints).
.agents/skills/bintanong-phase-handoff/references/artifact-contract.md:19 (flag), :21 (start transition).

SHA256 values are in frozen-files.json. Root owns remaining plan/index metadata and broad verification gates.
