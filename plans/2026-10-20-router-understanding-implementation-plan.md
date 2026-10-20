# Router question understanding implementation plan

> For agentic workers:use executing-plans inline with test-driven-development.

**Goal:** preserve each requested answer part from pre-evidence interpretation to
validated candidate output,including the correct structured or documentary path.
**Architecture:** extend the existing interpreter,bind its parts to original
question/request/release,and require per-part output accounting. Reuse existing
documentary support/ledger contracts;host canonical symbolic results alone cover
structured parts. No extra classifier call or experimental profile.
**Stack:** existing Python3.13/Pydantic/Bintu/Prolog adapters;no dependency changes.
**Spec:** [reviewed design](2026-10-20-router-question-understanding-recovery-design.md).
Baseline37e8bda;Phase09 stays active. Owner's continue authorizes implementation.

## Constraints and execution

Accuracy first;retain source text,privacy,release binding,unknown semantics,separate
language call,one shared routing repair and one answer-repair/deadline. No source/
benchmark changes,installs,training,DB mutations,Phase10 or activation. Existing
failed observations remain sealed;new schema/mocked green is not actual quality.
The 15-20s browser target and conditional20-30s complexHybrid range remain proposals.

Use the existing isolated p09 worktree. Keep the authoritative ledger in this plan
and phase checkpoint;raw scripts/logs under workspace/audit-evidence/
p09-router-understanding-20261020/. Native PowerShell commands replace Unix-only
skill helpers and obey the owner's evidence-location rule. Read both Conventional
Commits skills before each cohesive commit;explicit staging only.

Preflight interfaces:Interpretation -> RoutingResult -> bound understanding in
IntegrationResult -> PreparedEvidence -> generator/checker -> CandidateAnswer.
Every producer/consumer migrates together;no empty-plan/default compatibility path.
Historical observations remain historical;do not rewrite sealed artifacts or make
the failed detached analyzer a runtime fallback. New candidate remains unvalidated
until a separately frozen actual-model gate passes;do not claim selection/promotion.

## Task1: grounded interpretation and host route consistency

Files:routing contracts,prompt,validation;focused tests/test_routing_understanding.py;
existing routing fixture helpers. Interpretation v2 requires1-8 RequestParts for a
route;terminal controls require none. Each part uses Quote,part_id,evidence_need
document/structured/unknown and explicit operation_indices. Duplicate spans/IDs,
invalid operation associations and ungrounded quotes fail. Host declared-needs
consistency prevents structured work becoming RAG;unknown/unavailable remains held.
Preserve compound-operation clarification and audience/control precedence.

- [x] Focused RED for omitted/duplicated/misbound parts,quote grounding,unknown and
  route inconsistency;observe assertion/validation failures before implementation.
- [x] Implement minimal versioned contract/prompt/grounding/host changes;no call added.
- [x] Migrate synthetic routing fixture helpers explicitly;relevant routing GREEN;
  record exact commands/results and commit a cohesive increment.

## Task2: bound propagation and per-part generation

Files:orchestration contracts/orchestrator;generation evidence/contracts/generator/
validation;one request-understanding helper and shared ledger-contract extraction
if needed to avoid circular imports. Tests:test_request_understanding_pipeline.py,
existing integration/generation fixtures. Integration v2 requires an explicit
nullable understanding;ready evidence requires a bound nonempty plan. Bind original
question SHA256,request ID,pinned release,parts,proposed operations and validated
predicate request. Generator checks exact text/identity;model payload omits private
request/fact IDs. CandidateAnswer v2 carries per-part ledger or explicit no-ledger
control. Reuse RequirementReview/PartMapping/RequirementLedger;canonical structured
parts are host-bound to the performed operation/result,never documentary prose.

- [x] RED for cross-question/request/release replay,missing plan,missing fee mapping,
  structured-via-document substitution and Hybrid loss;retain language/call/deadline
  and cancellation guards. Expected:failures from missing new boundary/coverage.
- [x] Implement bound propagation and existing support-call per-part accounting;
  no new model call. Unknown/missing mappings cannot yield answered status.
- [x] Explicitly migrate all current synthetic producers/consumers;reject v1 payloads
  at new runtime boundaries. GREEN relevant generation/orchestration/routing suites;
  keep historical loaders/evidence separate. Commit verified cohesive changes.

## Task3: review,software gate and actual-quality prerequisite

- [x] Update developer documentation and dated results with exact contract versions,
  behavior,limits and any provisional implementation calls.
- [x] One fresh independent whole-change reviewer as executing-plans requires;one
  focused TDD fix pass for important findings,no re-review. Preserve source/privacy/
  unknown/operation binding and no extra language/classifier calls in review focus.
