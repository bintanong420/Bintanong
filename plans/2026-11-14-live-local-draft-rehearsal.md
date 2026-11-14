# Actual local draft rehearsal — 14 November 2026

Continues the [intake checkpoint](2026-11-14-ingestion-continuation-checkpoint.md)
at `dc9f2ae7`; no numbered phase or activation. No production code changed.

## Checklist and outcome

- [x] Native PDF -> actual Docling -> explicit synthetic review -> actual SEA-LION
  embeddings -> verify -> retrieval check -> inactive local Supabase draft.
- [x] Repeat staging: same draft, no duplicate source/release/chunk/vector.
- [x] Read back one source version, one chunk/vector/span and the draft status.
- [x] Original active release stays `p12-research-faqsplit-20261030`.
- [x] Anonymous queries cannot see the draft release, chunk or source version.
- [x] Loader RPC execute privileges: anon denied, service_role allowed for source
  registration, batch loading and draft creation.
- [x] Read-only release validator refuses this unapproved synthetic draft.
- [x] Hosted GET-only fingerprints remain unchanged over the covered data.
- [ ] PNG -> usable extracted text -> embeddings -> local draft. Actual raster
  conversion produced an unresolved page with empty text; nothing from it was built.
- [ ] Browser/operator acceptance, Gemma assistance and real policy review/measurements.
- [ ] Governed fresh-upload activation and rollback; no activation call attempted.

## Evidence and recovery

Ignored root: `C:/Coding-projects/bintanong_workspace/audit-evidence/ku-live-rehearsal-20261114/`.
Scripts `fixture.py`, `convert.py`, `review_fixture.py`, `build_check.py`, `stage.py`
and `readback.py` retain executable assertions; logs and receipts are alongside them.
All source files are generated synthetic fixtures, explicitly labelled as such.
The supported checked-candidate-bundle path supplies `synthetic=True` source records;
source approval remains `not_requested`, not institutional approval.

PDF upload `d5f9eddcd47e83a4`, source SHA-256
`f8c246e08d049923d47feefae4d709e5cb09f2419b49ff81ef83bd05ca94439a`.
Packet `0280394d5d213b319da51a5e0e015756f5408cfc6452a543250d1e39f30cea58`;
package `07023f64eebe48211e9a7c42974002b164483d1016a98c84c664487252efeac3`.
Draft retained locally as `ku-rehearsal-20261114-pdf`, unpublished and runtime-hidden.
The header remains held; only the authored action/receipt body was selected.
Docling merged the two known body sentences; no original wording was changed.

Native PDF conversion 78.91s; final real embedding/build/check 28.56s. PNG conversion
32.64s produced no text. These are single process-level timings, not browser latency.
Existing frozen Python3.13 venv / CPU Docling and existing local SEA-LION weights;
HF/Transformers offline flags set, no dependency/model downloads or Gemma calls.
Initial build script asserted approval `pending`; reviewer corrected it to the contract's
`not_requested`. Readback script's nonexistent `document_versions.synthetic` column
was corrected to `source_register.synthetic`. Script checks then passed; neither issue
required production changes or extra DB writes.

Before staging: 16 content fingerprints + 9 count checks matched on both sides.
After staging: +1 local row in each of documents, document_versions, embedding_sets,
chunks, chunk_embeddings, source_spans, knowledge_releases, release_chunks and
release_document_versions; no other fingerprint-covered row-count changes.
Hosted fingerprints/counts and active-release fingerprint unchanged. This covers
selected columns/counts, not every database byte. The existing fingerprint script uses
hosted GET only; `local_release` binds writes to `http://127.0.0.1:54321` without proxies.

The next local write must use the preserved freeze baseline at
`<ignored root>/freeze-baseline/` and rerun the fingerprint. Local now intentionally
differs from hosted by this inactive fixture; do not sync it to hosted or fake equality.
Independent read-only review approved the bounded staging path after the script-state
assertion correction. `readback-receipt.json` records validator refusal and RLS checks.

## Raster diagnosis and next action

`intake._image_pdf` preserves the uploaded image in a derived one-page PDF.
`loader.load_document_result` uses `conversion_settings()` with `do_ocr=False`, and
the converter honors that setting. A raster-only PDF has no native text, so the
pipeline emits a held page-omission item. The earlier mock rehearsal supplied synthetic
text and therefore did not demonstrate actual OCR. No source content was inferred.

Next: connect bounded image OCR to the institutional preparation path with original
image/PDF/settings hashes preserved. Existing Tesseract executable is present, but
its use through the reviewable production path is not implemented or verified here.
Do not enable OCR globally or reuse an OCR-enabled converter with native-only metadata.

Context retained: thesis physical17–18, runtime routing PNG, master3/11/13/18.3,
owner ledger and undergraduate/source/privacy policies. Current official Supabase
[changelog](https://supabase.com/changelog.md) checked; no upgrade or API change needed.
Only existing local containers were used. Binturong was temporarily stopped with owner
authorization. After rehearsal Bintanong db/rest/kong returned to their initial stopped
state. Original three Binturong containers restarted; both DBs healthy, storage `/status`200.
Both fixture upload originals retain their original SHA-256 hashes.
