# PalSU prospectus extractor: Phase 2 handoff for Bintanong

**Snapshot:** 26 September 2026 (Asia/Manila)  
**Status:** PDF conversion and review artifacts work across the corpus. Curriculum extraction is **not** validated for automatic release.  
**Purpose:** Give the Bintanong codebase the exact state, evidence, known defects, and next gates. This report describes the dataset workspace; it does not grant institutional approval to any prospectus.

## Read this first

1. The only authority for a fresh extraction is the PDF under `PalSU Undergraduate Prospectus Website Dump/`. Generated JSON is output and diagnostic evidence, never the input for a fresh regression run.
2. The latest complete source-PDF run is `docling_jsonified_output/v5_final_cross_college_2026-09-26/batch_manifest.json`: **44 PDF paths, 39 distinct PDF hashes, 0 processing exceptions, 7 extractor-audit passes, 37 review-required results**. Strict mode returned exit code **1 because 37 audits failed**.
3. An audit pass (`promotion_status: "VERIFIED"`) means the extractor's checks passed. It does **not** mean a human checked every field or that PalSU verified the curriculum version. The seven audit-passing files must still pass those independent gates before active RAG/Prolog use.
4. The current evidence does **not** support a claim of 90–95% course-field accuracy. The Values Education and Psychology examples below still contain wrong or missing course facts.
5. The local Bintanong parser file currently matches the dataset extractor line for line, but its Git working tree has an uncommitted modification. Integration with Bintanong's ingestion, review, release, and query paths has **not** been demonstrated by this corpus run.

## Locations and source of truth

| Item | Path or meaning |
| --- | --- |
| Dataset workspace | `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump` |
| Original PDF corpus | `PalSU Undergraduate Prospectus Website Dump/` under that workspace |
| Current extractor | `src/docling_prospectus_extractor.py` |
| Focused regression tests | `src/tests/test_real_docling_prospectus.py` |
| PDF inventory test | `src/tests/test_source_pdf_inventory.py` |
| Latest complete output | `docling_jsonified_output/v5_final_cross_college_2026-09-26/` |
| Earlier comparison output | `docling_jsonified_output/v4_final_source_pdf_2026-09-26/` |
| Original focused parser brief | `CODEX_HANDOFF_prospectus_extractor_v3_focused.md` |
| Adaptive design note | `src/docs/superpowers/specs/2026-09-26-adaptive-prospectus-extraction-design.md` |
| Local Bintanong repo | `C:\Users\Hawksprey\source\repos\Bintanong` (`https://github.com/bintanong420/Bintanong`) |
| Existing Bintanong parser copy | `backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py` under the Bintanong repo |
| Existing generic Bintanong ingest tool | `backend/bintanong_tools/ingest.py` under the Bintanong repo |

The source folder contains five pairs of byte-identical PDFs: Communication, Political Science, Midwifery, Culinary, and BSEd Mathematics. All five pairs produced identical course facts and audit errors in the latest batch. Count **39 unique PDFs** for an accuracy sample, but retain all **44 paths** in the regression run to catch path and metadata behavior.

## Work completed in this dataset workspace

### Extractor and output contract

- Kept Docling as the production converter. The current extractor has no `fitz`/PyMuPDF import. It uses Docling tables and their row/column spans, page data, and source-cell IDs; its backend fallback is Docling's PyPdfium backend.
- Preserved raw Docling JSON for inspection, enriched `*_prospectus.json` for detailed evidence/audit, `*_review.csv` for course-level review, and a separate compact `*_essentials.json` for Bintanong-style curriculum facts. The compact schema is uniform across all 44 outputs.
- Each compact course includes code, title, year, semester, total/lecture/lab units, resolved and raw prerequisites, unresolved prerequisites, standing requirements, category/elective data, and source page. It also carries top-level `extraction_status`, `audit_errors`, and `audit_warnings`.
- Kept audit failures visible and blocked downstream Prolog/RAG generation for those failures. Missing year/semester evidence, unclaimed course candidates, duplicate codes, unit mismatches, and structural anomalies remain review issues instead of being silently accepted.
- Earlier structural parser work improved split year/semester headings, continuation rows, Psychology's third-year first-semester assignment, and Summer-to-next-year handling. That work improved selected PDFs but did not eliminate broad audit failures.

### Latest cross-college parser work

