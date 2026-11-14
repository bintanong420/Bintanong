# Faster replies: results and remaining work

20October2026;p09/feat/p09-generation-validation. Research plan8f502fb,
implementation791413e. [Focused plan](2026-10-20-fast-replies-research-plan.md),
[previous latency evidence](2026-10-20-phase09-latency-results.md). Owner requests
faster replies and research. Phase09 remains active;Phase10 separate/unstarted.

## What improved

| Actual route | Previous24layer,cold encoder s | New resident application s |
| --- | ---: | ---: |
| RAG | 85.297 | 35.662 |
| Symbolic | 79.815 | 35.058 |
| Hybrid | 148.043 | 52.967 |

Each new result uses actual LLM routing/style,required SEA-LION/PostgREST/pgvector
and/or Janus,integration,draft,support check and final rendering. Same original
fictional English questions/spec,4calls,1draft/1check/0repairs each. Expected routes,
typed decisions and full decoder schema hashes match the prior observations.
This is one observation per route,not a latency distribution or accuracy claim.

Application startup was recorded separately:0.744s imports,25.131s strict encoder
verification/load/first encode,26.408s total process startup. A one-shot CLI still
pays cold encoder cost on RAG/Hybrid;it does not gain a resident process merely
because this batch reused one. With server already ready,startup plus the observed
RAG duration sums to62.070s;that sum is not an additional cold measurement.
Pure Symbolic does not need an encoder. Server/model boot is separate too.

The application already retains its encoder. The batch built it once,then ran
3requests with original distinct contexts and fresh per-request orchestration.
Every actual retrieval re-encoded its question and rechecked the release;no query,
answer,student-fact or prompt-prefix cache was substituted. Warm retrieval took
0.330s RAG/0.435s Hybrid versus22–24s cold previously. No new student API was added.

## Root cause and bounded changes

Read-only GGUF metadata inspection shows42blocks and large separate embedding
tensors. Total file size5.126GB had overstated the GPU-placement constraint.
The explicit24layer profile left1828MiB free and its output projection on CPU.
The pinned runtime's memory-aware auto placement selected34repeating layers plus
the output layer:35/43offloaded. CUDA model buffer2480.70MiB,KV122MiB,compute139.19MiB.
Final observed total VRAM roughly2.8GB,about1.1GB free;not all model data is on GPU.
Auto fitting retains explicit8192context and512MiB requested margin in its own
device-memory budget. Actual selection varies with hardware/free memory.

Before changing prompts,one auto-placement Hybrid request with unchanged messages
answered83.059s versus148.043s on24layers. Its model calls totaled58.378s;observed
decode approximately23tokens/s,previously roughly8–15. Same pinned CUDA build,
weights,template,sampling/decoder/context/output budgets;this is a single observed
profile comparison,not a controlled throughput distribution. Then logging level4
was enabled to capture actual fit/tensor placement;no extra layer/seed sweep.

All4prompts now ask for compact one-line JSON with complete strings/required fields.
Their versioned instruction hashes change accordingly. Full decoder schemas,host
guards,all pre-existing instructions,question/source payloads,repair bounds and
deadlines remain. This reduces decoded formatting work without removing checks.

| Route | Previous output tokens | New output tokens | Model-call seconds |
| --- | ---: | ---: | ---: |
| RAG | 642 | 462 | 35.278 |
| Symbolic | 824 | 540 | 34.579 |
| Hybrid | 1113 | 859 | 52.024 |

11/12new outputs obey one-line guidance. Hybrid's draft still emits pretty JSON
and530tokens;guidance is not a deterministic whitespace constraint. Its new output
has4claims versus3in the unchanged-prompt auto control,so compare actual content,
not token count as a pure formatting experiment. Hardware,content and cold/warm
effects remain separate explanations;no isolated compaction speed/accuracy claim.

## Research and next choices

