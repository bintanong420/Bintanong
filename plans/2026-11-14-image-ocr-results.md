# Uploaded-image OCR continuation — 14 November 2026

Continues the [live rehearsal](2026-11-14-live-local-draft-rehearsal.md), base
`ff973c92`, task `feat/ku-image-ocr` / `p12-ku-image-ocr`, code `64a7879c`. No numbered phase.

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

## Verification

- RED: new conversion tests 5 expected failures/1 native-default pass; options test
  separately fails for absent image OCR settings. No production code preceded RED.
- GREEN: focused image/rehearsal/cache/identity gate57pass; edge gate12pass.
- Independent read-only review approved; independent42pass, no blocking findings.
- Broader affected ingestion/prospectus roster:1885pass/93subtests,286.60s,exit0.
- Actual old PNG source, fresh bundle/packet: Docling+Tesseract returns the two exact
  authored records (header and merged action/receipt body), all pending;73.14s.
- Explicit synthetic review selected the action/receipt body only. Real SEA-LION
  build/verify/retrieval checks pass;48.35s. These single timings are not browser latency.
- Actual inactive local PNG draft `ku-rehearsal-20261114-png` created and repeated
  without duplicate registration/release; one chunk/vector/span, source synthetic,
  approval not_requested. Anonymous queries cannot see draft/chunk/version; read-only
  release validation refuses unapproved evidence. Active560 remains unchanged.
- All25 hosted fingerprint/count checks unchanged; local delta is exactly+1 in
  the nine expected draft/source/chunk/vector/membership tables from the PDF baseline.
  This covers recorded columns/counts, not every hosted byte. Both original image
  and derived PDF hashes unchanged. Old empty-text packet preserved as failed evidence.

Actual OCR: Tesseract `v5.5.3.20260724`, installed executable SHA-256
`c66f0f12ed76f6aa455dac97684bbc86756d6a732380bee09122454cfda3f420`;
English traineddata `7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2`.
PNG's existing derived-PDF bytes `0a2d8ccde47b20ef36c4bf3dbc10ceee36e8600f69ff05cb1d856f929e0d76df`
stay unchanged. Fresh packet `ec3d4d831b09d0f972b8056ba9222155c65d74130f1ae1774804a2852d53e401`;
package `f5725cefdea0839792919aa968651aff6575bd6cd16d2d39baccb1c71c0000bf`.

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

The updated freeze baseline remains at `ku-live-rehearsal-20261114/freeze-baseline/`;
next local write must use it and rerun fingerprints, never pretend hosted/local equal.
Two synthetic drafts (PDF and PNG) remain local/inactive; no activation/hosted writes.
Temporarily started Bintanong services returned to their initial stopped state;
original Binturong containers restored after the resource-intensive checks.

Next: U0 read-only mapping for the unified prospectus build (existing reviewed
ledger/runtime inputs), without source edits or release writes. Governed activation,
browser/Gemma acceptance and real-source extraction accuracy remain open. No full
repository/frontend suite or general photo/multilingual OCR accuracy claim.

Consulted scope/context and master3/11/13/18.3 from the prior continuation. Installed
Docling2.133 API/source and official [OCR example](https://github.com/docling-project/docling/blob/main/docs/examples/full_page_ocr.py)
and [pipeline reference](https://docling-project.github.io/docling/reference/pipeline_options/)
support the existing Tesseract CLI/full-page path; no upgrade proposed.
