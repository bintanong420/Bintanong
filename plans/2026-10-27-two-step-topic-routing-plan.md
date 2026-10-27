# Two-step topic routing implementation plan

**Goal:** route questions against the expanded source menu without exceeding the
existing 8192-token model window or dropping requested evidence.
**Architecture:** opt-in `Router(topic_selection=True)` first selects at most eight
subjects with the same transport, then supplies complete selected topics to the
existing semantic router. The default and menus of eight or fewer retain their path.
**Stack:** existing Python/Pydantic/llama.cpp; no dependency or runtime-pin changes.
**Spec:** [binding/capacity design](2026-10-27-expanded-topic-binding-results.md),
existing Phase 11 plan and master sections 3/11/13/16/23/24.
**Execution:** inline synthetic TDD; continue the recorded next action under the
owner's standing autonomous-work direction. This refines existing scope and does
not add product requirements or infer corpus activation approval.

## Baseline and constraints

Existing requirements reviewed with create-prd: undergraduate students asking
policy/procedure questions, course checks and mixed follow-ups; cited, bounded
answers or explicit unavailable/clarification outcomes. Existing plans establish
users, needs, scope and release gates; a replacement PRD adds no requirement here.
Thesis physical 17–18/39–44 and routing PNG consulted on 27 October: retain
undergraduate/read-only/privacy limits and structured Prolog versus document RAG.
The thesis closed-world example is illustrative; missing grades remain unknown.

Preserve all selected topic fields, source context, not-stated claims and cues.
Unknown IDs, duplicates, extra keys, invalid types, ambiguity and >8 selections
withhold; never trim selections. An empty selection may still reach semantic
routing for structured/greeting/excluded requests; documentary requests without a
selected subject cannot dispatch through the candidate path. No selector repair.
Do not infer semantic completeness from schema validation: recall needs live probes.
The previous-turn signal contains only the existing bounded identifiers/availability,
never transcripts or student facts. Final routing receives the original context.

Exact per-call guards reuse `LlamaTransport.infer` (`/apply-template`, `/tokenize`,
768 output +8 margin); no new token estimator or evidence truncation. Current
[official server docs](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
checked through Context7 on 27 October. No library upgrade is proposed.

## Tasks and acceptance

1. [x] Add `tests/test_routing_topic_selection.py` using synthetic source menus and
   the existing real router with a fake inference boundary. Observe RED before code.
   Cases: opt-in/default/small menu, complete selected-topic binding, unknown and
   duplicate IDs, malformed/oversized/ambiguous/empty responses, failed transport,
   multiple document parts, Hybrid/structured/excluded controls, follow-up context,
   and request isolation. Assert final routing decisions as well as sent payloads.
   Add `topic_selection.py` prompt/schema/parser; integrate locally in `router.py`.
   Add separate `selection_attempts` accounting without changing repair counts.
   Run routing regressions; commit verified implementation and evidence.
2. [x] Exercise the candidate with real `LlamaTransport` over synthetic HTTP responses:
   exact boundary and overflow before selector, detail and repair completions.
   Preserve all messages; failures withhold and do not fall back. Run focused tests.
3. [ ] Run bounded actual-model observations against the inactive 146-topic menu,
   record selected IDs, route/part/style outcomes, exact input counts and selector
   versus total warm routing time. Compare small-menu accepted regressions without
   source/pin changes. Stop rather than tune an unbounded prompt sweep.
4. [ ] Run the project suite, docs/phase/diff checks and review this change. Record
   exact results, limitations and the next remaining gate in progress/checkpoint.

## Review focus

- Cross-request selected topics must not mutate `Router.topics`.
- A detailed model cannot escape selected subjects even if the full menu contains them.
- Empty selection cannot silently answer one part of a mixed request.
- Excluded audience/ambiguity controls and structured operations retain host validation.
- Repair prompts can be larger than the first call; they must independently fit.

## Verification

Use shared Python 3.13, `-X utf8 -B -m pytest -q -p no:cacheprovider`, external
basetemp under workspace/audit-evidence/p11-two-step-routing-20261027.
Focused: new selector tests, `test_routing_*.py`, document-topic orchestration tests.
Full: `tests`; retain existing skipped/xfail disclosures. Existing docs hygiene,
phase-state validation and `git diff --check`; no new tool installation.
No active pin/hosted write/frontend integration/Phase 12 advancement. Expanded
answer-quality and service/image structural/release gates remain separate.

## Execution evidence

Baseline89tests passed. RED28failures for missing constructor option after repairing
an oversized pytest parameter ID (Windows environment-variable limit). GREEN28.
Existing transport boundary/overflow coverage plus new candidate integration:33passed.
Review added request-isolation/style-repair coverage;35passed/accounting RED1missing
selection_calls. Added explicit evaluation selector counts;combined routing,
orchestration-topic,docs and phase-state checks:477passed/14subtests39.22s.
Independent review:33tests passed,no blocking finding;minor accounting gap repaired.
Full project suite and bounded actual-model observations running;no quality claim yet.
