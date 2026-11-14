# Unified Task 3 implementer report

Status: DONE, pending root acceptance and independent Spec then Standards review.

Parent: `6f9a3ec5b5df8b44a5d42a1d7358dee7f68c8dd8`; clean worktree verified before implementation. The brief's `57b5985` is historical delivery context, not this task's parent. No staging, commits, descendants, self-review, owner checkout writes or protected-path changes. Root owns acceptance, commit, freeze and reviews.

## Delivered scope

- NEW `backend/bintanong_tools/document_ingest/prospectus_rules.py`: `prepare_rule_candidates(Path) -> dict[str, Any]`, checked prospectus-only bundle to existing pure compiler artifact in memory.
- NEW `tests/test_prospectus_rule_handoff.py`: 36 focused synthetic cases, including actual snapshot/converter -> producer/parser/audit -> checked loader -> bridge -> compiler acceptance.
- EXTEND `docs/decisions/phase-02-unified-ingestion.md`: actual evidence mapping, inactive/review boundaries, limitations, external-bundle library command and stable synthetic acceptance node.

The bridge reuses evidence_adapter, actual parser anomalies/footnotes, existing column layout and section/FieldCandidate ownership helpers. It checks retained row source locators, validates supplied cell records against raw normalized cells, refuses unrelated/foreign/malformed ownership, and supplies individual field cells rather than row/chunk unions. SourceSpan parsing/binding uses the exact selected register version, captured metadata page sizes and native bbox origin. Missing or ambiguous evidence, unlocatable cells and semantic repairs stay blocked. Units.total can cite a complete printed unit cell; inferred lecture/lab zeros and derived category/term fields cannot. Year/semester require exact direct wording. Raw cell wording is retained on spans; mismatched repaired candidate wording cannot borrow another row's matching cell.

The compiler artifact is returned unchanged. Every record remains inactive with null approval; unresolved XX999 remains source-supported but blocked. Optional existing checked payload.review_evidence is forwarded to the existing compiler's ledger checks. Normal producer output has no ledger entries, so blank prerequisites stay blank_unreviewed; counts/status never confer review. Applicable accepted-blank decisions retain existing compiler refs. Other correction decisions remain in the captured review inputs; this bridge does not materialize corrections, change schemas or introduce separate review truth.

## Read and preflight evidence

Read COMPLETE D/unified-task-3-brief.md, unified_ingestion_design/SPEC.md and IMPLEMENTATION_PLAN.md, phase6_prologifier/SPEC.md, owner extractor-implementer.md and Claude implementer-prompt.md as Markdown only, and Codex test-driven-development/SKILL.md plus writing-good-tests.md. Read actual producer/bundle/compiler, source contracts, loader/evidence/parse/sections/layout/units/courses/ledger/pipeline and relevant existing tests. User/dispatch system-Python and focused-test constraints supersede the historical extractor agent's uv suggestion and skill's broad-suite suggestion.

Every PowerShell invocation first selected R; all file paths and pytest root/confcutdir/basetemp paths were absolute. Python used system py -3.13 -B. Test processes set PYTHONPATH=R, no-bytecode/offline flags and checked module origins before pytest. READ_ONLY_CODEX_USAGE.ps1 was read fully before execution and R restored afterwards. Usage RPC snapshots: 12:09:51 Manila 18% primary/3% weekly; 12:23:54 Manila 29% primary/5% weekly. Both allowed continued work. No installs, downloads, dependencies/lockfiles/global settings, API/Docker, routing, embeddings, Prolog execution or actual private inputs.

## Actual tests, exits and commands

All commands below include the actual process-only environment, explicit roots and unique external basetemp used. The module-origin commands immediately preceding them succeeded (exit0): initial RED verified bundle.py under R; later runs verified prospectus_rules.py and/or rule_candidates.py; final focused run verified prospectus_rules, producer, bundle and compiler under R.

### RED1: exit 1

33 failed in 30.68s; all failed on the explicit missing-feature assertion after real producer success.

```powershell
Set-Location 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'; py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_rule_handoff.py' -q -p no:cacheprovider --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests' --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-red-20261011-1219' 2>&1 | Tee-Object -FilePath 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-3-red.log'; exit $LASTEXITCODE
```

### RED2: exit 1

2 failed, 33 deselected in 26.53s; both explicit missing-feature assertions, before implementation.

