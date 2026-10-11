# Phase D F3/F6 implementation report

Owner: d_identity implementer. Base: 641523d212839084da03d966ffbfca66c7e83e42.
Implementation only; independent review and all other Phase D findings remain controller work.

## Delivered behavior

- identity.bytes_sha256 owns byte digests; file_sha256 delegates it. InputSnapshot(path) captures resolved path, immutable bytes and their digest together. It accepts no declared digest or external byte payload. Frozen fields reject ordinary reassignment; require_path rejects a snapshot linked to another path.
- process_prospectus captures once, uses that digest for provisional source verification and run identity, and passes the capture to the loader. Batch captures one item at a time, carries the same snapshot from skip identity into processing, releases it before the next item, and lets the existing loader/shared-converter cache initialize a converter only when conversion is required.
- PDF conversion uses installed docling.datamodel.base_models.DocumentStream(name=original filename, stream=BytesIO(snapshot bytes)). The bad_alloc fallback receives a fresh stream from the same bytes. JSON review inputs are parsed from the captured bytes used for their run identity.
- Immediately before pipeline publication, current original bytes are compared with captured bytes. Changed bytes, including equal size and restored mtime, raise ValueError and preserve the published files. Standalone loader conversion also compares before directly overwriting its cache pair.
- Existing batch skip-check exception fallback is preserved: an unreadable identity/manifest check records its reason and proceeds with the captured item. This was briefly dropped by the loop rewrite, exposed by a new failing regression test and restored before the final suites.
- No schema bump, semantic-map architecture change, publish-v2 implementation, CLI digest acceptance, or model/dependency sync.

## Interface for F1

loader.load_document_result(..., *, snapshot: InputSnapshot | None = None) returns frozen DocumentLoadResult:

    document: LoadedDocument
    raw_json_path: Path | None
    cache_status: str  # converted, reused, not-applicable
    raw_json_bytes: bytes | None
    raw_json_sha256: str | None
    meta_bytes: bytes | None
    meta_sha256: str | None

For converted PDFs, these are the exact serialized raw/meta bytes written to staging and their digests. For reused PDFs, raw/meta bytes are each read once; the metadata is parsed from meta_bytes, raw_json_sha256 is checked against those raw_json_bytes, and those same raw bytes are parsed into the returned document. A replacement after either read cannot change the retained result. F1 can bind raw_json_sha256 and meta_sha256 without reopening the paths. pipeline's local loaded variable already holds the result.

Public loader.load_document keeps its original signature and returns exactly (document, raw_json_path). Public load_reusable_cache also keeps its (document-or-None, reason) contract. run_identity accepts optional snapshot while retaining path-only compatibility. ProvisionalSource.verify_pdf retains file-based compatibility and delegates its check to verify_digest; pipeline supplies the captured digest to verify_digest. process_prospectus accepts internal-only _snapshot; no CLI argument exposes it.

## Verification commands and actual results

All commands ran from C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d. MAIN denotes C:/Users/Hawksprey/source/repos/Bintanong/backend/.venv/Scripts/python.exe. GUI denotes the existing %TEMP%/gui-review-venv/Scripts/python.exe. Shell Tee-Object redirected output to the named scratch log; listed exit codes are pytest/process exit codes, not Tee-Object's exit status.

