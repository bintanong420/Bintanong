# Phase6 Task1 resumable implementation checkpoint

Status: INCOMPLETE / NOT ACCEPTED. No staging, commits, descendants or self-review. Base verified clean at `8cdb8cfdce03c69f718bb63390903b484437112a` before writes. Root retains acceptance, commit, freeze and fresh independent Spec/Standards ownership.

## Scope and implementation

Only the three additive paths and conditionally authorized fourth test changed. New pure compiler reparses source/span contracts, checks register/digest/version binding, validates field schemas/numbers, recomputes prerequisites, blocks cycles, preserves unresolved/source text, emits inactive views and canonical hashes. Existing ledger decision helpers supply applicable accepted-blank evidence through the source-version wrapper. Unsupported program/term/elective mappings remain blocked. Legacy Prolog is ignored; only quoting is reused. No files/network/Prolog execution occurs inside preparation.

Fourth path adjustment was made only after its exact static assertion failed. It excludes the inactive compiler consumer from the literal vocabulary writer scan, without quote-style evasion; runtime extractor/classifier and ledger assertions remain. All 35 materialise tests pass in the bounded run. ADR documents wrapper and compatibility decision.

- `backend/bintanong_tools/prospectus_extractor/rule_candidates.py` SHA256 `7297194747693367f3d6697a14bfb361d8685d9cf983a307ac305ac3e3d1a589`
- `tests/test_rule_candidates.py` SHA256 `2238023ab415a00d5977f1f1b7ac05e9b7c5cb6dfb251986016f4fe4a7402e39`
- `docs/decisions/phase-06-prospectus-candidates.md` SHA256 `6d25af2cce038d8fb7f64624736d4061cb821e3b9280c548504a289362411c90`
- `tests/test_prospectus_materialise.py` SHA256 `564cda3cc99cfc16b6ca3172c10c2224abe2516016fbc9c1c35e71cc95c960ca`

## Prerequisites read

Complete task brief, exact Phase6 SPEC, shared ingestion SPEC, owner `.claude/agents/extractor-implementer.md`, exact Claude S implementer template (Markdown only), Codex TDD SKILL and writing-good-tests reference read. SourceSpan/governance, generator, prerequisite resolver/classifier, cycle detector and ledger applicability implementation inspected. System Python 3.13 only, process-only worktree PYTHONPATH, bytecode/cache disabled, offline flags, unique external basetemps. Import origin asserted for prerequisites and compiler test wrapper asserts worktree origin.

## Actual verification

### RED first

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_red_20261011_0311' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-red.log'
$testExit=$LASTEXITCODE
```

44 failed, exit 1. Five fixture calls also had an incorrect make_entry keyword; corrected before final RED.

### RED corrected

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_red_corrected_20261011_0312' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-red-corrected.log'
$testExit=$LASTEXITCODE
```

44 failed, exit 1, absent new rule_candidates module.

### First implementation attempt / compatibility reproduction

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_materialise.py::test_extractor_never_emits_reviewed_empty' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_attempt_20261011_0314' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-green-attempt.log'
$testExit=$LASTEXITCODE
```

45 failed, exit 1. Compiler syntax typo; exact authorized static writer assertion failed on new consumer.

### Bounded checkpoint

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_materialise.py' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_bounded_20261011_0315' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-bounded.log'
$testExit=$LASTEXITCODE
```

3 failed, 76 passed, exit 1. Syntax and materialise scan corrected. No GREEN claim.


Final `git diff --check` exit 0. Final Git scope: one modified existing materialise test and exactly three untracked allowed files. New files are unstaged, so root must include their own whitespace/scope checks. No broad suite, corpus checks, staging/archive or independent review was run.

## Remaining failed expectations / resumable next actions

