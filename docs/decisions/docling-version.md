# Decision: Docling version policy

Date: 2026-10-04. Status: policy decided by the user; **the pin was moved to `docling==2.133.0` on 2026-10-04 after the gate passed** (see "Current pin").

## Policy

**Track the latest Docling release.** The thesis used Docling 2.93.0 because that was the latest release when it was written; the project follows the same rule instead of freezing that number. The master plan's table (section 2, "Docling 2.93.0") is therefore a record of the thesis, not a pin.

An upgrade is a deliberate change to `backend/pyproject.toml` and `backend/uv.lock` and must pass this gate first:

1. **Cached-input gate.** `scripts/prospectus_course_compare.py` over all 44 cached `*_docling.json` inputs, run in an environment with the candidate Docling version: every input identical between the old and new side, markup invariants intact (each cell id exactly once). This tests the parser and the evidence adapter under the new `docling-core` types, not Docling's conversion.
2. **Cross-version diff.** The same 44 candidates produced under the current pin and under the candidate version must have no differing course fields or audit counts (`compare_payloads`).
3. **Re-conversion check.** At least 3 to 5 real PDFs converted from scratch with both versions on CPU; course fields and Docling table cell counts, rows and columns must match. Any difference is reported to the user before the pin moves.
4. The full test suite passes in the new environment.

The user decides when the pin moves; an agent only reports the gate results.

## Current pin

`backend/pyproject.toml`: `docling==2.133.0` (uploaded 2026-10-03). Locked by `uv lock`, which moved only these packages:

| Package | Before | Now |
|---|---|---|
| docling | 2.129.0 | 2.133.0 |
| docling-slim | 2.129.0 | 2.133.0 |
| docling-core | 2.97.1 | 2.99.0 |
| docling-parse | 7.20.0 | 7.22.2 (newer than the 7.22.1 seen when the gate was run; the lock picked the latest allowed) |
| docling-ibm-models | 4.0.3 | 4.0.3 (unchanged) |

No other package version changed; one duplicate `torch 2.14.0` lock entry (the macOS source variant) was merged away. If this branch's `uv.lock` conflicts at merge time, re-run `uv lock` after merging.

Re-check after the move, in a fresh throwaway venv synced from the new lock (`uv sync --locked --extra tools --extra dev --extra ocr-gpu`): the 44-input comparer is 44/44 identical with markup invariants intact, and the full suite passes (326 passed, 13 subtests).

## Gate results for 2.133.0

Environment: a throwaway venv built from a copy of `backend/pyproject.toml` with `docling==2.133.0` and a fresh `uv lock`. The 2.129.0 side is the repository's earlier environment. (At that time PyPI showed docling-parse 7.22.1 and docling-core 2.99.0.)

- Cached-input gate under 2.129.0: 44/44 identical. Under 2.133.0: 44/44 identical, markup invariants hold in both (44 files with `data-gap`, 9 with `data-unplaced-cell`, largest 25543 bytes).
- Cross-version diff of the 44 candidates: 0 inputs differ.
- Re-conversion from the PDFs on CPU with both versions (BSA architecture, ABComm, BSEd-Math twice, BS Accountancy): course counts 77, 50, 50, 50, 32 on both sides; no differing course fields; Docling table cell counts, rows and columns identical for every table. The audit status is `error` on both sides for all five, as it already was.
- Docling conversion times on CPU were within a few seconds of each other between versions (41 to 63 s per PDF).

The user's standing policy ("track the latest Docling, gated") then applied: the pin was moved to 2.133.0.

## Notes

- Docling pulls `docling-core`, `docling-parse` and `docling-ibm-models`; the lock records all of them, so an upgrade changes several lines of `uv.lock`.
- The OCR path calls a private Docling helper (`docling.models.stages.ocr.rapid_ocr_model._resolve_rapidocr`) to resolve `iso:fil` to PP-OCRv6 `tl`; an upgrade can break it, and `tests/test_ocr_bench_engines.py` plus the six-config smoke run would show it.
- The Docling GPU findings in the OCR plan (device option, RapidOCR cuDNN setting) were measured on 2.129.0.