1. MAIN -m pytest -q tests/test_prospectus_input_snapshot.py -p no:cacheprovider: RED, 8 failed, pytest exit 1. Authoritative rerun corrected the batch fake boundary before this log. The source-mutation test failed with DID NOT RAISE ValueError; old conversion used the live path. Other missing capture/result APIs and live-path fallback failed as expected. task-d-identity-red.log.
2. MAIN -m pytest -q tests/test_prospectus_input_snapshot.py tests/test_prospectus_identity.py tests/test_prospectus_cache.py tests/test_prospectus_batch_skip.py tests/test_prospectus_publication.py -p no:cacheprovider: intermediate GREEN, 73 passed, exit 0. Later final focused log supersedes this run.
3. MAIN -m pytest -q tests/test_prospectus_input_snapshot.py -k 'standalone_loader or cache_reparse' -p no:cacheprovider: RED, 1 failed, 1 passed, 8 deselected, exit 1. Standalone changed-source conversion overwrote cache instead of refusing. Cache-only batch did not request a converter. task-d-identity-standalone-red.log.
4. MAIN -m pytest -q tests/test_prospectus_input_snapshot.py tests/test_prospectus_identity.py tests/test_prospectus_cache.py tests/test_prospectus_batch_skip.py tests/test_prospectus_publication.py tests/test_prospectus_authority.py tests/test_prospectus_markup.py -p no:cacheprovider: first 334 passed/1 failed due an obsolete batch prewarm monkeypatch in an existing markup test; corrected that test dependency boundary. Rerun GREEN, 335 passed, exit 0. task-d-identity-green.log stores the final focused run.
5. MAIN -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider: first full run 640 passed, 13 subtests passed, 3 warnings, exit 0. GUI -m pytest -q tests -p no:cacheprovider: first comprehensive run 646 passed, 13 subtests passed, 5 warnings, exit 0. These preceded the preserved skip-check fallback regression and remain in task-d-identity-fullsuite.log and task-d-identity-comprehensive.log.
6. MAIN backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py --self-test: 80/80, exit 0. task-d-identity-selftest.log.
7. MAIN -m pytest -q tests/test_prospectus_input_snapshot.py -k 'skip_check_is_unreadable' -p no:cacheprovider: RED, 1 failed, 10 deselected, exit 1. It exposed the lost fallback in the loop rewrite. task-d-identity-skip-error-red.log.
8. MAIN -m pytest -q tests/test_prospectus_input_snapshot.py tests/test_prospectus_batch_skip.py -p no:cacheprovider: GREEN after restoring fallback, 26 passed, exit 0. task-d-identity-skip-error-green.log.
9. Final MAIN baseline full-suite command from item 5: 641 passed, 13 subtests passed, 3 warnings, exit 0. Final GUI comprehensive command from item 5: 647 passed, 13 subtests passed, 5 warnings, exit 0. These reruns were necessary because the fallback changed code after the initial suites. task-d-identity-final-fullsuite.log and task-d-identity-final-comprehensive.log.
10. git diff --check: exit 0. Git emitted autocrlf working-copy notices; edited code/test files were written with LF via pathlib. No .gitignore or historical handoff file was changed or staged.

The final warnings are existing upstream deprecations: Docling OCR/table-image options and RapidOCR; GUI additionally has FastAPI/Starlette/httpx and AnyIO portal deprecations. No tests failed in either final full suite. Main API/embedding exclusions remain justified by that venv lacking FastAPI; the comprehensive GUI run covered them without exclusions.

## Files and remaining gates

Production: backend/bintanong_tools/prospectus.py; prospectus_extractor/{identity,loader,pipeline,batch}.py.
Tests: tests/conftest.py; tests/test_prospectus_input_snapshot.py (11 new regressions); tests/test_prospectus_{authority,batch_skip,markup}.py (existing dependency boundary adaptations).
Progress: plans/plan_current_progress/extractor_split_progress.md, preserving the controller's earlier checkpoint.

NOT RUN in this task: independent reviews, 44-corpus comparer, real-corpus conversion trial, B2/C gates, publish-v2 failure-injection matrix, Task10 documentation. These belong to the controller queue. F1 must bind retained cache digests; the current v1 manifest still does not bind caches. Original semantic-map bytes are still read through existing behavior and were outside this PDF/JSON snapshot task. File-by-file publication still has its existing concurrency ceiling; this task checks input before publication, not an atomic lock over subsequent external source edits.

Commit: 53e3c000958eae9cf4e12e197a6e54b7cc7b2e84. Range: 641523d..53e3c00. Explicit 11-file staging, required final Co-Authored-By trailer, post-commit git status clean. No push, merge, branch switch, worktree removal, main-checkout edit, .gitignore staging, or historical handoff staging.