The [official llama.cpp performance guide](https://github.com/ggml-org/llama.cpp/blob/master/docs/development/token_generation_performance_tips.md)
supports checking offload and physical CPU threads. The [server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
describes memory fitting,caching and n-gram speculation. Pinned binary help and
actual startup logs verify the options used here. The laptop has6physical cores;
8threads were retained for this comparison,no thread sweep or thread-speed claim.

The current859token Hybrid output alone costs about37s at23tokens/s,before prompt
processing/transport. A roughly10second working aim is **not achieved**. The next
substantial gains require fewer decoded tokens/model calls or faster hardware:

- Combine routing and style into one structured call while preserving independently
  validated route,language evidence and bounded repair. Master12 permits shared
  interpretation/routing inference;multilingual quality must be revalidated.
- Reduce wire overhead with request-local short evidence references that map back
  to canonical hashes before host validation. Exact provenance/unknown semantics
  must survive;this is a design candidate,not implemented or measured here.
- Use existing canonical rendering for a narrowly defined pure structured response
  when sufficient;retain prose generation/checking when explanation is required.
  Define that capability boundary before changing the four-call flow.
- N-gram speculation may reuse repeated JSON/source sequences without new weights.
  It needs one separate compatibility/performance check;no speculative decoding
  or shared n-gram cache was enabled by this delivery.

[Sentence Transformers' efficiency documentation](https://www.sbert.net/docs/sentence_transformer/usage/efficiency.html)
also covers precision and ONNX/OpenVINO alternatives. Those change dependencies or
embedding execution and need compatibility validation;resident model reuse gave
the immediately useful startup improvement here. Do not convert/re-embed by default.
Prefix caching primarily saves prompt work and changes runtime reproducibility;
cache_prompt remainsfalse. Streaming unvalidated answers would violate validation
before rendering,so it cannot be used to report an artificial response-time win.

## Quality, verification and recovery

Independent review assessed8new claims:7clear support/scope fits;Hybrid c2 repeats
the known executed-check claim using only documentary evidence. Canonical eligible
decision/conditions remain correct;the fallible checker accepts the wrong support
basis. This remains an unresolved quality issue. Existing quote-offset anchoring
corrects3mentions/claims for Symbolic/Hybrid;do not call raw model extraction perfect.
English only;two prior Taglish errors and all institutional/private/auth holds remain.

TDD:4focused RED failures for absent compact guidance,then196passed4.19s with actual
builders/schema/payload checks. Final48-selection regression gate1898passed/
66subtests89.01s,exit0. One independent final review found no new P1/P2 code defect;
the existing Hybrid issue is preserved. Setup docs now describe auto placement and
fixed24/CPU rollback. No new weights,project dependencies,hosted changes or release
activation. Fixed240s inference/generation,300s stage,600s request budgets retained;
these observations do not prove general default-budget readiness.

Raw:workspace/audit-evidence/p09-fast-replies-20261020/;`run_observation.py` binds the
unchanged-message control,`run_warm_batch.py` the resident batch,`resident-startup.json`
its startup. Four reports/16call traces,`comparison.json`,resolved Compose,
`gguf-metadata.json`,pinned help,server/VRAM snapshots,RED/GREEN and full regression
logs plus `independent-fast-review.md` preserve the exact conditions and limitations.
Input/code hashes were captured before inference;old evidence remains sealed.
Final `delivery-manifest-final.json` SHA256:
6cc6a7df6e5f6e6f95f32dfdea04b9ec28743cd3420dcda3039be3bc126e4990.
All95listed raw/source/config files verified. It extends the immutable first seal
with reused24layer baselines;mutable delivery docs/test temporaries are excluded.
Final docs hygiene586passed1.34s;86local links resolve,compact snapshots within caps.

Next Phase09 action:fix the demonstrated Hybrid citation/scope flaw,then design
bounded call/token reductions against a stated latency goal with multilingual
quality evaluation. Keep source/release gates;do not repeat resolved placement
diagnostics or promise sub10s replies from this hardware/profile evidence.
