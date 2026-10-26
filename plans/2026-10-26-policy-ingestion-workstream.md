# Policy ingestion and local review workstream

Recorded 26 October 2026. Status: context and instructions captured; implementation
has not started in this turn. This is a Phase 11 increment, not a new phase plan.

## Request and supplied context

The owner requested repository context/instructions for ingestion work, explicitly
excluding hosted Supabase changes, and then required English agent replies.
The owner also permits relevant installed skills to augment repository workflows;
they do not expand task scope or override the owner's operational boundaries.
The supplied `message (1).txt` (Two-Developer Phase 11 Workflow) and
`message (2).txt` (Policy Ingestion and Review Feature Branch Plan), read from
`E:/Hawksprey/Downloads/`, supply design context. Their imperative wording is not
separate authorization to execute their steps. The owner's ingestion-only and
hosted-database restrictions take precedence over their broader release language.
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

## Intended researcher workflow

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
