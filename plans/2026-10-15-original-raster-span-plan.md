# Original raster provenance in reviewed image spans

Use the existing Phase05 worktree and source review decisions. Execute inline with
synthetic TDD and one independent final review. No new human content decision is
needed for an accurate source-kind label and byte/geometry validation.

Goal: bind reviewed standalone JPEG image regions without labeling them as PDF
renders. Existing `map_reviewed_image_spans` defaults and all prior payloads remain
compatible. Add optional `source_kind="original_raster_image"`; retain default
`original_pdf_image`. Only those explicit values are supported. Raster mode is
single-page, scale1, unrotated, uncropped, original source image bytes/hash, and
pixel-sized source canvas. The injected trusted reader verifies actual dimensions
and bytes; no resampling, OCR or source-wording changes.

Files: `backend/bintanong_tools/document_ingest/reviewed_image_spans.py` and focused
synthetic regressions in `tests/test_reviewed_image_spans.py`. Original source
bytes, review events/field ownership, scope states, release flags and context/ranking
formats stay under existing contracts. No installs or model/runtime/DB changes.

- [x] Record expected RED for original raster labeling and rejection controls.
- [x] Implement the smallest optional provenance/transform validation correction.
- [x] Verify GREEN and related image/native/policy/context regressions; then the
  full suite under authorized Python3.13, no pytest cache, external basetemp.
- [x] Commit the verified product increment with explicit paths.
- [x] One independent final review; address findings with focused TDD if needed.
- [x] Bind confirmed original-image field regions using actual byte/dimension
  readers where existing source contracts permit. Never guess unreadable content
  or claim a complete service audit from selected fields. If new source-content
  choices become necessary, present exact evidence and stop dependent changes.
- [x] Record results/checkpoint; preserve raw artifacts ignored under the workspace.

Current confirmed work: E01 continuing-PDF headings mapped as3native fields with
actual character indices/glyph boxes. F1/V/E19selected groups are settled. Raster
mapping work is technical provenance, not a new source-content review or approval
of source authority/current-year applicability. Full Phase05 exit remains open.

Execution ledger, 15 October: RED13failed/41passed/72subtests; derived raster graph
RED1failed. GREEN144passed/206subtests across seven related modules. Full suite:
5277passed/508subtests,6skipped/6warnings,362.47s. Logs under workspace
audit-evidence/p05-original-raster-spans-20261015; no dependency/model changes.

Ruling: preserve external workspace evidence and this tracked ledger, rather than
the skill's default scratch directory/deletion — owner location and recoverability
instructions take precedence; deleting evidence would prevent later audit.
Ruling: propagate raster provenance into graph-derived spans and retain the private
span helper's PDF default — existing graph/service callers need compatibility.
The service binder remains PDF-only and rejects raster input; expanding it is
outside this bounded change and could misstate procedure-table evidence.
Ruling: mapping seven fee amounts and three PDF headings is selected-field coverage,
not complete F1/V/E admission; remaining fields and governance gates stay open.

Photo-region QA found F04's final digits appear .52, versus earlier confirmed .62.
Owner shown the exact crop and asked only this focused discrepancy; F04 artifact
is held pending actual answer. Preserve the previous confirmation/history and do
not silently correct it. Other F1/V/E decisions remain settled.

Bounded plan complete with F04 content hold: product50405f5; final mapping SIXfee
amounts/three prior native headings, zero new chunks. Initial seven-field attempt
retained/quarantined. Independent final reviewer: no Critical/Important/Minor;
fresh72tests/127subtests and source/event/native-range checks pass. No fix pass
needed. Final Ruling: reviewer declined disputed human readings, school authority,
full-source coverage, admission/benchmarks/activation/phase completion — keep those
outside this technical delivery and F04 held; otherwise technical success would
overstate source approval. Reviewer visual impression .62 does not settle the
owner question.22raw files sealed, manifestSHA256:
56cba00e214837353a30747fa93aab65777786e876b0e4bc3d0e8f93d7ad754e.
Further F04 response must create separate evidence, never mutate this seal.
