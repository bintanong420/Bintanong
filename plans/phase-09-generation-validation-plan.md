---
artifact: phase-plan
phase: 9
status: in_progress
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-08-handoff.md
---

# Phase 09 generation and validation implementation plan

**Goal:** generate bounded candidate explanations from Phase08 evidence, preserving
canonical decisions, source identities, unknowns, privacy and language preferences.
**Spec:** master14; Phase08 final handoff; scope/source-gap policy; standing
19October2026 prompt/validation decision. Owner's current "continue" resumes the
next permitted phase after successful can-advance. Keep the isolated p08 branch.
**Execution:** executing-plans inline, focused TDD and cohesive commits. One fresh
whole-change review before exit; no new infrastructure, dependency or lock changes.

## Design and constraints

Institutional release/loading remains held. Build explicit candidate-only contracts
over existing IntegrationResult; do not weaken institutional EvidenceBundle or
AnswerEnvelope. Revalidate integration policy before preparing generation evidence.
Use the existing supplied Bintu transport; no weight training/fine-tuning/LoRA.
Carry the one-week accuracy-work cap; no prompt/model/seed sweep or new downloads.

Host code copies structured outcomes/conditions and renders the canonical decision.
The LLM emits a strict draft of source-cited explanatory claims, never executable
goals, authoritative status or a replacement decision. Validate request release,
language, outcome and source references deterministically. A separate constrained
LLM evidence check judges each prose claim's support and absence of contradiction;
its verdict is fallible and must be evaluated separately from schema/guard success.
Citation presence alone is not support. Validate final assembled output as well.

Non-ready integration controls/unknowns/conflicts bypass claim generation and get
localized deterministic fallbacks. Ready draft failures permit exactly one answer
repair using the unchanged evidence; at most two draft/two support-check calls.
One overall generation deadline covers all calls. No unvalidated token streaming.
Router repair counters stay separate. No raw query/facts/prompt/error-body logging.

## File responsibilities and interfaces

Create `backend/bintanong_generation/`: `contracts.py` (strict draft/check/candidate
answer contracts), `evidence.py` (validated allowed evidence cards and canonical
decision), `prompt.py` (versioned draft/support prompts), `validation.py`
(deterministic and support checks), `render.py` (localized canonical/fallback
rendering), `generator.py` (bounded loop and optional orchestration composition),
`README.md` and `__init__.py`. Update developer pipelines/root navigation.

Entry: `await Generator(transport, timeout_seconds=...).generate(text, integration)`
returns `CandidateAnswer`; optional `AnswerPipeline(orchestrator,generator).run(text,
context)` composes the same request under an overall deadline spanning both stages.
Model-visible evidence excludes request/session
IDs, private fact refs and telemetry. Canonical course/curriculum and rule context
remain scoped. Source cards preserve complete supplied passages/locators and gaps.

## Tasks

Each behavior task:write focused failing tests, observe RED, implement minimally,
verify GREEN/relevant regressions, record commands/results and commit.

1. [x] Evidence preparation and strict candidate contracts.
   Files:contracts/evidence; tests/test_generation_evidence.py.
   Verify reassembly rejects mismatched status/release/components, deterministic
   source-card identity/locators, decision copying, private-ID exclusion, dependency
   listing semantics and no institutional-answer conversion.
   Consult [orchestration research/context audit](2026-10-19-orchestration-research-and-context-alignment.md).
2. [ ] Versioned prompts, validation and localized rendering.
   Files:prompt/validation/render; tests/test_generation_validation.py.
   Verify fabricated IDs/wrong version/language/outcome and contradictory or
   unsupported claims rejected; complete support verdict required per claim; final
   decision text/conditions host-rendered; English/Filipino/Taglish fallbacks.
3. [ ] Bounded generator and request composition.
   Files:generator; tests/test_generation_loop.py and test_generation_pipeline.py.
   Verify one repair/shared evidence, separate counters, malformed/checker failure,
   whole-request and generation deadline/cancellation, no streaming/raw logging, controls skip model calls,
   concurrent sessions and all three routes preserve outcomes.
4. [ ] Bounded synthetic model observations and developer guide.
   Files:module README/developer pipeline guide; dated evaluation report in plans.
   Reuse supplied existing runtime/assets if locally available; no download/install.
   Keep held institutional corpus inactive and accepted75wordings untouched.
   Use distinct synthetic dev families from prompt examples; report actual source
   support, decision/language results and operational failures separately. If actual
   inference cannot run within authorized assets, record NOT RUN and leave required
   exit unresolved; mocks cannot establish actual-language performance.
5. [ ] Independent whole-change review, scoped regression and final exit mapping.
   Preserve residual semantic errors, source/release holds and precise measured
   denominators. Close only verified written offline exits; otherwise checkpoint
   active9 with one exact next action. Do not start Phase10 here.

## Verification and review focus

Python3.13 existing readiness environment, `-B -m pytest -q -p no:cacheprovider`;
TEMP/TMP/basetemp and raw outputs under workspace/audit-evidence/
p09-generation-20261019. Test synthetic fixtures only. Existing contract/routing/
orchestration regression gate must pass. Fresh model report is separate from mocks.

Review focuses on prose contradicting a preserved structured field, incomplete or
duplicated support verdicts, source prompt injection, session/private-ID exposure,
repair changing evidence/authority, and deadline exhaustion during verification.

## Exit gate

Contradictory/fabricated-citation/wrong-version/unsupported-claim drafts are rejected;
regeneration terminates after one repair; final canonical output preserves symbolic
status. Source cards and scope remain pinned; no unvalidated answer is exposed.
Report multilingual synthetic observations honestly, including residual checker/
language failures; no universal correctness or institutional deployment claim.
