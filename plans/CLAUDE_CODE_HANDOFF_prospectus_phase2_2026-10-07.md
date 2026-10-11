# Claude Code Handoff: Prospectus Phase 2

**Snapshot:** 2026-10-07
**Purpose:** Resume the prospectus Phase 2 work after Codex context/usage limits. This is a recovery handoff, not completion evidence and not institutional curriculum approval.

## Read first

1. Run the phase-state inspection from the repository root:

   ```powershell
   python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .
   ```

2. Read `plans/INDEX.md`, this handoff, and the relevant worktree progress ledger:
   `plans/plan_current_progress/extractor_split_progress.md`.
3. Treat Git state and fresh tests as authoritative. Do not trust old checkpoint counts without rerunning the named command.
4. Preserve dirty worktrees and user-owned files. Do not reset, clean, or use `git add -A`.

## Repository state at snapshot

Main checkout:

```text
Path: C:/Users/Hawksprey/source/repos/Bintanong
Branch: dev
HEAD: 58d4bb6 docs: plan Phase B2 year and semester fixer
State: M .gitignore
       ?? plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md
```

The formal ledger currently reports **Phase 0 complete**, no active formal phase, and Phase 1 ready. The prospectus extractor work is a parallel review-only workstream and does not itself advance the formal phase ledger.

## Skills and subagents used

These are the relevant process tools behind the current state. Load them again only when the next action matches their trigger; they are recorded here to preserve provider-switching context.

### Used or directly applied

- `bintanong-phase-handoff`: phase-state inspection, checkpoint rules, dirty-worktree preservation, and completion-gate discipline.
- `writing-for-agents`: structure and completion criteria for this handoff document.
- `code-review`: review framing for standards/specification findings; use only when a fixed comparison point and review target are available.
- `extractor-reviewer` subagent: read-only B2 review against the Phase B2 plan; it identified the unfinished Tasks 12-14, the B2 diff-hygiene issue, and ledger/filesystem review risks.

### Prescribed by the Phase 2 plans

- `extractor-implementer` subagent: test-first implementation of one bounded extractor-plan task. Use for a specific B2/C/D/E/F task only, then run `extractor-reviewer`.
- `extractor-reviewer` subagent: read-only review after an implementation task; do not use it as evidence that a phase is complete until the plan's exit gates and handoff are also complete.
- TDD-style red/green task flow: required by the B2 plan for implementation tasks; preserve the existing focused-test evidence before widening scope.

### Model/provider handoff context

- Earlier Claude/Codex sessions produced the implementation commits and progress ledgers; the current handoff records their claims but does not replace fresh verification.
- Codex read-only review was used for B2 review-fix batches and final-gate scrutiny. Do not infer that a passing Codex review closed the human trial or formal phase handoff.

## Worktrees

| Path | Branch / HEAD | State | Use |
| --- | --- | --- | --- |
| `C:/Users/Hawksprey/source/repos/Bintanong-wt/b2` | `feat/prospectus-phase-b2-section-fixer` @ `2414252` | clean; ahead 20 of origin | Primary B2 continuation point |
| `C:/Users/Hawksprey/source/repos/Bintanong-wt/task13` | `feat/prospectus-b2-banner-split` @ `db16b26` | clean | Separate Task 13 implementation |
| `C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-c` | `feat/prospectus-phase-c-status-separation` @ `81ac0f1` | clean | Phase C implementation and final-gate fixes |
| `C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d` | `feat/prospectus-phase-d-safe-cache` @ `08a8290` | dirty progress ledger | Phase D runtime/final-gate work; preserve changes |
| `C:/Users/Hawksprey/source/repos/Bintanong-wt/gui` | `feat/prospectus-review-gui` @ `ffe0a10` | untracked implementation/tests | GUI work is not closed |
| `C:/Users/Hawksprey/source/repos/Bintanong-wt/gui-plan` | `docs/prospectus-review-gui-plan` @ `4de3829` | clean | GUI planning only |
| `C:/Users/Hawksprey/source/repos/Bintanong-wt/ocr` | `feat/ocr-measurement-harness` @ `5467f51` | clean | OCR harness exists; measurement gates remain |
| `C:/Users/Hawksprey/source/repos/Bintanong-wt/d-baseline-641523d` | detached @ `641523d` | clean | Phase D comparison baseline; retain |
| `C:/Users/Hawksprey/AppData/Local/Temp/rv_new` | detached @ `388222d` | generated artifacts dirty | Temporary review checkout |
| `C:/Users/Hawksprey/AppData/Local/Temp/rv_old` | detached @ `bde999e` | untracked test | Temporary review checkout |

