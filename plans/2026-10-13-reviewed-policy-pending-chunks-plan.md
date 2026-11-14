# Reviewed policy pending-chunk adapter

Execute inline under the existing Phase 05 recovery plan, using executing-plans,
focused synthetic TDD and a final independent review. Owner continuation covers
the bounded next step; it does not authorize institutional activation or Phase 06.

## Goal and inspected seams

Convert explicitly applicable, fully located, reviewed readings to a separate
pending `Chunk` derivative, while accounting for every withheld reading. Existing
canonical bundles and original/raw/review evidence remain unchanged.

Inspected: reviewed-policy preparation builder, `document_ingest/register.py`,
`policy_chunks.py`, SourceSpan/Chunk binding contracts, retrieval context/engine,
master section10, scope/source-gap/service-table policies and ingestion README.
Thesis physical17–18/36 and runtime routing PNG reconsulted on resume. Git clean
`0293b9f`; checkpoint's preceding code head6279985is reconciled by that closure.

The raw chunk builder requires complete located spans. SourceSpan geometry uses
left/top/right/bottom with explicit TOPLEFT/BOTTOMLEFT origin and page size.
Review-image pixel regions and native character ranges are not interchangeable
with canonical source locators. Review status cannot appear inside chunk metadata;
source verification/content-review claims come only from the pending register.
Retrieval uses `required_neighbor_chunk_ids` for atomic context groups, but does
not currently carry source defects through context. Therefore gap-bearing readings
are withheld from this adapter; their exact limits remain in its sidecar/report.

## Interface and boundaries

New `backend/bintanong_tools/document_ingest/reviewed_policy_chunks.py` exports
`build_reviewed_policy_chunks(bundle, *, sources, review_events, source_versions,
field_spans=None, required_readings=None, token_cap=480)`.

- Rebuild preparation using original source/event bytes and compare all core keys
  to the supplied bundle. Reject tampered selection/fields/events or active flags.
  Reject missing/mismatched source versions; load only byte-derived pending
  institutional register records. Existing complete-bundle loader stays separate.
- One candidate chunk per eligible reading. Require intended audience and explicit
  applicability both undergraduate, and every field accepted/corrected. Unknown,
  mixed or excluded applicability is withheld with an explicit reason.
- `field_spans[reading_id][field_name]` is an ordered list of explicit SourceSpan
  records. Reparse and check source/version/page, complete finite geometry and exact
  joined scalar text against reviewed wording. Every required physical page must
  be represented. Never invent spans or reassign raw cells. Literal blank fields
  retain empty strings and no invented glyph spans. Null/structured values require
  a later defined mapping and are withheld, without flattening their evidence.
- Chunk source_text is the ordered source-span text. Chunk text is deterministic
  JSON of named scalar fields and source-blank flags, keeping rows/action groups
  together. Metadata retains field-to-span indexes, exact event digests, reading
  identity and required neighbors, with no privileged review labels. Pending
  chunk states remain bound to the unchanged register. Scope is only the explicit
  `audience:undergraduate`, never a guessed college/curriculum.
- `required_readings` supplies explicit reading dependencies. Reject unsafe
  keys/unknown targets; require dependencies from the same source version. Withhold
  roots whose required context is withheld, including transitive dependencies.
  Cycles are permitted as atomic context groups, and chunk IDs include dependency
  reading identities. Link surviving chunks through required_neighbor_chunk_ids.
- Gaps, unsupported structured fields, missing/mismatched anchors, nonreviewed
  fields, empty evidence and oversized chunks produce no chunk for that reading.
  Preserve original readings and gap details in an inactive sidecar. No partial
  row/step truncation or executable rules. Measure token cap on both source and
  structured display text using the existing honest estimate; model counts later.
- Return inactive candidate flags, chunks, reading-to-chunk coverage, withheld
  reasons, preserved readings/evidence and selected-only accounting. This is not
  an importable replacement root bundle or a whole-source review result.

## Tasks and expected evidence

1. **Plan and resume:** reconcile checkpoint, record context and these interface
   rulings, commit the bounded plan/progress increment. Preserve all owner changes.
2. **Adapter under TDD:** add `tests/test_reviewed_policy_chunks.py` with synthetic
   original bytes/pending registers, actual prep builder and explicit spans. Watch
   RED before writing adapter. Cover pending round-trip/determinism, row/role/blank
   associations, unknown/excluded scope, source/event tampering, field decisions,
   gaps/structured values, incorrect page/version/text/geometry, byte binding,
   missing/transitive/cyclic dependencies, over-cap atomic withholding and unchanged
   inputs. GREEN plus related preparation/contract/ingestion/context regressions.
   Commit verified code, checkpoint and progress as a cohesive increment.
3. **Actual sealed-bundle check:** use a new ignored workspace packet under
   `audit-evidence/p05-reviewed-policy-pending-chunks-20261013/`. Check earlier
   ten-file seal and original/canonical/input inventories; reuse both pending
   source registers and actual event bytes without rerunning normalization. All
   66 real applicability declarations remain unknown, so expect zero chunks and
   66 withheld readings. Report additional anchor/gap/structured requirements
   explicitly. Preserve and independently verify earlier evidence before/after,
   seal new outputs, run final code review, update report/index/checkpoint/progress
   and commit. Keep source/applicability/retrieval-calibration gates open.

Use system Python3.13.7 for unittest and existing approved Python3.13 environment
for pytest. No cache; TEMP/TMP and basetemp live under workspace audit-evidence.
No installs/downloads/dependency locks, original conversions, model execution,
database writes, runtime/API/Docker changes, Prolog, push or activation. This
separate candidate adapter advances the Phase 05 recovery work only.

Tasks1–3 delivered at83b17b2/21833d8; see
[actual results and exact next step](2026-10-13-reviewed-policy-pending-chunks-report.md).
Independent reviewer reports no findings; actual zero-chunk result retains all66
unknown applicability declarations. No source or formal-phase approval inferred.
