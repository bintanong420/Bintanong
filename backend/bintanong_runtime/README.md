# Actual service composition

This internal runner connects the existing LLM Router, strict local SEA-LION
QueryEncoder, Supabase PostgREST/pgvector retrieval, Janus CurriculumRuntime,
evidence assembly and Generator/validator/plain-text renderer. It takes natural
text and request context. It accepts neither a route override nor a preassembled
evidence package. The LLM still chooses the route.

The current authorization boundary is **fictional test sources only**. A runtime
specification contains `synthetic:true`, a complete generated runtime bundle,
ReleasePin, reviewed CatalogEntry records and SHA256 embedding asset manifest.
The bundle is rebuilt/validated before any service opens. Request-time pinning
uses anon/RLS reads to check the active release, exact chunk/version membership,
source hashes and `documents.synthetic=true`. Source or release mismatches hold
the request. This module has no ingestion, publication, source approval or
activation operation. The default Orchestrator institutional hold is unchanged.

Set `MODELS_DIR` to the existing owner-approved model root; the strict encoder
verifies its manifest and uses local files only. Set the existing storage client's
`SUPABASE_URL`/`SUPABASE_ANON_KEY` when needed. Requests use only the runtime role;
the runner does not use administrative database credentials. Reuse the existing
llama.cpp server; the runner does not start services or download models.
The verified CUDA sidecar uses18088;pass `--url http://127.0.0.1:18088` explicitly.
The CPU default remains18087 and its reference container is currently stopped.
See [CUDA setup/results](../../docker/bintu-cuda.md) for startup and rollback.
For repeated requests,keep one RuntimeApplication alive and initialize its strict
encoder at startup when retrieval is needed. Its encoder already retains the model;
each app.run still encodes its own question and pins/checks its release. Contexts
and orchestration remain per request. The single-request CLI still pays cold encoder
cost;[warm timings and startup are reported separately](../../plans/2026-10-20-fast-replies-results.md).

```powershell
python -B -m backend.bintanong_runtime runtime-spec.json request.json `
  --url http://127.0.0.1:18088 `
  --output C:/Coding-projects/bintanong_workspace/audit-evidence/run.json `
  --evidence-root C:/Coding-projects/bintanong_workspace/audit-evidence `
  --inference-timeout 240 --stage-timeout 300 `
  --generation-timeout 240 --request-timeout 600
```

Request JSON contains only `question` and `context` (RequestContext). Context
must be established by the owning caller; identifier consistency is not login or
session authentication. Private uploads/authentication remain separate work.
The spec is a trusted developer configuration, not browser/model input. See
[composition boundary tests](../../tests/test_runtime_composition.py) for a small
synthetic spec builder. Real preparation/observations stay in ignored evidence.

Trusted `--routing-profile` defaults to `separate`; RuntimeRun records that choice.
The opt-in `combined` developer candidate failed its fixed multilingual promotion
gate and remains experimental. Keep the default selected; fewer calls established
no further full-chain speed gain. See [candidate results](../../plans/2026-10-20-combined-routing-results.md).
The profile is application configuration, never request JSON or a model override.

Defaults remain 120s per inference/routing/generation and 180s per whole request.
Explicit `--inference-timeout`, `--stage-timeout`, `--generation-timeout` and
`--request-timeout` flags bound observations; stage maximum300s, others600s.
A longer observation budget is not evidence that default latency is acceptable.

Output is a candidate-only RuntimeRun: final typed answer/rendered text, evidence
stage timings/outcomes, release/evidence IDs, model-call schema hashes, fixed
operational diagnostics, budgets and input digests. General console output has
only completion status. Output must stay inside the explicit evidence root and
cannot overwrite an earlier observation. No intermediate unvalidated draft is
returned. Same-model support checking remains fallible; final human/independent
output assessment and institutional release authorization are still separate.

The database must already contain the checked fictional release and the committed
`20261012013339_phase5_retrieval_snapshot` migration. The runner performs no schema
changes. A missing RPC produces a held/error fallback; inspect service readiness
before an expensive model run. The [live composition record](../../plans/2026-10-20-live-backend-composition-plan.md)
defines the proof and retained limitations.
