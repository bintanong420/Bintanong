# Prospectus extractor recovery and Phase 2 handoff — 29 September 2026

## What was recovered

The paused work was Task 1 of `plans/2026-09-26-prospectus-phase2-implementation-draft.md`: a PDF-checked baseline for the parallel prospectus workstream. There was no half-written extractor patch to recover at that point. The earlier uncommitted Bintanong parser matched the dataset extractor after line-ending normalization. No session evidence established that rate limiting caused that earlier stopping point. During this continuation, two delegated agents did stop with an explicit usage-limit error; their incomplete work was inspected and finished locally.

Task 1 is now a bounded, independently reviewed pilot, documented in `.superpowers/sdd/2026-09-26-prospectus-phase2-implementation-draft/task-1-report.md` and progress commit `6d447ab`. Original BSCS and Architecture PDFs were freshly converted and every scheduled row compared visually with the original pages. The two PDFs contain 132 scheduled rows. Across nine critical field groups per row, the pilot recorded 1,112 matches, 73 mismatches, and 3 unresolved source references out of 1,188 comparisons. Those numbers describe only two PDFs; they are not corpus accuracy. The 39-distinct-PDF reference set remains incomplete.

## Source and working tree

- Authoritative conversion input: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump`, restricted to original `*.pdf` files. Generated JSON is output and diagnostic evidence, never a substitute input for the fresh regressions.
- Bintanong repo: `C:\Users\Hawksprey\source\repos\Bintanong`, branch `dev`.
- Production parser being changed: `backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py`.
- Focused new regression: `tests/test_prospectus_parser.py`.
- The earlier dirty parser baseline is included with the focused repairs because the repairs depend on it. `.gitignore` and the pre-existing untracked handoff were left alone. The earlier parser baseline had 41 insertions and 3 deletions relative to `6d447ab`; the resulting commit must be judged as that combined snapshot, not as only the new repairs. No PDF or generated corpus was added to Git. Task 2 has no independent code-review pass because the delegated reviewers hit a service usage limit.
- The formal phase ledger still says Phase 1 is next. This is authorized parallel review-only prospectus work; it does not mark Phase 2 or any curriculum release approved.

## Task 2a: merged course cells

The original Clinical Psychology page visibly has separate `Psych 9` (Abnormal Psychology, 3 units) and `Psych 10` (Field Methods in Psychology, 5 units), but Docling flattens their codes, titles, and units into cells `t0-c124`–`c126`. The next `Psych Elect`/`GE-IER` pair is similarly fused in `c129`–`c131`. The original Values Education page has separate `Ed 12` Environmental Education (3) and `FS 2` Field Study 2 (3), flattened into `c200`–`c202`/`c205`. Its other second-term `Ed 12` Integrating Course in Education is genuinely printed; duplicate code alone is not grounds to discard it.

The parser now detects two plausible codes in a single code cell, withholds the ambiguous row, and makes audit status ERROR. The anomaly includes both candidate codes, the PDF page, all contributing source-cell IDs, each cell's text and row/column span, and native page bounding boxes. This is a **safe block**, not automatic recovery of the missing courses. Detailed candidate JSON retains the audit issue for the future local reviewer; the compact essentials file says `REVIEW_REQUIRED` but does not carry the full cell evidence, so the reviewer must use the detailed candidate.

A first detector pass incorrectly treated the single Petroleum Engineering code `PetE 42 E2` as two courses. The original PDF confirms it is one code. A regression now excludes that single-letter suffix form. Petroleum Engineering still has other parsing problems; its `PetE 42`/`E2 Elective II` split in the candidate remains wrong and audit-blocked.

## Tests and source-PDF runs

The actual Docling cell texts, row/column spans, and bounding boxes for the Psychology and Values Education cases are embedded in the focused test. Against the Task 1 baseline parser, its three merged-row subcases failed. After the repair they pass, including evidence completeness and preservation of the source-real second-term `Ed 12`. The Petroleum false-positive test failed before its guard and passes afterward. Focused parser result after the Hospitality extension: **3 tests, 13 subtests passed**. Extractor self-test: **80/80**. The final complete suite is **25 passed, 13 subtests passed, 5 third-party dependency warnings**. The five warnings are dependency deprecations, not parser test failures.

Fresh original-PDF spot runs with the repaired parser:

| PDF | Observed result | Important interpretation |
| --- | --- | --- |
| Clinical Psychology | Audit ERROR; 41 candidate courses, 129 units; four merged-cell issues, including the two source-backed pairs above | Unresolved courses are withheld; the result is incomplete. |
| Values Education | Audit ERROR; 53 candidate courses, 158 units; `Ed 12`/`FS 2` merge flagged | `FS 2` is not recovered. |
| Architecture retry | Conversion completed; 77 courses, 230 row units; audit ERROR | Source PDF prints 23 for a term whose rows sum 22, and 231 grand vs row sum 230. Do not change course units to satisfy the printed conflict. |
| Petroleum Engineering after false-positive guard | Audit ERROR; `PetE 42 E2` is no longer flagged as two codes | The existing code/title mis-split remains. |

The first 44-path batch attempted every original PDF and produced 43 candidates. One Architecture conversion threw `httpx.ReadError` / WinError 10053; a fresh one-PDF retry completed. That first batch is **not** a clean 44/44 conversion result. The second forced batch, after the Petroleum guard, produced **44/44 candidates, 0 conversion exceptions, 37 audit errors, 7 warnings, 0 clean audits; strict exit 1**. Its only old-to-new audit status change was BSBA Human Resource `ok` to `warn`, caused by the Bintanong repo's missing default college semantic map. A fresh HRM run with the original source folder's semantic map explicitly supplied returned audit `ok`, 49 courses, 146 units, strict exit 0. Audit `ok` remains extractor-only and does not mean institution or human approval.

The second batch's 44 paths have 39 distinct PDF hashes. It reported 45 merged-code anomalies in 14 paths (13 distinct PDFs). Candidate course counts and units decreased in those 14 paths because ambiguous fused rows were withheld; that is a review burden, not increased extraction accuracy. BSCS and Architecture pilot candidate fields were unchanged from Task 1 in the first batch. The final batch below is the source of record for the exact final code.

## Additional source-backed code repair: old ComSci and Hospitality

The fresh 44-path candidate comparison found changes in 16 PDFs. Fourteen have the new merged-code flags. The other two were Social Work (one title spelling) and the old Computer Science prospectus (18 changed candidate records). Visual inspection of the ORIGINAL old ComSci PDF confirms codes such as `CC 3/L`; a fresh Docling cell held `CC 3 / L`, and the parser incorrectly emitted code `CC 3` with `/ L` prefixed to the title. A focused test failed on that actual cell text before the fix. The code-field adapter now removes spaces around a slash before interpreting code/title ownership. A fresh original-PDF run restores the affected codes and titles, including `CC 3/L`, `CS 1/L`, `CC 4/L`, `CS 2/L`, and `Electronics/L`. Compared with the old v5 candidate, 18 changed records fell to 2, both the consistent normalization of `Electronics/L` and its resolved prerequisite. The old ComSci result remains audit ERROR because other source and parser defects remain. Social Work's `World` → `Worl d` change is a row-ownership problem: the ORIGINAL PDF places `World` at the end of the preceding `Mathematics in the Modern World`; `SW 13` begins `Filipino Personality and Social Work`. Both the old and current candidates wrongly prepend that word. It needs source-backed diagnosis, recorded in the local Task 2c brief.

## Final runs and interruption evidence

The forced 44-PDF process under `docling_jsonified_output/task2a_final_2026-09-29/` crashed with Windows access-violation exit `-1073741819` after 36 candidates and before its normal batch manifest. Its eight missing Education PDFs were rerun separately from the ORIGINAL PDFs. All eight produced JSON and exited 1 because their audits failed. `recovery_manifest.json` honestly records the 36+8 split: 44 source paths, 39 hashes, 1 audit OK, 6 WARN, 37 ERROR, zero missing candidate outputs, and 45 merged-code issues with complete page/cell evidence. The 45 issues are in `merged_code_review_queue.jsonl` with source hash, page, text, and geometry; they are machine flags awaiting PDF review. This recovery is **not a successful single-process batch**. Candidate-to-candidate differences for all 44 paths, not source accuracy judgments, are in `candidate_delta_report.json`.

After the ComSci code fix, a fresh process-isolated run under `docling_jsonified_output/task2b_final_isolated_2026-09-29/` completed **44/44 originals, 0 processing errors, 1 audit OK, 6 WARN, 37 ERROR, strict exit 1**. It exposed another instance of the same code-boundary defect: Hospitality and Tourism code cells such as `HPC 4 / FL 1` were parsed as code `HPC 4/FL` plus title prefix `1`. The ORIGINAL Culinary and Tourism PDFs show that final digit in the code. A focused test failed before the fix. The shared course-code recognizer now accepts a numeric suffix following slash letters. Fresh affected-original runs emit `HPC 4/FL 1`, `HMPE 6/LL 1`, `HPC 8/FL 2`, `TPC 1/FL 1`, `TPC 2/FL 2`, and `TMPE 1/LL 1` with clean titles; their other audit errors remain. The old ComSci correction also persisted in the 44-path run.

A new `backend/bintanong_tools/prospectus_batch.py` command now processes only original PDFs, one child process per PDF, and atomically checkpoints `isolated_manifest.json` after each result. Its tests simulate a child access violation and verify that later PDFs still run and the prior checkpoint survives; it rejects an output directory containing an existing run. This addresses the observed single-process crash as an operational path, but it does not resolve extraction field errors or automatically resume an interrupted run.

The final source-PDF regression for this parser used the external process-isolated runner in `docling_jsonified_output/task2c_final_isolated_2026-09-29/run_isolated.py`. The supported repo command has the same one-PDF-per-child boundary and passed a fresh two-original-PDF Psychology smoke run: 2/2 candidates, 0 processing errors, 2 audit errors, exit 1. The external 44-path run and repo-command smoke are separate tests.

## Final corpus result and candidate deltas

The final isolated manifest at `docling_jsonified_output/task2c_final_isolated_2026-09-29/isolated_manifest.json` records **44/44 original PDF paths, 39 distinct hashes, 0 processing errors, 1 extractor audit OK, 6 WARN, 37 ERROR**. The runner exited **1 because 37 audits failed**; 37 child strict exits were 1 and seven were 0. Every candidate's `source_path` matches its original PDF, and every manifest hash was recalculated from that PDF. The output contains 44 detailed `*_prospectus.json`, 44 compact `*_essentials.json`, and 44 raw Docling JSON files. No `.pl` or `_rag.jsonl` companions were emitted. The compact files are review artifacts; they do not become active Bintanong facts by existing.

All 44 compact files have the same top-level key set; their 2,031 emitted course records have the same course key set. This checks JSON shape consistency with the established ComSci-style projection, not whether the field values are correct. Duplicate source paths are included in that record count.

The final run has **45 merged-code review issues in 14 paths (13 distinct PDFs)**. All 45 serialized issues have page, source-cell IDs, text, and bounding boxes. `merged_code_review_queue.jsonl` adds the PDF hash and review status `needs_original_pdf_review`. The final audit status for every one of the 44 paths is the same as the older v5 run when both use the source semantic map. The detailed `final_regression_summary.json` compares all 44 candidates. Twenty paths have at least one candidate-field difference from v5: 14 paths with merged-code flags, four Hospitality/Tourism paths with source-checked slash-code repairs (two Culinary paths are identical bytes), old ComSci with source-checked code repairs, and Social Work with an unresolved title spill. Compared with the immediately preceding complete isolated run, only those four Hospitality/Tourism paths changed candidate fields. The 132 scheduled rows in the two fully checked pilot PDFs (new BSCS and Architecture) have **zero changed candidate field values** from Task 1; their existing PDF-backed errors remain.

The 14 merged-code paths have fewer emitted course records because ambiguous rows were withheld:

| PDF | Flags | Candidate courses v5 → final | Candidate units v5 → final |
| --- | ---: | ---: | ---: |
| Clinical Psychology | 4 | 45 → 41 | 145 → 129 |
| Industrial Psychology | 2 | 46 → 44 | 140 → 134 |
| Environmental Science | 1 | 49 → 48 | 165 → 162 |
| BEEd | 1 | 55 → 54 | 185 → 182 |
| BSEd Filipino | 2 | 55 → 53 | 164 → 158 |
| BSEd Mathematics (both identical PDF paths) | 2 each | 52 → 50 each | 202 → 196 each |
| BSEd Science | 1 | 53 → 52 | 171 → 168 |
| BSEd Values Education | 1 | 54 → 53 | 161 → 158 |
| BSEd Social Studies | 2 | 56 → 54 | 161 → 152 |
| Civil Engineering | 9 | 51 → 42 | 145 → 114 |
| Electrical Engineering | 3 | 47 → 45 | 119 → 114 |
| Mechanical Engineering | 8 | 61 → 53 | 148 → 127 |
| Petroleum Engineering | 7 | 62 → 55 | 224 → 203 |

These are candidate-to-candidate deltas, **not** measured extraction accuracy or a claim that each flag is source-correct. The original PDF remains the arbiter for every withheld row.

## Remaining defects and gates

1. **BSCS standing spill:** Original BSCS page 1 has `CS Elect 4/L` standing `70% of the total units of the past semesters`; `GE-STS` below has blank prerequisite. The candidate truncates the first at `past` and assigns `semesters` to GE-STS. Cells `t0-c180`/`c181`. Current WARN/strict exit 0 misses this critical field error. The next source-backed brief is `.superpowers/sdd/2026-09-26-prospectus-phase2-implementation-draft/task-2b-brief.md`.
2. **Architecture and other titles/prerequisites:** Task 1 found 33 wrong Architecture titles, 13 wrong raw prerequisites, and 11 wrong resolved prerequisite groups. Its source-total conflict is separate. Other original PDFs show more merges and source ambiguity. The current block only prevents some fused records from looking valid.
3. **Incomplete reference set:** Only two PDFs have full row-field pilot comparisons. The other 37 distinct PDFs need source-page review before any corpus field-accuracy or 90–95% consistency claim. Forty-five machine flags are review leads, not human-certified source corrections.
4. **Release boundary:** No automatic ingestion into active Bintanong RAG/Prolog follows from an extractor audit. Phase 1 source identity/version verification, human curriculum field review, and later rule approval are still required. Full candidate JSON contains proposed RAG/Prolog objects even when audit-blocked; downstream code must enforce the release gate, not rely on their presence.
5. **Portability:** The repo default semantic-map path is absent. Bintanong must pass an explicit approved map or use a packaged source identity/configuration mechanism. An earlier diagnostic run without the map turned BSBA Human Resource from audit OK to WARN; the final run supplied the source map and had no status changes relative to v5.

## Reproduction

From `C:\Users\Hawksprey\source\repos\Bintanong`, use the locked `uv` environment and a **new output directory** for each run. The supported review-only batch command is:

```powershell
$source = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump'
$map = Join-Path $source 'Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md'
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_batch `
  -i $source -o 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\next_fresh_run' `
  --semantic-doc $map --device cpu
```

The command reads `*.pdf` originals, creates detailed and compact review JSON, and writes `isolated_manifest.json` after each PDF. It returns 1 for audit errors and 2 for processing errors. It refuses to overwrite an existing run. The final 44-path evidence above used the external `run_isolated.py` script in its output directory; the supported module was separately smoke-tested on two original PDFs.

Test commands:

```powershell
uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_parser.py tests/test_prospectus_batch.py
uv run --project backend --extra tools --extra dev python backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py --self-test
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
```

The review-only pilot artifacts are under `docling_jsonified_output/task1_baseline_2026-09-29/`. The old complete manifest is `docling_jsonified_output/v5_final_cross_college_2026-09-26/batch_manifest.json`. Keep all generated artifacts outside Git by default.
