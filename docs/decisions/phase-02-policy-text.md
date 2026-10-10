# Phase 2 draft: pending-register preflight and policy candidates

This is owner-authorized draft continuation in `draft/phase2-candidates-20261010`, based on `0caeaba8d8221a0f75b154e94bc3167b780f1407`. It is not a formal phase start, institutional adoption or phase exit. The formal ledger, plan status, integration GUI and progress documents are unchanged.

## Sequence and contracts

Pending-register minting and validation move ahead of conversion in this draft. This is the prerequisite prefix of Task 5, needed by Task 3: a converter must never run against an invalid or unregistered source identity. The actual Phase 1 `SourceDocumentVersion.parse`, `check_register`, `SourceSpan.parse` and `check_span_binding` are reused; contracts and schemas are unchanged.

`register.py` exposes:

- `mint_pending_register(manifest, *, synthetic=False) -> tuple[SourceDocumentVersion, ...]`: each entry has exactly `filename`, `sha256`, `acquisition_locator`. The caller maps inspection hash-manifest entries to explicit logical locators. Local paths are refused by the existing contract.
- `pending_version(snapshot, locator, *, synthetic=False) -> SourceDocumentVersion`: captures identity from the caller's `InputSnapshot`, verifies that snapshot and delegates to the same minting function.
- `load_pending_register(records) -> tuple[SourceDocumentVersion, ...]`: reparses contracts or JSON-compatible mappings, checks the whole register and enforces initial states and byte-derived IDs.
- `version_for_snapshot(snapshot, records) -> SourceDocumentVersion`: validates the whole register and unchanged snapshot before selecting its exact byte identity.

IDs are `doc-<sha256>`, `ver-<sha256>` and `edition-<sha256>`. Duplicate bytes produce one version with sorted unique acquisition locators and a deterministic display filename. Different bytes always produce different versions and editions. No filename implies authority, effectivity or supersession. Category is `source_document`; selection of a curriculum proposal remains a future owner-named step. Scope fields and supersession stay pending, acquisition and source verification stay pending, content review stays pending, approval stays `not_requested` with null approval ID and no evidence. Loading also refuses non-initial states, even when another workflow could validate their evidence.

## Candidate representation

`policy_text.py` exposes:

- `read_policy_items(raw, version, *, printed_page_labels=None) -> PolicyCandidates`: library reader for raw Docling structures bound to a pending version. This does not authenticate association of arbitrary caller-supplied JSON with source bytes; the conversion wrapper supplies that association.
- `extract_policy(snapshot, register, *, input_root, out, converter=None, printed_page_labels=None) -> PolicyCandidates`: PDF-only wrapper with explicit root and external new/empty output folder. Input containment, pending-register validation and unchanged snapshot checks precede conversion.
- Frozen `PolicyUnit`, `ItemOmission` and `PolicyCandidates`; `PolicyCandidates.check_invariants()` and `as_dict()` are the Task 5 consumer interface. Units carry `item_id`, `label`, exact `source_text`, every physical page, full raw provenance JSON, heading path, printed scope candidate, preceding-clause exception link, validated spans and explicit rejection reason.

The reader always uses raw Docling text items. A raw-provenance/adapter spike on institutional Handbooks is NOT RUN: institutional conversion is gated. Synthetic tests demonstrate both adapter gaps, so a reader that retains every raw item and every provenance entry is necessary without waiting for a corpus result. There is no claim about the frequency of those gaps in actual documents.

Each raw item occurs exactly once in a unit or item omission. Empty items retain their raw ID, raw text and all pages. Repeated furniture is an omission only when identical whitespace/case-normalized text occurs wholly in the top or bottom ten percent on at least three distinct pages. Raw punctuation, numbers, dates, negation, en dashes and superscripts remain unchanged. A page lacking a nonempty text item receives `scanned_no_text_layer`; this is an extraction finding, not proof about the original PDF's native text layer. Empty pages are not silently accepted as extracted text.

Heading paths accumulate raw `section_header` labels in raw reading order, without nesting-depth claims. Body/group references, then furniture references, establish order when a body is supplied; unresolved, duplicated or cyclic references are refused. Otherwise raw text-array order is used. Scope is a printed candidate only for a raw `scope` label or text under a heading exactly naming Scope, Coverage or Applicability. Exceptions beginning Except, Unless or Provided link to the preceding non-heading clause. These are candidate links requiring human reading, not semantic rule interpretation. USG never implies CSG. Issuer, effectivity and all register scope fields remain pending.

Every anchored unit has actual Phase 1 spans with the source digest/version, physical page, optional caller-supplied printed folio, bounding-box origin, page size and raw text. PDF page labels are not treated as printed folios. Missing or invalid geometry yields an explicit unanchored unit/rejection, preserving its text and full provenance. For multiple provenance entries, raw character ranges must locate all the text; ranges are sliced without cleaning. Missing ranges, gaps and malformed ranges are rejected rather than assigning the whole multi-page text to each page. Non-PDF slide locators are outside this interface.

The shared namespace scan refuses private-session IDs/facts in register entries and raw structures. It is not a semantic personal-data detector: authorized source selection remains a caller boundary, and no private upload or institutional original is processed in this draft. Tables are outside this text-item batch and require the later table/procedure/chunk workflow.

## Conversion and publication

The wrapper uses installed `loader.load_docling()` and explicitly imports `docling` and `docling_core` before `loader.load_document_result()`. A missing installed environment therefore raises before the loader's relaunch helper is reached. Once imported, that helper returns through its importable-environment branch. No production monkeypatch, environment mutation, installation, interpreter relaunch or extractor edit is used.

The loader receives caller `snapshot=`, an explicit external `raw_json_path` and `stage_dir`. All conversion writes occur under the external output folder. The caller calls `snapshot.verify_unchanged()` before publishing because the loader skips it with `stage_dir`. Raw JSON, its metadata and `policy_candidates.json` are written atomically, followed by another unchanged-source check and `manifest.json` last. A missing completion manifest means incomplete output and must not be consumed. Failed publication does not authorize retry into that nonempty folder; use a new output folder. Originals are never opened for writing.

## Validation boundary

Synthetic focused tests cover pending register round trips, duplicate locators, edition separation, malformed types/digests/IDs/namespaces, negative promotion before conversion, raw text fidelity, raw reading order, exception/scope candidates, printed folios, multi-page provenance and character ranges, omissions, accounting, geometry refusal, immutable records, external containment, missing installed imports, actual loader execution with a stub converter, and input mutation before publication. Red and green results and archive parity hashes are recorded outside Git under `phase2_policy_candidates` in the takeover evidence root.

The seven previously reviewed Task 1/2 source/test/decision files are adopted verbatim from the external `draft_review_archives/p2_final` archive. The generic `ingest PATH` command remains; there is no Phase F command.

NOT RUN: four institutional conversions, Handbook spike, authorized source/scope selection, content review, ten-document OCR gate, phone photographs, broad mutation campaign, broad suite, Linux/macOS/containers, exact tokenizer and institutional approval. Independent Spec and Standards acceptance remain root-managed. This batch does not meet the formal plan's real-source or phase-exit gates.
