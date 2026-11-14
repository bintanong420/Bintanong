# Phase 11 policy-ingestion developer task

Status: **not started; waiting for the primary's review-complete shared baseline**.
This is a dedicated workstream record, not a numbered phase plan/checkpoint.
[Coordination contract](2026-10-26-phase11-two-developer-workflow.md).

## Brief and boundaries

Build reusable researcher ingestion commands and a separate local review UI by
connecting the existing candidate, review, embedding, staging and release components.
Reuse the [implementation assessment](2026-10-26-ingestion-pipeline-assessment.md),
[existing ingestion specifications](ingestion/README.md), approved field decisions
and existing interfaces. Keep newly generated chunks inactive and isolated.

The primary retains source decisions, active knowledge, chatbot/frontend/runtime,
hosted database, releases, runtime pin and central checkpoint ownership. This
developer owns new ingestion modules, local review UI, ingestion-specific tests and
this task record. Existing parsers/contracts/storage/dependencies require a recorded
agreement and one designated implementer before modification.

## Start receipt — fill from verified evidence

| Item | Current state |
| --- | --- |
| Review-complete shared Git commit | Not established; do not substitute current HEAD |
| Source/package manifest | Comparison-only snapshot linked above; final baseline pending |
| Feature branch | `feat/p11-policy-ingestion-review`, not created yet |
| Separate worktree | Not created yet |
| Generated outputs | Workspace `audit-evidence/p11-policy-ingestion-review-20261026/` |
| Disposable local database | Not configured or validated |
| Shared interface changes | None agreed or implemented |

Do not copy the primary `.env`, hosted credentials, hosted release job configuration
or runtime pin. Supply database targets explicitly. Verify that every persistence,
staging, review, publication, migration and rollback operation is confined to an
identified disposable local instance before executing it. Missing, hosted or
unverified targets must be refused before mutation. Loopback wording alone does
not establish a disposable local database when a proxy/forwarder is in use.
The existing Orca post-create script copies ignored `.env` files and runs `npm ci`;
avoid that setup path until credential copying and unapproved installs are excluded.
Do not edit shared workstation setup as an incidental ingestion implementation step.

## Delivery checklist

- [ ] Verify baseline Git/source/package identities; retain original PDFs and
      settled decisions. Use evidence copies, not the primary's mutable paths.
- [ ] Inspect existing requirements/tests and write a bounded implementation plan
      in this repository before code. Reuse current dependencies and interfaces.
- [ ] Implement resumable commands and local review UI in separate modules through
      meaningful RED/GREEN tests. Bind each new-edition decision to its own bytes
      and locators; distinguish suggested readings, delegation, human decisions,
      exclusions and unresolved fields.
- [ ] Preserve audience, conditions, source gaps, complete logical services,
      field associations, companion context and topic/claim/package metadata.
- [ ] Demonstrate fail-closed database target checks with zero writes for absent,
      hosted and unverified targets; test actual persistence, inactive staging,
      local publication and rollback only in the disposable local database.
- [ ] Generate candidate chunks locally when needed and explain differences from
      the reviewed baseline. Do not publish them into the primary runtime.
- [ ] Coordinate resource-heavy embeddings with the primary's latency work.
- [ ] Report exact commits, changed interfaces, commands/results, package comparison,
      local database identity/reset procedure, known gaps and generated-output paths.
- [ ] Submit the branch for primary review and integration; merging tooling does
      not authorize hosted changes or activation of its generated packages.

## Shared-change agreement and updates

No shared-change proposals or implementation updates yet. For each proposal record
the interface, resulting behavior, compatibility, agreed implementer and commit;
then report both ingestion and runtime compatibility test results. Keep this record
compact and leave central Phase 11 progress/checkpoint edits to the primary.
