# Phase 02 unified ingestion: prospectus candidate binding

Task 1 adds `bind_prospectus_chunks(payload, version, *, page_sizes)` in
`backend.bintanong_tools.document_ingest.prospectus`. It consumes existing extractor
`rag.semantic_chunks` followed by `rag.hierarchical_chunks`, preserving each group's order.
The result has `version_id`, `source_sha256`, serialized existing `Chunk` contracts,
and explicit rejections carrying original `chunk_id` and stable `reason`.

The pending register is authoritative for identity, verification, content review and
evidence references. `load_pending_register` reparses and checks the version before
conversion. The payload's `run_identity.pdf_sha256`, every chunk and every span must
name those exact bytes. Global malformed shapes, duplicate identities, privileged
fields and preexisting non-null source identity claims refuse the entire call before
binding anything. In particular, foreign span versions cannot be silently overwritten
by the shared `bind_chunk` helper. Inputs remain unchanged on success and refusal.

`adapt_chunk` retains legacy IDs, content hashes and printed source text. Unsupported
chunks are explicit individual rejections, including unavailable captured page sizes,
raw-text hash mismatches and incomplete printed/geometry support. Geometry must come
from the captured PDF through `page_sizes`; the binder never invents a page or box.
`check_span_binding`, `bind_chunk` and `check_chunk_binding` enforce the existing
contracts and copy the pending registered states/evidence. Scope stays empty; issuer,
approval and institutional activation are never inferred from extracted text.

Legacy chunk IDs include the PDF byte digest. The current pending register uses
`ver-<byteSHA>`, so preserving those IDs keeps versions separated. A future register
scheme allowing multiple versions of the same bytes requires an explicit identity
migration policy before this boundary can accept it.

This is a domain candidate result, not a new public contract, loader replacement,
extractor change or runtime integration. Synthetic focused tests exercise binding,
refusal, rejection accounting and input immutability at the new boundary. Its
check-before-write coverage does not recheck historical M1 or change the historical
52/52 claim; that review debt and other F/session debts remain separate.
