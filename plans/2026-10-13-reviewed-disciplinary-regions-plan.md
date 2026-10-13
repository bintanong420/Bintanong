# Reviewed disciplinary regions implementation plan

> Execute inline using executing-plans and test-driven-development; retain the
> existing isolated worktree and use one final independent review.

**Goal:** Map eleven confirmed disciplinary rows on handbook physical87/88/89,
including37 nonblank fields and18 literal source blanks, without changing sanctions.

**Architecture:** Extend the original-image mapper with optional trusted
`table_region_formats`, keyed by source SHA256/physical page. Declare
`source_region_pixels` for retained TOPLEFT pixel regions or `raw_cell_points`
for retained raw-cell TOPLEFT PDFpoint boxes. Validate each through the existing
hash-bound full-page render before mapping; blanks retain evidence and any recorded
region with empty span lists. Explicit raw_cell:null blanks have no fabricated
rectangle. These are reviewed transcription regions, not glyph ranges
or invented Docling cell IDs. Existing image and corrected-field paths stay intact.

**Spec:** Undergraduate/source-gap/service-table policies and the next action in
`plans/2026-10-13-reviewed-graduation-image-report.md`.

**Tech Stack:** SystemPython3.13.7; existing approved Python3.13 environment,
pypdfium2 5.14.0/pytest9.1.1. Context7 render documentation consulted this session.

## Global constraints and review focus

- Retain all original/preparation/event/raw/register/sealed bytes. No repeated
  owner reviews, previous conversions, downloads/dependencies/model copies.
- Unknown undergraduate applicability/authority remains unknown; actual chunks
  remain zero. No runtime/API/database/Prolog/activation/Phase06 advancement.
- Explicit coordinate declarations only; reject missing/unsupported formats,
  wrong origins, nonfinite/out-of-page boxes, split pages and mismatched renders.
- Only confirmed, correctly named scalar fields map. Blank flags must agree with
  retained proposed_blank and empty reviewed/proposed values; no zero/no-penalty
  inference. Diagnostic glyph overhang does not override reviewed column ownership.
- Preserve malformed weapon wording and its unresolved meaning/source gap.
  New formats cannot bypass exact corrected-field review requirements.
- Synthetic tests in Git; source-derived artifacts/logs/temp/seals stay ignored
  under workspace audit-evidence. Models remain C:/Coding-projects/MODELS.

## Task 1: Explicit retained region formats and blank evidence

Modify `backend/bintanong_tools/document_ingest/reviewed_image_spans.py` and
`tests/test_reviewed_image_spans.py`. Optional `table_region_formats=None` is an
additional trusted layout input, not an authority or review decision.

- [x] Focused RED for pixel/point conversion, exact blank preservation, explicit
  format/origin/geometry requirements, invalid flags/text/field/page/review,
  render identity, excluded audience, gaps and input invariance.
- [x] Minimal GREEN; existing image/native/preparation/pending/source/governance
  regressions. Record exact results; cohesive code/test/checkpoint commit.

## Task 2: Additive original disciplinary evidence

- [ ] New ignored packet `audit-evidence/p05-reviewed-disciplinary-regions-20261013/`.
  Verify preceding graduation seal, fresh87/88/89 renders and actual review events.
  Preserve37 field texts/18 blanks and original column/region associations.
- [ ] Merge additively with96 prior nonblank spans/nine blank mappings; expect133
  spans/27 blanks, scalar requirements129to92, zero chunks/66unknown-applicability
  readings. Preserve all seven source-gap groups and prior evidence.
- [ ] Independent verifier without mapper imports checks original/render/field/
  event/region/blank/gap associations and all previous hashes. Seal new packet.
- [ ] Final fresh-context review; resolve actionable findings under TDD. Curated
  report/decision/index/checkpoint/progress, docs/diff/phase checks and local commit.

## Pre-flight rulings

Task1 produces field_spans consumed by the existing pending adapter in Task2.
Empty lists already represent explicit blanks; no chunk-contract change needed.
Actual page88 evidence retains raw_cell:null for five confirmed blanks. Ruling:
map those literal blanks after full-page validation with no invented region;
missing raw_cell keys or nonblank null cells stay withheld. Focused RED/GREEN
records this discovery separately from the earlier complete-region test fixtures.
The prior native mapper requires saved character ranges/page-size evidence absent
here. Ruling: use declared retained regions against original images, retaining all
native/raw diagnostics, rather than fabricate ranges or mutate the sealed bundle.
This loses glyph-level precision but honestly preserves reviewed transcription
provenance. Caller-supplied coordinate formats remain trusted layout declarations
and will be independently checked against original proposal/render metadata.

Owner has authorized Phase05 continuation and the scope/retention requirements.
Incoming collection remains incomplete; notify owner of exact folders at intake,
before final calibration including that batch. No incoming files inspected now.