## Phase 2 status

### Finished or implementation-complete

- **Phase A: extractor package split:** complete; prior golden comparison was `44/44 identical`; self-test `80/80`.
- **Phase B: markup twin:** complete; decision record exists and the work was merged locally into `dev`.
- **B2 Tasks 1-11:** implemented on the B2 branch: course checks, verifier, fixes, placement, ledger, materialisation, review sheets, CLI, trial artifacts, triage, and end-to-end checks.
- **B2 review-fix batches:** implemented through the B2 branch tip, including strict ledger values, stale decisions, row-local banner evidence, wrapped-code handling, and Codex re-review fixes.
- **Task 13:** implementation exists separately on `feat/prospectus-b2-banner-split`; it must still be reviewed, approved, integrated, and regression-gated.
- **Phase C Tasks 1-7:** implemented. Latest recorded evidence includes `44/44 identical`, `494 passed + 13 subtests`, and extractor self-test `80/80`.
- **Phase D runtime work:** safe cache/publication, context-sensitive skip, TUI force behavior, failure injection, real-PDF checks, and corpus comparisons have recorded passing runtime evidence. Latest documented final runtime evidence includes `990 passed + 13 subtests`, `44/44 identical`, and self-test `80/80`.

### Not formally complete

- **B2 Task 12:** human review of the trial sheets and explicit go/no-go decision.
- **B2 Task 13:** integrate or explicitly defer the banner split; rerun the selected 44-input comparer gate.
- **B2 Task 14:** decision record, final Codex review, final handoff, and B2 closeout.
- **Phase C Task 8:** review gates were recorded as not run; perform specification/quality review and final handoff.
- **Phase D:** whole-range specification review, independent quality review, and documentary closure remain pending. Its progress ledger is dirty.
- **Review GUI:** implementation/test files are untracked in the GUI worktree; completion and review remain.
- **OCR:** harness and model setup exist; the corpus/photo measurement plan, scoring, human review, and final gates remain.
- **Phase E: RAG provenance:** planned, not started/formally integrated.
- **Phase F: tools/CLI boundary:** planned, not started/formally integrated.
- **Formal Phase 1:** marked ready in `plans/INDEX.md`, but no active Phase 1 plan exists.

## Primary next action

Resume from the B2 worktree. Do not start a new implementation slice before the B2 trial decision is resolved.

```powershell
Push-Location C:\Users\Hawksprey\source\repos\Bintanong-wt\b2
git status --short --branch
git log --oneline dev..HEAD
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --self-test
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_fixer --help
Pop-Location
```

Known prior B2 verification: full suite `335 passed, 13 subtests passed`; self-test `80/80`; fixer CLI help passed. Reconfirm before relying on these counts.

Then:

1. Read the trial instructions in the external review folder recorded in the B2 plan and make the human Task 12 decision.
2. Review `task13` against `plans/2026-10-04-prospectus-phase-b2-section-fixer.md`; merge only after the decision permits it.
3. Complete B2 Task 14 and write the final handoff before calling B2 complete.
4. Resume Phase C review gates.
5. Resume Phase D whole-range reviews and closeout.
6. Only after those gates, continue GUI, OCR, Phase E, and Phase F.

## Do not repeat

- Do not recreate the extractor package split or markup twin.
- Do not rerun broad real-PDF corpus work merely to reproduce old counts; use the recorded evidence and rerun only the named gate needed for the current decision.
- Do not treat extractor audit success, `EXTRACTED`, `VERIFIED`, or content review as institutional approval.
- Do not activate RAG/Prolog output for unreviewed or unverified curricula.
- Do not merge Task 13 automatically; its plan explicitly requires a human go/no-go.
- Do not discard dirty `.gitignore`, Codex handoff, Phase D progress, GUI files, or temporary review artifacts.

## Known review risks

- B2 `git diff --check` previously reported trailing whitespace in `tests/test_prospectus_materialise.py`.
- The B2 reviewer flagged malformed-ledger append behavior and filesystem output-guard edge cases. Treat these as review items; do not change them without a focused failing test and an explicit contract decision.
- Phase C has strong runtime evidence but its review gate is still not complete.
- Phase D has strong runtime evidence but is explicitly not fully complete until whole-range reviews and documentary closure pass.

## Handoff completion criterion

This handoff is successful when Claude Code can identify the correct worktree, reproduce the current focused gates, complete the B2 human/review closure, and leave a final handoff with exact commits, commands, results, deviations, and risks. Do not mark any phase complete from this document alone.
