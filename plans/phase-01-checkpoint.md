---
artifact: phase-checkpoint
phase: 1
status: in_progress
sequence: 4
plan: plans/phase-01-source-governance-contracts-plan.md
head_commit: f33cc7c
working_tree: clean
updated_at: 2026-10-10T12:00:00+08:00
---

# Phase 1 Checkpoint

## Completed Tasks

- Formal start: f7b7752 (plan in_progress, checkpoint, index pointers).
- Task 1 (consumer inventory, Direct routing discrepancy, no runtime change): 664beb5, docs/decisions/phase-01-consumer-inventory.md. Line citations re-verified against the tree on 2026-10-08.
- Task 2 (governance vocabulary, transition table, four schemas, synthetic examples, guard tests, decision doc): c7e298f.
- Review fix pass 1 on Tasks 2 and 3 (governance checks): d110d5d control characters repaired in two older plans plus tests/test_docs_hygiene.py; f03e6dd wording; 0092b20 governance schemas and test-local checker hardened (evidence order enforces the transition table's `from` column on records, supersession, authorization refs, local paths, real timestamps, namespace scan); f33cc7c decision record. Package-level findings in backend/bintanong_contracts/ are not fixed yet and are the next pass.
- Task 3 (shared contracts in backend/bintanong_contracts/, tests first): b580064 base and versioning; bf1f485 SourceDocumentVersion, SourceConflict, SessionFact; 464dc3e SourceSpan, Chunk and the read-only extractor chunk adapter; 501212c EmbeddingRecord; f5b0cb2 NormalizedQuery, RoutingDecision, RetrievalResult and the legacy routing adapter; 17aab66 DecisionOutcome, SymbolicResult, capability registry, EvidenceBundle, AnswerEnvelope; 983c9d9 adversarial, determinism and schema-compatibility tests; 6ef3f64 mutation-driven tests; d4ccbaa decision record docs/decisions/phase-01-contracts.md. Verified, not completed: Phase 1 as a whole is NOT complete (Tasks 4 to 6, independent review and the final handoff remain).

## Current Task

- None active. Task 3 is done; Task 4 is next.

## Repository State

- Branch `feat/phase-01-source-governance-contracts` in worktree `Bintanong-wt/phase-1`, based on reviewed Phase E tip ec0eac7.
- Local `dev` is untouched (5c34fd7). Nothing pushed or merged.
- Working tree clean at f33cc7c before this checkpoint update. Prospectus extractor changes in the owner checkout are untouched.
- No runtime behaviour of bintanong_api, bintanong_embedding or bintanong_tools changed. The contracts package is new code; its adapters read the extractor chunk shape and the legacy routing shape and edit neither.

## Verification Evidence

- Baseline before Task 3 on system Python 3.13.12: full suite 1805 passed, 1 skipped, 13 subtests; prospectus jsonifier self-test 80/80.
- After Task 3: `py -3.13 -m pytest -q tests` = 2325 passed, 1 skipped, 13 subtests passed (1805 + 520 new in tests/test_contracts_*.py). Self-test 80/80.
- After fix pass 1: `py -3.13 -m pytest -q tests` = 2536 passed, 1 skipped, 13 subtests passed (2325 + 157 new governance tests + 54 in tests/test_docs_hygiene.py). Self-test 80/80. Skill tests 19 passed, 11 subtests.
- Red first for each contract group (collection failed with the module missing), then green.
- Fix pass 1 mutation check on the governance schemas, vocabulary and test-local checker (scratch copies): 168 mutations; first run 151 killed, 16 survived, 1 not applicable; after the added tests 167 killed, 0 survived; 1 mutant retired with the redundant guard it targeted. Governance test file: 288 tests (was 131); tests/test_docs_hygiene.py: 54.
- Mutation checks for the contracts package in a scratch copy (Task 3, not re-run in the fix pass): first run 192 guard mutations, 160 killed, 32 survived; six survivors were redundant guards and were deleted, the others got new tests; re-run 188 mutations, 188 killed, 0 survived.
- Adapter: every semantic chunk the extractor's own builders produce on a synthetic candidate (course, program overview, term schedule, plus a layout fallback chunk, anchored and unanchored) maps with ids and hashes preserved; the missing page size for bounding boxes is reported as a named gap, not invented.
- phase_state.py validate: State valid, active phase 1, working tree clean (head_commit warning for the commits since the previous checkpoint). can-advance: refuses, phase 1 has no complete handoff.

## Versions and Digests

- Pydantic 2.13.4 is importable under `py -3.13`; `pydantic==2.13.5` is declared in the `api` and `embedding` extras of backend/pyproject.toml but not in `tools` or `dev`. No dependency, pyproject or lock file was changed. See owner decision 11 in docs/decisions/phase-01-contracts.md.
- Contract schema versions: bintanong-source-register-v1, -source-conflict-v1, -session-fact-v1, -decision-v1, -source-span-v1, -chunk-v1, -embedding-record-v1, -normalized-query-v1, -routing-decision-v1, -retrieval-result-v1, -symbolic-result-v1, -evidence-bundle-v1, -answer-envelope-v1.

## Decisions

- 2026-10-08: the owner explicitly instructed to continue with "the subphases of Phase 2 and Phase 1 prep and exec". This is the owner's go to FORMALLY START Phase 1 on this local branch only. It does not complete Phase 1, does not advance Phase 2, does not activate any institutional source, and does not authorize a merge or push.
- Plan status uses the contract value `in_progress` (the artifact contract has no `active` status); `preparation_only` was removed as the contract requires.
- The prospectus extractor/review/OCR workstream is parallel and does not advance this ledger. Extraction audit success, EXTRACTED, VERIFIED and content review are never institutional approval.
- Open owner decisions: the Direct routing meaning (legacy Direct is refused by the adapter and is not a contract route), the Task 3 list in docs/decisions/phase-01-contracts.md (page-size source, geometry tolerance, unconfirmed student facts, predicate request producer and registry authorization, conflict capability mapping, multi-edition comparison, intent taxonomy, exact token count convention, release ids, dependency declaration) and the earlier list in docs/decisions/phase-01-source-governance.md. None was decided here.

## Known Failures or Blockers

- No authorized institutional source evidence exists; approval ids stay null. The Direct routing discrepancy is unresolved (owner decision needed on contract meaning).
- The extractor does not record page size next to bounding boxes, so extractor chunks with boxes are rejected by the chunk adapter unless page sizes are supplied or the boxes are dropped with a reported gap.

## Next Action

- Task 4: bind one synthetic source version and span to one reviewed chunk, one rule draft and one evaluation case with traceability checks (synthetic, remains synthetic until authorized source coverage exists). Reuse the contracts (bind_chunk, check_chunk_binding, SymbolicResult, CapabilityRegistry); do not change runtime routing behaviour until the owner decides the Direct meaning.

## Do Not Repeat

- Do not redo the formal start or Tasks 1 to 3 unless repository evidence invalidates them. Do not recreate knowledge/manifests/ files or backend/bintanong_contracts/; extend them.
