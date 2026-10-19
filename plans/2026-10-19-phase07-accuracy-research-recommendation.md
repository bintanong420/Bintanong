# Phase07 accuracy research and recommended next step

19October2026. Research baseline:docs03c361c, product bec3d8e. No product change,
new inference, runtime restart, installation, weight download or accuracy gain.
Owner requests minimal errors/high accuracy and asks for research. Keep Phase07
open; the former quality-priority question is answered. Numerical targets below
are recommendations, not an owner-approved exit gate or institutional approval.

## Local evidence and scope

The [operation correction](2026-10-19-phase07-operation-constraint-correction.md)
has6fresh routing calls and6reused style outputs:operations/entities/claims6/6,
routes5/6. Prerequisite-fil wrongly selects Hybrid instead of Symbolic. The
[independent style profile](2026-10-19-phase07-style-stage-evaluation.md) has13/15
correct labels; procedure-taglish and excluded-taglish wrongly select Filipino.
These are different runs/conditions; do not combine them into a current accuracy
percentage. Literal grounding and valid JSON do not establish semantic correctness.

Context consulted this turn:thesis physical17-18 saved extraction and actual
runtime routing PNG; master12/17 evaluation guidance and2.2 model identity, with
prior3/11/13 and thesis39-44/58-59 architecture decisions preserved. Undergraduate
2026-27/read-only scope, source gaps, EMPTY_REGISTRY and release holds remain.
Supplied Gemma4E4B is the intended Bintu-1 artifact. No fine-tune is assumed.

## Primary-source findings

