# Source-bound routing context correction plan

**Goal:** distinguish reviewed services and grading claims in the inactive expanded
router without changing policy text,release pins or the default runtime path.
**Baseline:** Phase11plan/master3/11/13/16/23/24 and
[saved failures](2026-10-27-two-step-topic-routing-results.md);owner “aight proceed”
continues that recorded next action. Existing users/scope/requirements remain.
**Execution:** inline synthetic RED/GREEN,small verified commits,one independent
review and bounded replay. No new product scope,dependency/model or activation.

## Diagnosis and chosen design

Borrowing's reviewed heading uses `service_title_and_description`;TOR uses
`service_context`. Existing context recognizes neither,while compact selection
shows IDs alone. Grading claims name rows but omit printed ratings. Four service
claims have33–48bound field names and lose diagnostic field maps at the32-name cap.
The saved multipart TOR result selects a not-stated instruction limitation instead
of the visible service claim. Keep these failure mechanisms separate from style
and empty-clarification behavior;do not silently change model decisions into RAG.

Add optional `DocumentTopic.source_labels` (complete reviewed label fields,max4)
and `claim_context` (bound short column values,max8per claim) only through
`topic_menu(..., routing_context=True)`. Default remains false;empty new fields
are omitted from serialization. Labels accept service_title,
service_title_and_description and service_context. Column hints accept grade,
descriptive_rating and percentage_equivalent;these are printed facts,not a grade
interpretation rule. Only source-present/nonblank,assigned,review-referenced chunk
fields qualify. Records with unresolved limits supply no new labels/column hints;
do not relax existing holds. Complete values only;no truncation or invented aliases.
Candidate field maps accept up to64names (actual max48);default keeps32.

Compact selection shows source_labels as untrusted context alongside current IDs.
Detailed routing shows these labels plus claim-index-bound column values;claims,
not-stated limits,cues and output selection limit8remain. A matched procedure uses
its visible service claim;not-stated limits are selected when that exact fact is
asked. Generic prompt guidance may clarify this distinction;no keyword routing.
Existing exact per-call transport guards remain the sole capacity boundary.

## Tasks and acceptance

1. [x] Add synthetic regressions in `tests/test_source_bound_routing_context.py`;
   observe missing opt-in/metadata behavior RED. Implement source-bound extraction
   in a focused runtime helper,contracts and opt-in topic_menu integration. Verify
   original register/chunks unchanged and default serialized topic/menu unchanged.
   Cover foreign/missing/held/blank/duplicate metadata,unselectable claims,complete
   legacy labels,grading columns and33–64name bindings. Commit verified increment.
2. [x] Add menu projection regressions RED;implement conditional compact labels
   and detailed per-claim values,leaving absent-metadata prompts unchanged. Ensure
   fields cannot move to another claim and limits/grammar remain intact. Preflight
   actual146-topic selector and every selected detailed replay with the existing
  8192/768/8profile. Overflow withholds;never truncate labels or source limits.
3. [x] Regenerate candidate topics locally from sealed465/register/catalogue,
   preserving all claims/IDs/source bytes/active pins. Replay the saved eight
   expanded/two paired small-menu questions once;record subject/claim/style/control
   separately and stage timings. No final benchmark or answer-quality claim.
   Stop on new capacity/source ambiguity or repeated unresolved quality mechanism;
   do not run a broad prompt sweep. Remaining structural/release gates stay held.
4. [x] Independent review,focused routing/runtime/topic suites,full project suite,
   docs/phase/diff checks;update compact progress/checkpoint/results and commit.

## Verification and evidence

SharedPython3.13 `-X utf8 -B -m pytest -q -p no:cacheprovider`;external basetemp
and ignored evidence under workspace/audit-evidence/p11-source-routing-context-20261027.
Run all test_routing_*.py,runtime research catalog,service context and new tests;
then `tests` at the final code tree. Existing unavailable lint tools disclosed.
No hosted writes,frontend changes,new source approvals or Phase12advancement.

## Current verification

Metadata RED17/GREEN69;projection RED3;combined routing/runtime source tests507pass.
Repaired two test-fixture assumptions (a not-stated-only topic needs another visible
claim;schema maxItems is min(8,offered facts)). Independent review found missing
source_limits incorrectly defaulted to[];focused regression RED1then explicit-key
fix. Final routing/runtime/topic-orchestration520tests pass14.27s.
Candidate146topics,32labelled services,18column-hinted grading claims. Original
465/register/catalogue hashes unchanged;default146serialized topics exactly equal.
Exact Gemma preflight:selector5768input;borrowing+TOR4729;grading4919;TOR4464,all fit.
Use of Field(exclude_if) preserves absent-metadata dumps;current Pydantic docs
[checked via Context7](https://github.com/pydantic/pydantic/blob/v2.13.4/docs/concepts/serialization.md).
Saved replay complete:grading3.0and borrowing/TOR claims corrected;follow-up quote
still rejected. Full frozen36d5f56suite6956passed/1595subtests,6skip/2xfail/6warnings,
2878.18s,exit0. Independent final51passed;docs/phase30passed/14subtests15.28s.
[Results](2026-10-27-source-bound-routing-context-results.md). New
[owner reply policy](2026-10-27-english-taglish-response-decision.md) recorded
separately;runtime migration remains the next approved unit.
