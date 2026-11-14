# Exact task brief from plans\2026-10-04-prospectus-ocr-measurement.md

Read approved_execution.md and preflight-ledger.md first. They supersede obsolete base/merge/dev/version/path snippets in this preserved historical plan. Do not edit the original plan. Preserve original task requirements below unless an approved ruling supersedes them.

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
