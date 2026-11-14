# Algorithms for developers and the thesis panel

Start here for inspectable algorithm code and the paper demonstration.
The [detailed algorithm map](../../docs/development/algorithms.md) explains the
formulas, runtime call paths, evaluation metrics and implementation limits.

```text
backend/algorithms/
├── similarity.py          Cosine similarity and L2 normalization
├── nearest_neighbors.py   Runnable synthetic exact top-k reference
├── curriculum_runtime.pl  Generic Prolog reasoning and dependency traversal
└── README.md              This catalogue and presentation order
```

| Algorithm | Code to inspect | Application caller |
| --- | --- | --- |
| Cosine similarity | [similarity.py](similarity.py), `cosine_similarity` | The synthetic demo and offline checks; [embedding adapter](../bintanong_embedding/adapter.py) re-exports the same function for existing imports |
| L2 normalization | [similarity.py](similarity.py), `normalize_l2` | Existing embedding adapter's mock-vector preparation; real encoder normalization is delegated to the model library |
| Exact cosine nearest-neighbor selection | [nearest_neighbors.py](nearest_neighbors.py), `demonstration` | Synthetic paper demo: score, filter, sort, take up to k |
| Live exact top-k retrieval | [versioned SQL migration](../../supabase/migrations/20261012013339_phase5_retrieval_snapshot.sql), `public.retrieve_context` | [RetrievalEngine.retrieve](../bintanong_retrieval/engine.py) calls the pgvector RPC |
| Prerequisite/co-requisite evaluation | [curriculum_runtime.pl](curriculum_runtime.pl), `run/5`, `evaluate/5`, `combine/3`, `completion/4` | [CurriculumRuntime](../bintanong_symbolic/runtime.py) invokes the fixed [Janus worker](../bintanong_symbolic/_janus_worker.py) |
| Transitive affected-course traversal | [curriculum_runtime.pl](curriculum_runtime.pl), `dependencies/4`, `reaches/4` | The same runtime's `list_affected_courses` operation |

These Python math and Prolog files are the canonical implementations. The database
algorithm stays in its versioned migration, with one definition to inspect and
maintain. The Python nearest-neighbor example demonstrates its mathematical steps;
live retrieval uses SQL, including release, source-version and scope guards.

The Prolog engine contains generic reasoning, with reviewed curriculum facts and
requirement trees supplied by the authoring/compiler bundle. It preserves unknown
and conflicting inputs; a blank prerequisite field does not mean no prerequisite.
No course-specific policy copy belongs in this folder.

## Run the paper demonstration

From the repository root with Python3.13:

```powershell
python -B -m backend.algorithms.nearest_neighbors
```

This standard-library-only demo prints four synthetic candidates, cosine scores,
distances, ranking and selection. With query `(1,0)`, scores are `1, 0.8, 0, -1`.
At `k=3` and minimum similarity `0.5`, only the first two qualify. It loads no
model or database. The previous `python -B -m scripts.demo_cosine_top_k` command
forwards to this implementation.

For the panel, show `similarity.py` for the formula, run the demo, then open the
SQL function and its RPC caller to establish what the application executes.
Show Prolog separately for structured curriculum decisions. Use the exact commit
in paper code-listing captions, and attribute pgvector and SWI-Prolog/Janus.

## Other algorithms and workflows

Keep control flow beside the modules that own it. The detailed map links source
chunking, context dependency closure, cycle detection, semantic LLM routing,
orchestration, answer validation and retrieval evaluation. The
[pipeline guide](../../docs/development/pipelines.md) shows how those modules fit.
Models and their external inference libraries own neural encoding/generation;
this folder does not contain a new trained model.

Synthetic demonstrations establish arithmetic and software behavior. Current
candidate, source, privacy and institutional-release limits remain recorded in
the [phase index](../../plans/INDEX.md) and current handoff.
