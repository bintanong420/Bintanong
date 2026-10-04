# Prospectus OCR Measurement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task, with superpowers:test-driven-development inside each task. Steps use checkbox (`- [ ]`) syntax for tracking. Tasks 1 to 3 are already built (see "Status"); Tasks 4 to 9 are not started and need the decisions below.

**Goal:** Find out, with numbers, whether any of six OCR configurations can read a photographed PalSU prospectus well enough to be called "supported" (Q11), before any OCR is wired into the pipeline. The born-digital extractor output (JSON plus markup twin) is the answer key. Disagreements become review rows in the Phase B2 format, so a human decides; OCR never promotes itself.

**Architecture:** A sibling package `backend/bintanong_tools/ocr_bench/` (simulator, scorer, engine grid) plus one driver `scripts/ocr_bench.py`. The scorer reuses `course_checks` (`normalise`, `loose`, the audit-flag reader). No extractor module changes. This is a standalone bake-off: pipeline integration of OCR comes after Phase D, as its own plan, and only if this one finds a configuration that passes.

**Tech Stack:** Python 3.13, pytest, pypdfium2, Pillow, numpy, opencv (all already in the `tools` extra). OCR engines (Tesseract 5, RapidOCR through Docling 2.129.0) are NOT installed and are not needed for Tasks 1 to 3.

**Base:** branch `feat/ocr-measurement-harness` at `6846da4`. Baseline before this plan: 277 passed + 13 subtests when the whole suite can be collected. The venv used here has no `fastapi`, so `tests/test_api_probes.py` and `tests/test_embedding_service.py` fail at collection (before and after this plan); with those two ignored the suite is 306 passed + 13 subtests, of which 35 are this plan's.

---

## Decisions (Q8 to Q16)

None of these has been confirmed by the user. The plan is written assuming the recommendation; each row says what changes if the answer differs.

| # | Question | Assumed answer | Status | If the answer changes |
|---|---|---|---|---|
| Q8 | How the digital markup is used when a photo arrives | (b) Identify the edition: match the photo's OCR'd codes and titles to one of the 39 known prospectuses, show that edition's reviewed data, OCR only as the matching key; any disagreement or no match goes to human review. Never (c), snapping text to the nearest known value. **This plan only measures the matcher (Task 7).** The run-time matcher belongs to Phase 10 (private uploads). | assumed, pending user confirmation | (a) only: drop Task 7. (c): rejected, a new edition would silently become an old one. |
| Q9 | Photo set | Simulated photos for all 43 pages plus real phone photos of all 43 in "flat, good light" (about 30 minutes with printouts). | assumed, pending user confirmation | Fewer real photos: Task 8 gate is computed on the smaller set and says so. |
| Q10 | Review after OCR | OCR output goes through evidence, parser, audit and twin like born-digital. Every disagreement with the reference becomes a row in the B2 ledger and sheet format. | assumed, pending user confirmation | A different format would duplicate the fixer; not recommended. |
| Q11 | What "supported" means | All four: no missing or invented courses on any document; critical fields exact at least 98% (pooled); cell-text CER at most 2% on the worst document; zero silent critical errors. | assumed, pending user confirmation | Thresholds are constants in `score.py` (`MIN_CRITICAL_RATE`, `MAX_WORST_CER`); loosening is a one-line change plus a decision record. |
| Q12 | Can an OCR-derived candidate become "reviewed"? | Only through a human decision in the ledger. It stays labelled `ocr` and is never promoted automatically. | assumed, pending user confirmation | Not measurable here; enforced in the later integration plan. |
| Q13 | Tesseract model | One pinned `fil.traineddata` from tessdata_best, verified by SHA-256, used on Windows, Docker and macOS through `TESSDATA_PREFIX`. Skip `tgl` (only a legacy 4.x model, not packaged for Debian). `eng` from tessdata_best likewise. | assumed, pending user confirmation | tessdata_fast is smaller and faster but less accurate; if chosen, the bake-off must be re-run. |
| Q14 | Language grid | 6 configurations: Tesseract x {`eng`, `fil`, `eng+fil`}, RapidOCR x {`en`, `latin`, `iso:fil`}. RapidOCR reads one language per run, so it has no "both". Docling maps `iso:fil` to RapidOCR PP-OCRv6 `tl` and to Tesseract `fil`. | assumed, pending user confirmation | Grid is `engines.GRID`; adding a row is one line. |
| Q15 | New dependencies | Add `onnxruntime` to the `tools` extra; install the Tesseract program per OS (see "Dependencies and install steps"). Recorded in a decision record. **Deferred: nothing is installed by this plan's built tasks.** | assumed, pending user confirmation | Without onnxruntime RapidOCR cannot run, so the RapidOCR half of the grid is dropped (Tesseract only: 3 configurations). |
| Q16 | OCR confidence | Docling stores none on table cells. Build it by matching Docling's OCR text lines (the textline cells from `generate_parsed_pages=True`, the only cells that carry confidence) to table cells by position, threshold calibrated on the reference set. | assumed, pending user confirmation | Without it nearly every OCR error is "silent" and Q11 can never pass; the bake-off would still report, but every config would fail the fourth criterion. |

