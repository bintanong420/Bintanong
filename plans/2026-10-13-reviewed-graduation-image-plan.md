# Reviewed graduation image mappings implementation plan

> Execute inline using executing-plans and test-driven-development. Preserve the
> existing isolated worktree and use one final independent review.

**Goal:** Map the nine confirmed graduation rows, including the separately reviewed
diploma-cover correction, while preserving the unfinished original process.

**Architecture:** Extend the pure original-image mapper with optional
`correction_rows`, a trusted reading-ID to event-row-ID association. A changed
scalar value maps only when the exact hash-bound field review confirms the source,
page, image, original proposal, corrected text and original region. Keep preparation
and proposal bytes unchanged. No graph or END is inferred from the clipped source.

**Spec:** `plans/source-gap-policy.md`, undergraduate scope policy and the recorded
next action in `plans/2026-10-13-reviewed-image-flowchart-report.md`.

**Stack:** Python3.13.7; existing pypdfium2 5.14.0 and pytest9.1.1 environment.

## Constraints and review focus

- All output is inactive; all66 applicability declarations remain unknown.
- Corrected original region/text must match the actual review event; a row alias
  is a trusted caller association, independently checked against the original.
- Preserve row6 clipping annotations and row9 cutoff, including affected claims.
- No blank/default/continuation/END inference, source or canonical overwrite.
- Preserve sources, raw/history/registers and all earlier seals. Private execution
  artifacts stay ignored under workspace audit-evidence; models remain inMODELS.
- No installs/downloads/dependency changes, runtime/API/database/model/Prolog work,
  remote write or phase advancement. Synthetic tests only in Git.

## Task 1: Exact corrected-field event binding

Modify `backend/bintanong_tools/document_ingest/reviewed_image_spans.py` and
`tests/test_reviewed_image_spans.py`. Add optional `correction_rows=None` to
`map_reviewed_image_spans`. For changed corrected fields, select exactly one
`reviewed_rows` entry and field from the existing event bytes, validate source/page/
image and original/reviewed/evidence equality, then retain that exact event field
in the mapping sidecar. Accepted-field behavior remains the same.

- [ ] Write focused regressions for a corrected field, absent/mismatched/ambiguous
  review, wrong original proposal/image/page/region, input invariance and preserved
  source gap. Observe expected RED.
- [ ] Implement the smallest correction binding; observe focused GREEN and relevant
  mapper/preparation/pending/source/governance regressions. Record results and commit.

## Task 2: Additive original-image graduation evidence

- [ ] New ignored packet `audit-evidence/p05-reviewed-graduation-images-20261013/`.
  Verify preceding seal and original full-page64 render at scale2. Map27 scalar
  fields in nine rows using actual event row8 correction. Reuse69 earlier spans/
  nine blanks. Combined96 nonblank spans/nine blanks; missing scalar requirements
  expected156to129. Actual pending chunks remain zero/66 unknown applicability.
- [ ] Independently compare saved fields, review event, original regions/render,
  source gaps and earlier hashes; preserve all previous output. Seal new evidence.
- [ ] Final independent code/evidence review, bounded report, checkpoint/progress/
  index, documentation/diff/phase checks and curated commit. Record exact next step.
