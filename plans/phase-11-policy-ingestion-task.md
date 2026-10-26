# Phase 11 policy-ingestion developer task

Status: **T1 preparation implemented; T2 source-bound review in progress**.
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
| Review-complete shared Git commit | `4e99fb655022e694c73bbd98dd6daec9d7d88fb5`; bounded review only |
| Source/package manifest | Upstream recorded; local comparison directory missing, path requested |
| Feature branch | `feat/p11-policy-ingestion-review`, created from the fixed fork |
| Separate worktree | `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p11-policy-ingestion-review` |
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

Owner approved [the feature plan](2026-10-26-policy-ingestion-workstream.md), including
Next.js/React/TypeScript UI plus FastAPI and prospectus reuse extended to Handbook/CC.
Six ingestion documentation commits were initially made on frontend in error; they
have been transferred here. Frontend was reset to origin/frontend e172f53 with its
pre-existing dirty files restored. Recovery ref: recovery/p11-ingestion-misplaced-20261026.
All further ingestion changes belong in this worktree. No frontend push occurred.

Baseline synthetic checks:77 passed/110subtests,30.01s using Python3.13,pytest cache
disabled and external basetemp. Initial setup errors came from a missing basetemp
parent;creating that directory resolved them without code/dependency changes.
Source/package byte verification,UI/device/reviewer choices and local DB remain pending.
No credentials copied,no installs,hosted access or runtime/source activation.

T1:manifest validation,immutable source/candidate packet,replay,resume,visible page
holds and prepare CLI implemented in knowledge_update/. RED11missing-module failures,
then GREEN11;edge RED3 then GREEN68with existing bundle/report checks;CLI RED1 then
final GREEN69,21.31s. Commands:Python3.13 -Xutf8 -B -m pytest -q -p no:cacheprovider
tests/test_knowledge_update_prepare.py tests/test_candidate_bundle.py
tests/test_ingestion_report.py;external basetemps under the workstream evidence root.
T2 RED10 observed for missing ReviewSession;implementation and verification underway.
Ruling:missing real baseline defers byte/replay acceptance,not independent synthetic
implementation. Real-source accuracy/compatibility cannot be claimed until supplied.
Ruling:reuse one-writer ledger locking as the safe implementation default;no claim
that owner separately accepted simultaneous-review/UI-language/device choices.
Docker daemon is unavailable;actual-role local DB rehearsal remains an explicit gate.

No shared modules/dependencies changed. For each proposal record
the interface, resulting behavior, compatibility, agreed implementer and commit;
then report both ingestion and runtime compatibility test results. Keep this record
compact and leave central Phase 11 progress/checkpoint edits to the primary.
