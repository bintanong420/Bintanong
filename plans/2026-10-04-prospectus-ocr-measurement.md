# Prospectus OCR Measurement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task, with superpowers:test-driven-development inside each task. Steps use checkbox (`- [ ]`) syntax for tracking. Tasks 1 to 3 are already built (see "Status"); Tasks 4 to 9 are not started. Task 4a (installing GPU/CPU dependencies) is gated on the user's go-ahead, and the real-photo half of Task 8 waits for the user to take the photos.

**Goal:** Find out, with numbers, whether any of six OCR configurations can read a photographed PalSU prospectus well enough to be called "supported" (Q11), before any OCR is wired into the pipeline. The born-digital extractor output (JSON plus markup twin) is the answer key. Disagreements become review rows in the Phase B2 format, so a human decides; OCR never promotes itself.

**Architecture:** A sibling package `backend/bintanong_tools/ocr_bench/` (simulator, scorer, engine grid) plus one driver `scripts/ocr_bench.py`. The scorer reuses `course_checks` (`normalise`, `loose`, the audit-flag reader). No extractor module changes. This is a standalone bake-off: pipeline integration of OCR comes after Phase D, as its own plan, and only if this one finds a configuration that passes.

**Tech Stack:** Python 3.13, pytest, pypdfium2, Pillow, numpy, opencv (all already in the `tools` extra). OCR engines (Tesseract 5, RapidOCR through Docling 2.129.0) are NOT installed and are not needed for Tasks 1 to 3.

**Base:** branch `feat/ocr-measurement-harness` at `6846da4`. Baseline before this plan: 277 passed + 13 subtests when the whole suite can be collected. The venv used here has no `fastapi`, so `tests/test_api_probes.py` and `tests/test_embedding_service.py` fail at collection (before and after this plan); with those two ignored the suite is 306 passed + 13 subtests, of which 35 are this plan's.

---

## Decisions (Q8 to Q16, O1 to O3)

The user answered every question on 2026-10-04. Where the answer differs from the recommendation, the user's wording governs and the row says so.

| # | Question | Decision | Status |
|---|---|---|---|
| Q8 | How the digital markup is used when a photo arrives | **Identify the edition.** Match the photo's OCR'd codes and titles to one of the 39 known prospectuses, with OCR only as the matching key. When OCR disagrees with the matched edition, the student sees that edition's reviewed data with a visible note "photo differs in N places, awaiting your review", and the disagreeing rows are marked. A photo that matches no edition goes to review too. **Never** correct OCR text toward the nearest known value. The run-time matcher belongs to Phase 10; this plan builds and measures it (Task 7). | confirmed 2026-10-04 |
| Q8 review style | **User requirement.** The user-facing review is question-style, like a Claude Code or Codex prompt, one question per item: "Is the subject `<title>` with course code `<code>` correct?" with the options Yes, No, Other (free text). It is not a raw diff table. Each answer becomes a decision-log entry (mapping in "Question-style review" below). The B2 Markdown sheet stays as the developer and maintainer tool. | confirmed 2026-10-04 |
| Q9 | Photo set | Simulated photos for all 43 pages, plus real phone photos of all 43 in "flat, good light". **The user will take the real photos later**, so the real-photo half of Task 8 is deferred, waiting on the user. | confirmed 2026-10-04; real photos deferred |
| Q10 | Review after OCR | OCR output goes through the same chain as born-digital (evidence, parser, audit, twin). Every disagreement with the reference becomes a review row in the B2 ledger format. | confirmed 2026-10-04 |
| Q11 | What "supported" means | The strict four: no missing or invented courses on any document; critical fields exact at least 98% (pooled); cell-text CER at most 2% on the worst document; zero silent critical errors. | confirmed 2026-10-04 |
| Q12 | Can OCR-derived data become "reviewed"? | **Changed from the recommendation.** OCR-derived data becomes reviewed only through the uploading user's own decisions, and only for that user. It never touches, and is never promoted into, the institutional knowledge base. There is no staff promotion path. This is a hard rule (see "Hard rule"). | confirmed 2026-10-04; changed |
| Q13 | Tesseract model | One pinned `fil.traineddata` from tessdata_best, verified by SHA-256, used on Windows, Docker and macOS through `TESSDATA_PREFIX`. `eng` likewise from tessdata_best. Skip `tgl`. | confirmed 2026-10-04 |
| Q14 | Language grid | The 6 configurations: Tesseract x {`eng`, `fil`, `eng+fil`}, RapidOCR x {`en`, `latin`, `iso:fil`}. | confirmed 2026-10-04 |
| Q15 | New dependencies | Yes. **Extended by the user:** wants CUDA for speed and throughput (RTX 4060; torch here is a CPU build). Plan `onnxruntime-gpu` with its CUDA/cuDNN requirements for Windows and Linux, CPU `onnxruntime` as the fallback, a CUDA torch build for Docling's layout and table models, per-platform wheel-index selection in `uv`, macOS on CPU or CoreML, Docker GPU runtime, a pages-per-second CPU versus GPU measurement. Nothing is installed until the user gives the go-ahead (Task 4a). | confirmed 2026-10-04; extended |
| Q16 | OCR confidence | Yes: build it by matching Docling's textline cells to table cells by position, threshold calibrated on the reference set. | confirmed 2026-10-04 |
| O1 | Ledger fields for units and prerequisites | **Extend the B2 decision log** with units and prerequisite fields. A separate agent is doing this on the B2 branch (`feat/prospectus-phase-b2-section-fixer`). This plan references that work and does not touch `ledger.py`, `sheet.py` or `fixes.py`. | confirmed 2026-10-04 |
| O2 | The combined `hard` condition | Keep it. | confirmed 2026-10-04 |
| O3 | Simulation versus real photo size | Score both: downscaled and full size. | confirmed 2026-10-04 |

