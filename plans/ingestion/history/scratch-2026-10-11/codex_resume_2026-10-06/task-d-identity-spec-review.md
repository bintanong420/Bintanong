# Phase D F3/F6 independent specification review

Verdict: APPROVED. Confirmed findings: NONE. Unresolved suspicions: NONE.

Reviewed committed range `641523d212839084da03d966ffbfca66c7e83e42..53e3c000958eae9cf4e12e197a6e54b7cc7b2e84` in `C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d`.

## Specification

Read the external review package, approved_execution.md F3/F6 requirements, implementer's task-d-identity-report.md, and main .claude/agents/extractor-reviewer.md. Checked actual committed diff and callers independently. F1-v2, semantic-map capture, F2/F4/F5/S1/S2/S4 and subsequent corpus gates were excluded from implementation acceptance here.

- `identity.py:23-53`: shared bytes_sha256 owner; file_sha256 delegates it. InputSnapshot reads and hashes one captured bytes object, stores immutable bytes in frozen fields, accepts no declared digest, validates path linkage, and compares current bytes directly on verify_unchanged. Stat size/time is not used as proof of identity.
- `pipeline.py:303-320`: the same capture supplies source.verify_digest, run_identity and load_document_result. `identity.py:125-128` and `loader.py:412-438` reuse its digest; they do not hash the input again. Source verification remains before output directories/staging are created. JSON review loading uses captured.data at `loader.py:417`.
- `loader.py:445-455`: primary conversion receives real DocumentStream(name=input_path.name, stream=BytesIO(captured.data)); the existing bad_alloc fallback builds a fresh stream with that same original filename and bytes. Installed Docling's public re-export and convert signature support this type; independent runtime conversion of the synthetic PDF also succeeded.
- `pipeline.py:350-351`: direct byte comparison occurs after staging and immediately before publish_staged; changed or removed inputs refuse publication through the existing failure path. Same-size/restored-mtime mutation is covered by a passing regression. `loader.py:482-483` supplies the analogous pre-write guard for standalone converted cache publication.
- `batch.py:223-247, 283`: capture is created per item and passed through skip_check to processing, then released before the next item. There is no eager capture list or prewarm converter. Cache-only reparse and all-skipped behavior do not request a converter. The skip-check exception fallback at `batch.py:224-228` records the error and proceeds with the captured item; its new regression passes.
- `loader.py:324-331, 347-383, 471-493`: the frozen internal result retains the exact raw JSON and metadata bytes and their digests. Cache reuse parses metadata from retained meta_bytes, verifies raw_json_sha256 against retained raw bytes, and parses those same raw bytes. Converted bytes match the serialized files written to staging or direct cache output. The pipeline retains the internal result for the subsequent F1 implementation.
- `loader.py:386-390, 497-509`: load_reusable_cache retains `(document-or-None, reason)` and load_document retains its previous parameter order/defaults and `(document, raw_json_path)` result. Existing exports/callers in package __init__, cli and tui continue to use the wrapper. ProvisionalSource.verify_pdf retains file-based compatibility, delegating to verify_digest.

No concrete specification gap, unrelated production change, circular import, hardcoded production Windows path, or broken public tuple contract was found. Five production files change coherently; existing test edits update fakes at the changed dependency boundary. The progress documentation is additional authorized bookkeeping, not behavior. No PDFs, generated conversion output, .gitignore or historical handoff were committed.

## Independently executed evidence

Interpreter: `C:/Users/Hawksprey/source/repos/Bintanong/backend/.venv/Scripts/python.exe`. Set `PYTHONDONTWRITEBYTECODE=1`; pytest used `-p no:cacheprovider` and external scratch `--basetemp` paths. Worktree remained clean.

1. `-m pytest -q tests/test_prospectus_input_snapshot.py tests/test_prospectus_identity.py tests/test_prospectus_cache.py tests/test_prospectus_batch_skip.py tests/test_prospectus_publication.py tests/test_prospectus_authority.py tests/test_prospectus_markup.py -p no:cacheprovider --basetemp <scratch>/task-d-identity-spec-pytest-temp`: **336 passed in 25.40s, exit 0**, no reported warnings. Log: task-d-identity-spec-tests.log.
2. `-m pytest -q tests/test_prospectus_sources.py -p no:cacheprovider --basetemp <scratch>/task-d-identity-spec-source-temp`: **1 passed in 0.13s, exit 0**. This specifically checks legacy verify_pdf and pending source authority.
3. Independent Python assertion probe loaded `tests/fixtures/synthetic_academic_guide.pdf` through real CPU Docling via load_document_result with an InputSnapshot, wrote only to external task-d-identity-spec-runtime, and verified converted status, exact raw/meta bytes against the files, both SHA-256 digests, PalSU document content, then cache-reused status/bytes/digests/content and the public load_reusable_cache tuple. **14 assertions passed, exit 0**. Log: task-d-identity-spec-runtime.log. This is a synthetic API/byte-retention check, not a real-corpus quality gate.
4. `git diff --check 641523d..53e3c00`: exit 0. `git status --short`: no changes.

Independent pytest total: **337 passed**. No whole-suite rerun was needed after these passing focused checks.

## Implementer report versus evidence

Actual diff and committed file list support the delivered-behavior and F1-interface claims. There are 11 new snapshot tests. Historical full suites were not independently rerun: inspected log tails agree with the report's final main **641 passed / 13 subtests / 3 warnings** and comprehensive **647 passed / 13 subtests / 5 warnings**. The implementer's focused green log says **335 passed** because it predates the added skip-check-fallback regression; the independent same-file-list run at the committed tip now has **336 passed**. This chronology is disclosed in the report, and the later full-suite results supersede the earlier code state. Historical red logs were not reconstructed or claimed as independently executed here.

## Boundaries

The current v1 manifest does not yet bind retained cache digests; that is the explicitly queued F1 task. The prepublication check does not lock the source across later file replacements; that existing concurrency ceiling is accurately disclosed. Neither is a missing F3/F6 requirement. No real-corpus trial, 44-corpus comparison, B2/C gate, Task10 work or later queued finding was represented as complete by this review.

APPROVED
