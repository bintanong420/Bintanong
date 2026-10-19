# Algorithm implementation and paper demonstration map

Start with the dedicated [backend/algorithms folder](../../backend/algorithms/README.md)
and use this with the [pipeline map](pipelines.md). It identifies existing code and
callers so developers can explain the implementation in the paper or a defense.
Established algorithms,library operations and project-specific control workflows
are distinguished below; they are not all newly invented algorithms.

## Cosine similarity and exact k-nearest-neighbor retrieval

| Part | Implementation | Caller / role |
| --- | --- | --- |
| Explicit cosine formula | [similarity.py](../../backend/algorithms/similarity.py), `cosine_similarity(v1,v2)` | Existing offline embedding tests and the presentation demo; the embedding adapter re-exports this function and the current retrieval engine delegates distance computation to pgvector |
| Current exact top-k search | [Phase05 retrieval migration](../../supabase/migrations/20261012013339_phase5_retrieval_snapshot.sql), SQL function `public.retrieve_context` | `RetrievalEngine.retrieve` calls the RPC; SQL computes similarity,filters,sorts and limits candidates |
| Current Python retrieval caller | [engine.py](../../backend/bintanong_retrieval/engine.py), `RetrievalEngine.retrieve` | Invoked through `RetrievalAdapter.retrieve` in [adapters.py](../../backend/bintanong_orchestration/adapters.py) |
| Configuration | [types.py](../../backend/bintanong_retrieval/types.py), `RetrievalSettings` | Carries `top_k`,minimum similarity and context budget; current allowed k values are3,5,8 |
| Earlier Phase04 interface | [storage retrieval.py](../../backend/bintanong_storage/retrieval.py), `KnowledgeRetriever.search` | Calls the separate `match_chunks` RPC; its later definition is in [release security migration](../../supabase/migrations/20261012010002_phase4_release_security.sql). Do not confuse it with the Phase05 `retrieve_context` path |

The helper implements,for equal-dimensional nonzero vectors:

```text
cosine(q,x) = sum(q[i]*x[i]) / (sqrt(sum(q[i]^2))*sqrt(sum(x[i]^2)))
cosine_distance(q,x) = 1 - cosine(q,x)
```

In the current SQL function,the `eligible` CTE computes
`1-(e.embedding <=> query_embedding)` as similarity. Its `ranked` CTE then applies
the minimum-similarity and entity-hint filters and finishes with
`order by c.similarity desc, c.chunk_id limit p_top_k`.
Release membership,embedding configuration,scope and source-version checks also
belong to this function. Open the complete migration when explaining those guards.

The operation is **exact nearest-neighbor retrieval**,not k-NN classification or
regression:it returns up to k relevant chunks rather than voting on a class label.
Larger similarity means closer vector direction;smaller cosine distance means
closer direction. Similarity is not probability,authority,recency or answer accuracy.
Required neighboring clauses can expand the later context beyond k primary hits;
the context budget and evidence checks can also remove candidates.

The checked-in migrations contain no HNSW/IVFFlat index. Do not describe this
version as approximate nearest-neighbor search or claim ANN performance. This is
a repository-code observation,not a fresh inspection of a hosted database. The
[hosted migration record](../../plans/2026-10-19-hosted-migration-status.md) retains
its separate reconciliation limits.

