# Reviewed native PDF field spans

Bounded continuation from the pending-chunk adapter handoff, clean `a8d3421`.
Execute inline with synthetic TDD and final independent review. Existing Phase 05
source/applicability/retrieval gates remain open; original artifacts stay intact.

## Interface and decisions

Add `document_ingest/reviewed_native_spans.py` exposing
`map_reviewed_native_spans(bundle, *, sources, review_events, source_versions,
read_native_range)`. Rebuild the preparation core from exact source/event bytes,
compare all cached core fields and load only matching byte-derived pending source
registers. Inspect fields with saved native evidence in `locator.evidence`.

`read_native_range(source_bytes, physical_page, start, end)` is an injected trusted
original-PDF reader. It returns exact text, union glyph bbox, page_size,
coordinate_order and origin. It receives verified source bytes and an end-exclusive
native range. Tests inject synthetic readers; actual preparation reuses installed
pypdfium2 against the unchanged PDF, with no new conversion/OCR/acquisition.

Eligible mappings require accepted/corrected scalar wording, one explicit physical
page, evidence field identity, exact native/reviewed text, valid native range,
saved original PDF box, explicit coordinate order/origin, and page_size in retained
row evidence. Validate observed text/box/page dimensions against that captured
evidence. Convert only declared native PDF point coordinates to SourceSpan's
left/top/right/bottom order. Numeric boxes/dimensions must be finite and in bounds;
character offsets/pages are strict integers. No pixel-to-point guessing.

Use supported `text_item` locators in an explicit native namespace:
`native-pdf:p<physical_page>:chars<start>-<end>`. These name actual original PDF
character ranges, not Docling text/table cells. SourceSpan extraction identifies
native PDF range resolution and a hash-bound mapping evidence ID. Preserve raw
column association diagnostics and historical review evidence in the unchanged
sidecar; duplicate ranges cannot become independent fields.

Literal blanks require empty reviewed/native/proposed values and absent range/box;
map them to empty span lists with explicit blank evidence, never numeric defaults.
Non-native/image evidence, unconfirmed readings, malformed ranges/boxes, wrong
text/field/page, missing page sizes and original-reader failures remain explicit
per-field withholding reasons. Unsupported fields do not cause guessed mappings.
This technical mapping can proceed while institutional applicability is unknown;
feeding it into the pending adapter must still withhold the actual 66 readings.

Return inactive flags, `field_spans` for the existing pending adapter, per-field
mapping evidence (original/observed native values and canonical span), withheld
field reasons and selected mapping counts. No source-register transition, chunk
activation, executable rules, runtime/API/Docker/database writes or model run.

## Tasks and verification

1. Record resumed context/seams and commit this plan/checkpoint/progress increment.
   Context: thesis physical17–18/36, routing PNG, master10, scope/source-gap rules,
   original grading preparation and pending chunk contracts. No discrepancy.
2. Write focused synthetic `tests/test_reviewed_native_spans.py`; watch absent
   module RED, then implement the smallest pure mapper. Cover native coordinate
   conversion, end-exclusive ranges, text/field/geometry/source/event mismatches,
   duplicate ranges, missing metadata, literal blanks, non-native evidence,
   partial review and unknown-applicability integration with unchanged inputs.
   GREEN and relevant span/preparation/chunk/source/governance regressions; commit.
3. New ignored packet `audit-evidence/p05-reviewed-native-field-spans-20261013/`:
   verify earlier seals/source/registry/history; map actual 45 nonblank fields and
   nine blanks from 18 undergraduate grading rows. Independently reread original
   text and union character geometry; compare mappings/diagnostics/unchanged review
   sidecar. Pending adapter still emits zero actual chunks; missing scalar mappings
   decrease225to180. Other structured fields/source gaps remain recorded. Seal new
   evidence, final code review, report/index/checkpoint/progress and verified commit.

System Python3.13.7 and existing approved Python3.13 environment; no cache,
external TEMP/TMP/pytest basetemp. No installs/downloads/lock changes, original
conversion/normalization reruns, original or canonical overwrite, push or Phase06.
Unknown meaning/authority/effectivity stays unknown; no repeat owner page review.

Tasks1–3 delivered5e8eab1/ba8aae4/b9e614d; see
[exact verification/digests and next action](2026-10-13-reviewed-native-field-spans-report.md).
45native/nonblank andnineblank fields mapped; zeroactualchunks/66unknown
applicabilitywithheld. Final independent review has no residual findings.