1. `test_supported_views_are_inactive_and_match_supported_generator_values`: expected pending approval incorrectly; actual governed initial approval state is `not_requested`. Compiler inherits it unchanged. Reconcile test expectation with authoritative contract.
2. `test_raw_semantics_remain_distinct[co-requisite: CS 1-unreadable]`: existing resolver/classifier returns `unresolved_reference`, preserving raw co-requisite and blockers. Decide whether retaining this existing state plus explicit co-requisite blocker is desired; current output blocks it.
3. `test_raw_semantics_remain_distinct[not required — ²-unreadable]`: existing resolver/classifier returns `unresolved_reference`, not unreadable. Raw Unicode/negation is retained. Add a genuinely ambiguous-cell unreadable case when continuing.

Role instruction says stop/report when expected result differs, rather than adapting tests silently. Therefore this checkpoint leaves all three failures visible. No test was removed or weakened. Earlier OR fixture was corrected to avoid including its own course, which must globally refuse self edges; updated fixture uses `CS 1 or XX999`.

Next session: reconcile these expectations, add missing malformed-container/year/semester/reference coverage and actual producer pending-payload interop; check stable identity of review refs/time/path and span collection reordering against exact spec. Then run focused compiler plus minimal existing prerequisite/generator/contract tests. Do not claim implementation complete merely from current 76 passing checks. Compiler source code has not had independent review; hidden gaps remain possible.

## Usage and stop

Exact external READ_ONLY_CODEX_USAGE.ps1 read completely and executed three times, restoring worktree cwd each time: primary 74/secondary25 at03:06:14; 78/26 at03:09:03; 80/26 at03:10:53; 81/26 at03:11:34 Manila (four samples including latest). Stopped at natural bounded-test boundary to conserve root recovery quota. No pending test/tool process.

Skipped broad suite/corpus/runtime/reviews/commits as required; draft is incomplete and must not be treated as accepted or active.

## Narrow coordinator clarification and GREEN follow-up

Coordinator resolved all three invented fixture expectations after the checkpoint: register initial approval is not_requested; co-requisite and negated/superscript examples honestly recompute to unresolved_reference, with exact raw text retained, blockers present and no supported prerequisite view. Only these three literal expectations changed. No production edit followed that checkpoint.

Exact final command (same process prefix above):

```powershell
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_materialise.py' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_green_20261011_0317' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-green.log'
```

Actual result: 79 passed, exit 0 (44 new compiler tests +35 existing materialise tests). Earlier failed outcomes remain above as history, now resolved. Status remains resumable implementation checkpoint, not independently accepted/reviewed or complete against all planned coverage. Minimal existing generator/prerequisite/source-contract verification and noted coverage follow-up remain. No staged files/commit/archive/reviews. Latest usage JSON sampled again after final GREEN; root has exact external timestamp/percentages. No pendingprocess.

## Coordinator local draft checkpoint
Root independently verified candidate importorigins and ran compiler+materialise+test_contracts_source+existing authority prerequisite-classification/generator-status nodes:185passed/exit0; phase6-task-1-root-checkpoint.log. Exact4path stage/diffcheck passed; localdraftcommit84eba1c4e14c615d03cfbf854e61ffbba9599e19; cleanworktree/ownerFOUR/pins preserved; frozen376files phase6-task-1-review-84eba1c4. This captures tested work under owner localdraftcommit authorization, NOTtaskacceptance/completion: above missingcoverage/interop andfreshSpec/Standards remain. Actualscopehashes phase6-task-1-root-checkpoint-scope.json. Quota83%/27%03:15Manila; earlyrecoverycheckpoint, no independentreviewstarted.

# Continuation completion — 2026-10-11

Status: IMPLEMENTER DONE, pending root acceptance/commit and fresh independent specification then standards review. Earlier checkpoint limitations and failed expectations above are historical; the three original fixture mismatches were already resolved before this continuation. No self-review or independent review was performed by the implementer.

