# Unified Task 2 scoped independent SPEC repair recheck

**PASS — APPROVED. M-T2-S1: ADDRESSED. Confirmed findings/new fix-diff breakage: NONE.**

This is the ONE owner-authorized Medium Spec repair recheck recorded in AUTHORIZATION.json. Scope exactly `361b5ad41af7d5f202a8152edc0ae989c171f2a2..8cdb8cfdce03c69f718bb63390903b484437112a`, frozen package `unified-task-2-review-8cdb8cfd`. It grants no adoption, merge, source/content approval, institutional use or activation. Separate Standards may now start; this reviewer did not perform Standards.

## Requirement and actual correction

Read review-common.md completely first, then its exact extractor-reviewer/spec-reviewer Markdown templates, AUTHORIZATION.json, prior unified-task-2-spec.md, complete Task2 brief, source SPEC.md and IMPLEMENTATION_PLAN.md. Read actual fix patch, changed source/test and interacting loader/factory/identity helpers. Implementer repair report (appended to unified-task-2-report.md) was context only.

The default path now calls `_converter_settings(active, settings)` at prospectus.py:251-252 before conversion. The helper requires introspectable options for this factory path and compares backend, tracked pipeline options, enabled OCR languages and installed Docling package versions with the declared settings. `_StrictConverter.convert` repeats the same shared verification at :139-140 after conversion returns and before returning its result to the loader. The protected loader's raw export at loader.py:471 follows its `active.convert` return at :446. Therefore a mismatched default converter is refused before conversion, and drift during conversion is refused before raw export or writing.

The helper preserves bounded opaque injected-converter attestation: passing no explicit factory settings uses the injected converter's attestation; real exposed options still undergo the existing checks. The fix adds no new API, dependency, framework or approval behavior, and does not change protected loader/factory/contracts. Only prospectus.py and its regression test changed. No missing correction, unrequested addition or new behavior breakage was found within this fix diff.

## Independently executed evidence

Archive import assertion passed (exit 0) for prospectus, bundle, loader, docling_env and identity; every resolved module.__file__ was under the exact absolute archive. Evidence: `unified-task-2-spec-recheck-imports.log`.

Focused tests: **13 passed in 26.03s, exit 0**, no skips/errors. Evidence: `unified-task-2-spec-recheck-tests-rooted.log`. The new three cases use an actual installed cached DocumentConverter and actual pipeline options, replacing conversion execution only. Before-conversion options drift refuses with zero conversion/writer calls; during-conversion drift refuses after one synthetic conversion and zero writes; unchanged defaults publish and are accepted by the checked bundle consumer. Both refusal cases preserve the original bytes and empty output. Existing checks cover injected attestation drift, five malformed/unverifiable settings cases, OCR-language mismatch plus matching success, and three installed-version mismatches.

Exact successful command (PowerShell variables expand to these absolute paths):

```powershell
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
$D='E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10/delivery_execution_20261011'
$A="$D/unified-task-2-review-8cdb8cfd/candidate"
$env:PYTHONPATH=$A
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_DATASETS_OFFLINE='1'
$env:PIP_NO_INDEX='1'
Set-Location -LiteralPath $A
py -3.13 -B -m pytest "$A/tests/test_prospectus_ingestion.py::test_default_cached_converter_settings_checked_before_and_after_conversion" "$A/tests/test_prospectus_ingestion.py::test_settings_drift_during_conversion_refuses_before_any_writer" "$A/tests/test_prospectus_ingestion.py::test_unverifiable_converter_settings_refused_before_convert" "$A/tests/test_prospectus_ingestion.py::test_injected_docling_ocr_languages_must_match_actual_options" "$A/tests/test_prospectus_ingestion.py::test_injected_docling_versions_must_match_installed_packages" -q -p no:cacheprovider --rootdir $A --confcutdir $A -o faulthandler_timeout=30 --basetemp "$D/unified-task-2-spec-recheck-pytest-rooted-20261011-1052" *> "$D/unified-task-2-spec-recheck-tests-rooted.log"
$testExit=$LASTEXITCODE
Get-Content -LiteralPath "$D/unified-task-2-spec-recheck-tests-rooted.log"
"pytest_exit=$testExit" | Tee-Object -FilePath "$D/unified-task-2-spec-recheck-tests-rooted.log" -Append
Set-Location -LiteralPath 'C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010'
exit $testExit
```

An initial invocation selected the identical five nodes and offline environment, without explicit rootdir/confcutdir/faulthandler_timeout, using basetemp `unified-task-2-spec-recheck-pytest-20261011-1049` and Tee-Object to `unified-task-2-spec-recheck-tests.log`. It remained silent before test results and was interrupted with Ctrl-C; process exit 1, no product verdict or test count. Rooted rerun above resolved the harness issue. No obsolete retained bug-assertion reproducer was run or claimed to pass.

## Integrity and source boundaries

Before and after execution, independently verified the exact recursive archive file set AND all **373 SHA-256 hashes** against manifest.json. Both passed. Package hashes before/after were identical:

- manifest.json: `972e4c314a177ed8b95aee60ba463a796a0c8b126d1735da810639afde420b8c`
- change.patch: `2c7ffacd75799d34cb3b7200556eee9681dd39ff20b6ca989b169fa39eac546c`
- change-stat.txt: `bce1dbcde3824b20daa21c020d8f465cdf9ff088cf5d51a8e593ddfcc00243d3`

Evidence: `unified-task-2-spec-recheck-integrity-before.json` and `unified-task-2-spec-recheck-integrity-after.json`. Independently matched the exact two changed paths and their archive contents with the supplied fix commit after CRLF normalization. `git diff --check BASE HEAD` exit 0. Live worktree was clean, with unchanged HEAD `84eba1c4e14c615d03cfbf854e61ffbba9599e19`; this is the later Phase6 checkpoint, not a requirement to equal archive HEAD. No later code was reviewed.

Exact READ_ONLY_CODEX_USAGE.ps1 was read fully and queried independently: initial 10:46:49 Manila 2% primary/27% weekly; final 10:50:30 Manila 6%/28%, both below stop/save thresholds. Actual worktree cwd restored after usage and testing. No source/archive/index/ref writes, installs, downloads, model inference, private data, descendants, execution of Prolog or external review service. Reports/logs only were written outside Git under D (the required usage helper writes its own external usage records under parent E).

Skipped: broad seven-file/~4k reruns, corpus/OCR/phone-photo/domain approval, Phase6/later code and historical M1/F/session rechecks. Synthetic conversion execution does not establish extraction accuracy; this scoped approval clears only M-T2-S1 and new fix-diff breakage.

**APPROVED — M-T2-S1 ADDRESSED; findings NONE.**