## Established facts this plan relies on

- Docling 2.129.0. RapidOCR is the only OCR engine installed and it cannot run yet: `onnxruntime` is missing and its torch backend needs a model download.
- RapidOCR handles one language per run. Docling maps `iso:fil` to RapidOCR PP-OCRv6 `tl`, and to Tesseract `fil`.
- Tesseract is not installed. `fil` exists in tessdata_best and tessdata_fast; `tgl` exists only in legacy.
- Table cells carry no OCR confidence. Only the textline cells do (Task 5).
- The corpus is 43 pages: 39 distinct PDFs across 44 paths, mostly 612 x 936 pt.
- Torch is a CPU-only build, so expect minutes per page for RapidOCR's torch backend and seconds for ONNX. The development machine has an NVIDIA RTX 4060 (8 GB VRAM), which the master plan (section 5.3) also assigns to Bintu-1 and embeddings; Q15 now plans to use it for OCR.

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
| 4a Install GPU and CPU dependencies | **gated: needs the user's go-ahead** |
| 4b Engine adapters and the six-config run | not started; needs 4a |
| 4c Throughput measurement, CPU versus GPU | not started; needs 4b |
| 5 Confidence matching | not started |
| 6 Review-row adapter and question-style review model | not started; needs the B2 ledger extension (O1) |
| 7 Edition-matching measurement | not started |
| 8 Real-data gates | simulated part not started; **real-photo part deferred, waiting on the user's photos** |
| 9 Decision record | not started |

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

## The real-photo protocol (Task 8, deferred: the user takes the photos later)

Nothing in this plan waits on the real photos except the real half of the Task 8 gate. Task 8's simulated half, and everything before it, can finish first.

