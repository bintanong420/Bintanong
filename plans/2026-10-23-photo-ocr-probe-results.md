# Photo-OCR feasibility probe for grade rows (Phase 10 task 5), 23 October 2026

Owner decision D1 (23 Oct): an onnxruntime 1.30.0 CPU bake-off. Done here as a bounded probe, not a Q11 verdict.

## Why a probe instead of the ocr_bench score

`ocr_bench` (4 Oct plan) measures prospectus extraction. Its `ocr` step writes text and word boxes, while its
`score` step expects prospectus-extractor payloads. That bridge was never built (tasks 4-9 did not run). Grade
photos need a different check, so this probe compares grade rows instead.

## Setup

- Shared test venv: `onnxruntime==1.30.0` (CPU) was installed, and `rapidocr` was aligned from 3.10.0 to the
  locked 3.9.2, because Docling 2.133 rejects 3.10.
- RapidOCR models were fetched and hashed (manifest in the workspace `audit-evidence/p10-20261023/rapidocr-models.json`).
- Tesseract was not installed (not approved).
- Input: one synthetic grade-report page (8 rows, BSCS-like codes). `ocr_bench simulate` produced 7 phone-photo
  conditions. Configs were rapidocr-en, rapidocr-latin and rapidocr-iso:fil, at about 10-12 s per 7 images on CPU.
- Reference: `extract_grade_rows` on the born-digital PDF. Candidate: OCR boxes grouped into rows by vertical
  centre, then the same alias matcher.
- Raw: workspace `audit-evidence/p10-20261023/photo-probe/` (`compare.py`, `compare.json`).

## Result

| Condition | All three configs |
| --- | --- |
| flat_good, blur, dim, noisy | 8/8 rows, marks exact, nothing invented |
| hard | 5-7 rows; up to 7 rows got another row's grade (e.g. CC 1/L shown 2.00, printed 1.75) |
| perspective, tilt | 1-2 rows; marks from every row merged into one |

The OCR text itself is good. The failure is row reconstruction on slanted pages, which silently attaches
the wrong grade to a course. Q11 forbids any silent critical error, so photos are **not supported**. Uploads
keep returning `photo_ocr_unavailable`, and born-digital PDFs remain the supported path.

## What would be needed (not done; bounded-attempt rule)

- Deskewed row grouping (line fitting on box slopes, or Docling's table structure) with a refusal when rows
  are uncertain.
- Real phone photos of real report layouts (owner-provided, private, outside Git).
- A grade-row scorer with the Q11-style gates.
- A decision on Tesseract. Today this is a later-phase item for the owner.
