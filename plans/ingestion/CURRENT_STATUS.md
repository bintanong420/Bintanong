# Current ingestion delivery and remaining work

Snapshot: 11 October 2026, Asia/Manila. Candidate implementation: `5342587c56dd3dcb3cc1201bd8f7a1561b8c2f88`; repository baseline for this documentation migration: `493ba42fd35acb93e7a5b69ab8faa6c6771c73c0`. Git and fresh verification outrank this snapshot. Nothing here is institutional approval.

## Completed

- Phase 1 source-governance/contracts software exit is complete; see the [accepted handoff](../phase-01-handoff.md). Final source-backed benchmark and source authorization were explicitly outside that software exit.
- Unified candidate ingestion, the inactive prospectus compiler and the checked field-evidence bridge are implemented in the repository. The delivered branch has separate Spec/Standards acceptance and a saved completed independent whole-branch PASS with findings NONE. Earlier quota interruptions are historical; the final PASS was issued after the earlier push, not backdated.
- Recorded verification: 525 independent candidate checks and 18 integrated dev smoke checks passed. Documentation migration does not rerun or broaden those results.
- The ingestion CLI explicitly dispatches prospectus versus policy/procedure/Charter classifications and publishes a checked candidate bundle/report. `prepare_rule_candidates(bundle_path)` is a separate explicit library call returning inactive rule review JSON; the CLI does not automatically publish rules, and no runtime/API caller is delivered.

## Institutional documents: code support versus actual processing

| Source | Verified evidence | Remaining evidence |
| --- | --- | --- |
| Handbook PDFs | Both copied originals match the corresponding dataset-dump PDFs byte for byte; policy ingestion code exists | Completed source-bound bundles for those exact originals were not found in the delivery artifacts checked; end-to-end original migration and content validation remain unproved |
| Charter PDFs/PPTXs | Copied files match the corresponding dataset-dump files byte for byte; Charter/procedure ingestion code exists | Completed bundles for those exact originals were not found in the delivery artifacts checked; original migration and content validation remain unproved |
| Main-campus old-student enrollment procedure | Saved original-backed run: 11 chunks, complete accounting, one explicitly rejected unlocatable item; complete bundle's seven artifact hashes freshly matched | Human/source-span accuracy and institutional authorization remain pending |
| Prospectus | Connected candidate path and synthetic combined end-to-end acceptance | Corpus-level original-source accuracy, human field review and source/domain authorization remain separate |

Copies are inputs, not completed ingestion. Earlier Docling trial output is not proof that an original passed through the current governed bundle flow. The original-backed procedure evidence is in the external `actual_procedure_smoke_20261011` run; the source digest is `b1dfdfe29f8fc2d88a307acb5a8af8efa4fcb9d130915cada1ceeeea685523fb`. Raw conversion and source-derived artifacts remain outside Git.

## In progress and next work

1. Run the existing ingestion path on the exact original Handbook/Charter inputs into external output folders. Reuse the [Phase 2 tasks](../phase-02-document-ingestion-plan.md), pending register and checked bundle loader. Verify unchanged originals, page/item/table accounting and sampled critical source spans; retain rejections rather than silently discarding them.
2. Complete the remaining OCR-to-reader integration and independent source-backed measurement. The OCR runner/reference gate is separate tooling; startup/synthetic checks do not establish measured OCR/photo accuracy.
3. Resolve the [private lifecycle design](private_lifecycle_design/SPEC.md) before implementing real private processing. The known Windows cleanup High remains open; no indefinite-retention exception is approved.
4. Keep repository status, decision records and handoffs updated as these tasks produce actual evidence. Do not mark formal Phase 2 complete merely because candidate code was pushed.

## Owner sign-off and later phases

Human/domain/source validation, source scope/effectivity and institutional authorization remain applicable gates. Formal phase start/advancement and runtime/API/Docker/private-host work retain their applicable approval boundaries. Candidate Prolog stays inactive; embeddings, release activation and executable rules are later work. The [formal ledger](../INDEX.md) still records Phase 2 as prepared, not formally closed.

The historical F review debt, M01 historical 52/52 mutation claim and standalone session cleanup High are not closed by the bounded candidate branch review. No updated overall completion percentage is asserted by this migration.
