# Document loader readiness — 16 October 2026

At baseline `17c097b`, the existing document candidates now have validated loader
artifacts. A real disposable PostgreSQL rehearsal identifies two concrete source
registration prerequisites. Successful import, draft creation and runtime
retrieval of these institutional candidates remain unverified. Product code is
unchanged; Phase 05 Tasks 4/6 remain open.

## Capability and evidence path

This work advances source-backed document retrieval for undergraduate procedures
and policy explanations. It checks the Phase 05 governed-ingestion/runtime exit
requirement: can existing artifacts enter the existing loader without changing
their source states? It is not another retrieval parameter experiment. Curriculum
facts and eligibility remain on their structured/Symbolic path.

Inputs are the existing candidate corpus, source versions, subject catalogue,
claim reviews, 39-case trusted annotations and three compatible saved-vector
files. Selection includes every assigned chunk for the seven document subjects:
academic misconduct, grade completion, grading scale, overload, pre-enrollment,
special-class fees and vehicle pass. All required neighbors remain included.

Derived artifacts contain **19 unchanged chunks, 19 reused 1024-dimensional
vectors, 54 ordered source spans and five unchanged source versions**. Nine input
file hashes are preserved. Every chunk remains pending source verification and
content review. Source versions retain pending verification/review and
not_requested approval. Contract parsing, text/source/version/hash binding,
vector normalization and exact saved embedding token counts validate. Chunk
token estimates remain estimates; no tokenizer/model execution was needed.

The deterministic embedding-set ID is
`02fce0fc4caca1c15cc4a58f5e511f70d5dc27be77769f7cbb0f7ce423368811`.
The package contains the derived catalogue/review register and loader-compatible
manifest/embedding JSONL, plus unchanged chunk/version payloads. It is a validated
candidate package, not a successfully imported or authorized release.

## Fresh hosted inspection

Read-only Supabase MCP inspected the bound hosted project, PostgreSQL 17.6:

- Six Phase 04 migrations are applied. Repository migration
  `20261012013339_phase5_retrieval_snapshot.sql` is not applied;
  `public.retrieve_context` is absent from the function catalog.
- Documents, document versions, chunks, embeddings, releases and active-release
  pointer each have zero rows. All 19 public tables have RLS enabled.
- Security advisor returns zero lints. Administrative batch import and activation
  deny anon/authenticated EXECUTE; existing match_chunks is invoker and callable
  by those roles.

No hosted writes, migration application, credential extraction or activation
occurred. This snapshot is not an HTTP/JWT retrieval test. Context7's official
[Supabase function guidance](https://supabase.com/docs/guides/database/functions)
was consulted for caller-role execution/RLS and explicit grants. Changelog and
relevant PostgreSQL upgrade notice were checked; no upgrade was performed.

## Disposable database rehearsal

`rehearse_boundaries.py` used the existing `tests/storage_database.py` harness.
It created `bintanong_storage_test_8e72442e657c433aa0c0d8874a34ee4f`, applied the
seven existing repository migrations only there, and used the actual service_role
import RPC and anon retrieval RPC through psql. No approved synthetic source
fixture was substituted for the real pending records.

1. `BatchKnowledgeLoader.load_artifacts` rejects the package because its parent
   document/version registrations do not exist. The foreign-key failure rolls
   back the batch: documents, versions, chunks, spans, embedding sets, embeddings,
   releases and active pointer all remain zero.
2. An exact unchanged source-register document category, `source_document`, is
   rejected by `documents_document_category_check`. The database accepts five
   specific categories; no category was guessed or source state promoted.
3. Actual anon `retrieve_context` returns `release_changed` with no items for the
   candidate pin. Runtime chunks and document versions are empty. There is no
   imported draft, so this does not establish visibility behavior of a loaded
   draft or an active real-source release.
4. The disposable database was dropped through the harness's name-checked cleanup.
   All nine source input hashes remain unchanged. No activation was attempted.

This resolves the bounded readiness question. Repeating the negative import or
another similarity sweep will not resolve the missing registration contract.

## Recovery and boundaries

The next engineering step is a governed document/version registration contract
and importer, with explicit storage-category metadata and state-preserving
mapping from the source register. Existing BatchKnowledgeLoader imports chunks,
spans and embeddings; it does not register their parent sources. Do not call this
a loader bug or weaken its foreign keys. Use focused TDD for new importer
behavior, including unknown categories, pending states, idempotency and atomic
failure, before a positive isolated draft-import rehearsal.

Shared migration/application and institutional activation retain their existing
boundaries. Calibration still needs an adopted policy and formal reviewed
evaluation; source-aware positive field results remain uncalibrated. School
verification, F04, G01/original G02 and known gaps/conflicts remain held. This
increment needs no repeated wording or source-content approval and creates no
Phase 06 plan. The prior rough 80% technical estimate is unchanged and is not a
measured formal gate.

## Reproduction and evidence

Use the existing Python 3.13 readiness venv at
`workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
Raw artifacts/scripts/MCP responses and SQL outputs reside in ignored
`workspace/audit-evidence/p05-release-readiness-20261016`.
Executed `python -B prepare_package.py` and
`python -B rehearse_boundaries.py`, both exit 0 after the package script's initial
field-name correction (`verification_state`, not `source_verification`). An
earlier PDF reader attempt found fitz/pypdf unavailable; no package was installed.
Consulted the existing original scope renders, physical 17–18, and routing PNG;
no scope/routing discrepancy. No original conversion was repeated.

The 49-file evidence manifest SHA-256 is
`cf996f72c2f0234eacc1ceee04870115a5727bc56dcfb3c6b8084ae9d5794a1e`.
Use only `python -B seal_evidence.py verify`; do not rerun writers in this sealed
root. Prior source-aware and document-comparison seals remain untouched. Check
logs belong in sibling `p05-release-readiness-checks-20261016`.

Documentation/ledger verification: `python -B -m pytest
tests/test_docs_hygiene.py
.agents/skills/bintanong-phase-handoff/tests/test_phase_state.py -q
-p no:cacheprovider --basetemp <checks-root>/pytest-temp` passes 502 tests and
11 subtests in 13.07s, exit 0. Phase validation succeeds; can-advance refuses the
blocked Phase 05 as expected. `git diff --check` passes. No product changes
justify repeating the prior 5388-test full suite. Owner artifact changes remain
preserved and unstaged.
