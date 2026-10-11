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

Task 2 adds `run_prospectus_ingestion(snapshot, register, *, input_root, out, converter=None)`
and `load_candidate_bundle(path)`. The new wrapper preserves the protected extractor
and generic policy/procedure APIs. It preflights the pending register, snapshot digest
and new/empty external output before conversion. It passes the captured snapshot and
explicit staging/raw paths into the existing loader, then calls the actual curriculum
parser/audit through `build_payload` with `semantic_doc_path=None`, `semantic_map={}`
and a hash-matched `ProvisionalSource`. Ambient semantic files are never read.

The strict converter seam rejects any conversion errors and every explicit status
other than `success` before raw export, including partial results with surviving text.
A missing status remains `null` in metadata; it is never invented as success. Errors
also stop the loader's automatic backend retry so the recorded backend cannot silently
change. The default path uses the existing converter factory with its explicit current
settings. An injected converter must expose a JSON `conversion_settings` mapping with
nonempty `backend`, `profile` and string-valued `versions`. This is the caller's
attestation of the injected implementation's actual configuration, not independent
proof about arbitrary Python code. For converters exposing Docling `format_to_options`,
the known PDF backend class and OCR/table/text pipeline options must agree; unknown
backends or missing options refuse. Enabled OCR also requires declared languages to
match the actual `ocr_options.lang`; this checks an existing converter configuration,
without adding an OCR pipeline or certification. Declared `docling`, `docling-core`
and `docling-parse` versions must match `installed_versions()` for those converters.
Settings are checked again after conversion.
Metadata records this distinction as `settings_basis` and preserves the actual status.
The wrapper replaces the protected loader's generic settings metadata with the actual
seam settings and corresponding conversion identity; the protected loader is unchanged.

Page sizes come from `pypdfium2.PdfDocument(snapshot.data)`. Every page and document
handle is closed. Hash-checked metadata retains `pdf_page_sizes`, an object mapping
physical page numbers such as `"1"` to `[width, height]` in PDF points. This capture
remains available when a failed audit suppresses all chunks. Raw Docling page sizes,
when supplied, must agree within 0.01 points; neither the binder nor downstream field
support substitutes converter geometry for this PDF capture.

The published domain payload retains courses, row-level provenance, structured audit,
unresolved prerequisites and both legacy candidate chunk groups. It omits the entire
legacy `prolog` view, including consult-ready helper code. Its diagnostic
`quality_report.production_artifacts_emitted` is explicitly false. No `.pl` is written.
The report accounts for each candidate as emitted or rejected by the binder and
retains every extractor rejection separately. A curriculum audit error creates a
complete diagnostic candidate with `extraction_blocked=true`, `audit_status=error`,
an explicit review blocker and no ready chunks. Technical completion never implies
review eligibility, source/content approval or executable eligibility rules.

The exact artifact sets are:

| Location | Policy/procedure and existing classifications | Prospectus |
| --- | --- | --- |
| Root | `source_register.json`, `chunks.json`, `ingestion_report.json`, `manifest.json` | Same |
| `conversion/` | `raw_docling.json`, `raw_docling.meta.json`, `procedure_candidates.json`, `manifest.json` | `raw_docling.json`, `raw_docling.meta.json`, `prospectus_candidates.json`, `manifest.json` |

The root manifest hashes every artifact except itself, including the nested manifest;
the nested manifest hashes exactly its three conversion artifacts. Prospectus root
manifests add `document_kind=prospectus_candidate`, and both manifests name the same
source digest/version. Prospectus nested completion also names the conversion identity.
Atomic writers publish the root completion last, checking unchanged original bytes
before every publication. Interrupted folders cannot be consumed or silently reused;
retry requires a new/empty external output.

`load_candidate_bundle` reads and hashes the same bytes it parses, rejects duplicate
JSON object keys before dictionary collapse, requires both completion flags, exact
artifact sets and regular contained files, and refuses symlinks, extra files/directories,
escaping paths, unknown kinds and source/settings/raw mismatches. It reparses pending
institutional register records and every chunk/span, checking exact version membership
and claims against the register. Policy/procedure candidates, chunks and reports are
rebuilt from their captured raw bytes; manifests without `document_kind` use that
existing schema and must match the report's classification. Prospectus chunks and
accounting are rebound from the checked domain payload, while authority is independently
checked against the pending source. This validates handoff integrity and accounting;
it does not independently certify extraction accuracy or authenticate a malicious
producer that can replace all artifacts and hashes.

The checked result contains `document_kind`, `candidate_only=true`,
`review_eligible=false`, reparsed `source_register` and `chunks`, and the parsed `report`.
For prospectuses it also exposes `domain_payload` and `conversion`, whose `raw_docling`
and `metadata` entries are the hash-checked conversion inputs. Task 3 must map exact
field ownership against those raw normalized cells and the captured `pdf_page_sizes`;
whole chunks are not individual field evidence. The current register preparation stays
pending-only; this consumer never promotes a source or approves a rule.

The existing CLI adds only `--classification prospectus_candidate`; all earlier
classifications and flags retain their dispatch. It derives its success summary from
`load_candidate_bundle`, and converter initialization is unnecessary for `--help`.
Exact tokenizer accounting and the 512-token limit remain Phase 3 work; current
`estimate-v1` values are explicitly estimates.

The stable combined synthetic CLI/library smoke is:

```powershell
py -3.13 -B -m pytest tests/test_candidate_bundle.py::test_combined_synthetic_cli_library_smoke -q -p no:cacheprovider --basetemp <new-external-directory>
```