## Established facts this plan relies on

- Docling 2.129.0. RapidOCR is the only OCR engine installed and it cannot run yet: `onnxruntime` is missing and its torch backend needs a model download.
- RapidOCR handles one language per run. Docling maps `iso:fil` to RapidOCR PP-OCRv6 `tl`, and to Tesseract `fil`.
- Tesseract is not installed. `fil` exists in tessdata_best and tessdata_fast; `tgl` exists only in legacy.
- Table cells carry no OCR confidence. Only the textline cells do (Task 5).
- The corpus is 43 pages: 39 distinct PDFs across 44 paths, mostly 612 x 936 pt.
- Torch is a CPU-only build, so expect minutes per page for RapidOCR's torch backend and seconds for ONNX.

## Where the new code lives, and why

Chosen: sibling package `backend/bintanong_tools/ocr_bench/`, driver `scripts/ocr_bench.py`.

- `prospectus_extractor/` is the dependency-light parsing package (`course_checks.py` states "Pure functions"; Phase D keeps `identity.py` stdlib-only). The bench needs cv2, numpy, PIL and pypdfium2, and later an OCR engine. Putting it inside would drag those into every import of the extractor.
- The bench is measurement tooling with its own lifecycle (it may be deleted after the decision), while the extractor is shipped code. A sibling package can be removed without touching the extractor.
- The scorer imports `course_checks` (`normalise`, `loose`, `_audit_flagged`); the dependency points one way, bench to extractor, never back. `_audit_flagged` is underscore-named; if Phase C renames it the scorer test fails loudly and the import is the one line to fix.
- The driver goes in `scripts/` like `prospectus_course_audit.py` and `prospectus_course_compare.py`, and tests load it with `importlib` the same way.

```
backend/bintanong_tools/ocr_bench/
  simulate.py   photo simulator            tests/test_ocr_bench_simulate.py
  score.py      scorer and Q11 verdict     tests/test_ocr_bench_score.py
  engines.py    6-config grid, OCR stub    tests/test_ocr_bench_cli.py
scripts/ocr_bench.py                          simulate | ocr | score
```

## Status

| Task | State |
|---|---|
| 1 Photo simulator | built, tested |
| 2 Scorer and Q11 verdict | built, tested |
| 3 CLI driver and OCR stub | built, tested |
| 4 to 9 | not started; need Q15 (install) first |

---

## The six-configuration grid

| id | Engine | Language | Docling option it corresponds to |
|---|---|---|---|
| `tesseract-eng` | Tesseract 5 | `eng` | `TesseractCliOcrOptions(lang=["eng"])` |
| `tesseract-fil` | Tesseract 5 | `fil` | `lang=["fil"]` |
| `tesseract-eng+fil` | Tesseract 5 | `eng+fil` | `lang=["eng","fil"]` (Tesseract runs both models in one pass) |
| `rapidocr-en` | RapidOCR | `en` | `RapidOcrOptions(lang=["en"])` |
| `rapidocr-latin` | RapidOCR | `latin` | `lang=["latin"]` |
| `rapidocr-iso:fil` | RapidOCR | `iso:fil` (PP-OCRv6 `tl`) | `lang=["iso:fil"]` |

`python scripts/ocr_bench.py ocr --list` prints each id and whether its engine is present. Today all six say unavailable, with the reason.

## The photo simulation