Started from verified clean checkpoint `84eba1c4e14c615d03cfbf854e61ffbba9599e19`, whole-task base `8cdb8cfdce03c69f718bb63390903b484437112a`. Read the complete continuation, original brief and report. No staging, commits, descendants, protected module edits, dependencies, owner writes, network/converter downloads or runtime integration. All tests used system Python3.13-B, process-only worktree PYTHONPATH/offline/no-bytecode flags, explicit rootdir/confcutdir and unique external no-cache basetemps.

## Reproduced defects and focused repairs

- Malformed provenance/anomaly collections and authority container shapes now refuse consistently before an artifact returns.
- Nested run/source-record identity claims bind exact version/edition/document/namespace/digest. Normalized activation and completeness claims, forged nested identity/content review and privileged ledger fields refuse.
- Actual pending producer authority, metadata observation and audit diagnostics are accepted at exact known paths, without stripping fields or promoting source state. A real synthetic converter drives actual producer -> checked candidate-bundle public loader -> pure compiler; absent field support leaves all records inactive and blocked. No Task3 bridge was implemented.
- Evidence span/locator collections sort deterministically. Complete corroborating spans support the same printed field without treating repeated evidence as duplicated semantic text.
- Actual ledger refs remain intact; semantic ID/content_digest project applicable reviewer/reason/hash/locator/field/disposition/values and omit timestamp-derived reference hashes and display section paths. Changing a genuine reviewer reason changes semantic identity; recording-time/path-only changes do not. Ordered prerequisite values and exact raw text stay intact. ADR explains semantic digest versus serialized artifact integrity.
- Blocking unsupported records no longer excuses malformed term/elective/program field types or numbers. Unsupported root program fields remain visible as blocked `payload_fields`.
- Exact Decimal evidence comparison fixes reproduced false support when float rounding converted a tiny printed nonzero to zero or erased extra decimal precision. Missing numeric facts still remain unknown; supported printed zero stays supported.

Coverage also verifies genuine ambiguous unreadable blanks, explicit none/blank/recorded accepted blank, stale/foreign/field/locator/latest-decision review matching, preserved unknown XX999, filtered printed self edges, all-of order and /L course syntax, Unicode/raw text, input immutability and poisoned file/network/subprocess/in-process Prolog boundaries.

## Exact continuation commands and results

### Continuation RED

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py'  --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_resume_red_1109' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-resume-red.log'
$testExit=$LASTEXITCODE
```

Actual: 13 failed, 94 passed, exit 1.

### Strengthened malformed-code RED

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py::test_forged_source_or_activation_claims_refuse[malformed_code]'  --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_code_red_1112' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-code-red.log'
$testExit=$LASTEXITCODE
```

Actual: 1 failed, exit 1.

### Continuation GREEN

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py'  --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_resume_green_1114' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-resume-green.log'
$testExit=$LASTEXITCODE
```

Actual: 107 passed, exit 0.

### Blocked-data/authority RED

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py' -k 'blocked_records_do_not or semantic_review_change or unknown_source_supported or cannot_reach_inprocess' --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_tail_red_1120' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-tail-red.log'
$testExit=$LASTEXITCODE
```

Actual: 11 failed, 4 passed, 107 deselected, exit 1.

### Blocked-data/authority GREEN

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py' -k 'blocked_records_do_not or semantic_review_change or unknown_source_supported or cannot_reach_inprocess' --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_tail_green_1122' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-tail-green.log'
$testExit=$LASTEXITCODE
```

Actual: 15 passed, 107 deselected, exit 0.

### Numeric/program RED

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py' -k 'root_program_values or numeric_field_support' --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_numeric_red_1124' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-numeric-red.log'
$testExit=$LASTEXITCODE
```

Actual: 3 failed, 122 deselected, exit 1.

### Numeric/program GREEN

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py' -k 'root_program_values or numeric_field_support' --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_numeric_green_1126' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-numeric-green.log'
$testExit=$LASTEXITCODE
```

Actual: 3 passed, 122 deselected, exit 0.

### Final required focused GREEN

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_materialise.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_contracts_source.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_authority.py::test_prerequisite_state_of_one_course' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_authority.py::test_prolog_and_essentials_status_name_the_extraction_not_a_verification' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_ingestion.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_candidate_bundle.py'  --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_final_1128' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-final-green.log'
$testExit=$LASTEXITCODE
```