```powershell
Set-Location 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'; py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_rule_handoff.py' -k 'overlapping_cells or semantic_repair' -q -p no:cacheprovider --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests' --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-red2-20261011-1224' 2>&1 | Tee-Object -FilePath 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-3-red2.log'; exit $LASTEXITCODE
```

### GREEN1: exit 0

35 passed in 31.55s.

```powershell
Set-Location 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'; py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_rule_handoff.py' -q -p no:cacheprovider --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests' --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-green1-20261011-1232' 2>&1 | Tee-Object -FilePath 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-3-green1.log'; exit $LASTEXITCODE
```

### RED3: exit 1

1 failed, 35 deselected in 23.85s; reproduced unchecked TypeError for list-valued source cell ID instead of required deliberate ValueError. Fixed by validating the ID before the dictionary lookup using the existing bridge ID validator.

```powershell
Set-Location 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'; py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_rule_handoff.py' -k nontext_cell_id -q -p no:cacheprovider --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests' --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-red3-20261011-1237' 2>&1 | Tee-Object -FilePath 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-3-red3.log'; exit $LASTEXITCODE
```

### GREEN focused: exit 0

242 passed in 44.19s; includes all 36 handoff cases and the combined synthetic end-to-end case.

```powershell
Set-Location 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'; py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_rule_handoff.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_ingestion.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_candidate_bundle.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py' -q -p no:cacheprovider --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests' --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-green-focused-20261011-1240' 2>&1 | Tee-Object -FilePath 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-3-green-focused.log'; exit $LASTEXITCODE
```

Module-origin assertions actually used before the runs (each in the same prefixed PowerShell process, before pytest):

```powershell
py -3.13 -B -c "import pathlib,backend.bintanong_tools.document_ingest.bundle as b; assert pathlib.Path(b.__file__).resolve().is_relative_to(pathlib.Path(r'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010')); print(b.__file__)"
# RED2 used the same assertion without the print.
py -3.13 -B -c "import pathlib,backend.bintanong_tools.document_ingest.prospectus_rules as b,backend.bintanong_tools.prospectus_extractor.rule_candidates as c; r=pathlib.Path(r'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'); assert all(pathlib.Path(m.__file__).resolve().is_relative_to(r) for m in (b,c)); print(b.__file__); print(c.__file__)"
py -3.13 -B -c "import pathlib,backend.bintanong_tools.document_ingest.prospectus_rules as b; assert pathlib.Path(b.__file__).resolve().is_relative_to(pathlib.Path(r'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'))"
py -3.13 -B -c "import pathlib,backend.bintanong_tools.document_ingest.prospectus_rules as b,backend.bintanong_tools.document_ingest.prospectus as p,backend.bintanong_tools.document_ingest.bundle as l,backend.bintanong_tools.prospectus_extractor.rule_candidates as c; r=pathlib.Path(r'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'); assert all(pathlib.Path(m.__file__).resolve().is_relative_to(r) for m in (b,p,l,c)); print('four module origins verified')"
```

Each origin assertion was followed by `if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }`. No collection/import failure was accepted as feature RED. RED1/2 were missing-feature assertion failures. RED3 was a new adversarial malformed-input regression; final focused GREEN includes its fix.

`git diff --check` exited0. Git reported only a line-ending conversion warning for the existing decision Markdown, with no whitespace error. `git status --short` showed exactly the three allowed paths. Final scope/hash verification is recorded in unified-task-3-scope-hashes.json. No commit hash: staging and commits deliberately belong to root.

The installed Docling import logged `Preset 'granite_vision_v4' already registered for ChartExtractionVlmEngineOptions` in captured first-test RED logs. This was not a failing assertion or a bridge warning; final focused result was clean exit0 with all242 cases passing. No installed dependency was changed to suppress it.

## Scope hashes

- `backend/bintanong_tools/document_ingest/prospectus_rules.py`: SHA256 `8a22f4289b3f2cdfaca5f6e0fd3e7dbdaa62f3aa02789efa06e1aba555962f45`, 168 lines.
- `tests/test_prospectus_rule_handoff.py`: SHA256 `d117e8e00e519fbd431cb2ac7b1ca4b4274d529162ea67e326469c832c91ce39`, 265 lines.
- `docs/decisions/phase-02-unified-ingestion.md`: SHA256 `d3b87333d43cc6ef9f86863b786d2d76554e4c404e1044eb47a059d1a4b22a94`, 207 lines.

## Limitations and skipped checks

