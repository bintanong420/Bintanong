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

## Fine-tuning duration follow-up,14:08

Owner asks whether adding fine-tuning would greatly extend development; this is
a feasibility question, not a decision to start training. Rough engineering
allowance for a narrow routing/style LoRA or QLoRA pilot:1-3additional weeks,
assuming timely human data review and access to a suitable GPU. A reviewed dataset
and working training environment could shorten a first experiment to several
days; repeated failed validation or broader answer-generation tuning could take
longer. These are planning estimates, not measured runtimes or delivery promises.

[Google's tuning guide](https://ai.google.dev/gemma/docs/tune) identifies data
collection, tuning/testing and deployment as separate work, supports less
resource-intensive adapter methods, and requires testing on untrained requests.
The work here would include reviewed English/Filipino/Taglish input-output labels,
family-separated training/validation/test data, compatible training weights and
environment, training trials, export/runtime integration and full regressions.
Our75accepted development variants are not automatically a training dataset, and
final evaluation families must stay held out. Actual training duration cannot
be inferred from our inference timings or existing GGUF file size.

[PEFT documentation](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora)
describes training adapters with the base frozen. Context7 resolved /huggingface/peft
and confirmed adapter-only LoRA/k-bit training behavior. This is the recommended
method to investigate if tuning becomes necessary, rather than full-weight tuning.
Google's [QLoRA example](https://ai.google.dev/gemma/docs/core/huggingface_vision_finetune_qlora)
uses a compatible training checkpoint and separate training stack; its vision-task
hardware requirement is not a measured minimum for our text-routing task.

Read-only nvidia-smi --query-gpu=name,memory.total --format=csv,noheader returned
NVIDIA GeForce RTX3050 Laptop GPU,4096MiB. Current local GPU capacity makes larger
GPU/cloud access likely for a practical pilot; no assertion that every low-memory
configuration is impossible. No training setup, installs, downloads, paid service
or model change authorized/executed. Master20 still requires an explicit project
decision. Recommendation remains controlled inference evaluation first; if that
fails, tune routing/style behavior while policies stay in reviewed Prolog/RAG.

Follow-up docs gate:same pytest files/options as above, basetemp=raw-root/
finetuning-docs;571passed/11subtests18.48s,exit0,finetuning-docs.log.
Diff check and phase-state validation pass; product/runtime unchanged.

## One-week constraint and prompt-guidance follow-up,14:16

Owner sets a maximum one-week extension with final defense about a month away,
reports access to another GPU described as4080/8GB, and clarifies interest in
prompts as guides plus guardrails. The other GPU identity/memory are owner-reported,
not the locally verified3050; neither machine was changed or benchmarked here.

Recommendation:use prompt engineering with the current artifact, existing schema
and deterministic host guards within this budget. Technical soft-prompt tuning
still learns parameters; ordinary instructions/few-shot examples need no training.
See [PEFT's definition](https://huggingface.co/docs/peft/main/package_reference/prompt_tuning).
[Google's prompt-design guidance](https://ai.google.dev/gemini-api/docs/prompting-strategies)
supports explicit instructions and examples, but concerns Gemini and does not
prove an accuracy improvement for our Gemma artifact. Measure the intervention.

Suggested allocation, not a delivery guarantee or changed phase exit:day1 bound
the runtime-control audit/baseline; days2-3 one justified prompt revision for the
observed route/style confusions using separate synthetic examples; days4-5 paired
per-language regression/broader reviewed validation; days6-7 freeze the candidate,
finish verification and document results/limitations for the defense. Stop adding
experiments at the cutoff. Retain the best verified candidate if an intervention
regresses; unresolved errors remain disclosed and cannot imply phase completion.
No fine-tuning/training pipeline is recommended for this time budget.

LLM routing remains semantic. Schema, exact reviewed identities, capability and
curriculum checks reject detectable invalid requests; they cannot guarantee that
a well-formed wrong route or wrong language preference is caught. Missing facts
need clarification; known schema-valid semantic errors still require evaluation.
Curriculum/Prolog and document/RAG roles stay intact. Next action remains the
bounded runtime-control audit, now under the owner's one-week improvement limit.

Prompt-guidance docs gate:same files/options, basetemp=raw-root/prompt-guidance-docs;
571passed/11subtests14.13s,exit0,prompt-guidance-docs.log. Diff check and phase-state
validation pass. No new inference, implementation, hardware setup or training.
