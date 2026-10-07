---
artifact: phase-checkpoint
phase: 1
status: in_progress
sequence: 2
plan: plans/phase-01-source-governance-contracts-plan.md
head_commit: c7e298f
working_tree: clean
updated_at: 2026-10-08T13:00:00+08:00
---

# Phase 1 Checkpoint

## Completed Tasks

- Formal start: f7b7752 (plan in_progress, checkpoint, index pointers).
- Task 1 (consumer inventory, Direct routing discrepancy, no runtime change): 664beb5, docs/decisions/phase-01-consumer-inventory.md. Line citations re-verified against the tree on 2026-10-08.
- Task 2 (governance vocabulary, transition table, four schemas, synthetic examples, guard tests, decision doc): c7e298f. Verified, not completed: Phase 1 as a whole is NOT complete (Tasks 3 onward remain, no final handoff).

## Current Task

- None active. Batch 1 (formal start, Tasks 1 and 2) is done; Task 3 is the next batch.

## Repository State

- Branch `feat/phase-01-source-governance-contracts` in worktree `Bintanong-wt/phase-1`, based on reviewed Phase E tip ec0eac7.
- Local `dev` is untouched (5c34fd7). Nothing pushed or merged.
- Working tree clean at c7e298f before this checkpoint update. Prospectus extractor changes in the owner checkout are untouched.

## Verification Evidence

- Baseline on system Python 3.13.12: `py -3.13 -m pytest -q tests` = 1674 passed, 1 skipped, 13 subtests passed. Prospectus jsonifier self-test = 80/80.
- At c7e298f (re-run 2026-10-08): full suite 1805 passed, 1 skipped, 13 subtests passed (1674 + 131 new); 	ests/test_source_governance_manifests.py 131 passed; skill tests 	est_phase_state.py 19 passed, 11 subtests; self-test 80/80.
- Mutation re-check in a scratch copy (7 guard mutations: transition evidence kind, recorder role, authorization_ref, namespace scan, foreign prefixes, approval id without evidence, same-filename-same-edition): each failed the suite, restored copy 131 passed.
- phase_state.py validate: State valid, active phase 1, working tree clean, only a head_commit warning for the commits made since the previous checkpoint. can-advance: refuses (exit 1) with phase 1 has no complete handoff.

## Versions and Digests

- Pydantic 2.13.4 is importable under `py -3.13`. No dependency was added.

## Decisions

- 2026-10-08: the owner explicitly instructed Claude to continue with "the subphases of Phase 2 and Phase 1 prep and exec". This is the owner's go to FORMALLY START Phase 1 on this local branch only. It does not complete Phase 1, does not advance Phase 2, does not activate any institutional source, and does not authorize a merge or push.
- Plan status uses the contract value `in_progress` (the artifact contract has no `active` status); `preparation_only` was removed as the contract requires.
- The prospectus extractor/review/OCR workstream is parallel and does not advance this ledger. Extraction audit success, EXTRACTED, VERIFIED and content review are never institutional approval.
- Open owner decisions are listed in docs/decisions/phase-01-source-governance.md (document categories, who may record as issuing office, verifier independence, reopening, date format, session idle lifetime) and the Direct routing meaning in the consumer inventory. None was decided here.
- Task 3 (shared contracts in backend/bintanong_contracts/) is outside the first batch.

## Known Failures or Blockers

- No authorized institutional source evidence exists; approval ids stay null. The Direct routing discrepancy is unresolved (owner decision needed on contract meaning).

## Next Action

- Task 3: implement the shared contracts incrementally in ackend/bintanong_contracts/ (test first), starting with SourceDocumentVersion and SourceSpan adapters over the existing extractor fields. Do not change runtime routing behaviour until the owner decides the Direct meaning.

## Do Not Repeat

- Do not redo the formal start, Task 1 or Task 2 unless repository evidence invalidates them. Do not recreate knowledge/manifests/ files; extend them.