The tests use public synthetic PDF bytes and a synthetic converter seam while exercising actual existing extraction/publication/consumer/compiler code. They do not certify original prospectus accuracy, issuing-office/domain/source authorization, OCR accuracy, phone-photo behavior or private lifecycle. No original/private corpus, broad4k suite, mutation campaign, runtime/Janus/Prolog/release/network test or institutional activation was run. The root's refreshed authoritative reference files were not changed. No descendant/self-review/staging/commit/freeze was performed.

The bridge deliberately blocks unsupported normalized/derived wording, default unit splits and semantic repairs. Existing parser helpers are reused privately because public parsing drops FieldCandidates; future extractor helper changes need this focused suite. Captured bundle hashes and unsigned local ledger entries check consistency, not authenticity against a malicious producer capable of replacing all artifacts and hashes. Other correction records remain review inputs; only existing compiler-supported accepted-blank refs enter its current output. No feature-completion percentage or source/content approval is claimed.

Historical M1/F/session review debts remain separate. Root has queued the separately authorized M1 Standards exception after this worker; this task did not recheck M1.

## Root acceptance and checkpoint
Root module origins verified5;242PASS40.48s actualexit0. Exact3pathworker hashes, cleanindex, parent6f9a3ec5 and ownerFOURbyte/status/HEAD unchanged; gitdiffcheck0. Explicit3pathstage and localcommit12d5e373aaba2a2ec43e7a2624fa1e1a84af4a50;378file frozen packageunified-task-3-review-12d5e373. InitialindependentSpec/Standards pending. Rootlogtask3-root-acceptance.log.


# T3-S1 bounded implementer repair

Status: DONE with focused implementation verification; independent Spec repair recheck and Standards remain pending. No review PASS is claimed. Root must obtain the newly required Medium Spec-recheck exception after tested/committed/frozen repair; this worker did not review/recheck its fix.

Repair parent: `12d5e373aaba2a2ec43e7a2624fa1e1a84af4a50`, verified clean before edits. Read COMPLETE unified-task-3-spec.md and the original immutable task3-spec-adversarial.py. The original external script and existing Spec artifacts were not edited or run as a repair review; the exact failing behavior was persisted in the allowed test module and run against the current worktree.

## Root cause and minimal bridge repair

The compiler intentionally trusts the caller's accepted-blank field binding. The bridge previously validated ledger current-value consistency but did not bind accepted blankness to the untouched captured raw prerequisite field. A candidate changed to prerequisites_raw empty and prerequisite_state reviewed_empty could therefore erase printed CS102 with a valid current accepted-blank ledger entry.

The repair stays within the same three authorized paths. It reuses the existing compiler `_review_decisions` validator for source/version/hash/ledger/privileged-claim checks, then filters accepted-blank entries individually. A retained accepted-blank decision now requires the complete exact regenerated course owner/provenance, its actual layout/row prerequisite column, one genuinely blank owned cell, and locatable source geometry. Existing `_field_spans`/SourceSpan validation checks blank-cell geometry/binding through a private allow_blank flag; those blank spans are never supplied to the compiler. Missing, ambiguous, unlocatable and semantic-repair ownership cannot gain usable support. Valid unrelated review entries are retained individually rather than dropping the whole wrapper. No new review truth, parser, dependency, protected API change or correction materialization was added.

The exact persisted T3-S1 regression leaves the retained raw t0-c9 printing CS102 and its provenance/source unchanged; edits the candidate to reviewed_empty plus empty prerequisite containers; records a valid current accepted-blank ledger; rehashes both manifests; and explicitly asserts checked-loader acceptance before invoking the bridge. The blank_unreviewed variant is deliberately not used because it would refuse before reaching the defect. Five adjacent cases cover missing row-field provenance, duplicate blank field cells, semantic repair, missing blank geometry and absence of a prerequisite cell in this row while another course has a valid blank. Each asserts the unrelated CS102 accepted-blank reference survives. Existing normal genuine-blank ledger cases and the XX999 combined synthetic E2E remain passing.

## Actual RED/GREEN

- Repair RED against12d5: actual exit1, **5 failed, 1 passed, 36 deselected in27.16s**. The exact printed-CS102 regression and missing/ambiguous/unlocatable/other-course blank cases failed on blockerless review output. The semantic-repair variant already blocked through missing course identity and passed while preserving the valid other course. Log: unified-task-3-repair-red.log.
- Repair focused GREEN: actual exit0, **248 passed in41.58s** across handoff (42 cases), producer, checked bundle and pure compiler modules. Log: unified-task-3-repair-green.log. No additional test batch was run after this GREEN.

