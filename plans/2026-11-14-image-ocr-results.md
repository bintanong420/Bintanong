# Uploaded-image OCR continuation — 14 November 2026

Continues the [live rehearsal](2026-11-14-live-local-draft-rehearsal.md), base
`ff973c92`, task `feat/ku-image-ocr` / `p12-ku-image-ocr`. No numbered phase.

## Behavior and boundaries

- Only new Handbook/Charter preparations with verified `original_image` metadata
  opt into local Tesseract OCR. Ordinary native PDF/prospectus defaults stay unchanged.
- Installed executable and English `eng.traineddata` required; no install/download
  or OCR-provider fallback. `TESSDATA_PREFIX` or the executable's sibling tessdata
  directory is resolved explicitly and passed to Docling.
- Full-page OCR at scale1.0 preserves the upload's existing40MP bound; no upscaling.
  Engine version, executable/model SHA-256, language, mode and scale join conversion
  metadata/cache identity. Actual converter options must agree; changed assets refuse
  publication. OCR supplies pending candidates only; human review is still required.
- Original images/derived PDFs, prior packets and review decisions are not rewritten.
  Existing checked bundles preserve their actual settings; they are not silently OCRed.

## Verification so far

- RED: new conversion tests 5 expected failures/1 native-default pass; options test
  separately fails for absent image OCR settings. No production code preceded RED.
- GREEN: focused image/rehearsal/cache/identity gate57pass; edge gate12pass.
- Independent read-only review approved; independent42pass, no blocking findings.
- Broader affected ingestion/prospectus regression roster running; final result pending.
- Actual old PNG source, fresh bundle/packet: Docling+Tesseract returns the two exact
  authored records (header and merged action/receipt body), all pending;73.14s.
- Explicit synthetic review selected the action/receipt body only. Real SEA-LION
  build/verify/retrieval checks pass;48.35s. These single timings are not browser latency.
- Actual inactive local staging/repeat/RLS checks pending.

System Python3.13 for tests; existing frozen-lock3.13 venv for actual Docling/embedding,
HF/Transformers offline. No dependencies, locks, models, source authority or rules changed.
Test commands use `-B -q -p no:cacheprovider --basetemp <fresh external directory>`.
Affected roster includes knowledge-update, prospectus, procedure, candidate-bundle,
ingestion-report, image-span and assistance test files; overlapping counts not summed.

## Evidence and next action

Ignored evidence: workspace `audit-evidence/ku-image-ocr-20261114/`; scripts, conversion
settings, source hashes, logs, build/check receipts and service restore list stay there.
Old PNG source/derived PDF remain under `ku-live-rehearsal-20261114/uploads/`.
The checked-candidate-bundle path retains `synthetic=True` governance records in the
live test; automatic image selection is separately covered by prepare regression tests.

Next: finish affected regressions and local inactive PNG staging using the existing
`ku-live-rehearsal-20261114/freeze-baseline/`; preserve active release and hosted
fingerprint-covered state. Restore temporarily stopped services; integrate only after checks.
Activation, browser/Gemma acceptance and real-source extraction accuracy remain open.

Consulted scope/context and master3/11/13/18.3 from the prior continuation. Installed
Docling2.133 API/source and official [OCR example](https://github.com/docling-project/docling/blob/main/docs/examples/full_page_ocr.py)
and [pipeline reference](https://docling-project.github.io/docling/reference/pipeline_options/)
support the existing Tesseract CLI/full-page path; no upgrade proposed.
