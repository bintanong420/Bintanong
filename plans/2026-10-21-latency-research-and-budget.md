# Response latency: measured budget, research and recommendation (addendum)

21 October 2026, owner request. Extends (does not replace) the saved
[20 October recommendation](../Context/response-time-recommendation.md): accuracy first,
15-20 s typical warm browser-visible target, up to 20-30 s for complex Hybrid. Numbers
below are backend-only warm measurements on real data; browser/API/network are unmeasured.

## What the time is spent on (measured, real data, after fixes)

Development machine: **RTX 3050 Laptop GPU, 4 GB VRAM**, Gemma 4 E4B Q4 via llama.cpp
(`--n-gpu-layers auto`; the model does not fully fit in 4 GB). Decode ~20 tokens/s,
prompt reading ~550-900 tokens/s. One answered RAG question = four model calls:

| Call | Prompt tokens | Output tokens | Wall |
| --- | ---: | ---: | ---: |
| Routing (interpretation) | ~4,950 | ~260 | ~19 s |
| Response-style detection | ~840 | ~65 | ~4.6 s |
| Per-part answer | ~1,100 | ~170 | ~10.5 s |
| Per-part check (after `6d639f5`) | ~820-900 | ~62 | ~4.6 s |

Retrieval 0.3 s, Prolog 0.35 s. Output tokens dominate: at ~20 tok/s every 100 output
tokens cost ~5 s. Checker hash copying was removed (`6d639f5`: 212 -> 62 tokens,
12.4 -> 4.6 s, no validation removed). Profiled real questions: 41-51 s total (laptop
GPU variance is visible: identical routing prefill took 5.5 s and 14.3 s in two runs).

## Research (summarized; see sources in the owner report)

- Text chatbots: waiting is rated negatively beyond ~8 s, more so for complex tasks
  (between-subjects study, N=478). Classic HCI: ~10 s is the attention limit.
- LLM chatbots specifically (Tan & Nov, CHI 2026, N=240): identical answers after 9 s
  and 20 s were rated more useful/thoughtful than after 2 s; at the longest waits some
  users suspected a dropped connection. Delay is tolerated when the task feels complex,
  but needs visible progress.
- Visible progress/fillers improve perceived response time (VR agent study; UI progress
  research). Status messages are compatible with the owner's "no unchecked answer
  streaming" rule as long as no unvalidated answer text is shown.
- Local-model throughput is hardware-bound: small quantized models typically reach
  50-300 tokens/s on GPUs that hold the whole model; 4 GB VRAM cannot.

## Recommendation for this thesis system

1. **Keep the 15-20 s typical target as the deployment goal**, stated for the
   recommended hardware: a GPU with >= 8 GB VRAM (or equivalent server) so the model is
   fully offloaded. At ~3-5x the decode speed, today's ~500 output tokens per answer
   would take ~12-18 s. This is a projection to verify, not a measurement.
2. **On the 4 GB development laptop, report ~35-45 s warm as a disclosed prototype
   limitation.** It does not meet the target; say so honestly in the thesis.
3. **Show stage progress messages** in the web UI ("Understanding your question...",
   "Checking the handbook/curriculum...", "Verifying the answer...") so students see
   work happening; never stream unvalidated answer text.
4. **Accuracy-preserving reductions, in order of evidence/risk** (each needs the usual
   quality re-check before adoption): (a) send the router a compact field guide instead
   of the full branched JSON schema (~4,950-token prompt); (b) allow llama.cpp prompt
   caching for the identical static system prefix (currently disabled for
   reproducibility); (c) drop free-text router fields (`intent`, `reason`) that no code
   uses; (d) fold style detection into routing only if quality holds (an earlier
   combined attempt failed). None of these removes Prolog, retrieval or validation.
5. Measure student-visible end-to-end time (browser) and student acceptance in the
   evaluation phase; backend numbers alone cannot establish acceptability.
