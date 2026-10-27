# Prompt engineering and validation - standing owner decision

Current reply-language override,27October2026:
[English/Taglish decision](2026-10-27-english-taglish-response-decision.md).
English/Filipino/Taglish inputs remain;English/Taglish replies replace the older
Filipino-only reply target below. Historical decisions/results remain preserved.

Status:accepted19October2026. Applies to Phase07 and the remaining initial-build
phases. This is the decision record; the master plan and past evidence stay intact.

## Owner direction and terminology

After setting a maximum one-week extension for accuracy improvements before the
final defense, the owner accepts the proposed prompt-guidance/guardrail approach:
"ok let's proceed with this" and asks to save it for future phases. The owner
describes this as "training with the prompt engineering but no fine-tuning."
Preserve the intended approach while using accurate technical terminology:
prompt engineering supplies instructions/examples at inference time; it does not
train parameters, modify model weights or create a fine-tuned checkpoint.
Do not describe this implementation as model training in the manuscript or UI.

## Accepted approach

- Keep the supplied Gemma/Bintu artifact. Improve versioned instructions and a
  small set of reviewed examples, constrained output and deterministic validation.
  No full fine-tuning, LoRA/QLoRA or learned soft-prompt tuning in this build.
  A future training proposal requires a demonstrated need and a new explicit
  owner decision under master20; do not introduce it as an implicit dependency.
- LLM performs semantic interpretation and RAG/Symbolic/Hybrid routing. Host
  validation checks structure, grounded identities/facts, curriculum scope and
  supported capabilities. Do not replace routing with keyword rules or conceal
  a wrong proposal by silently rerouting it. Guards cannot establish that every
  schema-valid route or language preference is correct.
- Curriculum/prospectus facts and reviewed prerequisite/eligibility/dependency
  reasoning stay structured/Prolog. Handbook, Citizens' Charter and memos use RAG
  for applicable documentary evidence. Hybrid applies when both paths are needed.
  Missing facts, rules or evidence remain unknown and may require clarification.
- Preserve the user's conversational style:English -> English; Taglish -> Taglish;
  Filipino -> predominantly Filipino, retaining natural technical terms where
  needed. Course codes alone do not establish conversational mixing. No invented
  English/Filipino word-ratio quota or forced translation of technical terms.
- Preserve undergraduate academic-affairs/read-only scope, source gaps, private
  session boundaries, reviewed curriculum versions and institutional release holds.
  Final answer generation/validation and image attachments remain later-phase
  tasks; this decision does not claim they are implemented.

## Timebox and evidence

The one-week limit caps added improvement work, not a promise to finish the entire
system in a week or permission to waive a phase exit. Suggested allocation accepted
as the working approach:day1 runtime controls/baseline; days2-3 a focused prompt
revision; days4-5 regression/broader reviewed multilingual evaluation; days6-7 freeze
the best verified candidate and document limitations. Stop adding experiments at
the cutoff. Keep unresolved errors visible and honor formal phase boundaries.

Separate prompt examples from evaluation families; never insert sealed final
questions into examples. Reuse accepted institutional wordings where applicable
without reopening acceptance or assuming executable rule coverage. New questions
or labels retain their applicable review. Report proposed and effective routes,
meaning/operations, response style and guard behavior separately by language.
Guarded failure/clarification is not automatically a correct model decision.
Earlier suggested95% targets remain recommendations, not newly approved numeric
gates or measured results. No accuracy gain follows from this decision alone.

Keep prompt/schema/model/runtime identities and exact denominators with results.
Use focused RED/GREEN tests for changed behavior, then relevant regressions and
actual-model evaluation. No broad prompt/seed sweep or additional model download.

## Continuation across phases

`AGENTS.md` and `plans/INDEX.md` point here. Every later phase must carry this
decision into its plan/handoff and consult it before proposing training, replacing
the routing model or designing answer-generation prompts. It remains standing
until the owner explicitly revises it; a new session or phase is not a revision.
Use the active checkpoint for current work, not this record as proof of delivery.

Suggested manuscript description, to adapt after implementation verification:
"Bintanong uses a pretrained Gemma model with versioned instructions and in-context
examples for multilingual interpretation and adaptive routing. Structured outputs
are validated before integration with reviewed Prolog reasoning and RAG evidence;
the model weights are not fine-tuned."

## Start of execution,19October2026

Read-only audit of product bec3d8e confirms LlamaTransport pins temperature0/seed0,
reasoning_effort=none and schema/output limits, with matching reasoning selection
in template preflight. cache_prompt and other sampler controls are not explicit;
metadata does not capture a complete effective inference profile. Existing mock
transport tests cover payload/template/budgets but do not establish reproducibility
of actual inference. Legacy BintuClient/Direct remains separate from this module.
No runtime restart, inference call, prompt change or training occurs in this audit.

Next:specify and test an explicit cache/baseline profile with unchanged semantic
prompts before the bounded prompt comparison. The previous thinking probe's wrong
budget key remains documented in the [research report](2026-10-19-phase07-accuracy-research-recommendation.md);
do not repeat it unchanged or turn the optional reasoning check into a new sweep.

Delivery verification:existing readiness Python3.13 -B -m pytest -q
-p no:cacheprovider --basetemp=workspace/audit-evidence/p07-accuracy-research-20261019/standing-decision-docs
tests/test_docs_hygiene.py .agents/skills/bintanong-phase-handoff/tests/test_phase_state.py:
572passed/11subtests15.20s,exit0. TEMP/TMP under the same ignored evidence root;
standing-decision-docs.log retained there. Diff check/phase-state validation pass;
active7 has no complete handoff. This verifies docs/ledger, not model accuracy.
