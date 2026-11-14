# Independent candidate Standards review

Verdict: **FAIL** for the current read-only candidate at `7fe26c07fc5338dfeaae874438d8a802ae4ad774`, based on `0caeaba8d8221a0f75b154e94bc3167b780f1407` (four local draft commits).

Confirmed defects: **1 Medium**, 0 High, 0 Low. Suspicion-only findings: **NONE** retained. This report does not change the preceding Spec PASS and does not issue a formal Phase 2 exit verdict. No repair or repair recheck occurred.

## Authority and inspection

Read PHASE2_CANDIDATE_REVIEW_SCOPE.md and SPEC_REVIEW.md in full before code inspection. Read extractor-reviewer.md, code-quality-reviewer-prompt.md and its requesting-code-review/code-reviewer.md reference as Markdown only; no Claude invocation occurred. Applied Codex code-review and verification-before-completion guidance within this independent Standards-only assignment, without child delegation.

Read the full 374-line Phase 2 plan in consecutive chunks, master sections 7.1/7.2/7.3, INDEX, Phase 1 handoff, all six affected decision records, every affected production module and all nine affected test files. Inspected applicable source/register contracts and reused identity, loader, chunking and OCR adapter boundaries. Fresh Git confirms the four draft commits and 27 changed paths; no protected contract/extractor/API/embedding/dependency/lock edits appear. The original Task 1/2 adopted files remain part of this candidate, and inherited behavior is identified explicitly below.

## Strengths

- Conversion wrappers validate the whole pending register and immutable captured source before conversion; candidate classifications do not promote authority.
- Raw evidence, explicit omissions/rejections and deterministic report rebuilds make accounting reviewable. Table splits retain real header spans and original table counts.
- Root completion manifests are written last; failure tests verify that partial publication is nonconsumable. New PDF/PPTX candidate wrappers reject reported conversion errors.
- OCR stays gate-only, refuses unproved RapidOCR startup and uses independently frozen manual references with distinct-source coverage and conservative critical comparisons. Actual engine execution and institutional accuracy are not claimed.

## Confirmed issue

### Medium M1 — generic ingest silently succeeds on a reported partial conversion

**File:** `backend/bintanong_tools/ingest.py:51` (success output at lines 56–69).

`parse_document` immediately takes `.document` from `converter.convert(...)`, discarding the ConversionResult's errors and status. A result with surviving pages/text and an explicit page extraction error therefore returns ordinary `docling_markdown` JSON with a source digest and conversion identity. `ingest PATH` exits 0, with no indication that content is missing. The guards only catch thrown exceptions, zero pages and wholly empty text.

**Concrete bounded reproducer:** `standards/bounded_checks.py`. It patches only the converter seam in the review process, uses a copied committed synthetic PDF, the installed Docling `ConversionStatus.PARTIAL_SUCCESS`, and a real installed `ErrorItem(component_type=DOCUMENT_BACKEND, module_name='synthetic_backend', error_message='page 2 extraction failed', page_no=2)`. The surviving document has two page records and Markdown `Only page one survived.`. No engine is initialized.

**Observed:** `parse_document` returned `format='docling_markdown'`, `num_pages=2`, `text='Only page one survived.'`, a source SHA-256 and conversion identity. `CliRunner().invoke(ingest.app, [source])` returned **exit 0** with the same successful JSON payload. The shared `loader._conversion_errors` recognized the supplied ErrorItem. Full actual output is in `standards/bounded_checks.log` and `standards/partial_conversion_observed.json`; reproducer exit 0 means the defect assertions reproduced successfully, not that the product behavior is acceptable.

**Impact and standard:** a document with an explicitly reported extraction failure becomes an apparently successful generic-ingest result. This violates the supplied engineering instructions to handle errors intentionally, avoid silent failures, and validate failure paths (§6/§8/§10); it undermines the Task 1 hardening's refusal/error behavior. It is a correctness/reliability defect, not a style request or demand for deferred corpus validation.

**Inheritance:** BASE's generic ingest also discarded `conv_result.errors/status`; this omission was not newly introduced by Tasks 3–6. It survives the candidate's adopted Task 1 hardening while that function is materially changed and newly emits digest-bound success. The candidate's new PDF loader/PPTX wrapper already rejects nonempty conversion errors, so the defect concerns the preserved public generic command. `standards/inherited_base_ingest.txt` preserves the inspected BASE implementation. This is a candidate defect, not a newly introduced regression claim.

**Smallest correction:** retain the conversion result and refuse its reported errors/non-success status before accepting text; preserve the existing named ConversionFailed CLI failure. Add one focused regression with a partial result containing nonempty text and page records, asserting no successful library result and nonzero CLI exit/empty stdout. No such repair was made in this review.

## Fresh verification

System Python 3.13.12. Initial PowerShell cwd was the candidate worktree; the external runner then explicitly selected the frozen archive as cwd and first import root. `standards/bound_imports.json` binds the tested product and reused contract/extractor modules to the archive. The final fresh assertion additionally covers every affected backend import (including package and CLI) and all loaded reused contract/extractor modules: **52 modules**, all archive-bound, in `standards/final_bound_imports.json`.

Exact commands (all PowerShell invocations begin with the worktree selection):

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_HUB_DISABLE_TELEMETRY='1'
py -3.13 -B 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\phase2_candidate_review\standards\verify_focused.py'
py -3.13 -B 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\phase2_candidate_review\standards\bounded_checks.py'
py -3.13 -B 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\phase2_candidate_review\standards\finalize_preservation.py'
```

The fresh runner executes test_ingest_hardening.py, test_document_inspection.py, test_register_minting.py, test_policy_text.py, test_procedure_text.py, test_policy_chunks.py, test_ingestion_report.py, test_ocr_run.py and test_ocr_gate.py by archive absolute path with `-q -p no:cacheprovider` and a unique external basetemp. Full pytest arguments/environment: `standards/focused_command.json`.

**225 passed, 1 Docling deprecation warning, 116.80s, exit 0.** Log: `standards/focused_tests.log`; exit: `standards/focused_exit.txt`. Includes installed native synthetic PPTX and generic synthetic PDF CLI checks. Test success does not cover M1, which the independent bounded reproducer confirms.

The bounded checks additionally confirm both policy/procedure readers refuse a cyclic native `$ref` group. `standards/bounded_exit.txt` is 0. No actual OCR engine or institutional original was run.

## Preservation and assessment

All **368 archive files** match the frozen manifest before tests, after tests and at review end; every hash identical, **no additions**. Evidence: `standards/archive_before.json`, `archive_after_tests.json`, `archive_after.json`. Owner/candidate status and HEAD/dev/origin/dev are identical in `standards/git_before.json` and `git_after.json`. Final preservation assertions passed, exit 0 (`standards/preservation.log`, `preservation_exit.txt`). All writes were external Standards evidence and temporary synthetic artifacts. No product/archive/owner changes, commits, ref movement, installations, downloads or environment synchronization occurred.

Candidate Standards acceptance is withheld for M1. This report is not approval to merge/adopt/start formal Phase 2. Trusted converter and human-reference declarations remain declarations, not authenticated institutional authority; conservative critical line alignment is an explicit known limit. The separate session-cleanup High remains outside this candidate and unfixed.

Skipped as owner-deferred: broad suite/mutation campaign, original corpus/human validation, actual OCR engines/model/device/GPU/photos, deployment/platform and formal phase-exit gates. Extraction accuracy and source authority remain unverified.

CHANGES NEEDED — M1 (Medium): generic ingest must refuse reported partial conversion errors/status.