- [x] Run the prior explicit57-selection gate plus new focused files (no bare pytest),
  Python3.13 -B -m pytest -q -p no:cacheprovider with ignored TEMP/TMP/basetemp.
- [x] Freeze a bounded actual-quality gate separately before new inference:fictional
  questions/independent expected parts/route/operation labels,full source text and
  prompt/code/schema/settings hashes. Do not reuse failed cases as unseen validation.
  Software delivery may complete before that gate;quality/promotion/Phase09 exit
  remain unresolved until actual evidence. No repeated prompt/model/seed/budget sweep.
- [x] Seal evidence,update compact INDEX/progress/checkpoint,verify links/phase state
  and commit. No push,merge,deployment or institutional use.

## Review focus

Repeated/Unicode original spans;unavailable structured work disguised as documents;
cross-request/release/question identity;Hybrid canonical result covering the wrong
operation;missing/duplicate parts or claim mappings;terminal controls/deadlines/
cancellation;model-visible privacy;old payloads silently receiving empty plans.
Reuse existing regressions;add only tests with distinct consequential failure modes.

## Ledger

Start37e8bda,clean. Context thesis17-18/39-44,actual routing PNG,master3/11/12.4/13/14,
scope policy and prompt decision consulted. No new discrepancy;thesis illustrative
missing-as-false does not override host unknown. Timing recommendation preserved.

Task1 complete:RED6failed/6passed0.64s (parts rejected as extra or missing not
rejected);GREEN12passed0.42s. Routing regression14fail/174pass3.32s exposed old
fixture quotes/expected counters and schema's one-operation decoding limit. Fixture
migration preserves old guards,adds explicit original text;decoder now permits up
to4operations and host still clarifies compound requests. Intermediate4fail/184pass
was helper text passed to constructor,corrected helper signature only. Final routing/
format198passed3.67s. Exact logs task1-*.log. No inference or new call.
Implementation call:allow4decoded operations to preserve compound meaning,matching
the reviewed design;this changes old count=2 decoder rejection to host clarification.

Task2 complete:initial focused RED9fail1.11s;GREEN9pass0.75s. Symbolic all-profile
host-only regression RED1fail0.80s;now passes. Review-identity schema pin RED1fail
0.78s;effective support-prompt hash RED1fail/2pass1.10s;both corrected. Final
generation/orchestration plus both new focused files434passed8.64s. No inference.
First broad migration run was stopped when an outdated Hybrid fixture prevented
its cancellation-test event;test now bounds that wait to1s. Subsequent27fail/395pass
and4fail/418pass were explicit fixture identity/payload/hash migrations;logs retained.
Implementation calls:Symbolic results use host canonical rendering in every profile;
the old whole-question coverage experiment cannot bypass the new part ledger and
therefore withholds even with a complete verdict. Old sealed observations unchanged.
Both choices retain accuracy boundaries;experimental compatibility is narrower.
Test support adapters explicitly cover only one declared document part;multipart
regressions use independent scripted mappings,never automatic all-part acceptance.

Task3 review197passed3.07s found3Important gaps:nested support version not pinned,
operation target outside its credited part,and nonexistent claim ID in final ledger.
Root RED3fail0.99s;one fix pass pins nested schema,requires target-mention containment
before dispatch and validates final claim coverage. GREEN146passed2.15s. No re-review.
Initial59-selection gate3fail/1662pass/66subtests92.98s identified3remaining explicit
fixture migrations (reference request/release replay and Combined Hybrid quote).
AFTER corrections final59-selection1668passed/66subtests123.76s,exit0.
Review-set-aside rulings:actual semantic quality/latency and omitted/unrepresented
parts remain unresolved until actual evaluation;institutional authority/readiness
remain separate holds. These cannot be settled by more mocked tests. New gate
document is parent-owned and the final gate resolves the review's fixture exclusion.
No minor findings. Future8fictional dev question/reference records frozen SHA256
c1071bbab22cd200a400b500e8622c077a43c18e4ab7c814abfd8d3258daad34;
runtime inputs/readiness must bind before execution. NOT RUN,no quality promotion.

Software correction8fafaf7;delivery74sealed files,manifest
a8b4e1e5dc0b0b4e3d69bdfef778bb7a92e4e0b7f0ee048d692b91433f241d4a.
Candidate code/prompt/schema/default-settings freeze SHA256
dac9636ac92d08914d78bba7f75ea223c211093fbfd5811d8f8a30e2eff530b9.
Complete executable inputs/runtime readiness still required before actual inference.
Owner token-usage question scoped to this thread;local counter snapshot and official
guidance saved separately. No diagnostic agents,reasoning/config or source changes.