1. Print all 43 corpus pages (plain A4 or Letter, one page per sheet; the pages are mostly 612 x 936 pt, so print on long bond or scale to fit and note the scale).
2. One phone, one session, flat on a desk, daylight or a bright lamp, page filling most of the frame, no flash. Name each file `<pdf stem>_p<NN>_real_flat.jpg` so it pairs with the reference.
3. Do not edit, crop or enhance. Strip location EXIF before the files leave the phone.
4. Photos are institutional-derived data: they live only under `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\ocr_bench\real\`, never in Git (the repo already ignores `/artifacts/ocr/`; the bench never writes inside the repo).
5. Optional extra conditions later (dim, tilted) only after `flat` is measured.
6. Score each photo twice (O3): at full size and downscaled to a long edge of 1950 px, which is the size the simulation renders (150 dpi of a 936 pt page). The report keeps the two apart; a configuration is judged on both, and a large gap between them is itself a finding.

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

## Hard rule (Q12)

OCR-derived data stays labelled `ocr` and is reviewed only by the uploading user, for that user only.

- A decision by the uploading user changes what **that user** sees for **that upload**. Nothing else.
- No OCR-derived value, decision or ledger line is written into, indexed into, embedded into, or promoted into the institutional knowledge base (the master plan's `documents`, `chunks`, `chunk_embeddings`, `policy_rules`, `knowledge_releases`), and no code path, flag or staff action does so. There is no staff promotion path.
- The institutional prospectus data stays reviewed only through the existing researcher workflow on born-digital PDFs (master plan 7.1 step 7).
- A test in the later integration plan must assert that the OCR flow has no import of, and no write to, the institutional storage modules.

## Question-style review (Q8 review style)

The student does not see a diff table. The review is a sequence of questions, one per item, in the style of a Claude Code or Codex prompt. The B2 Markdown sheet (`sheet.py`) stays as the developer and maintainer tool and is unchanged.

A **review item** is one disagreement from the scorer-style comparison between the OCR candidate and the matched edition's reviewed data, or one OCR value with low confidence (Q16) when there is no matched edition. Each item produces one question:

| Item | Question | Yes | No | Other (free text) |
|---|---|---|---|---|
| A course row (code and title) | "Is the subject `<title>` with course code `<code>` correct?" | `accepted` | `unresolved`, or `edit` after a follow-up "What should it be?" | `corrected`, new value = the text typed |
| Term | "Is `<code>` in `<year> / <semester>`?" | `accepted` | `unresolved` or `edit` | `corrected` with the typed term (parsed by `parse_term`) |
| Units | "Does `<code>` have `<lecture>` lecture and `<lab>` lab units?" | `accepted` | `unresolved` or `edit` | `corrected` with the typed units |
| Prerequisites | "Is the prerequisite of `<code>` `<list>`?" | `accepted` | `unresolved` or `edit` | `corrected` with the typed list |
| A course the matched edition has but the photo lacks | "Your photo does not show `<code> <title>`. Is it on your page?" | `accepted` (it is, OCR missed it) | `accepted` as absent | `corrected` with what is printed |
| A row the photo has but the edition lacks | "The photo shows `<code> <title>`, which is not in the matched edition. Is it on your page?" | `accepted` | `corrected` (delete the row) | `corrected` with the typed value |

Each question shows the OCR value as the default, never the reference value as an answer. When the matched edition's reviewed value differs, it is mentioned as context ("the matching edition lists `<value>`"), and picking it is the user typing it under Other; it is never pre-selected, and nothing is ever auto-corrected toward it (Q8).

**Mapping to the B2 decision log.** Each answer is one `ledger.make_entry` call:

- `reviewer` is the uploading user's session identity (see the master-plan gaps: identity is undecided there); `reason` is the question id plus any note; `via` is `"questions"`; `section` is the year x semester section id; `fix_id` is empty (no proposal) or the id of the proposal shown.
- `pdf_sha256` is the hash of the photo file, so a re-shot photo cannot inherit decisions; `locator` is `course_locator` of the OCR candidate course (or `unclaimed_locator` for a row the photo lacks); `old_value` is the OCR value; `new_value` is the typed value for Other.
- Yes gives disposition `accepted`; Other gives `corrected` with the typed value (validated by `ledger.correction_problem`, so an invalid typed term or an empty title is refused and the question is asked again); No gives `unresolved`, or `corrected` if the user then supplies the value in the follow-up.
- Field names: `course_code`, `course_title`, `term`, `row`, `unclaimed`, plus the units and prerequisite fields the O1 extension adds on the B2 branch. Until that lands, Task 6 cannot map the units and prerequisite questions and does not start.

The questions are generated from data and answered through a thin interface (a CLI prompt first, the Next.js client in Phase 11 later), so the same answers feed the same ledger either way. `materialise` rebuilds a user-local corrected candidate from the immutable OCR extraction plus that user's applicable entries.

**Sheet versus questions.** A maintainer reviewing a failed bake-off page still uses `fixer_cli sheet` and `apply` on the OCR candidate; those commands need no change, and Task 6's gate checks that. The question flow is the product surface and the sheet is the diagnostic surface; both write the same ledger.

Rules that stay true: the OCR candidate is labelled `ocr` in its payload and in every sheet header and question header (Q12); an `accepted` or `corrected` entry is the only path to a user-reviewed state, for that user only; the ledger refuses unattributed, malformed or mismatched lines (existing behaviour).

## Dependencies, CUDA and install steps (Q15; nothing installed until the user says go)

Nothing in this section is run by Tasks 1 to 3, and nothing here may be run before the user gives the go-ahead (Task 4a). Version numbers below are what to verify against the vendors' compatibility tables at install time, then record; they are not guesses to hard-code.

### What uses the GPU and what does not

| Component | Accelerator | Notes |
|---|---|---|
| RapidOCR (ONNX backend) | `onnxruntime-gpu`, CUDA execution provider | The fast path. |
| RapidOCR (torch backend) | CUDA torch | Alternative; the plan measures it only if the ONNX path is not usable. |
| Docling layout and TableFormer models | CUDA torch (`AcceleratorOptions(device="cuda")` or `auto`) | Today torch is a CPU build, so Docling runs on CPU. |
| Tesseract | **CPU only.** It has no GPU path. Speed comes from running pages in parallel processes with `OMP_THREAD_LIMIT=1` per process. | |

### `onnxruntime-gpu` (Windows and Linux)

- The RTX 4060 is an Ada GPU (compute capability 8.9). It needs an NVIDIA driver recent enough for the CUDA major version the chosen `onnxruntime-gpu` build targets.
- Choose the `onnxruntime-gpu` release, then the CUDA and cuDNN versions its CUDA-provider requirements table names (recent releases target CUDA 12.x with cuDNN 9; CUDA 11.8 builds come from a separate package index). Record all three versions and the driver version.
- CUDA and cuDNN DLLs or shared libraries must be findable: system install on PATH or `LD_LIBRARY_PATH`, or the `nvidia-*` pip wheels with the library's own preload helper. Prefer the pip wheels in Docker, for reproducibility.
- **`onnxruntime` and `onnxruntime-gpu` must not be installed in the same environment** (they own the same Python module). "CPU `onnxruntime` as the fallback" therefore means a different extra or a platform marker selecting one or the other, not both. Proposed `backend/pyproject.toml` extras: `tools-ocr-gpu` (`onnxruntime-gpu`, Windows and Linux) and `tools-ocr-cpu` (`onnxruntime`, all platforms), declared as conflicting so `uv` never resolves both.
- Selecting the GPU in RapidOCR is a RapidOCR/Docling option (a CUDA flag or provider list); verify the exact key in the installed version and record the active provider in each run's output folder. A silent fall-back to CPU would invalidate the throughput measurement, so the adapter asserts the provider that actually ran.

### CUDA torch for Docling (Windows and Linux)

- PyPI's Windows torch wheel is CPU-only; that is why this machine has a CPU build. CUDA wheels come from PyTorch's own indexes (`https://download.pytorch.org/whl/cuXXX`), one per CUDA version. Pick the CUDA version the installed torch release offers that matches the driver, and use the same CUDA major version as `onnxruntime-gpu` where possible so one driver and one set of CUDA libraries serve both.
- How `uv` selects the wheel index per platform: declare each PyTorch index as `explicit = true` under `[[tool.uv.index]]`, then route `torch` (and `torchvision` if used) in `[tool.uv.sources]` with a marker, for example the CUDA index for `sys_platform == 'win32' or sys_platform == 'linux'`, and nothing for macOS so it takes PyPI's default wheel. Keep CPU and CUDA as separate extras marked as conflicting if a CPU-only install must stay possible (CI, macOS, machines without a GPU). Regenerate `uv.lock` and check it resolves on all three platforms.
- Docling picks the device through its accelerator options; the repo's `docling_env.py` currently fixes the pipeline options, so an OCR-specific options builder is added in Task 4b rather than editing the existing one. Note for later: Phase D decision D2 keeps device out of the cache identity on the grounds that CPU and CUDA give the same table topology; Task 4c's CPU-versus-GPU comparison is the evidence that decides whether that still holds.