It uses synthetic PDF bytes and a synthetic converter while running the actual
curriculum parser/audit, policy reader, publication, consumer and both CLI routes.
Focused tests also exercise invalid identity before any writer/converter call, partial
status before raw export, altered settings/raw artifacts, cross-version spans, duplicate
manifest keys, interrupted publication, audit blockers and unchanged originals. Original
corpus validation, office/domain review, OCR certification, private lifecycle, embeddings,
rule compilation and runtime execution remain separate work; historical M1 is not
independently rechecked by these new-boundary tests.

Task 3 adds the library entry point
`backend.bintanong_tools.document_ingest.prospectus_rules.prepare_rule_candidates(bundle_path)`.
It first calls `load_candidate_bundle`, requires `prospectus_candidate`, and selects
the exact registered version named by the checked report. It passes the unchanged
checked domain payload, that source, field spans and any existing `review_evidence`
wrapper to the pure `build_rule_candidates` compiler. The return value is the existing
compiler artifact in memory. The bridge writes no files, consults no Prolog, invokes
no network/runtime and never approves or activates a rule.

The bridge uses `evidence_adapter` on the hash-checked raw conversion, and reuses
`parse_curriculum_evidence`, `detect_column_groups`, `tokenize_table`,
`build_curriculum_sections`, `_assemble_section_candidates` and
`_candidate_to_raw_course` to recover the `FieldCandidate` ownership dropped by the
parser's return projection. This is evidence mapping around the current extractor,
not another curriculum parser. A unique table/row/column-group owner must agree with
the supplied row provenance. Each supplied cell record must exactly match the raw
normalized cell, and its IDs must belong to that owner; a legitimate cell from another
row cannot support this course. Malformed locators, duplicate/foreign IDs, changed
cell text/geometry/page and foreign source identity claims refuse preparation.

Only IDs present in both the row's retained IDs and its exact cell records can support
a field. Missing ownership or cell records, ambiguous owners/overlapping cells,
unlocatable fields and semantic/deterministic repairs remain unsupported. Fields never
borrow the row union or a chunk span. Each usable span names one actual owned cell,
retains its `raw_text`, physical page and native `SourceBBox.origin`, and uses
`pdf_page_sizes` from the hash-checked captured-PDF metadata. A page outside that capture
refuses; missing geometry/origin stays blocked. The compiler compares the retained
printed wording with the candidate field, so a changed title cannot borrow another
course's matching title or turn repaired wording into direct support.

A plain unit cell supports only `units.total`; the extractor's default lecture/lab
split is not separately printed evidence. A fractional/composite unit cell stays
unmatched unless the existing compiler can match its complete wording. Year/semester
support is supplied only when the owned source cells print the exact candidate field;
normalized/derived labels remain blocked. Category and term index have no direct field
ownership here. Program, elective and term summary records retain the compiler's
unsupported-evidence blockers. Pending source states, `activation_allowed=false`,
`approval_id=null`, raw prerequisite wording and unresolved references are preserved.

The normal producer does not emit ledger entries. Review counts or statuses never
substitute for them: a blank prerequisite stays `blank_unreviewed`. If a checked payload
already contains the existing compiler's `{version_id, entries}` `review_evidence`
wrapper, the compiler checks the existing ledger's version, PDF hash, field, course
locator, current old value and entry integrity. Applicable accepted-blank decisions
retain their `review_evidence_refs` only after the bridge binds the decision to the
regenerated exact owner: the entire row provenance must be retained, and its actual
layout/row must contain one genuinely blank, locatable prerequisite cell. The existing
span validator checks that cell's geometry/source binding, without supplying a blank
span as printed rule support. A candidate edited to blank cannot erase an untouched
printed prerequisite through an accepted ledger entry. Missing, ambiguous, unlocatable
or semantically repaired ownership stays blocked. The bridge reuses the compiler's
ledger validation before filtering accepted-blank entries individually, so unsupported
blanks do not discard unrelated valid review references. Foreign, stale or malformed
records cannot clear the blocker. This bridge does not materialize corrections or
create new review truth.
Other correction decisions and original conversion text remain in their captured
review inputs; this compiler's existing return format records accepted-blank references.
Neither the manifest hashes nor the local ledger authenticate a malicious producer
that can replace all bytes and recompute hashes.

From the candidate worktree, this stable library command reads an external complete
bundle and prints inactive JSON review data; replace the bundle path with the selected
external candidate directory:

```powershell
$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONDONTWRITEBYTECODE = '1'
py -3.13 -B -c "import json; from pathlib import Path; from backend.bintanong_tools.document_ingest.prospectus_rules import prepare_rule_candidates; print(json.dumps(prepare_rule_candidates(Path(r'E:/external/prospectus-candidate-bundle')), ensure_ascii=False, indent=2))"
```

The combined synthetic acceptance case is
`tests/test_prospectus_rule_handoff.py::test_combined_synthetic_conversion_bundle_bridge_compiler`.
It runs snapshot/converter, real curriculum parser/audit, producer, checked loader,
field bridge and pure compiler, checking exact cell/page/version support, inactive
states, the `XX999` blocker, deterministic output and unchanged source/bundle bytes.
Focused regressions cover hash damage, deliberately rehashed forged ownership,
missing/ambiguous support, native BOTTOMLEFT coordinates, repairs, blank review evidence,
policy/private misuse and absence of publication/network/runtime. This closes the
field handoff interface; original-corpus accuracy, office/domain review, OCR/private
lifecycle, runtime/release verification and historical M1/F/session debts remain separate.
