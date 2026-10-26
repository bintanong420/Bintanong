# Policy ingestion and local review implementation plan

Recorded 26 October 2026. Status: owner-approved; T0 preparation started, no
implementation code yet. This is a Phase 11 feature plan subordinate to the active
phase plan, not a new phase.

**Goal:** build a reusable ingestion pipeline and local researcher review UI for
new Handbook and Citizens' Charter editions, through verified local packages.
**Architecture:** connect existing ingestion, review, embedding and storage contracts
with a manifest-driven command suite; keep source review explicit and outputs inactive.
**Stack:** system Python 3.13 and existing FastAPI for ingestion/review services;
existing Next.js/React/TypeScript stack and suitable shared components for the UI.
**Execution:** use the installed executing-plans workflow task by task, with the
repository TDD/handoff rules. No agent delegation is needed for this plan.

## Owner approval and preparation state

26 October 2026: owner explicitly said **"I approve of the plan."** This approves
the feature plan and its recorded frontend-stack amendment. It does not establish
institutional/source approval,authorize hosted access or explicitly answer the
three remaining product questions. Those defaults remain proposed;independent
baseline/worktree preparation can proceed.

Created local `feat/p11-policy-ingestion-review` directly from the verified Git
fork4e99fb6 at the planned workspace path. The reported c76d988 commit could not be
found locally or by GitHub,and the named branch/path did not exist here before
creation. No existing workspace was replaced and no setup/install hook was used.
The upstream source/package comparison directory is missing locally;its path has
been requested. Git identity is verified;byte verification/rehearsal of the actual
reviewed package remains pending and must not be claimed from the notes alone.

## Request and supplied context

The owner requested repository context/instructions for ingestion work, explicitly
excluding hosted Supabase changes, and then required English agent replies.
The owner also permits relevant installed skills to augment repository workflows;
they do not expand task scope or override the owner's operational boundaries.
The supplied `message (1).txt` (Two-Developer Phase 11 Workflow) and
`message (2).txt` (Policy Ingestion and Review Feature Branch Plan), read from
`E:/Hawksprey/Downloads/`, serve different purposes: the first divides ownership
between concurrent developers; the second specifies software to build, its command
suite, local review UI, implementation sequence and acceptance tests. Together they
define this implementation plan, not merely background context. The owner's
ingestion-only and hosted-database restrictions constrain its release operations.
This repository record makes the context available without those external files.

## Original notes and fidelity

The supplied notes are preserved verbatim as
[developer workflow](2026-10-26-policy-ingestion-developer-workflow.md) and
[developer feature plan](2026-10-26-policy-ingestion-developer-plan.md).
These are reference snapshots, not instructions to execute hosted operations.
Original byte hashes: workflow `4dd54518f743e09c3d8ba0bd0c1a76fe6640c058c4f1e8671ba3963e67ec2473`;
feature plan `444f037dc5cfb8243f4a7e0b32940d07e260d59faa1a9308bbbb7d3197c371f6`.

Preserve the specified functionality and five-step sequence: packet/command
boundary; local review UI; reviewed package building; verification/release tooling;
documentation/rehearsal. The task breakdown below supplies engineering detail,
not a replacement specification. All seven commands remain in scope. The prior
grilling suggestions about changing the CLI/UI split, deferring release tooling
or changing unsupported-layout acceptance are withdrawn; the notes settle those.

Owner additions: ingestion-only work, no hosted access, English agent replies and
relevant installed skills. Owner explicitly amended the reviewer UI technology:
align both appearance and frontend stack with Bintanong,using Next.js/React/
TypeScript and reusable existing styles/components,while retaining FastAPI services.
This replaces only the note's plain HTML/CSS/JavaScript UI choice. Carry the Phase2
prospectus review capability forward and extend it to Handbook/Charter review;
preserve the rest of the developer's specified workflow and acceptance criteria.
The source note's hosted/package readback and maintenance wording describes a
broader operator release process; this developer rehearses it only against a
disposable local database/test descriptor. Future actual hosted operations stay
with the runtime owner under separate explicit authorization.

## Repository context to carry into implementation

- Phase 2 already has the prospectus browser review GUI at
  `backend/bintanong_tools/prospectus_review_gui/`. Its PDF display, region
  highlights, queue, ledger locking and access protections are reuse points;
  its course/prerequisite question schema is specific to prospectuses.
- The general institutional ingestion entry point at
  `backend/bintanong_tools/document_ingest/__main__.py` is CLI-based. Its pipeline
  and hash-checked bundle loader supply preparation and raw-candidate replay.
  They are separate from reviewed package replay; do not transfer source approval.
- Later reviewed-policy builders and service/flowchart bindings already enforce
  source-bound decisions and associations. The main new bridge is the policy
  review session/export feeding those existing records, plus command orchestration.