### macOS

No CUDA. The baseline is the CPU path (`tools-ocr-cpu`, CPU torch from PyPI). Two optional accelerators, each used only if measurement shows a real gain and the output matches: torch's MPS device for Docling's models, and the ONNX Runtime CoreML execution provider for RapidOCR if the installed RapidOCR supports passing providers. CoreML and MPS can change numerical output or fall back for some operators; Task 4c compares their output with the CPU baseline through the scorer before any is trusted.

### Docker GPU runtime

- The host needs the NVIDIA driver; on Linux also the `nvidia-container-toolkit`, configured as a Docker runtime. On Windows, Docker Desktop with the WSL 2 backend passes the GPU through when the Windows driver supports CUDA on WSL. Docker on macOS has no GPU.
- Compose requests the device with a `deploy.resources.reservations.devices` entry (driver `nvidia`, count 1, capability `gpu`). The master plan already warns (section 5.3) that the Compose override alone does not install a working GPU runtime; the OCR image must be checked by running `nvidia-smi` and the provider check inside the container.
- Base image: a CUDA runtime image with cuDNN matching the chosen versions, or a slim image plus the `nvidia-*` pip wheels. Tesseract and its pinned `fil`/`eng` models go in the same image on every build.
- A CPU variant of the image (no GPU reservation) stays buildable for CI and for hosts without a GPU.