Actual: 346 passed, exit 0 in 32.96 seconds.


Final import-origin check explicitly asserted compiler, producer, checked-bundle and source-contract origins within the candidate worktree before pytest. Source verification is synthetic; generated JSON is never a source-of-truth oracle. RED logs include an installed Docling preset registration ERROR during first real producer import; synthetic conversion succeeded and no download ran. Final focused GREEN output is clean (346 passed).

## Final scope, hashes and handoff

HEAD unchanged `84eba1c4e14c615d03cfbf854e61ffbba9599e19`; empty index; zero untracked files; continuation modifies only compiler/test/ADR; whole-task BASE-to-worktree diff is exactly the four authorized paths. `git diff --check` exit0. The conditional materialise scanner adjustment remains the checkpoint version and all35 materialise tests pass. Protected source/contracts/producer/loader/extractor files are unchanged. Full machine-readable evidence: `phase6-task-1-continuation-final-scope.json`.

- `backend/bintanong_tools/prospectus_extractor/rule_candidates.py` SHA256 `8b1c57d50f1c6531fb979b96f0b170cd50626f81eb2e0d2d688b61f0d952527c`
- `tests/test_rule_candidates.py` SHA256 `cf3624624b615431f5a73d416e7e6a6b204bc1357279750d3dc88d8e9e9ab34f`
- `docs/decisions/phase-06-prospectus-candidates.md` SHA256 `f7cb650c2761b2aa57387775e786e89ad73447d5ec6d214672a775a5b13e843b`
- `tests/test_prospectus_materialise.py` SHA256 `564cda3cc99cfc16b6ca3172c10c2224abe2516016fbc9c1c35e71cc95c960ca`

Actual quota snapshots this continuation:28%/32%11:06:50;33%/32%11:10:20;40%/33%11:19:20;41%/34%11:20:42; final snapshot is in scope JSON. Exact READ_ONLY_CODEX_USAGE.ps1 used, candidate cwd restored after every call. No pending tool/test process.

Skipped the broad4k suite, original-corpus/domain accuracy, release/runtime tests and independent reviews as required. Output is inactive candidate preparation; it confers no approval, activation, eligibility or phase advancement. Root owns acceptance, commit/freeze and separate fresh review seats.

## Root acceptance and full-task freeze
Phase6 worker/root346PASSexit0 after remainingadversarial+actualproducerinterop, exact4scope/ownerFOUR/pins/dev/origin-dev/hash/index/diffchecks0. Localfollowupcommit01d1d48b4b17fea59853a354fdfdf8800cf82bd7; fullPhase6BASE8cdb8cfd..01d1d48b frozen376files. Fresh independent /root/phase6_task1_spec gpt-6.1-sol/high active; Standardsnotstarted. Rootinitialimportharnessmistakenly imported helpermaterialise asmodule; corrected toledger beforetests, failurelogretained; no productfix. Fresh46%/34%11:24Manila.

# P6-S1 confirmed Medium repair — 2026-10-11

Status: IMPLEMENTER REPAIR DONE; initial independent Spec verdict remains FAIL until an owner-authorized independent repair recheck. No review/recheck or clearance is claimed here. Root owns acceptance, commit and freeze. The Medium finding does not itself authorize a recheck; owner exception remains required.

Read the complete initial Spec report and external reproducer. Verified clean repair base `01d1d48b4b17fea59853a354fdfdf8800cf82bd7`. Carried the exact accepted-blank two-cell locator reversal into `tests/test_rule_candidates.py::test_accepted_blank_locator_id_order_is_not_semantic`, strengthening assertions for original/reference ID retention, supported view equality and input immutability. RED reproduced the reported state mismatch before compiler edits.

