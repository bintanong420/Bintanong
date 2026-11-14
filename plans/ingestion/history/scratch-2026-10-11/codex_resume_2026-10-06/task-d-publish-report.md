# Phase D F1 publication consistency report

Baseline: 53e3c000958eae9cf4e12e197a6e54b7cc7b2e84. Worktree: C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d. F1 only; default output paths and staging/temp naming remain untouched for S1. No main checkout edits, syncing, push, merge, branch switch or worktree removal.

## Implementation and interfaces

- publish.py: publish-v2 manifest has mandatory main_file, output-only files, and separate cache_files. Shared structural validation rejects old v1, empty/malformed mappings, invalid SHA256 values/run keys, unsafe leaf names, overlapping/case-aliased names, missing PDF pairs and unsupported input kinds. verify_published fails closed on unreadable files, digest mismatch, invalid UTF8/JSON, escaping resolved targets and main/meta/input/settings cross-binding mismatch. Each listed file is read once: its digest and any JSON parsing consume that same bytes value.
- pipeline.py: carries both loader-provided snapshot hashes into payload.run_identity.cache_files before main serialization. Converted staging is checked against the captured hashes; reused raw/meta snapshots are staged and republished verbatim too, preserving cache='reused'. No expected cache digest is inferred by reopening the live cache. Missing/partial snapshots refuse publication.
- Publication order: essentials/prolog/rag/csv/optional markup -> main JSON -> staged raw cache JSON -> staged cache meta -> manifest. Stale deletion only considers the five known companions, never arbitrary prior-manifest entries, caches, main or manifest.
- Public read_manifest(path) and verify_published(directory,manifest) signatures are unchanged. publish_staged retains all six positional arguments and adds the approved keyword-only cache_hashes: Mapping[str,str] | None = None. PDF calls require this exact captured pair, supplied by pipeline. Loader public interfaces remain unchanged. Payload remains v3.2; CLI/output filenames/review/approval behavior are unchanged.

Approved deviation from original D Tasks5/6: cache-first publication and output-only publish-v1 are superseded by main-before-cache publish-v2 with exact cache cross-binding. Reused processing now stages two captured files rather than trusting later cache disk reads. File-by-file publication is NOT a whole-set atomic transaction. Before publication failures preserve existing files; interruptions either leave the old coherent set verifiable (byte-identical replacements are allowed) or a nonverifiable mixed set, while a final manifest replacement binds the coherent new set.

## Tests and evidence

MAIN = C:/Users/Hawksprey/source/repos/Bintanong/backend/.venv/Scripts/python.exe. GUI = existing %TEMP%/gui-review-venv/Scripts/python.exe. All commands ran from the worktree using PowerShell; logs are external under this scratch folder. Commands use -p no:cacheprovider. The first RED commands redirected pytest but did not propagate its exit through PowerShell; their pytest summaries establish expected test failure, rather than claiming the shell's success as a test success.

1. MAIN -m pytest -q tests/test_prospectus_publish.py tests/test_prospectus_publication.py tests/test_prospectus_batch_skip.py: original focused RED, 214 failed/72 passed in46.81s. task-d-publish-red.log. Tests were written before production edits.
2. MAIN -m pytest -q tests/test_prospectus_publication.py -k publish_v2_binds -x: focused RED confirmation, 1 failed/201 deselected in9.13s; expected schema-v1-versus-v2 assertion. task-d-publish-red-bind.log.
3. Same focused command as1 after minimal production changes: GREEN286 passed in42.28s, exit0. task-d-publish-green.log.
4. Same focused command after adding supplemental cross-binding/same-read/malformed-cache/partial-snapshot checks: GREEN310 passed in37.57s, exit0. No further production changes. task-d-publish-final-green.log.
5. MAIN -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py: first broad run2 failed/908 passed/13 subtests/3 warnings in93.87s, exit1. task-d-publish-fullsuite.log.
6. GUI -m pytest -q tests: first comprehensive run2 failed/914 passed/13 subtests/5 warnings in93.74s, exit1. task-d-publish-comprehensive.log.
7. MAIN -m backend.bintanong_tools.prospectus_extractor --self-test:80/80, exit0. task-d-publish-selftest.log. Production code has not changed since this run.
8. MAIN -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -x: isolated broad failure1 failed/41 passed in4.72s, exit1. task-d-publish-first-failure.log.
9. Explicit RED reconstruction against baseline53e3c00: task-d-publish-reconstructed-red.py replaces only the in-process publish module with git-show baseline source and runs selected current validation/stale tests.38 failed/5 passed/21 deselected in3.05s, exit1. task-d-publish-reconstructed-red.log. No worktree code was reverted. This is reconstruction, not original test-first evidence. The stale test's manifest schema now follows the running publisher's version so schema rejection cannot hide the old arbitrary-delete bug.
10. MAIN -m pytest -q tests/test_prospectus_authority.py tests/test_prospectus_cache.py tests/test_prospectus_publish.py tests/test_prospectus_publication.py tests/test_prospectus_batch_skip.py after correcting the two obsolete doubles: GREEN557 passed in59.93s, pytest0. task-d-publish-corrected-green.log.
11. MAIN -m pytest -q tests/test_prospectus_publish.py:64 passed in0.72s, exit0. task-d-publish-validation-green.log. Final schema-following validation tests unchanged thereafter.
12. Final MAIN broad command from5:910 passed/13 subtests/3 warnings in118.86s, exit0. task-d-publish-final-fullsuite.log.
13. Final GUI comprehensive command from6:916 passed/13 subtests/5 warnings in117.42s, exit0. task-d-publish-final-comprehensive.log.
14. git diff --check: exit0. Git reports existing autocrlf checkout warnings; edited files were written UTF8/LF through pathlib, with no .gitignore or Git configuration changes.

