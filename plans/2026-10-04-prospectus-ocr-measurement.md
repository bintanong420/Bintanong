# Prospectus OCR Measurement Implementation Plan

> **Publication scope (2026-10-07): plan only.** OCR implementation is excluded from this publication branch. The historical status and dependency snippets below describe their original baseline; current engine setup exists only in local worktrees. Accuracy must use fixed, PDF-backed reviewed references, never a newly generated candidate as its own answer key. Real-photo assessment and production integration remain pending. Fresh external environments are authorized; existing environments remain untouched. No attribution trailers are permitted.

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

- Docling 2.133.0 (pin moved from 2.129.0 on 2026-10-04 after the gate, see docs/decisions/docling-version.md). RapidOCR is the only OCR engine installed and it cannot run yet: `onnxruntime` is missing and its torch backend needs a model download.
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
| 4a Install GPU and CPU dependencies | done and committed; CPU is the default, the GPU path works and is faster (see "GPU and Docker") |
| 4b Engine adapters and the six-config run | bare-engine adapters built and run on one page for all six configs; the Docling payload conversion is not done |
| 4c Throughput measurement, CPU versus GPU | figures taken on 3 pages (ad hoc script, in "GPU and Docker"); the `bench` subcommand is not built |
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
- **Session only (decided 2026-10-04).** A user's OCR review decisions live in the anonymous session and vanish when it ends (explicit deletion, idle expiry, failure cleanup, service restart). They are never written to a file that outlives the session, to the database, to logs, traces or backups, and there is no account, profile or identifier to attach them to. This matches the master plan: no persistent identity (15.2), deletion after extraction (15.1 steps 8 and 9), no persisted identifiers in OCR artifacts (15.3). The B2 ledger *format* is reused, but in the session it is an in-memory (or session tmpfs) list of the same lines; the on-disk ledger file is only for the researcher's own bake-off runs and the maintainer tool.
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

- `reviewer` is the opaque anonymous session id (no account exists; it dies with the session); `reason` is the question id plus any note; `via` is `"questions"`; `section` is the year x semester section id; `fix_id` is empty (no proposal) or the id of the proposal shown.
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

## Setup from a clean clone

Everything needed is in the repository on this branch; nothing depends on this machine's state.

1. **Python environment.** From the repository root, pick ONE extra (they conflict by design):
   - NVIDIA GPU, Windows or Linux: `uv sync --project backend --extra tools --extra dev --extra ocr-gpu` (CUDA 13.0 torch wheels from the `pytorch-cu130` index, `onnxruntime-gpu[cuda,cudnn]`, the CUDA and cuDNN runtime libraries as pip wheels, so no system CUDA toolkit is needed; only an NVIDIA driver that supports CUDA 13).
   - CPU only, or macOS: `uv sync --project backend --extra tools --extra dev --extra ocr-cpu`.
   To try it without touching the working venv, set `UV_PROJECT_ENVIRONMENT` to a throwaway folder first.
2. **Tesseract program.** Windows `winget install -e --id tesseract-ocr.tesseract`; Debian/Ubuntu `apt-get install tesseract-ocr`; macOS `brew install tesseract`.
3. **Pinned models.** `python scripts/fetch_tessdata.py` downloads `fil.traineddata` and `eng.traineddata` from tessdata_best at commit `e2aad9b983032bb1beff9133104a67cdbb87ca4d` (tag 4.1.0), verifies SHA-256, and prints the folder to use as `TESSDATA_PREFIX`. Default folder is outside the repository (`%LOCALAPPDATA%\bintanong\tessdata`, `~/Library/Application Support/bintanong/tessdata`, `~/.local/share/bintanong/tessdata`); `--dest` overrides it, `--check` only verifies.
   - `fil` SHA-256 `04a7d20dcd2e1869375cbf47b59d8ed4ceea98c7f01706269eced3945b763647`
   - `eng` SHA-256 `8280aed0782fe27257a68ea10fe7ef324ca0f8d85bd2fd145d1c2b560bcb66ba`
4. **Check.** `tesseract --list-langs` (with `TESSDATA_PREFIX` set) must list `fil` and `eng`; `python scripts/ocr_bench.py ocr --list` shows which of the six configs can run.