Exact test commands (origin assertions below ran immediately before pytest, with if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }):

```powershell
Set-Location 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'; py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_rule_handoff.py' -k 'changed_nonblank_source or unsupported_blank_keeps' -q -p no:cacheprovider --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests' --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-repair-red-20261011-1253' 2>&1 | Tee-Object -FilePath 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-3-repair-red.log'; exit $LASTEXITCODE
```

```powershell
Set-Location 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONPATH='C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'; $env:HF_DATASETS_OFFLINE='1'; py -3.13 -B -m pytest 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_rule_handoff.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_prospectus_ingestion.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_candidate_bundle.py' 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests/test_rule_candidates.py' -q -p no:cacheprovider --rootdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010' --confcutdir 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010/tests' --basetemp 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/task3-repair-green-20261011-1300' 2>&1 | Tee-Object -FilePath 'E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011/unified-task-3-repair-green.log'; exit $LASTEXITCODE
```

Origin assertions, actual exit0 each:

```powershell
py -3.13 -B -c "import pathlib,backend.bintanong_tools.document_ingest.prospectus_rules as b; assert pathlib.Path(b.__file__).resolve().is_relative_to(pathlib.Path(r'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'))"
py -3.13 -B -c "import pathlib,backend.bintanong_tools.document_ingest.prospectus_rules as b,backend.bintanong_tools.document_ingest.prospectus as p,backend.bintanong_tools.document_ingest.bundle as l,backend.bintanong_tools.prospectus_extractor.rule_candidates as c; r=pathlib.Path(r'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'); assert all(pathlib.Path(m.__file__).resolve().is_relative_to(r) for m in (b,p,l,c)); print('four module origins verified')"
```

Every PowerShell first selected R; login:false, system py -3.13-B, process-only PYTHONPATH=R/no-bytecode/offline, no pytest cache, explicit absolute root/confcutdir and unique external basetemp. Usage helper was already fully read and was executed with R restored afterwards. Fresh actual usage:12:48:52 Manila58%primary9%weekly;12:52:54 Manila61%primary10%weekly. Stop/save thresholds were not approached.

`git diff --check` exited0, with only expected Git LF-to-CRLF conversion notices. `git status --short` contains exactly the same authorized three paths. Scope hashes were saved to unified-task-3-repair-scope-hashes.json; original initial implementation hashes remain unchanged in their earlier report/JSON as historical evidence.

- `backend/bintanong_tools/document_ingest/prospectus_rules.py`: SHA256 `429315053f2d90fbba47c2ead9f57be4e2ab292709826bc07c7a692b34f33f21`, 204 lines.
- `tests/test_prospectus_rule_handoff.py`: SHA256 `9b558ba6fc635062ce3d9990a6f1fa0f38c77554a1281f1b265723bd7b43b5a3`, 327 lines.
- `docs/decisions/phase-02-unified-ingestion.md`: SHA256 `4e2bf02160f3129a835ffd8b0ffe1c679197d3ffd6ab2f8865c1cb597fbcf505`, 216 lines.

Original external adversarial script current SHA256: `661f791f0b0f36432e01443e8c06b69b352d7967fe0d666d8302d87f7168c03e`. It was read only; no old review artifact was modified.

No stage, commit, descendants, self-review, owner writes, dependencies/locks/config changes, API/Docker, network/runtime/Prolog execution or real private inputs. Root handles acceptance, commit/freeze and any authorized independent recheck. Broad suite, original-corpus/OCR/private-lifecycle/human/domain/source approval/runtime/release/mutation checks remain skipped as dispatched. The repair proves synthetic reviewed-blank binding behavior; it does not authenticate a malicious producer or establish institutional source accuracy/approval. Historical M1/F/session debts stay separate.

## Root repair acceptance and freeze
Root248PASS42.47s actualexit0; fourmoduleoriginsverified. Exactrepair3pathhashes/cleanindex/parent/originalreprohash/ownerFOURbytes/status/devHEADpreserved. Explicit3pathstage/localcommit5596f810c4d08c7aef87503d06c0027d6b961a4b; clean378filefreeze unified-task-3-review-5596f810, repairBASE12d5e373; wholeTask3patch6f9a3ec5..5596f810 saved. ONE newMediumSpecexceptionREQUESTED_PENDING, notyetauthorized/used; independentSpecFAILremains/StandardsNOTRUN.