Fixed named conditions, each applied to every rendered page (pypdfium2 at 150 dpi), seeded so that one `(seed, condition, document, page)` always gives the same JPEG bytes in the same environment (same numpy, OpenCV and Pillow versions; the plan records those versions with each run).

| Condition | What it does |
|---|---|
| `flat_good` | No distortion, JPEG 92. The ceiling; also what the real "flat, good light" photos should approach. |
| `tilt` | Up to 5 degrees rotation (0.6 to 1.0 of the maximum, either direction), page shrunk 12% on a dark desk. |
| `perspective` | Each corner moved by up to 4% of page size, as when the phone is not square to the page. |
| `blur` | Gaussian sigma 1.6 (hand shake or soft focus). |
| `dim` | Brightness 0.45 plus a 35% light falloff across the page. |
| `noisy` | Gaussian sensor noise sigma 14, JPEG 75. |
| `hard` | A mild mix of tilt 4, perspective 3%, blur 1.1, dim 0.6, noise 9, JPEG 70. |

Randomness comes from `numpy.random.default_rng` seeded by `sha256(seed | condition | "<stem>/p<N>")`, so pages never share draws and nothing depends on Python's salted `hash()` or on processing order. Output files are `<stem>_pNN_<condition>.jpg`, plus `simulate_manifest.json` (seed, dpi, conditions, image list). Default seed 20261004.

Simulated photos are a stand-in, not proof: they cannot reproduce lens distortion, glare, curl or finger shadows. That is why the real-photo gate (Task 8) is separate and has the final say.

## The real-photo protocol (Task 8)

