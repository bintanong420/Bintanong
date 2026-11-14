# Phase 2 draft: procedure, form and Charter candidates

This is draft preparation on `draft/phase2-candidates-20261010`, following the pending-register and policy reader at `a904351`. It does not start or complete formal Phase 2, adopt institutional content, or authorize source approval. The phase ledger, contracts, extractor, API, embedding packages and dependencies are unchanged.

## Consumer interface

`procedure_text.py` exposes `read_procedure_items(raw, version, *, source_format="pdf", classification="procedure_candidate", printed_page_labels=None)` and `extract_procedure(snapshot, register, *, input_root, out, converter=None, classification="procedure_candidate", printed_page_labels=None)`. Both return a frozen `ProcedureCandidates` with `check_invariants()` and `as_dict()` for Task 5.

- `version` is the existing pending byte-derived source version. `pdf` is the unchanged `PolicyCandidates` representation for PDF text; PPTX sets it to null.
- `fields` are frozen `ProcedureField(item_id, kind, raw_text, printed_marker)` records. Numbered steps retain raw reading order, without numerical sorting. Literal numbered lines and explicitly enumerated Docling items are step candidates; separately exported markers are retained without prepending them to source text. Office, requirements, fees and processing-time fields are captured only from explicitly labelled nonempty printed lines. Their entire raw line is retained, without semantic value parsing or inferred defaults. Other printed structures, including table headings, remain in raw evidence for review.
- `classification` accepts only `procedure_candidate`, `charter_candidate`, `form` or `curriculum_proposal_candidate`. The caller explicitly selects it; filenames never imply Charter, approved curriculum or proposal status. Form classification denotes an artifact, not a rule. These classifications do not promote the pending register's `source_document` category or scope.
- `pptx_units` contain every raw text item, including empty items: ID, label, exact source text, one-based slide index when unambiguous, all observed slide indices, shape ID when explicitly exported, full raw provenance JSON and provenance gaps. They have no PDF page field and no spans; every one is rejected as `pending_locator_contract`.
- `tables` contain every raw table by ID, complete raw wrapper JSON and all raw page/slide geometry JSON. Raw cell array order, row/column offsets, exact text, headers and every provenance entry are preserved without the normalized adapter's cleaning, page fallback or provenance reduction. Tables are review-only: PDF reason `unresolved_table_span_coverage`, PPTX reason `pending_locator_contract`. Task 5 may resolve genuinely complete PDF cell evidence; this reader fabricates no cell span coverage and claims no complete table extraction.
- `reading_order` accounts for every text and table reference exactly once. `raw_reading_order_json` preserves original body, groups and furniture, including other references. With no body, raw array order is used and labelled `raw_arrays_no_interleaving_evidence`; no interleaving is inferred. `slide_geometry_json` retains native geometry outside the PDF span contract.

PDF text keeps Task 3 raw fidelity, physical-page accounting, printed folios, multi-page character ranges, explicit unlocatable rejections and omissions. Each text item appears exactly once in a unit or item omission. All physical pages are accounted for; `scanned_no_text_layer` is an extraction finding, not proof of an original's text-layer state. Tables have a separate exact count, so text accounting never silently drops them.

## Installed native PPTX and shared reference correction

The installed Docling native backend uses `DocumentConverter(allowed_formats=[InputFormat.PPTX])` from `load_docling()`, with a `DocumentStream` over captured bytes. Its provenance `page_no` is a one-based slide index, retained only as slide metadata; it never becomes `SourceSpan.page`. The installed backend does not export text shape IDs, so those remain null with `shape_id_not_exported`. Unsupported slide provenance remains null with an explicit gap. No application import of python-pptx or pypdf is added.

The real synthetic native smoke revealed that this installed version exports children with `$ref`, rather than legacy `cref`. The coordinator authorized the same small correction in Task 3's `policy_text._reading_order`, so direct policy extraction also works with native references. Both readers accept the two spellings, refuse conflicting values and invalid/negative group references, preserve original raw structures, and use nested groups in reading order. No synthetic reference rewrite or protected extractor change is used.

## Conversion and publication

InputSnapshot integrity, the whole pending register and exact matching byte identity are checked before any converter. Duplicate PDF bytes reuse one version and retain all logical acquisition locators; distinct PPTX bytes remain distinct versions. Sources must belong to an explicit input root. Output must be new/empty, outside that root and outside every Git repository, including worktree-style `.git` files.

Installed Docling imports precede the PDF loader's legacy environment helper; missing imports fail without interpreter relaunch. PDFs use the existing loader with explicit external raw JSON and staging paths. PPTX conversion uses the installed native backend directly; it has no model pipeline, dependency installation, environment synchronization or relaunch. PPTX metadata records source digest, installed versions, actual backend/settings, conversion identity and raw JSON digest. PDF metadata remains the loader's conversion metadata.

Raw JSON, metadata and `procedure_candidates.json` are written atomically. Source bytes are checked after conversion and after publication; `manifest.json` with output digests is written last. Missing completion manifest means incomplete output. A failed run uses a new output folder for retry. Nothing writes beside a source or promotes verification, scope, content review, approval or rule authority.

## Focused evidence and remaining gates

Synthetic tests cover raw step order/punctuation/markers, explicit form/proposal typing, no inferred fees, text/page/table accounting, duplicate PDF locators, distinct PPTX versions, native nested references, malformed data/classifications/namespaces/register digests, slide/page separation, provenance gaps, raw table evidence, external publication, source mutation and missing installed Docling without relaunch. The minimal stdlib OOXML fixture is converted by the installed native PPTX backend with Hugging Face and Transformers offline; its two slide texts and null shape-ID gap are checked. It is not an institutional conversion.

Red: the initial missing implementation produced 26 expected failures. Marker/type/group boundary tests produced four failures and two passes. Native smoke exposed the `$ref` incompatibility. Shared policy reference tests produced two failures and one pass before the correction. Focused green results are recorded outside Git; independent acceptance is coordinator-managed.

NOT RUN: institutional originals, human source reading, corpus/spike checks, mutation campaign, broad suite, OCR gate, authorized scope/issuer/effectivity/supersession, containers/Linux/macOS, exact tokenizer, API/Docker and adoption/merge. The locator schema decision and complete table anchoring remain pending. No readiness or phase-exit claim is made.