The official [pgvector documentation](https://github.com/pgvector/pgvector#querying)
defines the cosine-distance operator and conversion to similarity; its
[indexing section](https://github.com/pgvector/pgvector#indexing) distinguishes
default exact search from optional approximate indexes. Current documentation was
resolved/queried through Context7 for this map. No schema or database was changed.

## Runnable demonstration

Open [nearest_neighbors.py](../../backend/algorithms/nearest_neighbors.py). From the repository
root using the existing project Python3.13 environment:

```powershell
python -B -m backend.algorithms.nearest_neighbors
```

It calls the existing `cosine_similarity` helper and prints synthetic vectors,
their similarities/distances,the ranking and the thresholded top-k selection.
It loads no model,PDF,student input or database and uses only Python's standard
library. The old `scripts.demo_cosine_top_k` module forwards to the same demo.

For query `(1,0)`,the hand-computed results are:

| Candidate | Vector | Similarity | Distance | Selected at k=3,min_similarity=0.5 |
| --- | --- | ---: | ---: | --- |
| vector-a | (1,0) | 1.0 | 0.0 | yes |
| vector-b | (0.8,0.6) | 0.8 | 0.2 | yes |
| vector-c | (0,1) | 0.0 | 1.0 | no |
| vector-d | (-1,0) | -1.0 | 2.0 | no |

Display values are rounded here;selection uses the original floating-point scores.
Only two candidates qualify despite k=3. The0.5 threshold is a chosen illustration,
not a calibrated institutional answer policy. These two-dimensional hand-selected
vectors demonstrate geometry;real query vectors are validated1024-dimensional,
finite and L2-normalized in [query.py](../../backend/bintanong_retrieval/query.py).

The small Python exhaustive scan is an educational equivalent of score/filter/
sort/limit. It is not a second application retrieval implementation or a test of
SQL,RLS,query plans,real SEA-LION relevance or language performance. For runtime
code evidence,show the SQL function and its Python RPC caller alongside the demo.
The [demo regression](../../tests/test_algorithm_demo.py) checks the independently
hand-computed numbers,ordering and fewer-than-k result through the actual CLI.

## Other important algorithms and workflows

| Algorithm / workflow | Code to show | What actually executes |
| --- | --- | --- |
| L2 normalization and vector validation | [similarity.py](../../backend/algorithms/similarity.py), `normalize_l2`; [query encoder](../../backend/bintanong_retrieval/query.py), `validate_vector` / `QueryEncoder.encode` | Explicit norm math/validation; actual model encoding is delegated to the supplied pretrained SEA-LION model through SentenceTransformer,with normalized output requested |
| Structure-preserving policy chunk construction | [policy_chunks.py](../../backend/bintanong_tools/document_ingest/policy_chunks.py), `build_policy_chunks`; [reviewed_policy_chunks.py](../../backend/bintanong_tools/document_ingest/reviewed_policy_chunks.py), `build_reviewed_policy_chunks` | Project code preserves source spans,table/service associations and review boundaries; OCR/extraction is a separate preparation stage |
| Context dependency closure,deduplication and budget selection | [context.py](../../backend/bintanong_retrieval/context.py), `build_context` | Adds required neighbors,checks complete groups,deduplicates evidence and accepts fitting groups in candidate order; this is not a claimed optimal knapsack solver |
| Source-aware candidate evidence selection | [evidence_policy.py](../../backend/bintanong_retrieval/evidence_policy.py), `SourceAwareEvidencePolicy` | Optional injected research snapshot binding,subject selection and claim coverage assessment; it does not authorize institutional release |
| Prerequisite/co-requisite reasoning | [curriculum_runtime.pl](../../backend/algorithms/curriculum_runtime.pl), `run/5`, `evaluate/5`, `combine/3`, `completion/4` | SWI-Prolog evaluates reviewed expression trees,including all-of/any-of and explicit unknown/conflict states; missing facts are not automatically failed courses |
| Transitive affected-course traversal | [curriculum_runtime.pl](../../backend/algorithms/curriculum_runtime.pl), `dependencies/4`, `reaches/4` | Recursive graph traversal with a visited set and deduplication; lists potential dependencies,not a complete enrollment decision |
| Rule compilation and prerequisite cycle detection | [compiler.py](../../backend/bintanong_symbolic/compiler.py), `compile_curriculum_preview`, `_diagnostics` | Project code builds the reviewed graph and generated preview; Python's `graphlib.TopologicalSorter.prepare` supplies cycle detection,which produces a review hold |
| Semantic RAG/Symbolic/Hybrid routing | [router.py](../../backend/bintanong_routing/router.py), `Router.route`; [routing validation](../../backend/bintanong_routing/validation.py), `validate_interpretation` | Supplied LLM interprets meaning; host code validates grounded entities,operations and controls. This is not a keyword router or k-NN classifier |
| Route execution and evidence integration | [orchestrator.py](../../backend/bintanong_orchestration/orchestrator.py), `Orchestrator.run`; [integration.py](../../backend/bintanong_orchestration/integration.py), `assemble` | Project async control flow,release binding and explicit failure precedence; Hybrid waits for both required paths |
| Answer validation and bounded repair | [generator.py](../../backend/bintanong_generation/generator.py), `Generator.generate`; [validation.py](../../backend/bintanong_generation/validation.py); [render.py](../../backend/bintanong_generation/render.py) | Draft/check workflow,independent host checks,canonical rendering and at most one repair; the model-based prose checker remains fallible |
| Retrieval evaluation metrics | [evaluation/retrieval.py](../../evaluation/retrieval.py), `evaluate_rankings` | Computes hits/k precision,recall against known relevant chunk IDs,and language/category aggregates from separately supplied rankings; absent gold has undefined recall |

The Prolog caller is [runtime.py](../../backend/bintanong_symbolic/runtime.py),
`CurriculumRuntime.check` / `list_affected_courses`,via fixed Janus goals in
[_janus_worker.py](../../backend/bintanong_symbolic/_janus_worker.py). For a code
demonstration of eligible/ineligible/unknown/conflicting inputs,inspect
`test_actual_janus_distinguishes_completion_missing_and_conflict` in
[test_symbolic_runtime.py](../../tests/test_symbolic_runtime.py). Executing that
existing synthetic test requires the prepared SWI-Prolog/Janus environment.

## What to present in the paper

Show the cosine helper for the formula,the demo for transparent arithmetic,the SQL
for actual top-k retrieval,and the engine for its application call path. Show the
Prolog predicates separately for curriculum decisions. Use the module/function
names and the exact commit in captions,so code listings stay traceable after edits.

Attribute pgvector,SWI-Prolog/Janus and pretrained models as external components;
describe Bintanong's implementation of their integration,reviewed data,scope guards
and evaluation accurately. The demo proves mechanical calculations,not corpus
accuracy or institutional readiness. General scaffolds such as
`backend/bintanong_tools/evaluate.py` are not substitutes for the implemented metric
functions. Preserve the current candidate/source/privacy/release limits and actual
model errors recorded in the [Phase09 observations](../../plans/2026-10-19-phase09-observation-status.md).
