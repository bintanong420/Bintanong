---
artifact: phase-checkpoint
phase: 1
status: in_progress
sequence: 6
plan: plans/phase-01-source-governance-contracts-plan.md
head_commit: 8d7308e
working_tree: clean
updated_at: 2026-10-08T18:41:33+08:00
---

# Phase 1 Checkpoint

## Completed Tasks

- Formal start: f7b7752 (plan in_progress, checkpoint, index pointers).
- Task 1 (consumer inventory, Direct routing discrepancy, no runtime change): 664beb5, docs/decisions/phase-01-consumer-inventory.md. Line citations re-verified against the tree on 2026-10-08.
- Task 2 (governance vocabulary, transition table, four schemas, synthetic examples, guard tests, decision doc): c7e298f.
- Review fix pass 1 on Tasks 2 and 3 (governance checks): d110d5d control characters repaired in two older plans plus tests/test_docs_hygiene.py; f03e6dd wording; 0092b20 governance schemas and test-local checker hardened (evidence order enforces the transition table's `from` column on records, supersession, authorization refs, local paths, real timestamps, namespace scan); f33cc7c decision record.
- Task 3 (shared contracts in backend/bintanong_contracts/, tests first): b580064 base and versioning; bf1f485 SourceDocumentVersion, SourceConflict, SessionFact; 464dc3e SourceSpan, Chunk and the read-only extractor chunk adapter; 501212c EmbeddingRecord; f5b0cb2 NormalizedQuery, RoutingDecision, RetrievalResult and the legacy routing adapter; 17aab66 DecisionOutcome, SymbolicResult, capability registry, EvidenceBundle, AnswerEnvelope; 983c9d9 adversarial, determinism and schema-compatibility tests; 6ef3f64 mutation-driven tests; d4ccbaa decision record docs/decisions/phase-01-contracts.md. Verified, not completed: Phase 1 as a whole is NOT complete (Tasks 4 to 6, independent review and the final handoff remain).
- Task 3 fix pass 2 (package-level findings of the independent review of 2b6c503..6a35722; one High, many Mediums): 86e48a0 checkpoint of the previous pass; 1d44efc the `from` column, supersession, authorization, paths and the namespace scan ported to the package, with a parity test against the test-local checker; eaaa3f8 chunk text tied to spans, register bindings, pinned revisions, decision scope and rule spans, the register check inside retrieval, query markers, goal shapes, envelope rules, adapter against real extractor output; 3e44917 five redundant checks removed; fbc6d20 survivor tests, vocabulary pins and reason-asserting test helpers; 3b938f4 decision record. Verified, not independently re-checked: because the first finding was High, one independent re-check of Task 3 follows.

- Task 5 (case schema, split and group validation, freeze record, rubrics, run record, 21 synthetic development cases, decision record docs/decisions/phase-01-evaluation.md): 058c164 case schema; 9806a46 split and group validation; 0725676 rubrics and run record; 076e20c development cases; 4c1072d adversarial and survivor tests; dd4d7e2 decision record. No verified or final case exists; the coverage line reads "NOT MET: 0 verified final cases, 0 Taglish (target 50 Taglish, >= 10 per category)".
- Independent re-check of Task 3 (archive of 28ef15f): the earlier High (the unenforced transition `from` state) is CLOSED. It found no new High and three Mediums (M1 bound values refused 18 of 49 real BSBA-HRM course codes; M2 a revoked record skipped the approval guards; M3 decision scope and rule spans were not tied to the bundle or register) plus Lows.
- Task 3 fix pass 3 (answers the re-check; NOT re-reviewed again by design, because no High remains): 03a7c61 a bound value is data and a fixed renderer quotes it (all 49 BSBA-HRM and 53 IT real codes parse and render); 659ce71 a revocation meets every approval guard and the authorization date covers all relied evidence; 77e5307 a decided result's scope and rule spans must come from a carried register version; d2723b9 namespace scan reads past invisible characters, percent escapes and look-alike letters; fa7493f privileged stems, all-zero revisions, model_copy validates; 853560b span identity ignores whitespace-only differences; e98c63c the six surviving mutants killed and nothing/nobody added to the negation list; f6c0663 reasons asserted in pytest.raises; 58e71c9 look-alike map clean-up; ffab528 and 8d7308e decision record (89 targeted mutants, 88 killed, 1 equivalent).

## Current Task

- None active. The owner stopped all agents on 2026-10-08 to hand over to Codex. Remaining Phase 1 work: Task 4, then Task 6 (independent review of governance/contracts/privacy, honest exit-gate statement, final handoff).

## Repository State

- Branch `feat/phase-01-source-governance-contracts` in worktree `Bintanong-wt/phase-1`, based on reviewed Phase E tip ec0eac7.
- Local `dev` is untouched (5c34fd7). Nothing pushed or merged.
- Working tree clean at 8d7308e before this checkpoint update. Prospectus extractor changes in the owner checkout are untouched.
- No runtime behaviour of bintanong_api, bintanong_embedding or bintanong_tools changed, and nothing under those packages, backend/pyproject.toml or uv.lock was edited. The contracts package is new code; its adapters read the extractor chunk shape and the legacy routing shape and edit neither.

## Verification Evidence

- Baseline before Task 3 on system Python 3.13.12: full suite 1805 passed, 1 skipped, 13 subtests; prospectus jsonifier self-test 80/80.
- After Task 3: `py -3.13 -m pytest -q tests` = 2325 passed, 1 skipped, 13 subtests passed (1805 + 520 new in tests/test_contracts_*.py). Self-test 80/80.
- After fix pass 1: 2536 passed, 1 skipped, 13 subtests passed (2325 + 157 new governance tests + 54 in tests/test_docs_hygiene.py). Self-test 80/80. Skill tests 19 passed, 11 subtests.
- After fix pass 2: `py -3.13 -m pytest -q tests` = 3340 passed, 1 skipped, 13 subtests passed (2536 + 804 new or changed-by-parametrization tests: governance_fix2, parity, source_fix2, runtime_fix2, answer_fix2, survivors, survivors_2). Self-test 80/80 (`run_self_tests(verbose=True)`, exit 0).
- Red first for each contract group (collection failed with the module missing), then green. Fix pass 2: the governance and source groups were run red against the unchanged package; the runtime and answer groups were run against the pre-fix package in a scratch copy (72 failed and the answer file failed at collection).
- Parity: tests/test_contracts_parity.py gives the package and the test-local checker the same 367 documents (examples and the whole mutation corpus) and asserts one verdict. The test-local checker gained four rules the package has (effective dates, supersession across documents, authorization dated before its evidence, year window) so both agree.
- Fix pass 2 mutation check on the contracts package and the vocabulary (scratch copies): first run 846 mutants, 801 killed, 45 survived; after tests and the removal of five redundant checks, second run 835 mutants, 834 killed, 1 survived; a targeted re-run after one more test killed it. Details in docs/decisions/phase-01-contracts.md.
- Fix pass 1 mutation check on the governance schemas, vocabulary and test-local checker: 168 mutations; 167 killed after added tests, 1 retired with a redundant guard.
- After Task 5: 3507 passed, 1 skipped (3340 + 167 in tests/test_evaluation_*.py; the agent's mutation run on the evaluation machinery was 109 mutants, 108 killed, 1 equivalent).
- After fix pass 3, verified by the orchestrator at ffab528 on system Python 3.13 with `-p no:cacheprovider` and a basetemp outside the repository: `py -3.13 -m pytest -q tests` = 3927 passed, 1 skipped, 13 subtests passed; prospectus jsonifier self-test 80/80; `git diff --check` clean; 0 attribution trailers over ec0eac7..HEAD; zero diff under backend/bintanong_api, bintanong_embedding, bintanong_tools, backend/pyproject.toml and uv.lock; phase_state.py validate valid and can-advance refusing.
- Adapter on real extractor output: the extractor's own builders on a cached Docling JSON of the BSBA-HRM prospectus (fictional digest, no PDF read) gave 61 chunks; with the real page sizes from that JSON (612 by 936) 48 mapped before this pass and 58 map now; the other 3 are layout chunks with printed source text but textless spans (`span_missing_text`).
- phase_state.py validate: State valid, active phase 1, working tree clean (head_commit warning for the commits since this checkpoint). can-advance: refuses, phase 1 has no complete handoff.

## Versions and Digests

- Pydantic 2.13.4 is importable under `py -3.13`; `pydantic==2.13.5` is declared directly in the `api` and `embedding` extras of backend/pyproject.toml only. uv.lock shows `docling` (tools extra) reaching pydantic through docling-core, so the dependency is undeclared-direct under tools plus dev and low impact today. No dependency, pyproject or lock file was changed. See owner decision 11 in docs/decisions/phase-01-contracts.md.
- Contract schema versions: bintanong-source-register-v1, -source-conflict-v1, -session-fact-v1, -decision-v1, -source-span-v1, -chunk-v1, -embedding-record-v1, -normalized-query-v1, -routing-decision-v1, -retrieval-result-v1, -symbolic-result-v1, -evidence-bundle-v1, -answer-envelope-v1. Additive in pass 2: SourceSpan `original_page`/`page_offset`, locator kind `section`, Chunk `register_binding`, RetrievalResult `versions`, SymbolicResult `scope`/`rule_spans`; the vocabulary file gained `runtime` and `query_markers`.

## Decisions

- 2026-10-08: the owner explicitly instructed to continue with "the subphases of Phase 2 and Phase 1 prep and exec". This is the owner's go to FORMALLY START Phase 1 on this local branch only. It does not complete Phase 1, does not advance Phase 2, does not activate any institutional source, and does not authorize a merge or push.
- Plan status uses the contract value `in_progress` (the artifact contract has no `active` status); `preparation_only` was removed as the contract requires.
- The prospectus extractor/review/OCR workstream is parallel and does not advance this ledger. Extraction audit success, EXTRACTED, VERIFIED and content review are never institutional approval.
- Open owner decisions: the Direct routing meaning (legacy Direct is refused by the adapter and is not a contract route), the list in docs/decisions/phase-01-contracts.md (now 21 items, including the strict defaults chosen in fix pass 2 for the owner to overrule: identical-spans-only, pinned-revision format, l2 tolerance, the year window, claim and control vocabularies, the negation and time-qualifier word lists, one chunker version per result, answered decisions needing citations, the vocabulary path resolved at import time) and the earlier list in docs/decisions/phase-01-source-governance.md. None was decided here.

## Known Failures or Blockers

- No authorized institutional source evidence exists; approval ids stay null. The Direct routing discrepancy is unresolved (owner decision needed on contract meaning).
- The extractor does not record page size next to bounding boxes, so extractor chunks with boxes are rejected by the chunk adapter unless page sizes are supplied or the boxes are dropped with a reported gap.
- Three of 61 real BSBA-HRM chunks do not map (layout chunks whose Docling text is asserted as source text while their spans carry none).
- The 50 verified Taglish final cases do not exist and cannot until source-backed independent review and owner-authorized sources exist (coverage NOT MET, stated honestly by the validator).
- The three Mediums of the Task 3 re-check were fixed in fix pass 3, which has had no further independent review (by design: no High remained). Task 6 must include a narrow check of that pass.

## Next Action

- Task 4: bind one source version and span to one reviewed chunk, one rule draft and one evaluation case with traceability checks. Prefer ONE real prospectus chunk (BSBA-HRM, from the extractor's own builders on the cached Docling JSON, fictional or real digest as available, state left pending) plus a synthetic rule draft and the evaluation example already at evaluation/examples/traceability-synthetic.json; everything stays synthetic or pending until authorized source coverage exists. Reuse the contracts (bind_chunk, check_chunk_binding, SymbolicResult, CapabilityRegistry, prolog_quote); do not change runtime routing behaviour until the owner decides the Direct meaning.
- Task 6: independent review (Spec and Standards) of governance, contracts and privacy including a narrow check of fix pass 3; state the exit gate honestly (missing authorized source coverage documented, not fabricated); write plans/phase-01-handoff.md per the artifact contract; run `phase_state.py validate` then `can-advance`. Only a complete handoff permits Phase 2.

## Do Not Repeat

- Do not redo the formal start, Tasks 1 to 3, Task 5 or fix passes 1 to 3 unless repository evidence invalidates them. Do not recreate knowledge/manifests/ files or backend/bintanong_contracts/; extend them.