1. Print all 43 corpus pages (plain A4 or Letter, one page per sheet; the pages are mostly 612 x 936 pt, so print on long bond or scale to fit and note the scale).
2. One phone, one session, flat on a desk, daylight or a bright lamp, page filling most of the frame, no flash. Name each file `<pdf stem>_p<NN>_real_flat.jpg` so it pairs with the reference.
3. Do not edit, crop or enhance. Strip location EXIF before the files leave the phone.
4. Photos are institutional-derived data: they live only under `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\ocr_bench\real\`, never in Git (the repo already ignores `/artifacts/ocr/`; the bench never writes inside the repo).
5. Optional extra conditions later (dim, tilted) only after `flat` is measured.

## The scorer

`score_document(reference, candidate)` takes two extractor payloads. It reuses `course_checks.normalise` and `loose`.

- **Pairing.** Courses are paired by loose code (spaces and hyphens ignored, case folded), in document order for repeated codes. An unpaired reference course is **missing**; an unpaired candidate course is **invented**. An OCR slip inside a code (`CS 1O2`) therefore shows as one missing plus one invented, which is the honest picture.
- **Critical fields:** `course_code` (exact text), `year_level`, `semester`, `lecture_units`, `lab_units`, `total_units`, `prerequisites` (as a sorted list). The exact-match rate counts every critical field of every reference course; a missing course counts all seven as wrong.
- **CER per cell.** Cells are `course_code`, `course_title`, printed units (`units.raw`) and `prerequisites_raw`. CER = Levenshtein distance / reference length, on `normalise`d text. A document's CER is total edits / total reference characters. Missing courses count their full text as deletions and invented courses count their text as insertions, so losing or inventing a row cannot hide. The corpus report names the worst document.
- **Silent critical error.** A disagreement (field mismatch, missing course or invented course) the candidate did not flag. "Flagged" means: the course has non-empty `confidence_flags`; or its source cells appear among the candidate audit's unclaimed candidates or structural anomalies; or its code appears in their text (the same reader `course_checks` and the B2 verifier use). Q16 is what puts a `low_ocr_confidence` flag on a course; before Q16 exists, almost every error is silent by construction.
- **Output.** A per-document report (counts, critical rate, CER cells, silent count, every disagreement with page and cell ids, verdict) and a corpus report. The driver writes `ocr_score.json` and `ocr_score.md` (LF) and exits 0 only if supported.

## The strict "supported" criteria (Q11)

All four must hold, and the verdict lists exactly which failed:

1. No missing or invented courses on any document.
2. Critical fields match exactly at least 98% of the time (pooled over the corpus).
3. Cell-text CER at most 2% on the worst document.
4. Zero silent critical errors.

"Supported" is per configuration and per condition, never global: a config can be supported on `flat_good` real photos and not on `dim`. The Task 8 gate states the claim in those terms.

## Confidence matching (Q16)

Docling's table cells have no OCR confidence. Docling's parsed-page textline cells (from `generate_parsed_pages=True`) do. The plan:

1. For each table cell, take the textline cells whose centre falls inside the cell box (reusing `course_checks.text_in_box`'s top-left versus y-up frame rule), in reading order.
2. Cell confidence = the minimum over its textlines (the weakest line decides); a cell with no textline gets confidence 0 and is flagged.
3. A course's confidence = the minimum over the cells that supply its critical fields. Below the threshold it gets `confidence_flags: ["low_ocr_confidence"]`.
4. Threshold: choose the lowest value at which, on the reference set, every critical error is flagged (silent count 0), then report how many correct courses that also flags. That flag rate is the cost of the threshold and is reported next to the verdict, because a threshold that flags everything passes criterion 4 trivially and helps nobody.

Calibrating on the same pages that are scored is circular. The threshold is fitted on the simulated set and judged on the real photos (Task 8), never the reverse.

## Edition matching (Q8, measurement only)

Run-time use is Phase 10. Here we only measure whether it would work:

- **Key.** The set of course codes and normalised titles from the OCR output of a photo.
- **Candidates.** The 39 distinct reference editions (the 44 paths include duplicates by hash).
- **Metrics.** Top-1 edition accuracy on the 43 pages; leave-one-edition-out, where the true edition is removed from the pool, measuring how often the matcher wrongly accepts a near neighbour instead of answering "no match" (false-accept rate; the target is 0); the confusion between near-twin editions (for example `ABComm` and `ABComm (2)`).
- **Never** replace OCR text with the matched edition's text. The matcher output is a label and a score; every disagreement still goes through review (next section).

## How review rows feed the B2 ledger and sheet

The B2 chain is: `verify_candidate` groups courses into year x semester sections with flags; `sheet.py` writes one editable Markdown sheet per candidate; `apply` turns decisions into append-only ledger lines (`ledger.make_entry`: reviewer, reason, `pdf_sha256`, locator, field, old and new value, disposition `accepted|corrected|unresolved`, `fix_id`); `materialise` rebuilds a corrected candidate. The ledger refuses unattributed, malformed or mismatched input, which is what OCR review needs.

Mapping from scorer disagreements (Task 6 builds the adapter; nothing here changes `sheet.py` or `ledger.py`):

| Scorer disagreement | B2 shape |
|---|---|
| `mismatch` on `course_code` or `course_title` | A flag on the course's row; the reference value is offered as a proposal (`title_from_pdf`-style), never applied. The reviewer picks `ok`, `fix`, `edit` or `unresolved`; the ledger field is `course_code` or `course_title`. |
| `mismatch` on `year_level` or `semester` | Ledger field `term`; proposal is the reference term. |
| `missing` course | An `unclaimed` row (`ledger.FIELD_UNCLAIMED`, `unclaimed_locator`) built from the reference course's page and cell ids. |
| `invented` course | Ledger field `row` with disposition `unresolved` or `corrected` (delete) chosen by the reviewer. |
| `mismatch` on units or prerequisites | **Gap:** `ledger.COURSE_FIELDS` is only code, title and term. Either extend the ledger with `units` and `prerequisites` fields (a B2 change, needs the user's decision) or record these as `row` + `unresolved` with the note naming the field. Open decision O1 below. |

Rules that stay true: the OCR candidate is labelled `ocr` in its payload and in every sheet header (Q12); an `accepted` or `corrected` ledger decision is the only path to a reviewed state; the reference value shown as a proposal comes from the born-digital data of the matched edition (Q8) and is clearly marked as such; the reviewer reads the photo, not the reference, to decide. `pdf_sha256` in OCR entries is the hash of the photo file, so a re-shot photo cannot inherit decisions.

## Dependencies and install steps (Q15, deferred)

Nothing below is done by Tasks 1 to 3, and nothing here may be run until the user confirms Q15.

| | Windows | Docker (Debian/Ubuntu) | macOS |
|---|---|---|---|
| Tesseract program | `winget install tesseract-ocr.tesseract` (5.5.3), then confirm `tesseract --version` is on PATH | `apt-get install tesseract-ocr` (5.3) | `brew install tesseract` |
| `fil` and `eng` models | Download the pinned `fil.traineddata` (tessdata_best) and `eng.traineddata`, verify SHA-256 against the value recorded in the decision record, place in one folder, set `TESSDATA_PREFIX` | Same files, copied into the image at a fixed path, `ENV TESSDATA_PREFIX=...` | Same, `export TESSDATA_PREFIX=...` |
| RapidOCR | add `onnxruntime` to the `tools` extra in `backend/pyproject.toml`, regenerate `uv.lock`, `uv sync --extra tools` | same, in the image build | same |
| RapidOCR models | Downloaded on first use by Docling; for reproducibility pre-fetch and record their hashes | same | same |

Do not use `tgl`. The apt package's own `fil` may be the tessdata_fast variant; the pinned tessdata_best file through `TESSDATA_PREFIX` overrides it so all three OSes read the same model.

Files that change at install time, in a separate approved step: `backend/pyproject.toml`, `backend/uv.lock`, the Dockerfile, a decision record under `docs/`. This plan's built tasks touch none of them.

---

## Task 1: Photo simulator (built)

**Files:**
- Create: `backend/bintanong_tools/ocr_bench/__init__.py`, `backend/bintanong_tools/ocr_bench/simulate.py`
- Test: `tests/test_ocr_bench_simulate.py`

- [x] Red: tests import `ocr_bench.simulate`, which does not exist (`ImportError: cannot import name 'simulate'`).
- [x] Green: 15 tests pass, covering byte-identical output for the same seed per condition, a different seed or page id changing the random conditions, unchanged input array and output size, the fixed condition names, an error for an unknown condition, dim darker than `flat_good`, blur softer, noise noisier, tilt and perspective showing desk at the corner, and `simulate_pdf` repeatable across runs and skipping missing pages.
- One test needed its measure corrected before it went green: blur does not lower total edge variation (a blurred step has the same total), so sharpness is the steepest edge.

## Task 2: Scorer and Q11 verdict (built)

**Files:**
- Create: `backend/bintanong_tools/ocr_bench/score.py`
- Test: `tests/test_ocr_bench_score.py`

- [x] Red: `ImportError: cannot import name 'score'`.
- [x] Green: 13 tests pass: self-score is supported with 100% and CER 0; missing and invented reported and failing; a code slip is one missing plus one invented; spacing-only code difference pairs the course but fails the exact field; wrong critical fields lower the rate (18 of 21) and name the field; CER per cell and per document; Levenshtein; silent versus flagged (course flags and candidate audit); lost-course text counts in CER; the four Q11 criteria independently, including the exact boundaries 98% and 2%; corpus worst document and pooled rate; empty corpus is not supported.
- One real defect found by its own test: `score_corpus` reported an empty worst-document name because it read the name from the report, not from the mapping key; fixed to use the key.

## Task 3: CLI driver and OCR stub (built)

**Files:**
- Create: `backend/bintanong_tools/ocr_bench/engines.py`, `scripts/ocr_bench.py`
- Test: `tests/test_ocr_bench_cli.py`

- [x] Red: `ImportError: cannot import name 'engines'`.
- [x] Green: 7 tests pass: the grid is the six Q14 ids; a missing engine exits 3 with "engine not installed"; an unknown config exits 2; `--list` shows all six; `simulate` writes the images and an LF manifest; `score` exits 0 for a document against itself and 1 for a damaged copy with reasons in `ocr_score.md`; a reference with no candidate file counts every course as missing.
- `engines.availability` looks only for the `tesseract` executable and the `rapidocr` and `onnxruntime` packages (via `importlib.util.find_spec`, never importing them). `engines.ADAPTERS` is the plug-in point: Task 4 registers one function per engine.

---

## Task 4: Engine adapters and the six-config run (needs Q15)

**Files:**
- Modify: `backend/bintanong_tools/ocr_bench/engines.py` (register adapters)
- Create: `backend/bintanong_tools/ocr_bench/convert.py` (photo or PDF page to extractor payload through the existing evidence, parser, audit and twin chain with the config's OCR options)
- Test: `tests/test_ocr_bench_engines.py`

- [ ] Prerequisite: Q15 confirmed and the install done (separate commit touching `pyproject.toml`, `uv.lock`, decision record).
- [ ] Red: with a fake adapter registered, `run_ocr` calls it with the config and folders; with none, it raises `EngineNotInstalled`. With real engines, a one-page `flat_good` photo run produces a payload that `score_document` can read.
- [ ] Green: adapters call Docling's `ImageFormatOption` / pipeline with `do_ocr=True`, `force_full_page_ocr=True`, the config's lang list, and `generate_parsed_pages=True` (needed for Task 5). Each run writes the engine version, model file hashes, config id and Docling version into its output folder.
- [ ] Gate: all six configs run on one page without error; time per page is recorded (CPU-only torch).

## Task 5: Confidence matching (Q16)

**Files:**
- Create: `backend/bintanong_tools/ocr_bench/confidence.py`
- Test: `tests/test_ocr_bench_confidence.py`

- [ ] Red: with synthetic textline cells and table cells, a cell holding a 0.4-confidence line gets confidence 0.4, a cell with no textline gets 0, a course takes the minimum of its critical cells, and below threshold it receives `low_ocr_confidence`.
- [ ] Green: implement the matching in "Confidence matching" above; `calibrate(reference_docs, candidates)` returns the lowest threshold with zero silent errors plus the false-flag rate.
- [ ] Gate: calibrated on the simulated set; the false-flag rate is printed next to the verdict.

## Task 6: Review-row adapter to the B2 format

**Files:**
- Create: `backend/bintanong_tools/ocr_bench/review.py`
- Test: `tests/test_ocr_bench_review.py`
- Do not modify: `verify.py`, `fixes.py`, `ledger.py`, `sheet.py`, `fixer_cli.py`

- [ ] Prerequisite: open decision O1 answered.
- [ ] Red: a scorer report with one of each disagreement kind yields sheet rows and flags as in the mapping table; `ledger.make_entry` accepts each resulting decision; an entry recorded against another photo's hash is reported, never applied (existing ledger behaviour, asserted by the adapter test).
- [ ] Green: implement the mapping; the candidate payload carries `source_kind: "ocr"` and the sheet header shows it.
- [ ] Gate: the sheet for one real photo opens in the existing `fixer_cli sheet` / `apply` path with no change to those modules.

## Task 7: Edition-matching measurement (Q8, measure only)

**Files:**
- Create: `backend/bintanong_tools/ocr_bench/edition.py`
- Test: `tests/test_ocr_bench_edition.py`

- [ ] Red: with three tiny synthetic editions, the right one is top-1; with the true edition removed the matcher answers "no match" instead of a near neighbour; near-twin editions are reported as ambiguous.
- [ ] Green: set-overlap on course codes plus title similarity, score and margin reported, never any text substitution.
- [ ] Gate: top-1 accuracy, false-accept rate (target 0) and twin confusion printed for the 43 pages.

## Task 8: Real-data gates

- [ ] Simulated: run `simulate` over all 43 pages x 7 conditions (301 images), run all six configs, `score` each (config x condition). Record the table of verdicts.
- [ ] Real: photograph the 43 pages (protocol above), run the six configs, `score`. Report per config: missing, invented, critical rate, worst-document CER, silent count, verdict, false-flag rate.
- [ ] The result is one of: a named config is "supported" on flat good photos (and which conditions it also survives), or none is, with the criterion that failed. Either is a valid outcome; neither authorises pipeline integration by itself.
- [ ] Outputs only under `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\ocr_bench\`. `git status` shows no images, PDFs or reports.

## Task 9: Decision record

- [ ] Write `docs/` decision record: Q8 to Q16 final answers, the install, pinned model hashes, and the measured result. Only then does an integration plan (after Phase D) get written.

---

## Open decisions for the user

- **Q8 to Q16:** confirm "all recommended" or name the ones to change (table above).
- **O1:** B2's ledger can correct only code, title and term. OCR disagreements on units and prerequisites have no ledger field. Extend the ledger (recommended, small, but it changes B2) or record them as `row` + `unresolved` with a note?
- **O2:** Is `hard` (a mix of mild conditions) a useful condition, or should the set be single-fault only?
- **O3:** Simulation DPI is 150. Real phone photos are usually larger; should the real set be downscaled to match, or measured at native size?

## Smoke results (Tasks 1 to 3)

Recorded in the final report of the run that built them; they are not reproducible from Git alone because they use institutional PDFs.
