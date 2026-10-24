# Photo and scan grade rows (24.1): results, 24 October 2026

Phase 11 task 8, bounded per AGENTS.md. Raw output stays in workspace `audit-evidence/p11-20261023/photo-measure/`
(the owner sample results only as counts). Owner samples hold a real student's name and ID: never in Git.

## What was built (tested, mutation-checked)

- `backend/bintanong_private_context/photo_rows.py`:
  - Lines are chained left to right along each row's fitted baseline. Tilt and keystone pages line up; the Phase 10
    probe's y-centre grouping fails those tests.
  - A word near two lines, or between lines, refuses the page. Only critical words (course codes, marks, the FINAL
    header) can refuse. Non-critical words that cannot be placed, such as semester labels centred between rows,
    are dropped after a first pass.
  - Narrow boxes (row numbers) borrow the page slope. Tilt beyond 8 degrees is refused.
  - Header mode: when a header line names FINAL, only that column's value is shown, bounded halfway to its
    neighbours. A value near a column edge, two values in the column, or a FINAL without neighbours refuses.
- `backend/bintanong_tools/ocr_bench/grade_rows.py`: grade-row scorer with the Q11 strict gates.
  - Truth is keyed by course id. A wrong mark or an invented or duplicate row is a silent error.
  - A refused photo is safe, but every row counts as missing, so a refused photo is never "supported".

## Simulated photos (synthetic pages, RapidOCR 3.9.2 CPU with local models, 3 seeds per condition, 42 photos)

| Layout | Exact on every seed | Not exact |
| --- | --- | --- |
| Plain (code, title, grade, units; the Phase 10 probe page) | all 7 conditions: flat, tilt, perspective, blur, dim, noisy, hard | none |
| Report-of-Grades style (header with MIDTERM/FINAL/RE-EX, semester labels, summary rows) | flat, dim | noisy (1 row missed), perspective (1 of 3 refused), tilt, blur, hard (refused) |

Across all 42 photos there were **0 silent errors** (no wrong mark, no invented row).

For comparison, the Phase 10 probe on the plain page attached wrong grades on the hard photo and merged rows on
tilt and perspective.

## Owner sample (real registrar Report of Grades screenshot, private)

- **Refused** (`word_near_two_lines`), with the full image and with the student panel cropped away. No silent error.
- Cause 1 (pinned as a strict xfail): a far-left student-panel label joins a sparse row and bends its fit.
- Cause 2 (pinned as a strict xfail): OCR boxes are taller than the row pitch (21 px boxes, 18 px rows). A few
  pixels of centre jitter then look ambiguous.
- Two follow-up attempts (local robust slope; row-pitch distance unit) each broke another tested case. They were
  reverted under the bounded-attempt rule.
- Alias coverage, separately: the older p06 BSCS ledger catalog matches only 5 of the 32 printed codes. The hosted
  release catalog was not measured here. Printed forms such as "GE- Elect:", "PATH-Fit 1" and the system-truncated
  "ELECTRONI" need reviewed aliases before any code can match.
- The handwritten prospectus photo was not scored. Its OCR read about 11 of roughly 20 handwritten grades, and it is
  a different document type.

## Decision for the thesis build

Photos stay **unsupported**: uploads keep returning `photo_ocr_unavailable`. The Q11 gate requires real photos of
real layouts, and the only real layout sample is refused. The owner's O2 approval (add RapidOCR/onnxruntime to the
`api` extra) was conditional on the geometry passing. It did not, so **no dependency was added**. The geometry, the
scorer and the measurements are ready for a later attempt. That attempt needs:

- more real samples;
- either row-pitch-aware thresholds that keep the keystone tests, or table-region detection (crop to the table
  before grouping);
- reviewed aliases for the printed forms above.
