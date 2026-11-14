# M01 bounded recovery result

Status: DONE for the assigned scratch reproduction and regression. Independent Spec and Standards reviews and the root full gate remain pending. No production repair was needed or made. No commit was created.

## Pins and scope

- Source: `dd699958505996358864383ff9c184cb98aec985`; baseline: `0caeaba8d8221a0f75b154e94bc3167b780f1407`.
- `git get-tar-commit-id` verified both archive pins. All 351 source and 342 baseline extracted files matched their archive bytes before tests and at completion. No extra files appeared in either pinned tree.
- The original and mutant import probes each asserted that `prospectus` and `pipeline` loaded from their respective scratch tree. See `pins_and_original_imports.json` and `mutation_m01.json`.
- `mutant_m01/` differs from `pinned_tip/` in exactly `backend/bintanong_tools/prospectus.py`:262, replacing the one adapter digest check with `pass`. `final_tree_integrity.json` confirms the only changed file; `mutation_m01.diff` records the edit.
- Archive source uses CRLF. The first raw LF-only pattern assertion failed before mutation, exit 1. The successful edit verified one match of the requested logical LF pattern and preserved CRLF while replacing only that line. This was a harness newline correction, not a test or production correction.
- Final read-only Git check: `draft-f` still at the source pin with clean status. The owner checkout, other worktrees and refs were not written.

## Fresh results

All tests ran through system Python 3.13.12, with `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, a fresh external `--basetemp`, and cwd equal to the tree being tested. Every test log begins with its exact command and cwd; every exit is preserved separately.

| Run | Result | Pytest exit | Log |
| --- | --- | --- | --- |
| Original six focused files | 96 passed, 2 warnings, 18.79s | 0 | `focused_original.log` |
| M01, same unchanged six files | 96 passed, 2 warnings, 17.93s | 0 | `focused_mutant_original_tests.log` |
| Standalone boundary regression against M01 | 1 failed, 0.47s | 1 | `boundary_mutant_red.log` |
| Original six files plus standalone regression | 97 passed, 2 warnings, 17.83s | 0 | `focused_original_with_boundary_green.log` |

The two focused warnings are installed Typer/Click deprecations. The expected RED failed at standalone test line 28: the mismatched PDF had entered the real extractor call. It did not fail through collection, missing dependencies, a fabricated exception or altered downstream validation.

## Classification and regression

Classification: **later-guard masking of a defense-in-depth adapter coverage gap**. The harness used the correct mutant. No mismatch-to-conversion/output invariant bypass was reproduced.

The original test at `pinned_tip/tests/test_prospectus_candidate_run.py`:29 observes `load_document_result` through `fake_conversion`. In current production, `pipeline.py`:350 checks the same captured digest before `mkdir` at line 356 and before that loader. Removing the adapter check consequently preserves the tested rejection/no-conversion/no-output behavior; this explains the surviving unchanged suite.

The adapter additionally promises refusal before handing the input to the extractor (`prospectus.py`:237-241,262-263; plan Task 4 and mutation step). The new standalone `test_prospectus_adapter_digest_boundary.py` exercises that ordering with a wrapper which records entry and delegates to the unchanged real `process_prospectus`. It keeps both digest implementations, snapshot handling and pipeline guard real. It asserts refusal, zero extractor entry and no output parent. Removing the adapter check fails that observable boundary promise even though the pipeline still refuses safely.

Only this add-only regression is proposed; `regression_test.diff` is its reviewable patch. Neither existing tests nor production code in `pinned_tip` were changed. This result does not establish any total mutation score, including 52/52.

## Next root gate and reviews

Full-run and review the unchanged Phase F tree plus this absolute standalone test:

`E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\m01_recovery\test_prospectus_adapter_digest_boundary.py`

Review evidence is in this same directory, with the unchanged pinned source in `pinned_tip/` and isolated M01 in `mutant_m01/`. The root may run the full worktree suite plus the external standalone test to retain repository metadata assumptions. Expected count from the known unchanged full count plus this one test is 4134, subject to actual root verification.

NOT RUN by this implementer: broad full suite, other mutants, self-review or independent reviews, real Docling/institution PDF conversion, Docker, dependency/environment changes, API integration, embeddings, Prolog or routing. All historical mutation evidence was left untouched.