- Added a generic `multiple_course_codes_in_cell` anomaly when a **source code-column cell** contains two plausible course codes. It records the table row and source-cell ID and forces review. It does not guess how to split ambiguous titles or units.
- Added a conservative adjacent-row repair for a lone prefix such as `GE-` followed by `CW GE-PS`: it forms `GE-CW` and leaves `GE-PS` as the next course. The repair also normalizes a spaced prefix such as `GE -` to `GE-` before joining.
- Guarded the repair against composite previous cells such as `Elect: ES GE-`; an earlier broad version fabricated `Elect: ES GE-MMW`. A regression test caught that, and the final complete run used the narrower guard.
- Added focused tests for two codes in one cell, the safe `GE-` continuation, spaced `GE -`, and the unsafe composite case. The tests were observed failing before their corresponding fixes and passing afterward.

### Observed difference from v4 to final v5

The final comparison across all 44 enriched JSON files found **no change** in course count or audit-promotion status. There are **16 changed `course_code` fields in five blocked PDFs**:

| PDF | Code-field changes |
| --- | ---: |
| CAH Social Work | 4 |
| CCJE Criminology | 2 |
| CTE BSEd English | 2 |
| CTE BSEd Social Studies | 2 |
| CTE BSEd Values Education | 6 |

There were also **three changed resolved-prerequisite lists in Social Work**, caused by the normalized `SW 13` code becoming resolvable. Those prerequisite relations still require PDF-backed review before rule authoring. No other compared course fields changed in this v4-to-v5 comparison. The **2,075** extracted course records remained the same total; that count is not proof that every source course was recovered.

## Latest full-corpus evidence

The final batch command used the original PDF folder:

```powershell
& 'src/.docling-venv/Scripts/python.exe' 'src/docling_prospectus_extractor.py' `
  --batch -i 'PalSU Undergraduate Prospectus Website Dump' `
  -o 'docling_jsonified_output/v5_final_cross_college_2026-09-26' `
  --force --strict --export-all
