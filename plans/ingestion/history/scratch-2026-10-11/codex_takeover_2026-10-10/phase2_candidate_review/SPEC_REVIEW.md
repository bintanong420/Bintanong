# Independent candidate Spec review

Verdict: **PASS** for the owner-authorized candidate scope at `7fe26c07fc5338dfeaae874438d8a802ae4ad774`, based on `0caeaba8d8221a0f75b154e94bc3167b780f1407` (four local draft commits).

Confirmed defects: **NONE** (0 High, 0 Medium, 0 Low). Suspicion-only findings: **NONE** requiring escalation from this run. No Standards verdict is issued here; that must be a separate fresh review after this Spec PASS. Formal Phase 2 exit: **NOT RUN**, not PASS.

## Authority and inspection

Read `PHASE2_CANDIDATE_REVIEW_SCOPE.md` completely before inspecting product code. Read the 374-line Phase 2 plan consecutively to its end, master sections 7.1/7.2/7.3, `plans/INDEX.md`, previous Phase 1 handoff, all six affected Phase 2 decision records, applicable source/register contracts, affected code and all nine changed test files. The Claude-named role/template were read as Markdown only; no Claude tools/model/agent were invoked. Codex code-review and verification-before-completion skills informed this Spec-only run, with no child delegation.

The scope explicitly authorizes the pending-register preflight before conversion, minimal CLI/callable pipeline, shared policy/table route, and real `$ref`/legacy `cref` support. These are not unexpected scope additions. Changed-path evidence contains only the candidate package, generic ingest hardening, six decision records and nine focused tests; no protected extractor/contracts/API/embedding/dependency/lock changes appear in the candidate diff.

## Conformance evidence

- `register.py:58-89` reparses actual Phase 1 records, validates the whole register and immutable source snapshot, refuses noninitial governance states, and selects the byte-derived version before conversion. Scope/source/content states remain pending; approval remains not_requested/null. Filenames/classification do not establish institutional authority.
- `policy_text.py:125-241` preserves raw item text/provenance and physical pages, uses explicit geometry/character ranges, reports unlocatable/empty/furniture/page evidence and checks exact item/page accounting. It retains heading/scope/exception candidates without claiming nesting or authorized scope.
- `procedure_text.py:193-320` retains raw table wrappers, geometry and reading order; preserves explicit procedure markers/labels; converts captured PPTX bytes through installed native Docling. Slide indices remain slide metadata with no PDF spans. Unsupported slide/table locators stay review-only.
- `policy_chunks.py:55-241` reparses SourceSpan/Chunk contracts and verifies hashes/version bindings, refuses unlocated/oversize clauses, repeats real leading column headers at indivisible row groups and rejects unsupported cells. `report.py:15-100` deterministically rebuilds accounting, retains raw rejection/omission evidence and pending review needs; split parts/header copies do not inflate original counts.
- `pipeline.py:19-83` requires explicit root/output/classification and pending registration, verifies conversion manifest/artifact digests/source-settings identity, rebuilds candidates from captured raw bytes and writes the root completion manifest last. Partial bundles lack that root manifest and are explicitly nonconsumable.
- `ocr_run.py:25-188` uses captured source rendering and existing adapters, preflights local models, retains actual language/device/settings/timing/confidence/boxes and refuses unsafe RapidOCR initialization. `ocr_gate.py:46-172` validates frozen PDF-backed references and chronology/digests, requires critical annotations and ten distinct source byte identities, and reports worst/pooled/per-document CER plus conservative critical/missing/invented accounting. Detached candidate critical claims do not replace manual evidence.

## Fresh execution

System Python **3.13.12**, executable recorded in `spec/bound_imports.json`. Initial shell selected the candidate worktree; the external runner then explicitly selected the archive as cwd and first import root. Assertions prove all ten affected product modules plus protected reused contracts/identity/loader/chunking/publish resolve inside the frozen archive.

Exact executable review scripts and pytest arguments are preserved in `spec/verify_focused.py`, `spec/focused_command.json` and `spec/bounded_checks.py`. Commands:

```powershell
Set-Location -LiteralPath 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_HUB_DISABLE_TELEMETRY='1'
py -3.13 -B 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\phase2_candidate_review\spec\verify_focused.py'
py -3.13 -B 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\phase2_candidate_review\spec\bounded_checks.py'
```

The runner invokes archive absolute paths for test_ingest_hardening.py, test_document_inspection.py, test_register_minting.py, test_policy_text.py, test_procedure_text.py, test_policy_chunks.py, test_ingestion_report.py, test_ocr_run.py and test_ocr_gate.py with `-q -p no:cacheprovider` and a unique external basetemp.

**225 passed, 1 Docling deprecation warning, 93.36s; exit 0.** Includes actual installed native synthetic PPTX smoke and synthetic generic Docling CLI checks. No actual Tesseract/RapidOCR engine was initialized and no institutional original was converted. `spec/focused_tests.log` is the full output; `spec/focused_exit.txt` records exit 0.

Two additional bounded synthetic checks exited 0 (`spec/bounded_checks.log`): a table with explicit multi-page cell provenance split into two capped parts with a repeated real header and one-original-table accounting; removing one cell page on the multi-page wrapper yielded `unlocated_cell_on_ambiguous_table_page`. Independent identical manual/OCR text yielded CER 0, ten aliases remained blocked, and a dropped negation remained a critical error despite candidate critical claims and an explicit review flag.

## Preservation and limits

All **368** archive files match the frozen manifest before tests, after tests and at review end; all hashes identical, **no additions**. Full snapshots: `spec/archive_before.json`, `spec/archive_after_tests.json`, `spec/archive_after.json`. `spec/git_before.json` and `spec/git_after.json` are identical for owner/candidate status and HEAD/dev/origin/dev. All writes were external review evidence and synthetic temporary artifacts only; no product/archive/owner edits, commits, ref movement, installs, downloads or environment synchronization occurred.

Owner-deferred broad suite/mutation campaign, original corpus/human verification, actual OCR engines/model/device/GPU ruling, phone photographs, deployment/platform gates, exact tokenizer, source authorization and formal phase exit remain **NOT RUN**. The frozen-human-reference/converter seams use trusted caller declarations, not authenticated institutional credentials; namespace scanning is not semantic private-data detection. Accounting and candidate Spec PASS do not establish extraction accuracy, source approval or readiness for rule authoring.

APPROVED — candidate Spec scope only. Deferred checks and institutional accuracy/authority remain unverified.
