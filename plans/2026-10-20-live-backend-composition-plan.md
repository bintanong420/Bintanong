# Real-service backend composition

20October2026; p09/feat/p09-generation-validation; baseline684a2fe.
Owner directs continuation after the architecture audit and asks whether Phase07
functionality was omitted. Student capability: one natural request traverses the
diagram's actual backend components and returns a validated candidate answer.
Specification: master3/11/12/13/14, actual runtime PNG, thesis physical17–18/39–44,
standing prompt decision and source/scope holds. No Phase10 or HTTP/UI work.

## Design and boundaries

Add an explicit composition module/CLI around existing Orchestrator and
AnswerPipeline. Load a versioned synthetic runtime bundle, reviewed catalog,
release pin and embedding asset manifest; construct the real LlamaTransport,
strict local QueryEncoder, SupabaseStorageClient, RetrievalEngine and Janus
CurriculumRuntime. A read-only provider checks active release membership and
synthetic source identities before exposing resources. Default application release
hold stays. This controlled fixture proves service wiring, not institutional
authority, corpus readiness, language-wide accuracy or deployability.

No model/dependency downloads or service restarts. Existing local services/assets
are reused. The owner-corrected workspace/MODELS path is inherited; the former
C:/Coding-projects/MODELS path is absent. Configure the actual root explicitly.
Use anon/RLS for all request-time database operations; no admin credentials in
the runner. Any fixture setup stays separate from request execution and cannot
replace an existing active corpus. Raw data/evidence stays ignored under workspace.

Ruling: extend the existing callable modules instead of building a second router
or agent framework; this isolates the missing composition without changing
reviewed rules/prompts. A false assumption here would leave gaps in the full path;
the live per-stage trace and final independent review are the acceptance checks.

## Tasks and acceptance

1. Focused RED tests for manifest validation, real adapter composition, synthetic
   source/release mismatch holds and resource cleanup. Implement minimal GREEN.
2. Provide a bounded request CLI with explicit input/output files, finite budgets,
   safe stage/call metadata and rendered CandidateAnswer; no preassembled evidence,
   scripted model, manual vectors or database responses in the live invocation.
3. Prepare only fictional course/procedure data in an isolated controlled local
   fixture. Verify actual SEA-LION embeddings, PostgREST/pgvector, Janus and local
   model. Run one complete natural query per RAG/Symbolic/Hybrid route; preserve
   actual failures and independently inspect output scope/citations/decision.
4. Check Phase07 against master12/code/tests. Record implemented functionality,
   deliberate boundaries and confirmed defects without reopening a prompt sweep.
5. Run relevant regression gate and one independent final whole-change review;
   commit cohesive increments and update recovery/delivery evidence.

TDD uses existing Python3.13 readiness environment, -B -m pytest -q
-p no:cacheprovider with external TEMP/TMP/basetemp. Live budgets are explicit
observations, separate from existing default120/180s readiness claims. Exit needs
actual per-route stage identities/outcomes and honest output assessment, not just
passing mocks. Source/release/activation holds remain if a live attempt fails.