- Reuse compatible embedding batches and existing storage/review/release loaders.
  Supply verified disposable local clients explicitly; ambient configuration can
  otherwise target hosted services. Runtime-descriptor recovery needs a local journal.
- Historical Phase 2 delivery is software evidence, not universal extraction or
  content accuracy. Current PPTX slides remain withheld for unsupported locators;
  older Charter failures have not been freshly reproduced in this review.
- Semi-align the new local UI through scoped colors, borders, spacing and controls
  from `frontend/app/styles.css`. Keep the source-comparison workspace, independent
  audience/content decisions, reasons, companion context, history and export.
  Retain FastAPI services and original prospectus behavior;adapt browser controls to
  React,with document-specific policy/service decisions rather than course schemas.
  Use available local font assets/fallbacks; no new dependencies or remote assets.
- The fixed backend fork has a minimal older frontend and lacks the current UI
  primitives. Explicitly coordinate import of selected later frontend code/styles
  and compatible existing dependency declarations;forking4e99fb6 alone does not
  supply them. Inspect the exact manifest/lock diff before any change under the
  existing owner dependency rules. Student Supabase auth/chat proxy is not a
  researcher transport and must not be copied into this local workflow.

See [reuse/UI inspection](2026-10-26-policy-ingestion-plan-review.md) for limits and
the remaining product questions. Recommendations there are not owner decisions.

## Ownership and isolation

- Ingestion developer: reusable Handbook/Citizens' Charter preparation, local
  researcher review UI, local candidate packages and ingestion-specific tests.
- Runtime developer/owner: student frontend/API, routing, orchestration, generation,
  current source decisions, active knowledge, hosted Supabase and runtime pin.
- Proposed feature branch: `feat/p11-policy-ingestion-review`, isolated under
  `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/`, eventually integrated
  into `feat/p11-backend-api`. Do not switch or repurpose another developer's tree.
- Attachment base `7590a71` is historical context, not a verified current baseline.
  The synced backend workflow now identifies fixed reviewed fork
  `4e99fb655022e694c73bbd98dd6daec9d7d88fb5`;the local backend is at879748b.
  These are distinct: use the fixed fork,then integrate agreed later interface
  changes deliberately. [Sync evidence](2026-10-26-backend-origin-sync.md) records
  the upstream c76d988 workspace receipt,absent locally/on origin here;reconcile
  that receipt before creating a duplicate branch/worktree. Preserve actual bounded
  review records and holds;no whole-document approval or repeat reconstruction.
- Keep a dedicated ingestion task record here; supply concise updates for the
  central Phase 11 checkpoint/progress maintained by the coordinating developer.
- Generated/source-derived artifacts remain ignored under workspace `audit-evidence`.
  Coordinate expensive embedding runs with chatbot latency measurements.

## Hosted boundary

Follow the binding boundary in [AGENTS.md](../AGENTS.md). No hosted connection or
operation is part of this workstream, including inspection, review RPCs, staging,
publication, rollback, migration or activation. Do not copy hosted credentials
into the ingestion environment. Validate an explicit disposable local target before
any database operation; missing or ambiguous targeting must stop the operation.
Do not fall back to ambient hosted environment settings or linked-project defaults.

The attachments' stage/publish/rollback work means disposable local rehearsal only.
Use a local test runtime descriptor for rollback, never the chatbot's active pin.
Hosted publication remains a separate future operation requiring an explicit owner
instruction. Merging tooling does not publish its outputs.

## Researcher workflow to implement

Reuse `backend/bintanong_tools/document_ingest/`, existing contracts, reviewed-policy
builders and source/service/flowchart bindings. Add the connecting workflow under
`backend/bintanong_tools/knowledge_update/` only where existing tools do not suffice.
Read [ingestion status](ingestion/README.md) and relevant code before implementation;
historical delivery notes do not prove current readiness.

1. **Prepare:** accept original PDFs or hash-verified candidate bundles, explicit
   source metadata and an optional baseline. A manifest references originals,
   candidates, review inputs, baseline membership and the local target release.
   Preserve originals; produce extraction findings and an unreviewed packet.
2. **Review:** provide a loopback-only Next.js/React/TypeScript interface backed by
   FastAPI,using the installed frontend stack/components and prospectus-review patterns.
   Search by document, section, review state or finding; compare original PDF pages
   with extracted text/table fields and available region highlights. Show related
   blocks and required companions together. Support accept/correct/hold decisions,
   reasons, save/reopen, decision history and export.
3. **Build/verify:** consume source-bound decisions and reuse compatible builders
   and embeddings for chunks, receipts, topics, claim reviews and package metadata.
   Require explicit retained/replaced/removed membership against a baseline.
   Check tokenizer/context budgets; successful insertion does not prove coverage.
