# Phase 12 pre-phase research — evaluation write-up, 30 October 2026

Bounded to the Phase 12 workstream (master 17): writing up benchmark runs that already exist, by the owner's
30 October finish date. Reuses repository evidence; no new technology, dependency or model.

## 1. What already exists (do not repeat)

- Main benchmark v2 (24 English / 16 Taglish / 10 Tagalog): 38/50 at `cb82c53`; original 50: C 40/50 (`7f8c02b`),
  rerun 39/50 (`cb82c53`), plain Gemma A 3/50 strict, 8/50 content ([results](2026-10-29-phase12-benchmark-results.md)).
- Robustness: Tagalog 19/26, shorthand 15/26 (list built after seeing the probe), broken English 2/4.
- 91-case simple-question gate (run 4 77/91), live website checks, private-file tests (Phase 10/11 handoffs).
- Full test suite (batched) and latency observations (warm inner, not student-visible).

## 2. Options and recommendations

| Question | Options | Evidence | Recommendation |
| --- | --- | --- | --- |
| Uncertainty on 50 cases | none; Wilson 95% interval; bootstrap | Wilson (1927) / Agresti & Coull (1998): Wilson behaves well at small n and near 0/1, unlike the normal interval | Wilson 95% per condition. Done from existing outputs: C 40/50 [0.67, 0.89]; A strict 3/50 [0.02, 0.16] |
| A vs C comparison | difference of rates; exact McNemar on paired cases | McNemar (1947): same cases under two conditions are paired; the exact binomial form suits few discordant pairs | Exact McNemar: 37 discordant pairs all favour C, p ≈ 1.5e-11 (strict); 32/0, p ≈ 4.7e-10 (content) |
| Repeated runs (master 17.4 proposes 5 per case) | 5 runs x 50 x 2 conditions; single run + measured variance | C takes ~26 s per case: 5 x 50 = ~2 h for C alone. The absence-Taglish replay showed one-off server non-determinism on an identical request; [pinned llama.cpp server README](https://github.com/ggml-org/llama.cpp/blob/547208dca/tools/server/README.md) warns prefix-cache reuse can change logits (cited in the 19 Oct research) | Report single runs plus the observed C-vs-C rerun (40 vs 39, 1 discordant, p = 1.0) as a variance indication; disclose that 5-run repetition was not done. Owner may choose to run it if time allows |
| Condition B (RAG without rules) | run; skip | Owner 29 Oct: skipped | Skip; disclose that A–C is a whole-system comparison, not proof Prolog alone caused the gain |
| Route F1, retrieval P@k, RAGAS, BATAYAN, SUS/UAT | measure now; disclose as not measured | No per-case route labels or relevance judgements exist for the 50; SUS/UAT needs 30 consenting participants; RAGAS needs an evaluator model (new dependency) | Disclose as not measured in this build; do not fabricate inputs (master 17.3) |

## 3. Expected gain, cost, risk

Write-up only: about 2–3 hours. Risk: overclaiming. Mitigations: state that 40 of 50 cases were development cases,
author-written expectations and a single author scorer, no institutional validation, warm-inner latency only.

## 4. Open owner decisions

1. Hosted 560-chunk activation (owner 29 Oct: "after the accuracy freeze"): confirm the freeze is now.
2. Accept single runs with disclosed variance instead of 5 repeated runs.