Minimal compiler repair: after `entry_problem` validates the original entry/hash, deep-copy the entry, sort only copied locator cell IDs and pass that copy to existing applicability/latest-decision helpers. The original entry ID is preserved for returned lookup references; copied canonical locator is used for comparison and semantic projection. No entry is rehashed after normalization; source/field/current-value/unique-locator checks and ledger decision order remain intact. ADR adds one paragraph explaining validation-before-normalization and original reference retention. Shared ledger/contracts/extractor unchanged.

Compiler/ledger worktree import origins asserted before RED. Actual Codex read-only quota58%primary/36%weekly at11:32:27Manila, cwd restored after helper. No pendingprocess, staging, commits, descendants or self-review.

### P6-S1 RED

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py::test_accepted_blank_locator_id_order_is_not_semantic' --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_p6s1_red_1134' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-p6s1-red.log'
$testExit=$LASTEXITCODE
```

Actual: 1 failed in0.44s; actual exit1, original reviewed_empty versus reordered blank_unreviewed.

### P6-S1 focused GREEN

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py::test_accepted_blank_locator_id_order_is_not_semantic' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py::test_recorded_blank_review_reuses_applicable_ledger_semantics' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py::test_blank_review_must_match_exact_current_field_source_and_latest_decision' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py::test_genuine_ambiguous_blank_cannot_be_promoted_by_accepted_review' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py::test_review_timestamp_and_local_path_do_not_change_candidate_semantic_hashes' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py::test_semantic_review_change_changes_identity_without_changing_source_states' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_materialise.py' --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' -q -p no:cacheprovider --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/pytest_phase6_p6s1_green_1135' *> 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/phase6-task-1-p6s1-green.log'
$testExit=$LASTEXITCODE
```

Actual: 48 passed in0.86s; actual exit0.


Focused GREEN includes the new regression, five genuinely adjacent compiler review matching/hash cases (with parameters) and all35 existing materialise tests:48 total. Full346-test rerun and unrelated batches were not performed for this minimal repair. The external reproducer still targets the frozen original failing archive; its scenario is now retained as the local regression rather than rewriting independent evidence.

Repair scope: exactly3 authorized paths, HEAD unchanged, empty index, zero untracked files and `git diff --check` exit0. Machine evidence: `phase6-task-1-p6s1-repair-scope.json`.

- `backend/bintanong_tools/prospectus_extractor/rule_candidates.py` SHA256 `408c7500aacba74f597ba6c49fe854ad3e79e92adf2a2961c985e16f3c65e1e2`
- `docs/decisions/phase-06-prospectus-candidates.md` SHA256 `5417a42ed26ce23e52850591b674ed8f9feb63ecbd8092ff3a015d0ae63b1887`
- `tests/test_rule_candidates.py` SHA256 `e0d96b4415e72a65fc071d6e07b98e5205aeb3489e9da0081775580a9d7fc14f`

Skipped independent recheck/reviews and broad/corpus/runtime checks as instructed. All output remains inactive; no authority, review verdict or institutional state was advanced.

## Root P6-S1 repair acceptance and review gate
Phase6MediumP6-S1 repair6f9a3ec5b5df8b44a5d42a1d7358dee7f68c8dd8 worker/root48PASSexit0; validatedledgercopynormalization retainsoriginalIDs; exact3pathstage/diffchecks0; cleanHEAD/frozen376. Owner ONE scopedMediumSpec exceptionREQUESTED_PENDING/used0 afterconcretefixready. InitialSpecFAIL remains; StandardsNOTSTARTED/Task3NOTSTARTED. FullPhase6patch8cdb8cfd..6f9a3ec5 saved. Freshall24Git/pins/dev/origin-dev/ownerFOUR preserved; Alienista bothclean11:26readonly. Allchildrenfinished/nopendingprocessknown. Quota61%primary37%weekly11:35Manila, belowstop; wait is owner review rule, notquota.