Files that carry this setup: `backend/pyproject.toml` (extras `ocr-gpu` and `ocr-cpu`, declared conflicting; the `pytorch-cu130` index; `[tool.uv.sources]` routing `torch` and `torchvision` to it only for `ocr-gpu` on Windows and Linux), `backend/uv.lock`, `scripts/fetch_tessdata.py` with `tests/test_ocr_fetch_tessdata.py`.

---

## GPU and Docker

The user's decision (2026-10-04): CPU is the default and stays the default (master plan 5.3: OCR on CPU initially); a working GPU path is kept, especially in Docker, because Docker is part of CI/CD. This section is what was found and measured; the committed pieces are `docker/ocr.Dockerfile`, the `ocr-cpu`/`ocr-gpu` extras, the `gpu` marker (registered in `backend/pyproject.toml`) and `tests/test_ocr_gpu_smoke.py`, which skips itself without a CUDA device (no `tests/conftest.py`: Phase D owns the single conftest and can absorb this skip).

### Measured on this machine (RTX 4060 Laptop, 8 GB; driver 616.86; onnxruntime-gpu 1.30.0, cuDNN 9.24, CUDA 13.0 wheels)

Three real pages, one process, warm pass. The numbers earlier in this plan for the GPU (18 s per page) were taken with a setting that was avoidable; these replace them.

| Config | CPU s/page | GPU s/page | GPU speed-up |
|---|---|---|---|
| rapidocr-en | 7.05 | 3.2 | 2.2x |
| rapidocr-latin | 8.38 | 1.94 | 4.3x |
| rapidocr-iso:fil | 11.0 | 3.15 | 3.5x |

Peak GPU memory about 1.9 GB (system-wide reading, 0.4 GB of it already in use). Recognized text on the GPU was identical to the CPU text on the BSA page for all three configs (394, 376 and 394 lines, 0 differing lines). On a synthetic 40-line page the GPU and CPU text agreed except for one character on one unreadable line (hence the 98% line-similarity tolerance in the GPU smoke test).

Where the time goes (rapidocr-en, one page): CPU detection 1.4 to 2.0 s, classification 0.8 s, recognition 4.6 to 6.1 s; GPU detection 0.3 to 0.5 s, classification 0.5 to 0.8 s, recognition 2.7 to 3.1 s.

**Docling layout and table models on CUDA versus CPU** (`--device cuda` against `--device cpu`, whole extractor process including model load, 3 PDFs, one page each; torch 2.14.0+cu130):

| PDF | CPU | CUDA |
|---|---|---|
| BSA architecture | 98.2 s | 29.8 s |
| ABComm | 46.8 s | 29.8 s |
| ABComm (2) | 46.8 s | 31.2 s |

Course fields were identical between CPU and CUDA for all three (77, 50 and 50 courses, `compare_payloads` reports no difference). That is evidence for Phase D decision D2 (device stays out of the cache identity), on three pages; it is not a proof. Docling's own docs say table batching does not use the GPU yet and that larger `layout_batch_size` and `ocr_batch_size` help on GPU (not tried here).

### The cuDNN failure, the slowness, and what fixed them