### Tesseract and models (all OSes)

| | Windows | Docker (Debian/Ubuntu) | macOS |
|---|---|---|---|
| Tesseract program | `winget install tesseract-ocr.tesseract` (5.5.3), confirm `tesseract --version` on PATH | `apt-get install tesseract-ocr` (5.3) | `brew install tesseract` |
| `fil` and `eng` models | Pinned tessdata_best files, SHA-256 checked against the decision record, in one folder, `TESSDATA_PREFIX` set | Same files copied into the image, `ENV TESSDATA_PREFIX=...` | Same, `export TESSDATA_PREFIX=...` |
| RapidOCR models | Fetched on first use by Docling; pre-fetch and record hashes for reproducibility | same | same |

Do not use `tgl`. The apt package's own `fil` may be the tessdata_fast variant; the pinned tessdata_best file under `TESSDATA_PREFIX` overrides it so all three OSes read the same model.

### Files that change at install time (a separate approved step)

`backend/pyproject.toml` (extras, uv indexes, sources, conflicts), `backend/uv.lock`, the OCR Dockerfile and Compose GPU entry, and the decision record. Do it first in a throwaway environment (a separate worktree and venv) so the working venv, which the whole test suite uses, is never left half-converted.

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

## Task 4a: Install GPU and CPU dependencies (GATED on the user's go-ahead)

**Files:** `backend/pyproject.toml`, `backend/uv.lock`, an OCR Dockerfile and Compose entry, a decision record. Nothing else.

- [ ] Gate: the user says go. Until then nothing in this task is run.
- [ ] In a throwaway worktree and venv: record the driver version (`nvidia-smi`), pick the CUDA, cuDNN, `onnxruntime-gpu` and torch versions per "Dependencies, CUDA and install steps", add the extras, indexes, sources and conflicts, regenerate `uv.lock`.
- [ ] Check: `uv lock` resolves for Windows, Linux and macOS; the macOS resolve contains no CUDA wheel; the CPU extra resolves without `onnxruntime-gpu`.
- [ ] Check on the RTX 4060: `torch.cuda.is_available()` is true, the ONNX Runtime provider list contains the CUDA provider, a one-page RapidOCR run reports the CUDA provider as the one used.
- [ ] Install Tesseract per OS and fetch the pinned `fil` and `eng` models; record their SHA-256 values in the decision record.
- [ ] Docker: build the GPU image, run `nvidia-smi` and the provider check inside it; build the CPU image.
- [ ] Only then merge the dependency change, as its own commit, and run the full test suite.