4. **Local rehearsal:** stage an inactive draft in an explicit disposable database;
   test retry-safe staging, initial/supplementary review and local publish/rollback
   journals, including restoring the previous local release and test descriptor.
   The review UI has no publication button. Any stopped-service exercise uses the
   disposable local test service, not the active student runtime.
5. **Document/integrate:** provide synthetic examples and operator instructions;
   rehearse a sealed package with saved decisions/vectors. New source expansion
   requires its applicable review decisions and is not authorized by this record.

## Implementation tasks and dependencies

T0 preparation is in progress; T1–T5 are pending. Proposed new paths are targets, not
claims that modules already exist. Keep each task to a focused RED/GREEN cycle and
verified commit; do not build a second parser, reviewer or release manager.

### T0: Freeze the baseline and isolate the work

- [x] Check reported start receipt: c76d988 absent locally/GitHub;the named local
  branch/worktree and origin branch were absent before creation.
- [x] Create `feat/p11-policy-ingestion-review` in the dedicated worktree from
  `4e99fb655022e694c73bbd98dd6daec9d7d88fb5`,without switching the owner's checkout.
- [ ] Verify reviewed source/package bytes from the actual local baseline,not its
  historical receipt alone. Recorded evidence directory is missing;local path requested.
- [x] Carry this plan,verbatim notes and current owner boundaries into that tree.
- [ ] Inspect callers/contracts and tests of the reuse points below. Record the
  baseline hashes, affected interfaces and local output directory in this plan.
  Prioritize this tooling before new Handbook/Charter expansion; grading fixes stay separate.
- Exit: reproducible baseline, explicit ownership and no hosted credentials/target.

### T1: Manifest, prepare command and source-bound review packet

Depends on T0. Create `backend/bintanong_tools/knowledge_update/` with
`__main__.py` for `main(argv=None) -> int`, `manifest.py` for validated inputs and
`prepare.py` to connect existing extraction/bundle loaders. Reuse
`document_ingest/__main__.py`, `pipeline.py` and `bundle.py`; preserve their CLI.

- [x] Add `tests/test_knowledge_update_prepare.py`: two synthetic editions work
  from manifest inputs without Python edits; new packets start unreviewed;
  missing/altered inputs fail before output promotion; originals stay byte-identical.
- [x] Observe RED; implement `prepare` and verify GREEN with the existing ingest
  regressions. Packet identity must bind source/candidate hashes and review inputs.
- Exit: one command produces an inspectable packet and findings with no database access.

### T2: Persisted human review and local browser interface

Depends on T1. Add `review.py` and `app.py` in the new Python package for review
persistence/API. Build an isolated local Next.js/React/TypeScript reviewer using
the existing frontend dependency set and suitable components/styles. Reuse
session/rendering/security behavior from `prospectus_review_gui/`;carry prospectus
review into the new interface and add policy/service controls. Preserve existing
prospectus behavior and entry points. Expose `review` through the same CLI.

During T0,verify the smallest separate Next app layout and component import paths
against installed dependencies before adding UI files. Keep the local researcher
app outside student routes/authentication and protect both local servers;do not
reuse the student's hosted Supabase session/configuration. Shared component or build
changes follow the coordination contract. No installation or lockfile change is
implied by adopting the already-used stack.

- [x] Add `tests/test_knowledge_update_review.py`: save/reopen, revised decisions,
  independent audience/content decisions, stale evidence and concurrent writers.
  A proposal, pending field or one corrected field cannot approve a whole service step.
- [x] Add `tests/test_knowledge_update_review_api.py`: loopback/Host/Origin/access
  checks, escaped source text, missing geometry holds and source-bound export.
- [ ] Add researcher UI checks in the existing frontend test/browser conventions:
  prospectus behavior survives the React adaptation;Handbook/Charter controls keep
  required evidence/decision functionality;student builds/routes stay unaffected.
- [ ] Observe RED; implement the workflow's comparison/search/companion/history
  controls; verify GREEN plus browser comparison, navigation, correction and export.
- Exit: actual human decisions persist with history and exact evidence identities.

### T3: Reviewed package build and verification

Depends on T2. Add `build.py` and `verify.py` in the new package, exposing `build`
and `verify`. Reuse `document_ingest/reviewed_policy.py`, `reviewed_policy_chunks.py`
and reviewed context bindings, plus existing embedding/contracts validation.

- [ ] Add `tests/test_knowledge_update_build.py`: held/excluded/unresolved fields
  stay unusable; preserved blanks/gaps/cross-page associations and missing companions
  affect verification; baseline retained/replaced/removed membership is explicit.
- [ ] Add `tests/test_knowledge_update_verify.py`: missing topic/claim metadata,
  incompatible vectors, altered receipts and context-budget overflow are rejected;
  reusable compatible vectors retain identity and require no model download.