1. **Slowness is a known RapidOCR default.** RapidOCR sets `cudnn_conv_algo_search` to `EXHAUSTIVE`, which searches again whenever an input shape changes. The recognizer gets one differently shaped crop batch nearly every call, so the search never pays off. Docling issue 4167 measured 4.4 times slower than CPU on an L4 and shows `DEFAULT` giving 1.6 times faster; PR 4168 to pin it is open and not merged, so Docling 2.129.0 and 2.133.0 are unpatched. Sources: https://github.com/docling-project/docling/issues/4167 and https://github.com/docling-project/docling/pull/4168. ONNX Runtime's documentation for the CUDA provider lists `EXHAUSTIVE` as the default and gives the three options (https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html).
2. **`HEURISTIC` is the setting used here**, not `DEFAULT`: `DEFAULT` runs but picks a slow convolution algorithm (a 6x640 batch took 240 ms against 14 ms with `HEURISTIC` once the failure below was avoided, and CPU takes 124 ms). An earlier run in this plan reported 18 s per page because it used `DEFAULT`.
3. **The `CUDNN_STATUS_EXECUTION_FAILED_CUDART` failure** (a `ReduceMean` node of the PP-OCRv6 recognizer, `cudnnReduceTensor`) depends on the call order, not on the algorithm setting. It happened when the first call into a fresh recognizer session was a batch of 6 crops, under every algorithm setting except `DEFAULT`, and did not happen when a single-crop call (1x3x48x160) came first, for any later shape. A one-crop warm-up in `_rapidocr_engine` fixes it. I did not find the cause: no ONNX Runtime issue matched this exact message (the closest are generic cuDNN failures, e.g. https://github.com/microsoft/onnxruntime/issues/21825 and https://forums.developer.nvidia.com/t/reducesum-error/341556). Candidates not yet separated: a lazily loaded cuDNN runtime-compiled kernel (the pip wheels pair NVRTC 13.0.88 with nvJitLink 13.4.92), or a cuDNN 9.24 reduction bug. If a later onnxruntime-gpu or cuDNN wheel changes this, `tests/test_ocr_gpu_smoke.py` is the check, and the warm-up can then be removed.
4. **Tried and not needed.**
   - *Bucketed recognizer widths* (rounding each batch's width up to 160 or 320 px, which cut the distinct input shapes from 37 to 7 and 4): no change (17.9 and 17.8 s against 18.1 s per page) with `DEFAULT`, so shape count was not the bottleneck once the search was off; not adopted.
   - *IO binding*: output copy was not the cost (237 ms without copy against 252 ms with copy for a 36 MB output); not adopted.
   - *TensorRT provider*: it is listed by the wheel but needs TensorRT's own libraries, which the pip wheels do not include, and ONNX Runtime's TensorRT page documents engine caching and explicit dynamic-shape profiles (`trt_engine_cache_enable`, `trt_profile_*_shapes`) with a version table that, on the copy read, stops at CUDA 12 (https://onnxruntime.ai/docs/execution-providers/TensorRT-ExecutionProvider.html). Not tried: the CUDA provider already beats the CPU and TensorRT adds an install and a cache to maintain.
   - *RapidOCR torch backend*: not tried for the same reason.
5. **DLL source.** The adapter imports torch before onnxruntime so both use the same CUDA and cuDNN libraries, then calls `onnxruntime.preload_dlls()` (a no-op after torch). ONNX Runtime documents `pip install onnxruntime-gpu[cuda,cudnn]` and that `preload_dlls()` searches PyTorch's folders first, then the NVIDIA site-packages. The torch-first import was not shown to be necessary once the warm-up exists; it is kept because it avoids loading two copies of the CUDA libraries in one process.

### Versions and requirements (from the vendors)

- ONNX Runtime 1.30.x GPU wheels on PyPI are built for CUDA 13.0 and cuDNN 9.x; a CUDA 13.0 build needs CUDA 13.0 or newer, and cuDNN 8 and 9 builds are not interchangeable (ONNX Runtime CUDA provider page above). `onnxruntime-gpu` 1.30.0 declares optional `cuda` and `cudnn` extras that pull `nvidia-*` wheels for CUDA 13.
- uv: per-platform and per-extra wheel indexes for torch, with conflicting extras, are documented at https://docs.astral.sh/uv/guides/integration/pytorch/. The repository uses the documented pattern: `pytorch-cu130` for `ocr-gpu` on Windows and Linux, `pytorch-cpu` for `ocr-cpu` on Linux only (PyPI's Linux torch drags in the CUDA stack, which made the CPU image huge in principle; Windows and macOS PyPI wheels are already CPU), explicit indexes, extras declared in `[tool.uv] conflicts`.
- Docling: `AcceleratorOptions(device=...)` or the `DOCLING_DEVICE` and `DOCLING_NUM_THREADS` environment variables; OCR on GPU through `docling[onnxruntime]` with `RapidOcrOptions(backend="onnxruntime")` (https://docling-project.github.io/docling/usage/gpu/ and https://docling-project.github.io/docling/reference/pipeline_options/). The repository's `--device` option already passes the device.

### Docker

**Base image: slim Python is enough.** `python:3.13.15-slim-bookworm` plus the `ocr-gpu` extra works because torch's `+cu130` wheel and the `nvidia-*` wheels carry the CUDA, cuBLAS and cuDNN runtime. An `nvidia/cuda:13.0.x-cudnn-runtime-ubuntu24.04` image exists (Docker Hub: https://hub.docker.com/r/nvidia/cuda/tags) and is the fallback if a system-library issue appears, at a larger size; it was not needed. What the host must supply is the driver: the NVIDIA Container Toolkit injects `libcuda` at run time, and `NVIDIA_DRIVER_CAPABILITIES=compute,utility` is set in the image.

**Host setup.**
- Linux: NVIDIA driver, then the NVIDIA Container Toolkit configured as a Docker runtime, then `docker run --gpus all` or the Compose device reservation below.
- Windows with Docker Desktop (WSL 2 backend): install only the Windows NVIDIA driver; CUDA appears inside WSL 2 as a stub `libcuda`, and no Linux driver may be installed in WSL (NVIDIA: https://docs.nvidia.com/cuda/wsl-user-guide/index.html). That guide names R495 or later for CUDA on WSL 2, Windows 11 (Windows 10 needs the Insider channel), a WSL kernel of at least 4.19.121 with 5.10.16.3 or later recommended, the Container Toolkit minimum v2.6.0 with libnvidia-container 1.5.1, and says only `--gpus all` is supported on multi-GPU systems. This machine's driver (616.86, CUDA UMD 13.4) is far above R495 and above the CUDA 13.0 the wheels need. The `docker info` of this machine's Docker Desktop (29.4.3, later auto-updated to 29.8.1) lists an `nvidia` runtime.
- macOS: Docker has no GPU access; use the CPU image. On macOS outside Docker, use `ocr-cpu`.
- `wsl2` memory is capped at 8 GB in this machine's `.wslconfig`; one OCR container used under 2 GB of GPU memory, and the build is the heavy step.

**Images, built and run here.**
- CPU image: `docker build -f docker/ocr.Dockerfile -t bintanong-ocr:cpu .` built in 1221 s on this connection (the first attempt, 424 s in, failed when Docker Desktop restarted and its daemon dropped; the retry succeeded), 2.71 GB. In the container: Tesseract 5.3.0 (Debian bookworm's package) lists `fil` and `eng` from the hash-verified `/opt/tessdata`; torch 2.14.0+cpu; onnxruntime providers `CPUExecutionProvider` (plus Azure); `ocr --config tesseract-fil` and `ocr --config rapidocr-iso:fil` on the BSA page ran in 31 s in total, and the RapidOCR text was identical to the host CPU run (0 of 394 lines differ).
- GPU image: `docker build -f docker/ocr.Dockerfile --build-arg OCR_EXTRA=ocr-gpu --build-arg OCR_DEVICE=cuda -t bintanong-ocr:gpu .` -- built on the second attempt (the first stalled for more than 30 minutes downloading the 403 MB nvidia-cublas and 528 MB nvidia-cudnn-cu13 wheels inside the build and was stopped; the retry reused the cached layers and finished in 467 s), 10.8 GB. Run with `docker run --rm --gpus all`: `nvidia-smi` inside shows the RTX 4060 Laptop and driver 616.86; torch 2.14.0+cu130 reports CUDA available; onnxruntime lists `CUDAExecutionProvider`; `ocr --config rapidocr-iso:fil` ran on CUDA in 4.27 s for the BSA page and its text is identical to the host CPU run (0 of 394 lines differ). That first GPU image did not contain the RapidOCR models (they were fetched from ModelScope at first use and one fetch failed), so the models are now baked in; see "RapidOCR models baked into both images" below.

**Compose override** (kept in the plan; the repository's existing `compose.gpu.yaml` is the master plan's GPU override and currently holds only the `bintu` service, so this would be added to it as an `ocr` service when the master plan's ingest container is built):

```yaml
# compose.yaml (CPU, the default)
  ocr:
    build:
      context: .
      dockerfile: docker/ocr.Dockerfile
    environment:
      OCR_BENCH_DEVICE: cpu
    volumes:
      - ${OCR_INPUT_DIR:?Set OCR_INPUT_DIR}:/in:ro
      - ${OCR_OUTPUT_DIR:?Set OCR_OUTPUT_DIR}:/out

# compose.gpu.yaml (override: docker compose -f compose.yaml -f compose.gpu.yaml up ocr)
  ocr:
    build:
      args:
        OCR_EXTRA: ocr-gpu
        OCR_DEVICE: cuda
    environment:
      OCR_BENCH_DEVICE: cuda
      NVIDIA_VISIBLE_DEVICES: all
      NVIDIA_DRIVER_CAPABILITIES: compute,utility
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

**Image size and the CPU and GPU split.** One Dockerfile, one build argument (`OCR_EXTRA`), two tags. The CPU image installs CPU torch from the PyTorch CPU index on Linux, so it carries none of the CUDA stack (2.71 GB at that point, 3.98 GB after the RapidOCR models and Docling 2.133.0 were added, most of it Docling's own dependencies). The GPU image adds the CUDA 13.0 torch wheel and the `nvidia-*` wheels. The master plan's planned `docker/ingest.Dockerfile` (`uv sync --extra tools`, no OCR extra, no Tesseract, torch from PyPI, which on Linux pulls the CUDA stack) is not changed by this plan; when ingest and OCR merge into one image, this Dockerfile is the pattern (`--extra tools --extra ${OCR_EXTRA}`).

### RapidOCR models baked into both images

`scripts/fetch_rapidocr_models.py` (with `tests/test_ocr_fetch_rapidocr_models.py`) builds each of the three RapidOCR configs once on CPU, which makes RapidOCR download every model it needs, and writes the SHA-256 of each file to `/opt/rapidocr-models.json` in the image. RapidOCR itself checks each download against the SHA-256 listed in its `default_models.yaml` (it logs "File exists and is valid" and redownloads on a mismatch), and all five fetched hashes below are present in that file, so the fetch is hash-verified. The Dockerfile runs it as a `RUN` step after the Tesseract models.

| File | SHA-256 |
|---|---|
| `PP-OCRv6_det_small.onnx` | `090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f` |
| `PP-OCRv6_rec_small.onnx` | `6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884` |
| `ch_PP-OCRv5_det_mobile.onnx` | `4d97c44a20d30a81aad087d6a396b08f786c4635742afc391f6621f5c6ae78ae` |
| `ch_ppocr_mobile_v2.0_cls_mobile.onnx` | `e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c` |
| `latin_PP-OCRv5_rec_mobile.onnx` | `b20bd37c168a570f583afbc8cd7925603890efbcdc000a59e22c269d160b5f5a` |

Five files serve the three configs: `en` and `iso:fil` share the PP-OCRv6 detector and recognizer (the language difference is the recognizer's key set inside the file), `latin` uses the PP-OCRv5 Latin recognizer, and all three use the PP-OCRv5 detector and the classifier where they apply. These are the versions of RapidOCR 3.9.2 (models under `.../RapidOCR/resolve/v3.9.2/...`); a RapidOCR upgrade changes them and this table must be refreshed.

**Offline proof** (Docling 2.133.0 lock, images rebuilt): `docker run --rm --gpus all --network none bintanong-ocr:gpu python scripts/ocr_bench.py ocr --config <config> ...` for all three RapidOCR configs on the BSA page. Exit 0 for all; provider `CUDAExecutionProvider`; RapidOCR time 2.81 s (`en`), 1.97 s (`latin`), 2.90 s (`iso:fil`); container wall time 11.9, 7.8 and 8.3 s including start and model load; text identical to the host CPU run (394, 376 and 394 lines, 0 differing). The CPU image with `--network none`: exit 0 for all three, wall 15.3, 12.4 and 13.8 s. Image sizes after baking the models and moving to Docling 2.133.0: CPU 3.98 GB (builds in 769 s), GPU 12.1 GB (builds in 380 s with a warm layer cache).

### Known limits of this GPU and Docker work

- **Not tested: a Linux host with the NVIDIA Container Toolkit.** Everything above ran on Windows with Docker Desktop's WSL 2 backend and its `nvidia` runtime. The Compose device reservation, `--gpus all` and `NVIDIA_DRIVER_CAPABILITIES` are the documented Linux mechanism and are expected to behave the same, but that was not exercised; the first Linux CI GPU run is the test.
- Not tested: macOS (no GPU in Docker; native `ocr-cpu` only), Linux without a GPU outside Docker, and any GPU other than the RTX 4060 Laptop with driver 616.86.
- The GPU smoke test and the CUDA warm-up were validated on one GPU and one onnxruntime-gpu and cuDNN version; the cause of the first-batch cuDNN failure is not known.
- The GPU image is built but its test suite is not run in CI until a GPU runner exists.
- TensorRT, RapidOCR's torch backend and Docling batch-size tuning were not tried.
- The images carry no `pytest`; the in-container checks were `ocr --list`, `tesseract --list-langs` and OCR runs.
- Timings are three pages (one for the container runs) on a machine that was also running other work; they are indicative, not a benchmark.

### CI

No workflow exists in the repository yet (`.github` is empty). Design, to be written when the repository's CI is set up:

- **Every push (hosted runner, no GPU):** build `docker/ocr.Dockerfile` with the default CPU target; run, inside or beside it, `tesseract --list-langs` (must show `fil` and `eng`) and `python scripts/ocr_bench.py ocr --list`; on the runner run the test suite with `uv sync --locked --extra tools --extra dev --extra ocr-cpu` and `pytest -m "not gpu"` (the `gpu` tests skip themselves when `CUDAExecutionProvider` or `torch.cuda` is missing, so even a plain `pytest` is safe on a CPU runner). Use `UV_HTTP_TIMEOUT=300`. Cache the uv cache and Docker layers; the CPU build is about 2.7 GB and the cold build took 20 minutes here, mostly downloads.
- **GPU image:** build it on a schedule or on changes to `docker/ocr.Dockerfile`, `backend/pyproject.toml` or `backend/uv.lock` (building needs no GPU); run its smoke only on a GPU runner: GitHub's hosted GPU runners are larger runners with one Tesla T4 for Team and Enterprise plans (https://docs.github.com/en/actions/reference/runners/larger-runners), or a self-hosted runner with the NVIDIA Container Toolkit. The smoke is `docker run --gpus all bintanong-ocr:gpu python -m pytest -m gpu tests/test_ocr_gpu_smoke.py` after adding `pytest` to the image or running the tests from a mounted checkout; until a GPU runner exists, the GPU image is built and not run, and that must be stated in the job summary.
- **uv lock in Docker:** the extras `ocr-cpu` and `ocr-gpu` are in one `uv.lock` (declared conflicting, so uv never resolves both together); the image chooses one with `uv sync --locked --no-dev --extra tools --extra ${OCR_EXTRA}`. `--locked` fails the build if `pyproject.toml` and `uv.lock` disagree, which is the check CI needs. The lock is universal across Windows, Linux and macOS; it was produced on Windows and the Linux image build installed from it successfully.
- **GPU test marker:** `pytest.mark.gpu`, registered in `backend/pyproject.toml`; the test module carries a `skipif` that skips unless `onnxruntime` lists `CUDAExecutionProvider` and `torch.cuda.is_available()` is true. Run them with `pytest -m gpu`.

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

## Task 4a: Install GPU and CPU dependencies (done 2026-10-04, in a throwaway venv)

Approved by the user on 2026-10-04, on the condition that the setup lives in the repository. Verified in a throwaway environment (`UV_PROJECT_ENVIRONMENT` under `%TEMP%`); the main backend venv was not touched.

**Versions chosen, and why.** `nvidia-smi`: driver 616.86, CUDA UMD 13.4, RTX 4060 Laptop GPU, 8188 MiB. `onnxruntime-gpu` 1.30.0 (latest, has cp313 Windows and Linux wheels) targets CUDA 13.0 (its `cuda` and `cudnn` extras name `nvidia-*~=13.0` wheels and `nvidia-cudnn-cu13~=9.0`). PyTorch publishes `torch 2.14.0+cu130` and `torchvision 0.29.0+cu130` for cp313 on Windows and Linux, so one CUDA major (13.0) serves both libraries and the driver (13.4) covers it. The CUDA runtime, cuBLAS, cuFFT, cuRAND, NVRTC and cuDNN 9.24 come as pip wheels, so no system CUDA toolkit is needed. `onnxruntime` 1.30.0 is the CPU extra.

**What is committed.** `backend/pyproject.toml` (extras `ocr-gpu`, `ocr-cpu`, declared conflicting; index `pytorch-cu130`; `[tool.uv.sources]` for torch and torchvision gated on the `ocr-gpu` extra and Windows or Linux), `backend/uv.lock` (additions only: onnxruntime, onnxruntime-gpu, flatbuffers, protobuf, and the `+cu130` torch and torchvision; no existing pin moved), `scripts/fetch_tessdata.py` with `tests/test_ocr_fetch_tessdata.py`.

**Checks (throwaway venv, Python 3.13.5).**
- `uv lock` resolves with no existing pin changed. (Not yet verified: a lock check on a Linux or macOS machine; the lock was produced universally.)
- `uv sync --locked --extra tools --extra dev --extra ocr-gpu` succeeded. The first attempt failed on a download timeout of the 385 MiB `nvidia-cublas` wheel at uv's default 30 s; the retry with `UV_HTTP_TIMEOUT=300` succeeded. Slow connections should set it.
- `torch 2.14.0+cu130`, `torch.version.cuda` 13.0, `torch.cuda.is_available()` True, device "NVIDIA GeForce RTX 4060 Laptop GPU".
- `onnxruntime 1.30.0` providers: TensorrtExecutionProvider, CUDAExecutionProvider, CPUExecutionProvider.
- Tesseract 5.5.3.20260724 installed with `winget install -e --id tesseract-ocr.tesseract` (the first attempt was cancelled by an installer prompt; the second succeeded). It is not on PATH in an already-open shell; `engines.find_tesseract` also looks in `C:\Program Files\Tesseract-OCR`.
- `fetch_tessdata.py` downloaded both models and the hashes matched. `tesseract --list-langs` with `TESSDATA_PREFIX` set to that folder lists `eng` and `fil`.
- All six configs ran on one real page (the BSA architecture prospectus page, `flat_good`) through `scripts/ocr_bench.py ocr`.

**Findings that change the setup** (the first version of this section reported the GPU as slower than the CPU; that was wrong and is superseded by "GPU and Docker" below, which has the cause and the corrected numbers).
1. `onnxruntime.preload_dlls()` or importing torch first is needed before the first CUDA session, because a system CUDA 13.3 is on this machine's PATH and there is no system cuDNN.
2. The PP-OCRv6 recognizer failed on its first batch with `CUDNN_STATUS_EXECUTION_FAILED_CUDART`; a one-crop warm-up call before real work fixes it (see below).
3. Tesseract's `tsv` config name is not found when `TESSDATA_PREFIX` points at a models-only folder; Tesseract then silently prints plain text. The adapter uses `-c tessedit_create_tsv=1` and now raises if the output is not TSV (the first run had silently produced empty pages).

**Quality sanity check (not the bake-off).** On the same page RapidOCR returned 376 to 394 text lines at mean confidence about 99 and found `AD-1/L`; Tesseract returned about 790 words at mean confidence 70 to 76 and did not contain `AD-1/L` as one token.

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
| Edition matching against the 39 reference prospectuses | **Added to Phase 10 as a deliverable (decided 2026-10-04):** matcher, match threshold, a no-match path to review, and the "photo differs in N places, awaiting your review" note. It reads the 39 reviewed editions from institutional storage (read-only) and the session's OCR output. | Phase 10, using Phase 2 and Phase 4 artifacts |
| User review questions and the decision log (session only) | 15.1 step 6 ("ask the user to confirm ambiguous course codes, values, or consequential extracted facts"); 6.2 student facts with `private_upload` origin and an extraction/confirmation state; 16.2 clarification replies | Phase 10 (logic), Phase 11 (UI) |
| Reviewed OCR facts feeding answers | 11.3 "student facts as request-local arguments"; 8 and 9 evidence bundle with "scoped student facts" and "conditional" labelling | Phases 6, 8, 9 |
| Institutional reviewed prospectus data shown to the student for a matched edition | 4 and 9.1 `programs`, `curriculum_versions`, `courses`; 18.3 releases | Phase 4 (storage), Phase 13 (release) |
| B2 ledger and sheet (maintainer tool); decision-log extension for units and prerequisites | 7.1 step 7 (local reviewer GUI and ledger), 16.1 (hosted reviewer UI not required) | Phase 2 (B2 branch) |
| Hard rule: OCR never reaches the institutional knowledge base | 1.2 "private uploads never update institutional knowledge", 11 "student-uploaded document must never install a rule", 15.2, 15.3 "private content cannot be retrieved through the institutional search path" | Phases 6, 10; test in Phase 10 gate |
| OCR evaluation numbers for the thesis | 17 (Phase 12 evaluation), 17.4 "never live private student uploads" (the bake-off uses the researcher's own printouts, which is allowed) | Phase 12 |
| Throughput and VRAM numbers | 5.3 "Measure before making both models and OCR compete for 8 GB VRAM"; 13.3 failure and resource behaviour; 21 hosting decision | Phases 0, 8, 13 |

### What the master plan lacks (gaps found)

1. **No edition matching** (resolved 2026-10-04: added to Phase 10 as a deliverable, see the mapping table). The master plan text itself still has to be amended: section 15 needs the matcher, threshold, no-match path and the "photo differs in N places" note.
2. **No user-facing review flow with persistence of decisions.** 15.1 step 6 has one line on confirming ambiguous values. There is no question-style flow, no decision log per user, and no endpoint for questions and answers in 16.1. Needs `GET` and `POST` review endpoints (or an extension of `/chat` clarification replies) and a typed `ReviewQuestion` and `ReviewAnswer` in 6.2.
3. **Decision-log lifetime and identity** (resolved 2026-10-04: session only). A user's decisions live in the anonymous session and vanish with it, which fits the master plan's no-persistent-identity rule, 30-minute idle session and deletion after extraction. Consequence to state in the master plan: a user who returns after expiry re-uploads and re-answers; nothing is remembered. The ledger keys entries on the photo hash and an anonymous session id instead of a reviewer name.
4. **Privacy of the decision log.** Session-only storage satisfies 15.3, but the master plan should say so explicitly: the correction log is session data, excluded from logs, traces, telemetry, evaluation exports and backups.
5. **The hard rule has no test.** 15.3 checks isolation between sessions and from retrieval but not "OCR data is never written to institutional storage". Needs an explicit Phase 10 gate case.
6. **Docling version** (resolved 2026-10-04: track the latest; see docs/decisions/docling-version.md). The master plan pins Docling 2.93.0 (section 2), which was the latest when the thesis was written; the repository pins 2.129.0 and the latest is 2.133.0, which passes the 44-input gate. The master plan table should say latest, gated instead of a number.
7. **GPU.** Master plan 5.3 says run embeddings and OCR on CPU initially and measure VRAM contention. The user now wants CUDA for OCR and for Docling's models. The master plan has no VRAM budget across Bintu-1, embeddings and OCR on one 8 GB card, no scheduling rule for bulk ingestion versus chat, and its `ingest.Dockerfile` has no GPU or CUDA version. Phase 0 and Phase 13 need the Task 4a and 4c results.
8. **OCR accuracy claim.** Master plan 1.3 treats the manuscript's accuracy as unverified, and 7.3 asks for a 10-document check on scanned institutional documents. This plan measures 43 prospectus pages, a different corpus and goal; 7.3's 10 scanned documents (handbook, charter) are not covered and remain a Phase 2 task.
9. **Image input in the intake rules.** 15.1 accepts JPEG and PNG but sets no resolution, orientation, perspective or quality gate. The simulated conditions suggest a "photo too blurry or dark, please retake" check; it is not specified anywhere.
10. **Language configuration.** 7.1 says "language configuration" without naming one. Q14's six configurations feed that choice; the master plan lacks a place to record which wins, and the Tagalog (`fil`) model pin (Q13) as a versioned artifact.
11. **Reviewer-facing material for the question flow in the UI.** 16.2 student behaviour lists text entry, upload and clarification, not a multi-question review with Yes, No, Other.

## Decisions closed and what remains open

All of Q8 to Q16, O1 to O3, and the three follow-up answers (session-only decisions, edition matching in Phase 10, setup kept in the repository, Task 4a approved) are closed. Remaining items needing the user, none blocking Tasks 1 to 3:

- The user's real photos (Task 8, real half).
- Amending the master plan text for gaps 1, 3, 4 and the others in the list above (this plan records them; it does not edit the master plan).
- Switching the main backend venv to an OCR extra (a later step for the user; Task 4a verified in a throwaway venv only).

## Smoke results (Tasks 1 to 3)

Recorded in the report of the run that built them; they are not reproducible from Git alone because they use institutional PDFs.
