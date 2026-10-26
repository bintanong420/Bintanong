# Policy ingestion and local review implementation plan

Recorded 26 October 2026. Status: planned; implementation not started. This is a
Phase 11 feature plan, subordinate to the active phase plan, not a new phase.

**Goal:** build a reusable ingestion pipeline and local researcher review UI for
new Handbook and Citizens' Charter editions, through verified local packages.
**Architecture:** connect existing ingestion, review, embedding and storage contracts
with a manifest-driven command suite; keep source review explicit and outputs inactive.
**Stack:** system Python 3.13, existing FastAPI and plain HTML/CSS/JavaScript.
**Execution:** use the installed executing-plans workflow task by task, with the
repository TDD/handoff rules. No agent delegation is needed for this plan.

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

## Ownership and isolation

- Ingestion developer: reusable Handbook/Citizens' Charter preparation, local
  researcher review UI, local candidate packages and ingestion-specific tests.
- Runtime developer/owner: student frontend/API, routing, orchestration, generation,
  current source decisions, active knowledge, hosted Supabase and runtime pin.
- Proposed feature branch: `feat/p11-policy-ingestion-review`, isolated under
  `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/`, eventually integrated
  into `feat/p11-backend-api`. Do not switch or repurpose another developer's tree.
- Attachment base `7590a71` is historical context, not a verified current baseline.
  Before implementation, confirm a fixed, reviewed package/commit with the runtime
  developer; preserve it unchanged for comparison. No whole-document approval follows.
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
2. **Review:** provide a loopback-only FastAPI/plain HTML/CSS/JavaScript interface
   using installed dependencies and suitable existing prospectus-review patterns.
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

All tasks are pending. Proposed new paths below are implementation targets, not
claims that modules already exist. Keep each task to a focused RED/GREEN cycle and
verified commit; do not build a second parser, reviewer or release manager.

### T0: Freeze the baseline and isolate the work

- [ ] Establish the reviewed input/package identity and actual backend commit;
  create the dedicated feature worktree without changing the owner's checkout.
- [ ] Inspect callers/contracts and tests of the reuse points below. Record the
  baseline hashes, affected interfaces and local output directory in this plan.
  Prioritize this tooling before new Handbook/Charter expansion; grading fixes stay separate.
- Exit: reproducible baseline, explicit ownership and no hosted credentials/target.

### T1: Manifest, prepare command and source-bound review packet

Depends on T0. Create `backend/bintanong_tools/knowledge_update/` with
`__main__.py` for `main(argv=None) -> int`, `manifest.py` for validated inputs and
`prepare.py` to connect existing extraction/bundle loaders. Reuse
`document_ingest/__main__.py`, `pipeline.py` and `bundle.py`; preserve their CLI.

- [ ] Add `tests/test_knowledge_update_prepare.py`: two synthetic editions work
  from manifest inputs without Python edits; new packets start unreviewed;
  missing/altered inputs fail before output promotion; originals stay byte-identical.
- [ ] Observe RED; implement `prepare` and verify GREEN with the existing ingest
  regressions. Packet identity must bind source/candidate hashes and review inputs.
- Exit: one command produces an inspectable packet and findings with no database access.

### T2: Persisted human review and local browser interface

Depends on T1. Add `review.py`, `app.py` and `static/` in the new package. Reuse
app/session/rendering/security patterns from `prospectus_review_gui/` while keeping
its prospectus-specific behavior unchanged. Expose `review` through the same CLI.

- [ ] Add `tests/test_knowledge_update_review.py`: save/reopen, revised decisions,
  independent audience/content decisions, stale evidence and concurrent writers.
  A proposal, pending field or one corrected field cannot approve a whole service step.
- [ ] Add `tests/test_knowledge_update_review_api.py`: loopback/Host/Origin/access
  checks, escaped source text, missing geometry holds and source-bound export.
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