The180-case interruption matrix injects exceptions before and immediately after all9 replacements, with changed and byte-identical companions across changed-PDF, changed-settings, force-reconversion, changed-settings/identical-raw, and changed-PDF/identical-raw scenarios. Tests require a passing old manifest to describe the entire unchanged prior coherent set, and reject old-manifest verification after a changed main until final manifest replacement. Tests also cover converted/reused captured digests, reused raw/meta replacement/deletion after parse (captured pair restored), staged cache tampering before publication, missing/corrupt cache skip refusal, old-v1 skip refusal, malicious manifests, unreadability/escaping leaf resolution and arbitrary stale cache/neighbor preservation.

Both initial broad failures were test doubles violating the newly enforced contract:
- test_matching_hash_is_recorded_and_still_does_not_authorize returned DocumentLoadResult(document,None,'converted') with no raw/meta snapshots. Its fake now stages a complete raw/meta pair matching the fixture grid/PDF/settings and returns exact bytes/hashes. Existing authority assertions remain.
- test_born_digital_cache_is_never_reused_for_an_ocr_run changed loader.conversion_settings alone while pipeline run identity still declared born-digital settings. Failclosed publication correctly rejected the mismatch. The test now supplies the same captured OCR settings dict to both loader and identity boundaries. Existing second-conversion and OCR-metadata assertions remain. No production validation was relaxed.

## Files

Production: backend/bintanong_tools/prospectus_extractor/publish.py and pipeline.py.
Tests: tests/test_prospectus_publish.py, test_prospectus_publication.py, test_prospectus_batch_skip.py, test_prospectus_authority.py, test_prospectus_cache.py.
Progress: plans/plan_current_progress/extractor_split_progress.md. Evidence and reconstruction runner stay outside Git.

## Boundaries and remaining work

Verified: focused failure matrix/validation, final main baseline suite, complete GUI environment suite and80 selftests. Earlier failed runs are retained and superseded, not hidden. Implementer validation is complete; independent spec/quality reviews are NOT RUN and controller-owned. The remaining F2/F4/S1/S2/S4 fixes, F5 evidence, D44-document comparer/counts/trials, decision record/Task10 and later-phase queue remain parent-owned and are not claimed done here.

Publication still assumes one writer per output stem; no locks, rollback framework or atomic directory swaps were added. Verification checks a file-by-file snapshot and cannot authenticate a user who rewrites every artifact/manifest. Tests simulating replacement after a read prove digest/parse use the same captured bytes; a subsequent verification rejects the replaced files. No real institutional-PDF conversion was run for F1.

## Commit

Committed 597e8c0289b8c090edf494248a9bd3fedad6aeb4. Review range:53e3c000958eae9cf4e12e197a6e54b7cc7b2e84..597e8c0289b8c090edf494248a9bd3fedad6aeb4. Explicit staging covered only the8 listed files; git diff --cached --check passed. Required Co-Authored-By trailer is present. Final git status --porcelain is empty. No pending verification process remains.
