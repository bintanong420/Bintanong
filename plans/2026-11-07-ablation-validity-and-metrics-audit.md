# Ablation validity and shared metrics audit

Owner asks how the ablation can be implemented properly alongside RAGAS/BERTScore.
Read-only audit on `feature/p12-evaluation-ablation`; no formal experiment, install,
new model/judge call, source decision or student-path change performed.

## Verified current state

- Fetched evaluation branch `69fc7cea`: BERTScore export has42 candidates,42 empty
  references,14 each English/Tagalog/Taglish input. It covers14 documentary families,
  not the10 prerequisite families. It is preparation, not completed scoring.
- Its README notes Q11's two-turn rerun on newer routing code. All exported
  `code_commit` fields still say `1e499828060f`; Q11 notes disclose newer code.
  Fix/verify run provenance before claiming a common frozen-code comparison.
- Evaluation planning/report documents still mark RAGAS judge configuration pending.
  This does not establish the state of another worker's unpushed environment.
- Current page runs a source-backed production reference first, requires its
  successful symbolic answer, then compares model synthesis with evidence off/on.
  C is not the actual production pipeline; sources are selected reference cards,
  which can be fragments. Conditioning on reference success risks selection bias.
- Existing tests establish identical B/C source payloads/system prompt, no report
  in B, no gold/reference prose in model input, retained generation failures and
  unvalidated output labels. They do not establish experimental validity or accuracy.
- The72-case roster informed fixes, has24 scenario families, and lacks dedicated
  out-of-scope/unanswerable cases. Language variants are not independent scenarios.
  Pooled retrieval recall can miss unseen relevant chunks, as its scorer discloses.

## Experiment contract before thesis scoring

Keep the current page labelled exploratory. Distinguish:

1. Overall-system comparison: unaugmented Bintu-1 versus actual full Bintanong.
   Supports the explicit baseline/full-system research question; cannot uniquely
   attribute a gain to Prolog.
2. Symbolic-subsystem ablation: same preregistered cases, user facts, complete
   authorized institutional facts/text, fixed routing/context and answering settings;
   vary the solver/report and explicitly identified dependent checks. A RAG-only
   condition must actually have the applicable curriculum knowledge without the
   inferred result; isolated code fragments are not an adequate substitute.
   Removing dependent validation must be disclosed as a subsystem change, rather
   than claiming the Prolog algorithm alone caused the difference.

Build shared context from reviewed authoring/source records before examining any
condition's answer. Do not use a successful C answer or its chosen citations as
the sampling or context gate. Never weaken the production advisor to run a baseline.
Policy questions needing no symbolic execution serve as separately declared controls;
do not force them through Prolog or call them evidence of its benefit.

## Completion checklist

- [ ] Freeze cases/applicability, family/language IDs, provided facts, curriculum,
  source snapshot and independently reviewed expected outcomes/references first.
  Include unknown/unmet distinctions and declared incomplete/unsupported cases.
  Reuse accepted wordings; do not manufacture additional source policy or labels.
- [ ] Independent expected outcomes come from source review, not C's answer or the
  same implementation being tested. Preserve English/Taglish reply policy when
  authoring multilingual references; source quotations stay as printed.
- [ ] Implement explicit condition executors and capture their actual call traces.
  Tests prove A receives no institutional evidence, B never invokes/receives the
  solver, and C is the intended complete configuration. Gold never reaches generation.
- [ ] Test context/fact equivalence, edition separation, negation, numeric conditions,
  missing data, failure/cancellation and counterexamples where words look similar
  but eligibility differs. Invalid metadata/shape is not a semantic correctness test.
- [ ] Retain all predetermined cases and every failed/missing condition in the
  denominator report. No success-only selection, cherry-picked reruns or silent skips.
- [ ] Record per-run code, artifact/checksum identity, prompt/decoding versions,
  context hashes, conditions, case/family IDs and full multi-turn inputs. Resolve
  Q11's provenance/conversation mismatch instead of silently treating it as one turn.
- [ ] Reuse a common immutable export for all scorers, keyed by case/family/language,
  condition and run ID. Reject missing references, mixed releases/settings, missing
  conditions and unintended answer truncation. Log judge/metric versions and hashes.
- [ ] Score independently reviewed decision/policy correctness, unsafe unsupported
  claims, appropriate uncertainty and failures as primary outcomes. Prolog-report
  agreement is a consistency metric, not independent proof that the report is true.
- [ ] Add BERTScore as reference-text similarity, not an eligibility/logic oracle.
  Pin multilingual model/tokenizer/layers/version/settings. Explicitly handle its
  length limit; never silently score only the beginning of a long recovery answer.
- [ ] Add metric-specific RAGAS adapters with documented evidence inputs and fixed
  judge configuration, calibrated against blinded human judgments. Do not assume
  the generating model's own judgment is independent. Missing judges mean not run.
- [ ] Baseline retrieval/faithfulness metrics with no applicable context are N/A,
  not fabricated zero/perfect scores. Fixed-context B/C have unchanged retrieval
  metrics by construction. Use common source evidence for comparable grounding
  scores; separately label any proof-aware score that gets additional evidence.
- [ ] Counterbalance condition order/cache effects; distinguish inference/request,
  preparation, queue and browser times. Treat repeated greedy runs as repeated
  measurements, not independent questions. Report paired differences, uncertainty,
  per-language/per-category results and clustering by scenario family.
- [ ] Pilot the frozen protocol, audit artifacts/blinded judgments, then run the
  declared evaluation. The development72 set remains development evidence; do not
  retroactively rename tuning cases as an independent final set.

## Order of implementation

1. Freeze the experiment contract and independent shared context/reference schema.
2. Correct condition execution and non-selective accounting; add trace/invariant tests.
3. Unify export/provenance and scoring adapters with the other evaluation work.
4. Calibrate metrics against human correctness judgments; pilot before final scoring.

No new dependency/model acquisition or cloud judge is implied by this checklist.
Use approved existing resources; propose any additional requirement explicitly.

## Primary metric documentation consulted

- [BERTScore paper](https://arxiv.org/abs/1904.09675): contextual token similarity
  between candidate and reference, not an institutional rule-execution validator.
- [BERTScore implementation](https://github.com/Tiiiger/bert_score): report scoring
  configuration hash; tokenizer/library/model and truncation behavior matter.
- [RAGAS faithfulness](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/faithfulness/):
  support of response claims by retrieved context, with an evaluator configuration.
- Repository master17.1 already separates overall-system comparison from proposed
  symbolic ablation; [thesis interpretation](2026-11-07-thesis-ablation-interpretation.md)
  preserves the distinction between explicit thesis requirements and our inference.
