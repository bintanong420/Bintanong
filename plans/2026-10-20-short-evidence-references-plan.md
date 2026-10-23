# Short evidence references implementation plan

20 October 2026; Phase09 active. Continue the recorded next action from
[session handoff](2026-10-20-phase09-fast-replies-session-handoff.md).
Execution: inline, focused TDD, cohesive commits, one final independent review.

**Student capability:** faster cited undergraduate academic-affairs explanations.
**Evidence path:** unchanged LLM routing/style, RAG and/or reviewed structured
Prolog, generation, separate support check, host validation.
**Exit advanced:** Phase09 citation integrity and bounded actual-service validation.
**Question:** can short model-facing evidence labels reduce output work while
preserving exact canonical citations, decisions, language and support boundaries?

## Design and constraints

Owner clarification during execution:assess latency in the context of RAG and
neuro-symbolic processing, and never sacrifice answer accuracy for response speed.
Retain complete evidence, reasoning and validation; reject quality regressions.

Add an explicit `canonical`/`short` generation reference profile, default canonical
until bounded evidence supports selection. Keep separate routing/style selected.
An immutable request-local codec assigns e1..e32 in prepared-card order. Only card
identifiers and typed claim references change on the wire; full source text,
locators, source/version/hash metadata, structured context and limitations remain.
Use a separate strict wire draft contract. Reject unknown labels, canonical IDs
on the short wire, duplicate references/claim IDs, malformed or extra fields.
Restore hashes before existing draft/final validation and render canonical outputs.
Re-encode the canonical draft for the support checker with the same map. Repairs
reuse it. No process-wide maps, evidence truncation, string replacement in prose,
new cache, dependency/model change, skipped checker or unvalidated streaming.

`references.py` owns wire contracts and the codec; `prompt.py` builds matching
messages/schema; `generator.py` converts at the boundary; runtime settings expose
the experimental selection programmatically with truthful run metadata.
Public canonical contracts stay unchanged. Existing Hybrid support-scope failure
remains a quality hold; short references alone cannot repair entailment accuracy.

## Tasks

1. [x] Write focused tests in `tests/test_generation_references.py`; observe RED.
   Cover exact round trip, full payload preservation, all32cards, multiple
   references, duplicate/unknown/stale labels, unchanged prose, immutable schemas,
   request isolation, repair and final citations. Pin invalid profile rejection.
2. [x] Implement the small codec and optional prompt/generator/runtime wiring;
   verify GREEN and existing generation/runtime/routing regressions. Commit.
3. [x] Reuse existing fictional multilingual generation cases for one bounded
   actual-model quality observation, plus the existing three English full-service
   questions if the codec behaves correctly. No new institutional benchmark cases,
   prompt/seed sweep or parameter tuning. Report failures, token counts, timing,
   cold startup and warm requests separately; three points do not establish p95.
4. [x] Research response-time acceptability from primary HCI/LLM/education sources;
   distinguish complete validated answers from first tokens and task completion.
   Record source methods, limitations, proposed targets and stop conditions.
5. [x] Run the scoped final gate and independent review; record current progress,
   checkpoint and dated results. Keep Phase09 active and institutional holds.

## Verification

Use existing readiness Python3.13, `-B -m pytest -q -p no:cacheprovider`, external
TEMP/TMP/basetemp and evidence under workspace/audit-evidence/
p09-short-references-20261020/. Preserve old sealed evidence. No unrestricted pytest.
Actual observations reuse the existing CUDA18088 profile/fictional release and
resident encoder. Record exact code/input/prompt/schema identities before inference.

Ruling: the owner's continuation authorizes the handoff's small wire optimization;
no new source-content or architecture decision is needed. Proposed latency targets
are engineering recommendations pending local student evaluation, not approved SLAs.

Delivery: [actual results](2026-10-20-short-evidence-references-results.md),
[research judgment](2026-10-20-response-time-research-assessment.md). Ruling after
nine actual cases:selection fails on two semantic scope errors despite correct
mapping/positive checker verdicts. Keep canonical selected;skip the three planned
full-service timings after quality failure. No further speed gain established.
Explicit51-selection gate1963passed/66subtests89.42s;independent review confirms
the failure and finds no new P1/P2 software defect. Phase09 remains active.