1. [Google's E4B model card](https://huggingface.co/google/gemma-4-E4B-it)
   recommends sampling temperature1.0, top_p0.95 and top_k64. Our temperature0
   baseline differs. This is a comparison candidate, not evidence that increasing
   temperature improves this routing task. Record all active samplers and model
   overrides; do not silently retain extra filters when claiming a vendor recipe.
   [Google's thinking guide](https://ai.google.dev/gemma/docs/capabilities/thinking)
   supports E4B thinking on/off. Neither mode guarantees better classification.

2. The [pinned llama.cpp server source](https://github.com/ggml-org/llama.cpp/blob/547208dca/tools/server/server-common.cpp#L1324)
   handles reasoning_effort=none as disabled. Other nonempty strings are template
   inputs; low is not a numerical token budget. At1344-1345 it reads
   reasoning_budget_tokens or thinking_budget_tokens. Our ignored earlier
   probe-native-thinking.py instead sends reasoning_budget=128. Thus its recorded
   requested128-token budget is not established as enforced. Its three outputs
   remain real observations, but not a valid budget-controlled comparison or a
   reason to rule out native thinking. Verify effective behavior before new claims.
   [Google's prompt-format documentation](https://ai.google.dev/gemma/docs/core/prompt-formatting-gemma4)
   likewise distinguishes enabling thinking from controlling its length.

3. The [pinned server documentation](https://github.com/ggml-org/llama.cpp/blob/547208dca/tools/server/README.md)
   says cache_prompt defaults true and warns that prefix-cache reuse can change
   logits across batch sizes/backends. Current requests do not explicitly set this
   policy. That is a possible contributor to fresh/replayed semantic differences,
   not a proven cause. Explicit cache policy and complete effective sampling/batch
   settings are needed for interpretable comparisons. Disabling reuse can cost
   latency and does not establish absolute determinism.

4. [JSONSchemaBench](https://arxiv.org/abs/2501.10868) separates format coverage,
   output validity and task quality; some tested constrained tasks improve in
   accuracy. Conversely [The Constraint Tax](https://arxiv.org/abs/2605.26128), a
   2026 preprint on other small models, reports accuracy costs in some conditions.
   Neither establishes the effect on Gemma4/Taglish. Preserve schema/host guards;
   test a simpler decision representation only if controlled evidence warrants it.

5. [TweetTaglish](https://aclanthology.org/2022.lrec-1.225/) studies Tagalog-English
   mixing with word-level language annotations. Its social-media domain and
   dictionary/rule annotation method do not validate our student-response labels
   or justify replacing LLM classification with dictionaries. Our requirement is
   conversational response preference, including natural technical terms, rather
   than simply the dominant language. Future labels need a documented treatment
   of borrowings, mixed affixes, course codes and quoted text; settled labels stay.

6. [Calibrate Before Use](https://proceedings.mlr.press/v139/zhao21c.html) documents
   sensitivity to prompt/example choices on other models. Balanced contrastive
   examples are a plausible intervention, not a proven fix here. Separate example
   families from validation families and do not put the failing evaluation queries
   into the prompt. Avoid selecting the best seed or trying equivalent rewrites
   until one happens to pass. Aggregate repeat results and retain regressions.

## Recommended sequence

Student capability:equivalent English/Filipino/Taglish questions select the correct
evidence path and conversational response style. Intended evidence:original query
-> same-artifact LLM interpretation/style -> existing host validation -> per-case
proposed/effective outcomes, with no institutional execution. Phase exit advanced:
actual-model language/meaning quality, distinct from parser and safety checks.
Unresolved question:do accurately controlled inference settings improve the known
semantic errors without introducing errors in pure-language or scope controls?

1. Audit evaluation controls first. Capture effective samplers, cache policy,
   context/output/reasoning budgets, template, batch/thread settings and pinned
   digests. Verify the runtime-recognized thinking-budget field with a bounded
   synthetic smoke test before claiming an enforced budget. Account for reasoning
   and final structured output within the same context/output limits. This is
   new evidence correcting the prior probe, not repetition of its settings.
2. Predeclare a paired comparison using the same current15 synthetic cases,
   model/prompt/schema and explicit cache policy:thinking off versus correctly
   configured thinking on, first keeping sampling fixed. Include both stages,
   all three languages and terminal controls. Use a small fixed repeat count and
   report every repeat; runtime verification precedes the comparison. A separate
   vendor-sampling comparison is warranted only if this leaves a relevant question.
   Stop each diagnostic when its declared question is answered; no broad grid.
3. If errors persist, design one semantic intervention from observed confusion.
   Clarify the Symbolic/Hybrid distinction:explaining a symbolic result alone does
   not require external documentary evidence. For style, use separate balanced
   development examples illustrating conversational mixing and technical terms.
   The independent style stage already exists; splitting it again is not a novel
   fix. A smaller routing decision before extraction is only a later hypothesis.
   Preserve LLM semantic choice, compound handling and bounded repairs; no host
   keyword rerouting, arbitrary confidence cutoffs or unbounded self-correction.
4. Validate any selected improvement on broader, independently reviewed families.
   Reuse the75 accepted institutional variants where applicable, preparing route,
   control and response-style labels without reopening wording acceptance or
   assuming executable rule coverage. Keep final evaluation families sealed.
   New institutional questions/labels retain their applicable review boundaries.

Recommended development targets:all known regressions correct; at least95% route
and response-style agreement in EACH language on broader reviewed validation;
zero unchecked invalid dispatches. Measure route macro-F1/confusions, meaning and
operation preservation, style agreement, clarification/refusal rates and latency
separately. Correct clarifications count according to reviewed expectations;
abstention does not erase an otherwise answerable routing failure. These targets
need owner agreement before becoming formal gates. Fifteen correlated variants
cannot demonstrate95% population accuracy, even if every one passes. Report
family counts, denominators, uncertainty and proposed/effective decisions.

Keep the same Gemma artifact first. Higher precision, a larger model or fine-tuning
would need a separate evidence-backed project decision and consistent evaluation
conditions under master20; no download or model change follows from this research.
Final-answer language/grounding and image-input accuracy are later-phase measures.

## Delivery and recovery

Raw prior probe:workspace/audit-evidence/p07-implementation-20261019/
probe-native-thinking.py; original files and observations unchanged. Current
task-owned runtime remains stopped since12:25. No current15-case score is claimed.
Next action:audit and specify the controlled comparison above before implementation
or new model calls. Phase07 stays active; no final handoff/Phase08 authorization.

Documentation verification:existing readiness Python3.13 -B -m pytest -q
-p no:cacheprovider --basetemp=workspace/audit-evidence/p07-accuracy-research-20261019/docs
tests/test_docs_hygiene.py .agents/skills/bintanong-phase-handoff/tests/test_phase_state.py:
571passed/11subtests11.18s,exit0. TEMP/TMP redirected to the same ignored evidence
root; docs.log retained there. Product tests were not repeated for this docs-only
change. git diff --check and phase-state validate pass; active7 cannot advance.
