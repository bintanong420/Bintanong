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

- [ ] Record expected RED for original raster labeling and rejection controls.
- [ ] Implement the smallest optional provenance/transform validation correction.
- [ ] Verify GREEN and related image/native/policy/context regressions; then the
  full suite under authorized Python3.13, no pytest cache, external basetemp.
- [ ] Commit the verified product increment with explicit paths.
- [ ] One independent final review; address findings with focused TDD if needed.
- [ ] Bind confirmed original-image field regions using actual byte/dimension
  readers where existing source contracts permit. Never guess unreadable content
  or claim a complete service audit from selected fields. If new source-content
  choices become necessary, present exact evidence and stop dependent changes.
- [ ] Record results/checkpoint; preserve raw artifacts ignored under the workspace.

Current confirmed work: E01 continuing-PDF headings mapped as3native fields with
actual character indices/glyph boxes. F1/V/E19selected groups are settled. Raster
mapping work is technical provenance, not a new source-content review or approval
of source authority/current-year applicability. Full Phase05 exit remains open.
