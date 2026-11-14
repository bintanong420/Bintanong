# Service routing and completeness refinement

Baseline7f957c1. Existing Phase11 requirements, source-gap/service-association policies
and owner simple-question requirement apply. No new product scope/source reading.
Keep expanded release inactive; do not repeat verified fraud/checker work.

Student capability: explain the reviewed pre-enrollment requirements and visible
steps, preserving the Step3 cutoff and printed-total discrepancy. Distinguish
evaluation of grades for enrollment from grade-completion deadlines. Evidence path:
reviewed release title/description -> LLM topic selection -> existing retrieval ->
per-part generation -> complete-source coverage review and own-citation support.

Observed causes from saved traces/code: router menu has claim names but omits the
reviewed service title/description; the generator can omit steps, and confirmation
currently sees only cited sources, hiding omitted available rows from its coverage
judgment. This is not evidence of missing extraction/retrieval; reuse sealed sources.

1. RED synthetic runtime/router tests: release topic context must come only from
   its assigned, reviewed visible service_title/description field references and
   reviewed chunk membership. Missing/unreviewed/held fields, another topic or old
   unassigned chunks must not supply context. Expose short bound context only when
   present; menus without it retain prior display/schema and LLM topic choice.
2. Add optional bounded source_context to DocumentTopic; derive it in research.py
   and display as data in the menu. No new claim, route shortcut or source activation.
3. RED completeness regression: confirmation must see uncited documentary records
   as coverage context once, while each claim's support remains limited to its own
   cited sources. Rules/private/student facts stay outside this model payload.
   Exercise a partial procedure draft accepted only when the missing step is hidden.
4. Add available_sources to confirmation payload; concise generation/confirmation
   guidance for all requested procedure steps, conditions, progression and gaps.
   Keep schema/call/repair budgets, per-part identities and support scope unchanged.
5. Focused runtime/routing/generation/orchestration regressions; independent scoped
   review; one three-language pre-enrollment live battery using existing questions
   against the inactive local package. Capture raw packets/retrieval/drafts/review
   to distinguish routing, evidence and answer failures. No sweep; failures remain
   visible and may require a bounded next step. No weakening validation to answer.
6. Commit verified increment; full tests/ suite on frozen code, evidence seal/link/
   whitespace/phase validation; compact current snapshots. No dependency/schema/
   source/package/pin/frontend changes. Full suite not a semantic accuracy claim.

Review focus: source field approval/membership; data/instruction separation; claim
support cannot borrow uncited evidence; unrelated part sources cannot answer the
part; existing malformed/precedence/partial-answer guards; prompt/context budgets.
Use shared Python3.13 -X utf8 -B -m pytest -q -p no:cacheprovider, external basetemp
under workspace audit-evidence/p11-service-refinement-20261025. No installed linter.
Master3/11/13/14, thesis scope physical17-18 and routing PNG/39-44 already consulted
in this continued session. Standing unknown-versus-unmet/advisory/privacy rules apply.

## Bounded correction after the first live battery

First3-case battery: English selects the right service and includes all steps,
but blurs one client/agency-office association; Filipino/Taglish still omit steps
and receive false positive completeness verdicts. No live gate pass. Additional
source context fits, but a model-only completeness judgment is insufficient.

Carry exact reviewed service-record requirements from existing SourceAwareEvidencePolicy
assessment.source_fields through RetrievalAdapter -> optional DocumentResult coverage
-> merged documents -> PreparedEvidence -> per-part draft validation. Derive only
records with reviewed client_step fields, bound to the original subject/claim and
emitted chunk IDs. No topic keywords, hardcoded service/penalty facts or new source
reading. Omit absent coverage from serialization so legacy digests remain valid.

Add RED tests for adapter projection/validation, multi-topic merging and per-part
enforcement. When an answered part omits a required record's citation, reuse the
existing single answer repair with explicit required evidence IDs; if repeated,
abstain. Unavailable/independent/canonical parts keep existing semantics. This is
a record-citation coverage floor, not proof of semantic completeness or associations.
One further3-case observation is justified only after this new host boundary is
verified; no prompt-only retry/sweep. Preserve earlier outputs and all quality failures.

Execution so far: context/completeness inputa2a2f19 verified944 broad/14 independent
focused. First live battery failed as recorded above. Record-transfer RED5/4 includes
missing optional contract support; transfer then passed7 with host RED2. Final-bypass
test also failed (RED3/7), then host/final checks corrected. Broad1121 passed29.74s;
new-boundary independent review clean/10 focused passed0.95s. Full suite follows frozen
code and the single new3-case live observation; no source/package/pin change.

The second observation also FAILED semantic quality: English cited all four steps
but invented a continuation to the Step3 cutoff and blended client/agency offices;
Filipino drafts reordered Steps1/2 and were rejected for formal wording; Taglish
ended tool_error. Citation coverage is not a semantic guarantee. No further live
battery in this increment; retain raw traces for the next source-association fix.

The Filipino rejection exposed an older hard word ban conflicting with the settled
25Oct owner decision (owner-decisions-ledger: formality is a preference, no dedicated
guard). Regression-first correction: three formal-word cases RED3/40, then remove
the word ban while retaining the Filipino-function-word floor and ordinary support
review. Prompt expresses a preference. Broad1121 passed29.77s. No new requirement
or guard relaxation for evidence; the earlier21Oct wording is superseded here.
