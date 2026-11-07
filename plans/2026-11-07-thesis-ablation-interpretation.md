# Thesis support for an ablation comparison

Read-only interpretation requested by the owner, 7 November2026. No experiment,
thesis revision, evaluation rerun or phase advancement authorized by this note.

Source: `Context/bintanong_thesis_for_context.pdf`, 88 physical PDF pages.
Relevant physical pages12–15,62–64,68–72; printed pages are one less.
The PDF text contains no occurrence of “ablation”.

## Findings

- RQ2 (physical13 / printed12) explicitly compares full Bintanong with baseline
  Bintu-1 using the same benchmark, prompt template, model version, decoding and metrics.
- Specific Objective2 (physical14 / printed13) frames the question as whether adding
  symbolic reasoning improves correctness and reduces unsupported policy responses,
  but specifies comparison against baseline Bintu-1 rather than RAG-only Bintu-1.
- RQ3 / Objective3 (physical13/15) separately evaluate RAG retrieval accuracy,
  context relevance and response quality. Component measurement alone is not ablation.
- The rationale (physical12), evaluative design (physical62–63) and benchmark section
  (physical68–72) support controlled investigation, but do not explicitly prescribe
  a RAG-only condition or a component-removal protocol.

Interpretation: a RAG-only comparison is indirectly supported and methodologically
useful for the component-contribution wording of Objective2. It is not an explicitly
specified thesis requirement. Baseline versus full system measures their combined
difference; it cannot attribute that difference uniquely to symbolic reasoning.

The master implementation plan17.1 already distinguishes A (baseline), B (RAG-only,
proposed ablation) and C (full system). That plan supports implementation planning;
it is not evidence that the thesis itself explicitly prescribes B. Historical
Phase12 notes say B was skipped; this note does not turn it into completed evidence.

For a future supplementary symbolic comparison, document conditions and hold the
applicable cases, model, source snapshot, generation settings, retrieved context,
routing assignments and non-symbolic checks fixed as applicable. Vary symbolic
results and their dependent checks; otherwise disclose other changed components.
No broad ablation of every subsystem is implied by the thesis wording.
