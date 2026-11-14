# Ingestion plans and delivery documentation

Start with [current status](CURRENT_STATUS.md). These documents were brought into the repository on 11 October 2026 at the owner's request so Lawrence and future developers can inspect and maintain the same plans as the code.

Maintain plans, specifications, decisions, status and developer handoffs in this repository from now on. Use an isolated repository worktree when needed. External scratch is for raw inputs, private/source-derived artifacts, generated outputs, test temporaries and execution logs; it must not be the only home of a development plan.

## Plans and specifications

| Topic | Documents | Current interpretation |
| --- | --- | --- |
| Unified institutional ingestion | [Specification](unified_ingestion_design/SPEC.md), [implementation plan](unified_ingestion_design/IMPLEMENTATION_PLAN.md) | Bounded candidate implementation delivered at `5342587c`; original-document validation remains separate |
| Phase 6 prospectus prologifier | [Specification](phase6_prologifier/SPEC.md), [implementation plan](phase6_prologifier/IMPLEMENTATION_PLAN.md) | Pure inactive candidate compiler and explicit library handoff delivered; full formal Phase 6/runtime remains later work |
| Phase 6 planning history | [Owner decisions](phase6_prologifier/OWNER_DECISIONS.md), [inspected scope](phase6_prologifier/INSPECTED_SCOPE.md) | Historical pre-implementation notes; their old approval statements do not override subsequent owner instructions or delivered code |
| Private conversion lifecycle | [Architectural draft](private_lifecycle_design/SPEC.md) | Design only; owner review pending; cleanup High remains open |
| Earlier same-process cleanup option | [Proposal](session_cleanup_design/PROPOSAL.md) | Historical, unapproved alternative; indefinite retained files do not meet the selected lifecycle requirements |
| Master/thesis/architecture alignment | [Assessment](plan_alignment_20261011/REPORT.md) | Pre-implementation assessment; its two plan corrections were incorporated and implemented |

Imported documents preserve their original bytes and historical wording, including unchecked authoring steps and machine-local evidence paths. Use [current status](CURRENT_STATUS.md), Git and the implementation decision records for delivery state. Edit the repository copies for future planning changes; do not resume an obsolete scratch copy as the current plan. [Import provenance](IMPORTS.md) identifies the source snapshots and hashes.

## Delivery and review

- [Delivery report](delivery/DELIVERY_REPORT.md)
- [Actual CLI/library wiring](delivery/WIRING_VERIFICATION_5342587c.md)
- [Completed independent whole-branch review](delivery/final-branch-review-completed-5342587c-isolated.md)
- [Update for Lawrence](delivery/LAWRENCE_UPDATE.md)
- Implementation decisions: [unified ingestion](../../docs/decisions/phase-02-unified-ingestion.md), [inactive rule candidates](../../docs/decisions/phase-06-prospectus-candidates.md)

The imported delivery report's evidence references remain local execution records, not additional committed artifacts. The 525 candidate tests and 18 integrated smoke checks are recorded earlier runs, not tests rerun during this documentation migration.

## Formal phase state and earlier history

The [formal ledger](../INDEX.md), [Phase 1 handoff](../phase-01-handoff.md) and [Phase 2 plan](../phase-02-document-ingestion-plan.md) retain their separate advancement rules. This documentation migration does not start or complete a formal phase.

The September/October handoffs in `plans/` remain historical snapshots: [September 26](../CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md), [October 7 Claude pickup](../CLAUDE_CODE_HANDOFF_prospectus_phase2_2026-10-07.md), [October 7 master status](../phase2_prospectus_master_status_2026-10-07.md). Their older branch tips, percentages and queues are not current delivery evidence.

## Bulk scratch copies

`plans/progress_plans/` is a local bulk-copy destination, not a curated documentation source. It is ignored because a whole scratch tree can contain original PDFs, generated JSON/Prolog, model or parser caches, test archives and private artifacts. Do not stage that directory or use `git add .`/`git add -A` to publish plans. Select reviewed text documents explicitly.

## Full scratch documentation audit

The initial import above selected 13 documents. The [full scratch audit](documentation-audit-2026-10-11/README.md) now maps the remaining development records: 202 distinct missing Markdown documents and 31 rendered state snapshots are preserved in the [historical index](history/scratch-2026-10-11/README.md). Existing current files and published Git-history versions are mapped instead of duplicated. Exclusions and coverage limits are explicit in the audit.