```

Observed manifest summary: `total=44`, `ok=1`, `warn=6`, `audit_failed=37`, `skipped=0`, `failed=0`. The command exited `1` from `--strict`; conversion and parsing reported **zero exceptions**. The output contains 44 enriched prospectus JSON files, 44 compact essentials JSON files, 44 raw Docling JSON files, 44 review CSVs, and one batch manifest. Because this diagnostic command used `--export-all`, it also wrote seven `.pl` and seven `_rag.jsonl` files for audit-passing PDFs. Those files are **not** institutional release approval.

The seven extractor-audit passes are:

| College | Prospectus | Audit result |
| --- | --- | --- |
| CAH | AB Philippine Studies | warning |
| CBA | BS Entrepreneurship, Agribusiness | warning |
| CBA | BS Entrepreneurship, Franchising and Trading | warning |
| CBA | BSBA Human Resource Management | OK |
| CS | BS Biology, Marine Biology | warning |
| CS | BS Computer Science, new 2025–2026 file | warning |
| CS | BS Information Technology | warning |

The new BSCS file's name includes **“for BOR approval”**. Do not infer approval from its filename or extractor audit.

| College directory | PDF paths | Audit passes | Review required | Detected merged-code cells |
| --- | ---: | ---: | ---: | ---: |
| CAD | 1 | 0 | 1 | 0 |
| CAH | 8 | 1 | 7 | 5 |
| CBA | 9 | 3 | 6 | 0 |
| CCJE | 1 | 0 | 1 | 0 |
| CHTM | 4 | 0 | 4 | 0 |
| CNHS | 3 | 0 | 3 | 0 |
| CS | 6 | 3 | 3 | 2 |
| CTE | 8 | 0 | 8 | 11 |
| CoE | 4 | 0 | 4 | 28 |
| **Total** | **44** | **7** | **37** | **46** |

The 46 merged-code-cell anomalies occur in **15 PDF paths** across CAH, CoE, CS, and CTE. Other colleges have different failures; zero in this column does **not** mean their rows are safe. The audit also records 146 `unclaimed_course_candidate` items and 85 `course_without_verified_semester` items across the 44 paths. These are anomaly-item counts, not distinct courses or an accuracy percentage; duplicate PDFs contribute twice. The manifest and each enriched JSON contain the complete per-PDF audit details.

## Known problems that are still present

### 1. Text crossing course rows or columns

The user-supplied BSEd Values Education PDF screenshot shows this class of defect. Its final compact JSON is still `REVIEW_REQUIRED` and has 54 parsed courses, 161 computed units, and a printed grand total of 164. In the final output:

- `Ed 7` is titled `Foundation of Special and Inclusive`; the visible word `Education` has shifted into `Ed 9`, whose extracted title is `Education Assessment in Learning 1`.
- The source has separate `Ed 12 Environmental Education` and `FS 2 Field Study 2` rows. Docling merges code/title/unit content into one table row. The parser emits two `Ed 12` records and **no `FS 2` course**. The new generic anomaly identifies a source cell containing `Ed 12` and `FS 2`, but does not invent the split.
- `FS 3` has raw prerequisite `FS 1 and`; the next prerequisite cell begins `2 All Gen. Ed...`. That continuation is still assigned incorrectly.
- The narrow code repair did recover `GE-CW` / `Contemporary World` and `GE-PS` / `Palawan Studies` from split code cells. This did **not** fix the neighboring title/prerequisite errors.

The original Psychology PDF has separate `Psych 9 Abnormal Psychology` (3 units) and `Psych 10 Field Methods in Psychology` (5 units). The final Clinical Psychology JSON instead has one `Psych 9` record titled `Psych 10 Abnormal Psychology Field Methods in Psychology`, with 5 units, and **no `Psych 10` record**. The new anomaly flags the merged source code cell, but the parser still needs a PDF-grounded repair or human correction.

These examples are why a successful Docling conversion and a JSON schema check cannot establish course-level correctness.

### 2. Other structural failures across colleges

- **CoE:** large numbers of merged-code cells (28 anomaly items across four PDF paths), missing/unverified semesters, code fragments, and term/grand-total mismatches. BS Mechanical Engineering has 14 audit errors; BS Petroleum Engineering has 12. These are not safe for rule generation.
- **CTE:** Values Education, Filipino, Social Studies, Mathematics, and other Education PDFs have section/total inconsistencies. Both byte-identical BSEd Mathematics paths extract 202 units while the source declares 164, including a fourth-year term-total misread. Their duplicate outputs agree with each other; they are still wrong or unresolved against the PDF.
- **CBA:** BSBA Marketing Management places all 34 extracted courses into a single term with no verified semesters; it extracts 95 units against a declared 155. Other CBA programs also have audit failures even though three pass.
- **CHTM:** BSTM has five courses without verified semesters, a declared Summer term with no extracted courses, 10 unclaimed source-code candidates, and 119 extracted units against 152 declared.
- **CNHS:** Midwifery has only five extracted courses and 13 units against 73 declared; the parser misses a declared fourth-year second semester. The duplicate PDF path has the same result.
- **CS:** old ComSci remains blocked with term-total mismatches, an unparsed `CS 3` unit, and one structural anomaly. The new BSCS audit pass does not validate the old curriculum or university approval.
- **CAD/CAH:** previous source-PDF checks found incorrect printed totals in Architecture and Communication. Their audit mismatches must be classified against the visible PDF rows rather than “fixed” by altering extracted units. Psychology in CAH separately has clear parser defects.
- **CCJE:** Criminology still has a 193-versus-195 grand-total mismatch and two fields contaminated by structural markers despite the improved `GE-UTS` code.

The examples are representative, not an exhaustive defect list. See `records[*].errors` in the manifest and `audit.structural_anomalies`, `audit.unclaimed_course_candidates`, `audit.term_unit_audit`, and course `provenance` in each enriched JSON.

### 3. What the review artifacts do and do not contain

- `*_essentials.json` is the small candidate curriculum. It includes audit error strings and each course's source page, but not the full structural anomaly list or source-cell boxes.
- `*_prospectus.json` holds detailed audit/anomaly records and course provenance. `*_docling.json` preserves the raw Docling evidence; the original PDF remains the authority for a reviewer.
- `*_review.csv` is a flat course table. It does **not** by itself surface every anomaly. Bintanong's planned manual flagger should read the detailed audit, link an issue to the PDF page/table/cell and affected course field, and preserve corrections separately from the extracted candidate.
- A one-off **Docling NativePdf** probe on the original Values Education and Psychology PDFs recovered some separate text items that the table pass had fused. It is exploratory only: no secondary-view reconciliation is integrated, no corpus-wide validation exists, and no auto-repair claim follows from that probe.

## Validation performed and limits

The final source-PDF batch above processed all 44 paths. A fresh combined test run passed **39/39** (38 focused regression tests plus one PDF inventory test), and the built-in self-test passed **80/80** on the final code. The five byte-identical PDF pairs produced identical core course facts and audit errors. The v4-to-v5 comparison found no audit-status or course-count regressions, but it is **not** a PDF-checked gold-standard accuracy evaluation.

Commands to re-run from the dataset workspace:

```powershell
Push-Location 'src'
& '.docling-venv/Scripts/python.exe' -m unittest discover -s tests -p 'test_*.py' -v
& '.docling-venv/Scripts/python.exe' 'docling_prospectus_extractor.py' --self-test
Pop-Location
```

Observed environment: Python **3.13.5**, Docling **2.129.0**, `docling-core` **2.98.1**, `docling-parse` **7.21.0**. `src/repair_docling_env.ps1` pins Docling 2.129.0 and requires `docling-parse>=7.20,<8` for this workspace. The Bintanong backend `pyproject.toml` pins Docling 2.129.0 in its `tools` extra; verify the resolved `docling-parse` version in its own environment. Dependency agreement alone is not an end-to-end integration test.

## Bintanong transfer boundary

Read-only inspection of the local Bintanong repo on 26 September found:

- Its `bintanong_prospectus_jsonifier.py` is **line-for-line identical** to this workspace's current `src/docling_prospectus_extractor.py` at inspection time. Git reports that target file as modified with uncommitted changes. Preserve and review that working-tree state before any further copy or merge.
- Its existing `backend/bintanong_tools/ingest.py` is a generic Docling-to-Markdown/text command, not a wired consumer of `*_essentials.json`, audit issues, curriculum versions, or approval state.
- No Bintanong API/DB/RAG/Prolog integration test was run as part of the 44-PDF corpus validation. A matching parser file does not mean the Phase 2 pipeline is complete.

**Safe staging contract:** accept the original PDF plus hash, run Docling and the extractor, store candidate essentials and detailed evidence, present review issues, and keep `extraction_status`, human content-review status, and issuing-office/version verification as separate fields. An active Bintanong release must require the relevant approvals and applicable curriculum version. This follows the local Phase 2 plan's requirement that no unreviewed critical extraction error reaches rule authoring. The user intends to build the manual flagger in the Bintanong codebase.

**Current export caveat:** `--export-all` writes `.pl` and `_rag.jsonl` for the seven extractor-audit passes and embeds analogous content in their full JSON. These are generated staging artifacts, **not** evidence of human or institutional approval. A Bintanong loader must not activate them solely because `promotion_status == "VERIFIED"`. For a review-only run, use the JSON and review CSV without treating the optional downstream companions as a release.

## Next work, in order

1. **Build a PDF-checked reference set.** Cover all 39 distinct PDFs, starting with Values Education, both Psychology tracks, Engineering, BSBA Marketing, Midwifery, old ComSci, and known source-total conflicts. Record exact code/title/year/semester/units/prerequisites/elective scope and page for each course. Measure missed courses, false courses, and critical-field exact matches separately. Only then state an accuracy percentage.
2. **Improve the generic row evidence path.** For flagged table rows, test a second Docling-native text view and source-line geometry as supporting evidence. Apply a split or continuation only when PDF evidence uniquely supports it; otherwise retain a review issue. Keep the parser generic across colleges and avoid per-degree correction tables.
3. **Implement the manual flagger in Bintanong.** Show the source PDF page alongside table/cell evidence and candidate facts; record the reviewer, decision, reason, original PDF SHA-256, and affected field. A changed PDF hash must reopen the decision.
4. **Enforce release gates in Bintanong.** Keep candidate essentials, content-review decisions, and issuing-office/version verification distinct. Block active RAG chunks and executable Prolog relations until the relevant critical fields and source version are reviewed and approved. Do not equate missing prerequisite data with “no prerequisites.”
5. **Regression gate after each shared parser fix.** Re-run the original-PDF 44-path batch with `--force`, compare with the previous manifest and gold reference, and report both newly repaired and newly broken fields. Do not suppress audit errors to improve the pass count.

**Recommendation:** Transfer this converter for **staging, evidence capture, and manual review now**. Delay unattended curriculum-to-RAG/Prolog release until the PDF-checked critical-field and source-authorization gates are met. The present 7/44 audit-pass count is not an extraction-accuracy percentage, and the present 37 blocked files include both parser defects and source-PDF conflicts.
