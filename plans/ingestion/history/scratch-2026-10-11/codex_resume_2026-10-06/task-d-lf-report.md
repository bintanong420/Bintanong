# Phase D F4 LF artifacts report

Status: implementation verified; independent parent specification and quality reviews pending.
Owner: /root/d_lf_resume, sole implementer. No subagents.
Worktree: C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d
Base: 4a0cdb794a337b9cc91846d16585478c3bb5fde0
Commit: 52da4aaca7d734e83054b1ecd39221ac09302a3b

## Implementation
Reuse publish.write_text_lf for batch JSON; set DictWriter LF record separators. Preserve UTF8-sig BOM, native minimal quoting, schema, names, all 23 columns and exact values. Raw-byte/parsed regressions cover Unicode, manifest content, CSV embedded CRLF and bare CR without a comma.

## Corrected CSV hypothesis and TDD provenance
Preserved original worker LF RED3/GREEN3 logs unchanged, not reconstructed or repeated. RED failures were Windows JSON/CSV CRLF record separators.

Bare-CR RED attempt actually passed: characterization, not failing evidence. Both main and GUI-review Python3.13.5 already quote bare CR under LF/QUOTE_MINIMAL; backend requires ==3.13.*. Root superseded QUOTE_ALL ruling; native quoting remains. Exact probes: task-d-lf-runtime-probe.log.

## Test commands and results
All pytest commands ran from the worktree, using the existing main backend .venv, PYTHONDONTWRITEBYTECODE=1, no pytest cache provider and external basetemp. Exact invocation and complete output live in the named LF logs below.


### Initial LF RED: preserved original worker evidence
Log: task-d-lf-red.log

```text
COMMAND: C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe -m pytest -q tests/test_prospectus_batch_skip.py tests/test_prospectus_publish.py -k "batch_manifest_writes_utf8_lf or review_csv_uses_lf_records" -p no:cacheprovider --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\lf-red-temp"
3 failed, 126 deselected in 0.37s
EXIT_CODE: 1
ELAPSED_SECONDS: 1.669
```


### Initial LF GREEN: preserved original worker evidence
Log: task-d-lf-green.log

```text
COMMAND: C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe -m pytest -q tests/test_prospectus_batch_skip.py tests/test_prospectus_publish.py -k "batch_manifest_writes_utf8_lf or review_csv_uses_lf_records" -p no:cacheprovider --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\lf-green-temp"
3 passed, 126 deselected in 0.22s
EXIT_CODE: 0
ELAPSED_SECONDS: 1.078
```


### Resume bare-CR RED attempt: actually passed; not failing evidence
Log: task-d-lf-cr-red.log

```text
COMMAND: C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe -m pytest -q tests/test_prospectus_publish.py -k review_csv_uses_lf_records -p no:cacheprovider --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\lf-cr-red-temp"
3 passed, 64 deselected in 0.19s
EXIT_CODE: 0
ELAPSED_SECONDS: 2.524
```


### Resume fresh focused GREEN
Log: task-d-lf-resumed-focused.log

```text
COMMAND: C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe -m pytest -q tests/test_prospectus_batch.py tests/test_prospectus_batch_skip.py tests/test_prospectus_publish.py tests/test_prospectus_publication.py -p no:cacheprovider --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\lf-resumed-focused-temp"
361 passed in 69.66s (0:01:09)
EXIT_CODE: 0
ELAPSED_SECONDS: 71.253
```


### Resume fresh main full GREEN with approved exclusions
Log: task-d-lf-resumed-full.log

```text
COMMAND: C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\lf-resumed-full-temp"
956 passed, 3 warnings, 13 subtests passed in 99.43s (0:01:39)
EXIT_CODE: 0
ELAPSED_SECONDS: 102.301
```


## Verification boundaries
API/embedding exclusions approved: main venv lacks FastAPI. Pre-F4 baseline not repeated. Original focused360 log preserved; fresh361 supersedes it. GUI-review comprehensive suite and standalone final D selftest: NOT RUN for F4, deferred final gates.

Only F4 implemented; S1/S2/S4/F5/final D gates/Task10 and downstream remain. No main edits, venv changes, push, dev merge or worktree removal.

## Files changed
- backend/bintanong_tools/prospectus_extractor/batch.py
- backend/bintanong_tools/prospectus_extractor/views.py
- tests/test_prospectus_batch_skip.py
- tests/test_prospectus_publish.py
- plans/plan_current_progress/extractor_split_progress.md (preserved prior checkpoints and appended F4 evidence)

## Self-review
Reviewed full diff and all affected writer callers. Real writers, raw-byte checks and independent 23-field expected row; no mocks. git diff --check passed. No correctness concern found. Three upstream warnings below. Parent specification then quality review: 4a0cdb794a337b9cc91846d16585478c3bb5fde0..52da4aaca7d734e83054b1ecd39221ac09302a3b.


```text
tests/test_tools_contract.py::ToolsContractTests::test_synthetic_pdf_fixture_exists_and_parses
  C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Lib\site-packages\pydantic\main.py:542: DeprecationWarning: `force_full_page_ocr` is deprecated; set `mode=OcrMode.FULL_PAGE` instead.
    return self.__pydantic_serializer__.to_json(

tests/test_tools_contract.py::ToolsContractTests::test_synthetic_pdf_fixture_exists_and_parses
  C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Lib\site-packages\docling\pipeline\standard_pdf_pipeline.py:606: DeprecationWarning: This field is deprecated. Use `generate_page_images=True` and call `TableItem.get_image()` to extract table images from page images.
    or self.pipeline_options.generate_table_images

tests/test_tools_contract.py::ToolsContractTests::test_synthetic_pdf_fixture_exists_and_parses
  C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Lib\site-packages\docling\models\stages\ocr\rapid_ocr_model.py:581: DeprecationWarning: deprecated
    if self.options.rec_font_path is not None:

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
956 passed, 3 warnings, 13 subtests passed in 99.43s (0:01:39)

EXIT_CODE: 0
ELAPSED_SECONDS: 102.301
```


## Post-commit Git state
```text
M plans/plan_current_progress/extractor_split_progress.md
```
