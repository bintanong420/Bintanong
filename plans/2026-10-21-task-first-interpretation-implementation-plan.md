# Task-first interpretation implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans inline, task by task. Steps use checkboxes. One final whole-change reviewer; no per-task delegation.

**Goal:** implement the approved count/parts-before-operations/route protocol and
measure it once without weakening semantic quality or existing safeguards.
**Architecture:** model-wire v2 normalizes to the existing Interpretation-v2.
Host validates a declared count, exact quotes and existing scope/operation guards;
RAG, structured Prolog and final generation remain unchanged.
**Tech stack:** existing Python3.13/Pydantic, supplied Gemma via existing transport;
no new framework, dependency or model asset.
**Spec:** [reviewed design](2026-10-21-task-first-interpretation-design.md).
Owner approved with "oh ye definitely then" after its simple explanation and
approval request. This covers the specified change and one finite gate, not the
separate unanswered conditional-answer policy. Execute using the existing inline
Phase09 method; no repeated approval of this same scope.

## Global constraints

- Same original/normalized question, scope/facts/capabilities; catalog stays host-side.
- Wire v2, prompt v14; combined packet v3/prompt v5 remains explicit/unselected.
- part_count strict0..8 must equal len(parts); never invent/delete parts to match.
- Selected separate/canonical/scoped; existing repair/call/deadline limits unchanged.
- Existing CUDA18088 only; ctx8192,out768,temp0,seed0,cachefalse,reasoningnone;
  inference/stage/generation/request120/120/120/180s. No startup or rescue run.
- Undergraduate/read-only, unknown/source-gap/privacy/release holds; no Phase10,
  institutional activation, training, installs, dependency/lock/DB change or push.
- Workspace/MODELS unchanged. Raw evidence:workspace/audit-evidence/p09-task-first-20261021/.
- Existing readiness Python3.13; -B pytest -q -p no:cacheprovider, external TEMP/TMP/basetemp.

## Review focus

1. Wrong/missing/legacy count must reject without changing tasks or adding repairs.
2. Empty terminal controls remain valid; unresolved controls can preserve parts.
3. Forward part-operation references retain exact target/grade/negation semantics.
4. Both decoder schemas, displayed schemas and example agree in order/constraints.
5. Model-free fixtures stay distinct from actual outcomes; failed A prevents B.

## Task1: one cohesive wire/prompt boundary change

**Files:** modify backend/bintanong_routing/{wire,prompt,combined}.py and README.md;
create tests/test_routing_task_first.py. Migrate active literal/model fixtures in
tests/{routing_wire_fixtures,test_routing_wire,test_routing_wire_boundary,
test_routing_catalog_separation,test_routing_combined,test_routing_router}.py;
adjust other active fixtures only if the affected regressions identify them.
**Interfaces:** WireInterpretation.parse(v2) -> validated wire; unchanged
normalize_interpretation(text,wire) -> Interpretation-v2. build_messages and
output_schema signatures unchanged. No production compatibility coercion.

- [x] Write focused regressions using literal v2 packets: count2/one part rejects;
  missing count, bool count and wire-v1 reject; valid Hybrid preserves target,
  asserted failure and two parts. Terminal greeting count0 normalizes unchanged.
- [x] At actual separate/combined transport boundary verify prescribed property
  order on parent/all branches and displayed schema; worked example retains its
  original meaning with count3. Mismatched packet consumes only the shared repair;
  malformed style cannot obtain another. Reuse existing host/catalog/privacy tests.
- [x] Run new tests RED and record expected pre-change failures in red.log.
- [x] Implement required count and equality validator; remove wire-only count
  before normalizing. Reorder decoder/display/example; align only decision-order/
  schema-version guidance and version identities. Keep constraints/hashing helpers.
- [x] Migrate model-only test fixtures to v2/count and combined v3; leave normalized
  contracts and historical evidence unchanged. Update README's wire boundary.
- [x] Run new tests GREEN, then existing tests/test_routing_*.py plus existing
  schema-display regressions. Record explicit selection/results; no2200-test rerun.
- [x] Inspect/stage explicit files and commit the cohesive verified change.
- [x] Obtain one fresh whole-change read-only product review before inference;
  resolve actionable defects only. No extra review/model loop without a real need.

## Task2: freeze and run the single approved actual-quality gate

**Files:** new dated quality protocol/results in plans/; fixture runner, traces,
hashes, raw output and assessment under the ignored raw root above.
**Interfaces:** existing AnswerPipeline.run for A; selected
understanding.review_messages/review_schema/assess for B. No product evaluator change.

- [ ] Freeze unchanged four A questions/labels/order from catalog protocol,
  current code/schema/prompt/settings and prepared B fixture bytes/labels before
  inference. Verify prior sealed evidence and unchanged non-target modules.
- [ ] Verify resident18088 identity/readiness. If unavailable/mismatched, record
  NOT RUN; no startup, replacement server, setting change or extra service probe.
- [ ] One locked attempt: run d-en,d-fil,d-tl,h-en once each, maximum7calls each.
  Record meaning, count/order, distinct parts, route, target/facts, actual synthetic
  Janus status, prose relevance/support, language and timing separately.
- [ ] Author-assess against frozen labels/source, separately from model verdicts.
  Require unchanged response4/4 AND full-quality4/4. On failure, B is NOT RUN.
- [ ] Only if A passes, run the two reviewed prepared B challenges once each,
  max1actual selected-review call each. Require relevance r1 unresolved and omitted
  charge r2 unresolved; no false all-declared-parts-mapped result. No gold in payload.
- [ ] Maximum30physical model calls overall; no rescue/repair beyond A's existing
  limits. A/B have separate denominators and timing; keep raw failures intact.

## Task3: delivery and recovery snapshot

- [ ] Report actual gate outcome and all NOT RUN work; no schema/test accuracy claim.
  Keep component versus real retrieval/Supabase/API/browser/cold exclusions explicit.
- [ ] Update plan checklist, current progress and active checkpoint; index pointer
  only if needed. Keep caps80/80/160; preserve f1b7230 as prior full snapshot.
- [ ] Verify docs hygiene/local links/caps/diff and phase state. Seal raw evidence;
  explicitly stage/commit docs. No phase completion or candidate promotion from6/6
  alone; resume remaining written exits only when applicable prerequisites pass.

Self-review: all design requirements map to the three tasks; Task1 covers review
focus1-4, Task2's binding/stop assertions cover5. Execution is already authorized
inline; this plan introduces no additional scope or implementation-approval gate.