- [ ] Observe RED; connect builders and verifiers; verify GREEN with reviewed-policy,
  service-step/context and downstream package-consumer regressions.
- Exit: verified local package and a report that distinguishes coverage from insertion.

### T4: Disposable local staging, publication and recovery rehearsal

Depends on T3. Add `local_release.py` in the new package for `stage`, `publish` and
`rollback`; reuse `BatchKnowledgeLoader`, `SelectedReleaseReviewLoader` and
`ReleaseManager` in `backend/bintanong_storage/`. Change shared code only by agreement.

- [ ] Add `tests/test_knowledge_update_local_release.py`: missing/hosted/ambiguous
  targets are rejected before connecting; verified packages stage inactive; repeated
  staging is unchanged; conflicting identities fail without partial writes.
- [ ] Test initial/supplementary reviews using actual roles in a disposable local
  database. Inject interruptions and verify the journal restores both the previous
  local release and local test descriptor; active chatbot files remain byte-identical.
- [ ] Observe RED; implement the bounded local adapters; verify GREEN alongside
  storage idempotency/release-isolation regressions. No hosted smoke test is permitted.
- Exit: local release lifecycle is retryable and recovery evidence is recorded.

### T5: Operator documentation, rehearsal and integration delivery

Depends on T1–T4. Add `docs/development/policy-ingestion.md` with synthetic examples,
the seven commands, local target setup, review/export steps and failure recovery.

- [ ] Rehearse two synthetic editions end to end, then the fixed sealed package
  locally with saved decisions/vectors. Compare against the reviewed baseline.
- [ ] Run ingestion, existing review GUI, storage and chatbot compatibility checks,
  then the relevant full suite. Record failures/skips without weakening source guards.
- [ ] Deliver verified commits and compatibility results for integration into
  `feat/p11-backend-api`; update central Phase 11 progress/checkpoint by coordination.
- Exit: a researcher can repeat the workflow using commands and the local UI without
  editing package-specific Python. Outputs and hosted/runtime state remain separate.

For each test file, run `py -3.13 -m pytest -p no:cacheprovider <test-file>` with
`--basetemp C:/Coding-projects/bintanong_workspace/audit-evidence/p11-policy-ingestion/<task>`.
Expected RED must match the missing behavior, then GREEN must pass the same checks.
Local database tests require a verified disposable target; missing infrastructure
is an unavailable check, never permission to substitute hosted Supabase.

## Review and compatibility invariants

- Separate undergraduate-applicable, excluded and unresolved audience decisions.
  Staff actions inside undergraduate services remain legitimate. Mixed/unknown
  applicability stays unresolved; preserve the undergraduate study boundary.
- AI sessions may propose readings, grouping and mappings. Actual human decisions
  remain bound to exact source/candidate identities, with history preserved.
  No approval transfers automatically between editions or follows from opening a page.
- Preserve original text separately from corrections; reject altered/stale evidence.
  Missing geometry or unsupported layouts remain visible holds. Preserve blanks,
  cutoffs, conflicts, fees, conditions, procedure order and complete companion groups.
  Apply the source-gap and service-table policies; never invent missing content.
- Before changing shared contracts, schemas, parsers, topic/claim metadata, release
  formats, storage interfaces or dependencies, identify affected callers/tests and
  agree on compatibility with their owner. One designated developer makes the
  shared change; verify both ingestion and runtime compatibility afterward.
- Student API/frontend and runtime fixes remain with the runtime developer. Keep
  grading defects separate. No new dependencies, schema migrations, model downloads,
  built-in model reviewer, model training or public hosting are authorized here.

## Verification and completion

Use focused RED/GREEN regressions and small verified commits when implementation
starts. Cover two synthetic editions without Python edits; audience decisions;
cross-page steps, blanks, corrections/gaps and missing companions; save/reopen and
concurrent writers; stale/wrong-source evidence; safe rendering and loopback access;
missing metadata/incompatible vectors; local role boundaries, retries, interruption
and rollback; rejection of hosted or ambiguous targets; and browser export flows.
Use system Python 3.13, pytest without cache and external evidence/basetemp paths.
Run relevant ingestion/chatbot regressions and the appropriate full suite before
integration; disclose unavailable checks and validate Phase 11 artifacts.

Acceptance is a source-bound, reviewable, verified local candidate/staged package
with preserved originals/history. It does not establish arbitrary-PDF automation,
institutional approval, hosted activation, Phase 11 closure or Phase 12 advancement.
This documentation update makes no implementation or test-suite success claim.

## Final product questions

The remaining owner choices are one active reviewer versus simultaneous editing
of the same packet,English versus multilingual researcher UI,and desktop-first
versus full phone review acceptance. Proposed defaults are recorded in the review
document;none has been adopted without an answer. These choices do not reopen the
seven commands,source safeguards,frontend-stack amendment or local-only boundary.
