# Faster replies: focused research and implementation

20October2026;baselineefc6343,Phase09 active,p09. Owner explicitly requests further
speed work and research. Student capability:receive a validated answer sooner;
evidence path:actual LLM routing -> required retrieval/Janus -> generation/check.
Phase exit advanced:responsive,grounded candidate output;not source activation.
Prior timings are reused;the new unresolved question is whether incomplete GPU
placement and verbose decoded JSON explain the remaining serial model latency.

## Research and bounded choices

Official [llama.cpp performance guidance](https://github.com/ggml-org/llama.cpp/blob/master/docs/development/token_generation_performance_tips.md)
recommends checking offload and avoiding CPU oversubscription. Current8threads run
on6physical cores;do not claim a thread win without measurement. GGUF metadata,
read without weight data,shows42transformer blocks and large separate embeddings;
5.126GB file size alone does not prove transformer/output tensors cannot fit4GB.
The24layer profile leaves1828MiB free. Official [server options](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
and pinned binary help support --gpu-layers auto/--fit-target;test one512MiB-margin
auto placement,with8192context fixed. Read actual placement and memory;revert24if
load fails or memory is inadequate. No grid/layer/seed/model sweep or new download.

Actual outputs spend tokens on JSON indentation and repeated prose. Ask all4stages
for compact one-line JSON,retaining every required field and complete content.
Keep routing/style separate for now:the latter was added for multilingual quality;
combining requires renewed quality evaluation. Preserve the support check. Never
truncate source payloads or lower output budgets to make latency appear improved.

The [Sentence Transformers guidance](https://www.sbert.net/docs/sentence_transformer/usage/efficiency.html)
describes alternative backends/precision;those require conversion/dependencies and
embedding compatibility validation,so defer them. QueryEncoder already retains its
loaded model per application. Measure startup separately and reuse that application
for subsequent observations;do not present cold-vs-warm changes as inference gains.
Prompt-prefix caching mainly saves prefill;current decode dominates and private
cache/session behavior needs separate design. Keep cache_prompt=false. Streaming
unvalidated answers cannot replace the thesis's validate-then-render boundary.

## Execution

1. Save current runtime/readiness;inspect model metadata and pinned help. Try the
   single memory-aware placement and one unchanged Hybrid request as component
   evidence. Stop once placement/throughput question is answered.
2. TDD compact output guidance through all4real message builders;full decoder,
   instructions,guards,source payloads,repair counts and deadlines stay. Observe
   RED then GREEN. Record a new prompt profile;no old capture relabeling.
3. One fixed actual-service request per route;record encoder startup separately,
   actual tokens/model durations/outputs and cold/warm distinctions. Review scope,
   citations and language;preserve the known Hybrid concern if still present.
4. Relevant regression gate and one independent final review;record results,
   effective runtime/digests/rollback and practical latency limits. Commit small
   verified units;update compact progress/checkpoint. No Phase10 or new student API.

Thesis physical17–18/39–40,actual routing PNG/master12–14 and standing19October
prompt decision consulted. Undergraduate/advisory/unknown/source-gap boundaries,
one-week accuracy cap,no parameter training and institutional/private/auth holds
remain. Existing owner workspace/MODELS,Python3.13 environment reused. Raw evidence:
workspace/audit-evidence/p09-fast-replies-20261020/;no model/dependency installation.