## Task 4b: Engine adapters and the six-config run (needs 4a)

**Files:**
- Modify: `backend/bintanong_tools/ocr_bench/engines.py` (register adapters)
- Create: `backend/bintanong_tools/ocr_bench/convert.py` (photo or PDF page to extractor payload through the existing evidence, parser, audit and twin chain with the config's OCR options and an OCR-specific accelerator options builder)
- Test: `tests/test_ocr_bench_engines.py`

- [ ] Red: with a fake adapter registered, `run_ocr` calls it with the config and folders; with none, it raises `EngineNotInstalled`. With real engines, a one-page `flat_good` photo run produces a payload that `score_document` can read.
- [ ] Green: adapters call Docling with `do_ocr=True`, `force_full_page_ocr=True`, the config's lang list, `generate_parsed_pages=True` (needed for Task 5) and a device option (`cpu` or `cuda`). Each run writes engine version, model file hashes, config id, Docling version, device and the provider that actually ran into its output folder.
- [ ] Gate: all six configs run on one page without error on CPU; the five GPU-capable ones also on GPU.

## Task 4c: Throughput, CPU against GPU

**Files:** `scripts/ocr_bench.py` (a `bench` subcommand), `tests/test_ocr_bench_cli.py`.

- [ ] Red: with a fake adapter that sleeps a known time, the subcommand reports pages per second within tolerance and refuses a run whose reported device differs from the requested one.
- [ ] Green: for each config and each device, run N pages of the simulated `flat_good` set, one cold run (model load included) and a warm run, and record pages per second, seconds for the first page, and peak VRAM. Tesseract is CPU only and is measured at 1 process and at the machine's core count.
- [ ] Compare CPU and GPU outputs for the same config with `score_document` (one as reference, one as candidate): any field-level difference is reported, because it decides whether the device belongs in the cache identity (Phase D D2).
- [ ] Gate: a table of pages per second by config and device on the RTX 4060, with VRAM next to Bintu-1's measured footprint so the master plan's 8 GB sharing question has data.

## Task 5: Confidence matching (Q16)

**Files:**
- Create: `backend/bintanong_tools/ocr_bench/confidence.py`
- Test: `tests/test_ocr_bench_confidence.py`

- [ ] Red: with synthetic textline cells and table cells, a cell holding a 0.4-confidence line gets confidence 0.4, a cell with no textline gets 0, a course takes the minimum of its critical cells, and below threshold it receives `low_ocr_confidence`.
- [ ] Green: implement the matching in "Confidence matching" above; `calibrate(reference_docs, candidates)` returns the lowest threshold with zero silent errors plus the false-flag rate.
- [ ] Gate: calibrated on the simulated set; the false-flag rate is printed next to the verdict.

## Task 6: Review items, questions and the B2 ledger

**Files:**
- Create: `backend/bintanong_tools/ocr_bench/review.py`
- Test: `tests/test_ocr_bench_review.py`
- Do not modify: `verify.py`, `fixes.py`, `ledger.py`, `sheet.py`, `fixer_cli.py`

- [ ] Prerequisite: the units and prerequisites ledger fields (O1) exist on the B2 branch and have been merged into this branch's base. This plan does not do that work.
- [ ] Red: a scorer report with one of each disagreement kind yields one question per item with the wording in "Question-style review"; each answer (Yes, No, Other with text) yields a `ledger.make_entry` that `entry_problem` accepts; an invalid typed value is refused and re-asked; an entry recorded against another photo's hash is reported, never applied (existing ledger behaviour); the reference value is never pre-selected.
- [ ] Green: implement item generation, question rendering as data (id, text, options) and answer-to-entry mapping; the candidate payload carries `source_kind: "ocr"` and every question header shows it.
- [ ] Gate: the sheet for one OCR candidate still opens in `fixer_cli sheet` and `apply` with no change to those modules, and a ledger written by the questions materialises to the same corrected candidate as the equivalent sheet decisions.

## Task 7: Edition-matching measurement (Q8, measure only)

**Files:**
- Create: `backend/bintanong_tools/ocr_bench/edition.py`
- Test: `tests/test_ocr_bench_edition.py`

- [ ] Red: with three tiny synthetic editions, the right one is top-1; with the true edition removed the matcher answers "no match" instead of a near neighbour; near-twin editions are reported as ambiguous.
- [ ] Green: set-overlap on course codes plus title similarity, score and margin reported, never any text substitution.
- [ ] Gate: top-1 accuracy, false-accept rate (target 0) and twin confusion printed for the 43 pages.

## Task 8: Real-data gates

- [ ] **Simulated (can run first).** Run `simulate` over all 43 pages x 7 conditions (301 images, including `hard`, kept per O2), run all six configs, `score` each (config x condition), full size and downscaled (O3). Record the table of verdicts.
- [ ] **Real (deferred, waiting on the user).** The user photographs the 43 pages later (protocol above). Run the six configs, `score` at full size and downscaled. Report per config: missing, invented, critical rate, worst-document CER, silent count, verdict, false-flag rate.
- [ ] The result is one of: a named config is "supported" on flat good photos (and which conditions and which size it also survives), or none is, with the criterion that failed. Either is a valid outcome; neither authorises pipeline integration by itself.
- [ ] Outputs only under `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\ocr_bench\`. `git status` shows no images, PDFs or reports.

## Task 9: Decision record

- [ ] Write `docs/` decision record: Q8 to Q16 final answers, the install, pinned model hashes, and the measured result. Only then does an integration plan (after Phase D) get written.

---

## Mapping to the master plan (the pipeline still has to be wired up later)

The user's instruction: "remember you need to wire up all of the pipeline later (based on the master plan)". This plan is a standalone bake-off; this section says where each of its parts plugs into `plans/master_implementation_plan_original_long.md` and which master phase owns it. Section numbers are the master plan's.

| Part of this plan | Plugs into | Owning master phase |
|---|---|---|
| Photo simulator, scorer, six-config grid, Q11 verdict | Master 7.3 "Ingestion verification" (the OCR check, character error rate plus critical-field errors, "a high average OCR score must not conceal a wrong prerequisite") | Phase 2 (evidence) |
| Engine install, CUDA, Docker GPU image | 5.1 `docker/ingest.Dockerfile`, 5.3 GPU override, "OCR on CPU initially", 8 GB VRAM warning; 18.1 backend host | Phase 0 (environment), Phase 13 (host) |
| OCR conversion of a photo into the extractor payload (convert, Docling OCR options, textline confidence) | 7.1 steps 2 to 4 (Docling with a pinned OCR backend, "record the actual backend and settings") for the private path | Phase 10 step 4 (isolated Docling conversion job); settings from Phase 2 |
| Upload intake (size and page limits, media types, transient workspace, deletion) | 15.1 steps 1 to 4 and 8 to 9; 16.1 `POST /uploads`, `DELETE /uploads/{id}` | Phase 10; API in Phase 11 |
| Edition matching against the 39 reference prospectuses | None. See gaps. | Proposed: Phase 10, using Phase 2 artifacts |
| User review questions and the decision log | 15.1 step 6 ("ask the user to confirm ambiguous course codes, values, or consequential extracted facts"); 6.2 student facts with `private_upload` origin and an extraction/confirmation state; 16.2 clarification replies | Phase 10 (logic), Phase 11 (UI) |
| Reviewed OCR facts feeding answers | 11.3 "student facts as request-local arguments"; 8 and 9 evidence bundle with "scoped student facts" and "conditional" labelling | Phases 6, 8, 9 |
| Institutional reviewed prospectus data shown to the student for a matched edition | 4 and 9.1 `programs`, `curriculum_versions`, `courses`; 18.3 releases | Phase 4 (storage), Phase 13 (release) |
| B2 ledger and sheet (maintainer tool); decision-log extension for units and prerequisites | 7.1 step 7 (local reviewer GUI and ledger), 16.1 (hosted reviewer UI not required) | Phase 2 (B2 branch) |
| Hard rule: OCR never reaches the institutional knowledge base | 1.2 "private uploads never update institutional knowledge", 11 "student-uploaded document must never install a rule", 15.2, 15.3 "private content cannot be retrieved through the institutional search path" | Phases 6, 10; test in Phase 10 gate |
| OCR evaluation numbers for the thesis | 17 (Phase 12 evaluation), 17.4 "never live private student uploads" (the bake-off uses the researcher's own printouts, which is allowed) | Phase 12 |
| Throughput and VRAM numbers | 5.3 "Measure before making both models and OCR compete for 8 GB VRAM"; 13.3 failure and resource behaviour; 21 hosting decision | Phases 0, 8, 13 |

### What the master plan lacks (gaps found)

1. **No edition matching.** Nothing in the master plan identifies which known prospectus a user's photo is. Phase 10 only extracts "facts/context needed for the question". Needs a new Phase 10 deliverable: matcher, threshold, no-match path, and the "photo differs in N places" note.
2. **No user-facing review flow with persistence of decisions.** 15.1 step 6 has one line on confirming ambiguous values. There is no question-style flow, no decision log per user, and no endpoint for questions and answers in 16.1. Needs `GET` and `POST` review endpoints (or an extension of `/chat` clarification replies) and a typed `ReviewQuestion` and `ReviewAnswer` in 6.2.
3. **Decision-log lifetime and identity conflict.** The user wants decisions kept for that user (Q12). The master plan has no persistent identity or profile ("avoid persistent identity/profile infrastructure"), a 30-minute idle session (15.1) and deletion of upload bytes after extraction. The ledger keys decisions on the photo's hash and a reviewer name. Open: how long a user's decisions live, where they are stored (never in institutional tables), and under what identity. This needs a user decision before Phase 10.
4. **Privacy of the decision log.** 15.3 says OCR artifacts and traces must not persist grades or identifiers. A ledger of a user's corrections is user data; the master plan has no rule for it.
5. **The hard rule has no test.** 15.3 checks isolation between sessions and from retrieval but not "OCR data is never written to institutional storage". Needs an explicit Phase 10 gate case.
6. **Docling version.** The master plan pins Docling 2.93.0 (section 2); the repository runs 2.129.0. The plan, Phase 0 pins and Phase D identity must agree.
7. **GPU.** Master plan 5.3 says run embeddings and OCR on CPU initially and measure VRAM contention. The user now wants CUDA for OCR and for Docling's models. The master plan has no VRAM budget across Bintu-1, embeddings and OCR on one 8 GB card, no scheduling rule for bulk ingestion versus chat, and its `ingest.Dockerfile` has no GPU or CUDA version. Phase 0 and Phase 13 need the Task 4a and 4c results.
8. **OCR accuracy claim.** Master plan 1.3 treats the manuscript's accuracy as unverified, and 7.3 asks for a 10-document check on scanned institutional documents. This plan measures 43 prospectus pages, a different corpus and goal; 7.3's 10 scanned documents (handbook, charter) are not covered and remain a Phase 2 task.
9. **Image input in the intake rules.** 15.1 accepts JPEG and PNG but sets no resolution, orientation, perspective or quality gate. The simulated conditions suggest a "photo too blurry or dark, please retake" check; it is not specified anywhere.
10. **Language configuration.** 7.1 says "language configuration" without naming one. Q14's six configurations feed that choice; the master plan lacks a place to record which wins, and the Tagalog (`fil`) model pin (Q13) as a versioned artifact.
11. **Reviewer-facing material for the question flow in the UI.** 16.2 student behaviour lists text entry, upload and clarification, not a multi-question review with Yes, No, Other.

## Decisions closed and what remains open

All of Q8 to Q16 and O1 to O3 are closed (table at the top). Remaining items needing the user, none blocking Tasks 1 to 3:

- Go-ahead to install (Task 4a), including which CUDA version once the driver version is read.
- The user's real photos (Task 8, real half).
- Master-plan gap 3: how long a user's decisions live, where, and under what identity.
- Master-plan gap 1: whether edition matching is added to Phase 10 as a new deliverable.

## Smoke results (Tasks 1 to 3)

Recorded in the report of the run that built them; they are not reproducible from Git alone because they use institutional PDFs.
