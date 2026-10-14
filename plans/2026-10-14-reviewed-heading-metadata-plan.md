# Reviewed heading metadata implementation plan

> Execute inline using executing-plans and test-driven-development; one fresh
> whole-change review after verification. Maintain this ledger in the repository.

**Goal:** Represent the ten confirmed heading-derived curriculum fields as cited
metadata in inactive reviewed context, without treating their values as quotations.

**Architecture:** Add one contract module for the two bounded projection kinds and
their source/geometry validation. Extend the existing pending-chunk adapter with an
optional binding argument and the existing context codec with one explicit field kind.
Literal scalar behavior and default saved output remain unchanged.

**Tech stack:** Existing Python 3.13.7 environment/contracts/pytest; no new dependencies.
**Spec:** Exact next seam in `2026-10-14-curriculum-provenance-mapping-report.md`.
Owner says "just continue" after that delivery; routine technical execution is
authorized. Settled row/evidence decisions are not reopened for implementation.

## Global constraints

- Phase05/undergraduate/read-only scope; no authority, effectivity or applicability inference.
- Preserve original PDFs, conversions, events, questions, gaps and all earlier packets.
- Actual eight rows remain unknown applicability; output stays inactive/zero chunks.
- New bindings require source-limit context. No generic scalar normalization or policy edits.
- Source text stores literal headings; displayed metadata identifies the projection and
  retains literal headings. Proposed implementation is explicitly not established effectivity.
- Evidence/logs stay ignored under workspace `audit-evidence`; no installs or model downloads.

## Review focus

1. Wrong semester column or inverted coordinate origin must not attach a neighboring heading.
2. Same displayed value from another version/event/row must fail binding validation.
3. Stored context tampering must fail even after display text/content hash is regenerated.
4. A proposal must retain its proposed status; arbitrary normalization must be rejected.
5. Field reordering, partial anchors and optional-argument omission must preserve complete
   ordered citations and default literal behavior.

## Task 1: Adapter and context integration

Files: create `backend/bintanong_contracts/reviewed_heading_metadata.py` and
`tests/test_reviewed_heading_metadata.py`; modify only
`backend/bintanong_tools/document_ingest/reviewed_policy_chunks.py` and
`backend/bintanong_contracts/reviewed_policy_context.py` for integration.

Consumes the confirmed projection ledger's reading/field/source/version/event IDs,
accepted value, exact literal heading spans and complete course-code/title anchors.
Produces `build_reviewed_policy_chunks(..., heading_metadata_bindings=None)` with
bindings indexed by reading ID/field name, and stored `field_kind=heading_metadata`
associations validated by `validate_reviewed_heading_metadata(field, associations, spans)`.
Only `placement`/`year_term_heading_metadata` and
`edition_status`/`proposed_edition_heading_metadata` are supported.

- [ ] Write synthetic behavioral tests first: year/term and proposal display round trips;
  unknown scope withheld; default output identical; wrong row/event/version/text/field,
  wrong column/origin/pages, partial anchors and regenerated stored-context tampering
  rejected. Expected placement `Second Year / Second Semester`; proposal
  `PROPOSED 2025-2026`; raw headings remain uppercase/full proposed-date sentence.
- [ ] Run focused pytest and observe missing optional-argument behavior (RED).
- [ ] Implement the smallest opt-in binding/association validator and codec integration.
  Bind headings to complete actual code/title citations; use explicit coordinate conversion
  and fixed formatting. Never replace literal spans with projected strings.
- [ ] Focused GREEN and related contract/preparation/chunk/context/retrieval regressions.
- [ ] Commit verified code/tests with checkpoint/current-progress evidence.

## Task 2: Actual inactive replay and final verification

Consumes Task1's binding API; no additional product feature.

- [ ] Replay all ten recorded projections with existing 36 scalar mappings, actual owner
  event, source bytes and pending registers. Expect zero missing/invalid metadata fields,
  eight unknown-applicability readings withheld and zero actual chunks. Preserve all46values.
- [ ] Produce separate non-Chunk diagnostic contexts without declaring actual applicability;
  validate all citations and proposal warnings, confirm unchanged default adapter replay.
- [ ] Full repository pytest with external basetemp/no cache; preserve log and report all
  skips/warnings/failures. No real retrieval scoring or release claim.
- [ ] One fresh reviewer against this cohesive change, spec and review-focus list. Fix
  Critical/Important findings in one TDD pass; record any deferred minors/rulings.
- [ ] Seal ignored replay evidence; curate report/index/checkpoint/handoff/progress.
  Run documentation/ledger validation, keep Phase05 blocked, explicit staging/commit.

Context consulted: thesis physical17–18, routing PNG, master10/11, active Phase05
plan/checkpoint/handoffs, dataset/scope/gap policies. No scope/routing discrepancy.
Pre-flight: Task2 consumes exactly Task1's optional binding API; no conflicting interface.
Execution artifacts use workspace audit-evidence, overriding generic skill scratch paths;
retain evidence/history rather than deleting the audit packet.

## Execution ledger

- Baseline: clean `c1c295c`, isolated `feat/p05-retrieval-logic`; previous citations and
  confirmations complete. No original conversion, source-content review or intake repeated.
- Task1: pending RED. Task2: pending Task1.
