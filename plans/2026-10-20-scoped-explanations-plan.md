# Scoped explanations implementation plan

20 October 2026; Phase09 active in the existing p09 worktree. Execute inline with
TDD and one independent final review. Spec: master13.2/14; standing accuracy-first
owner direction; [saved failures](2026-10-20-short-evidence-references-results.md).

**Capability:** correctly explain a supported prerequisite result and an applicable
documentary procedure without turning either into full enrollment approval.
**Evidence path:** unchanged LLM semantic routing/style, RAG/Prolog, integration,
host structured rendering and separately checked documentary prose.
**Exit advanced:** Phase09 decision scope, citation/support integrity and actual
multilingual validation. **Question:** does separating the two evidence bases
resolve the demonstrated scope errors without removing necessary information?

## Design

The current free-prose generator/checker receives both a canonical decision and
documents. Its flat evidence-ID list does not distinguish the basis of a decision
explanation from that of a procedure. Saved positive checker verdicts accept an
unstated enrollment purpose and a prerequisite-to-enrollment scope expansion.

Add a bounded `scoped` explanation profile, with `legacy` retained for controlled
comparison until quality selection. The host exclusively renders structured
decisions/conditions/dependencies from existing typed results. A ready pure
Symbolic answer contains no new generated claims; host validation still runs.
Unknown/held/conflicting results retain existing fallbacks and withheld conclusions.

RAG/Hybrid use a separate strict DocumentExplanation contract:release/language and
document-cited claims only. Bind all references to the actual documentary cards.
The host constructs any final decision field from its own result. The model sees
complete documentary sources and scoped subject/version context, but no decision,
operation predicate, rule cards or student completion facts from which it could
invent a documentary purpose. Full structured evidence stays in host assembly and
final citations; this is separation by authoring responsibility, not truncation.
The separate checker receives the same documentary basis and must establish every
action/purpose/condition from the cited text itself. Original question is data,
not source evidence. Preserve valid enrollment wording actually in documents.

No keyword ban or semantic router substitution. Free prose remains fallible; the
typed boundary alone does not prove entailment. Preserve complete passages/gaps,
canonical source identity, scope/unknown semantics and all applicable checks.
One repair/shared evidence/deadline; no unvalidated streaming or cache. No new
models/dependencies/DB mutations or institutional activation. Existing short IDs
remain separate and unselected; scoped profile initially uses canonical IDs only.
Do not combine two unverified candidate changes into a promotion claim.

## Tasks and interfaces

1. [ ] TDD `tests/test_generation_scope.py` against `Generator(...,
   explanation_profile='scoped')`: ready Symbolic outcomes/dependencies and all
   languages, no invented free decision claim, host provenance/conditions,
   no draft/check calls for host-only text; controls/deadlines unchanged.
2. [ ] TDD `scope.py`: DocumentExplanation, isolated document payload/schema,
   canonical AnswerDraft conversion, all-reference document binding and strict
   release/language/extra-field validation. Bind actual cited cards for checking;
   reject rule-only or mixed rule/document claims, missing documentary explanation,
   private references and negative/incomplete support verdicts. Preserve full text,
   subject/version context and canonical final decision. Cover repair/concurrency.
3. [ ] Wire generator/runtime setting/run metadata and developer CLI selection.
   Verify focused GREEN/legacy regressions and commit. Keep legacy default until
   actual quality gate passes; document any later selection with regression checks.
4. [ ] Reuse existing9fictional multilingual generation cases once under scoped
   profile. Inspect each claim/purpose/scope/style and compare fixed expectations;
   host-only Symbolic is not an LLM generation accuracy denominator. If quality
   passes, run existing3English real-service requests with resident encoder and
   record complete timing, calls and support separately. Stop if quality fails;
   no prompt/seed sweep. New institutional wordings are not introduced.
5. [ ] Independent whole-change review, explicit scoped regression gate, dated
   results and compact progress/checkpoint/index. Preserve residual issues. Phase09
   active; no Phase10 advancement inferred from a candidate or latency result.

## Verification

Existing readiness Python3.13 -B pytest -q -p no:cacheprovider, external basetemp/
TEMP/TMP under workspace/audit-evidence/p09-scoped-explanations-20261020/.
Saved failure traces supply the investigation; do not rerun the rejected experiment.
Current CUDA18088/model/profile reused. Record exact input/code/prompt/schema IDs.
No further usability literature sweep; reuse the completed latency assessment.

Ruling: owner's continuation authorizes this scoped fix. This does not claim a
universal semantic guarantee or permit an accuracy-for-speed trade. Host-only
structured answers remove a redundant paraphrase opportunity; documentary claims
still require the independent support check and human evaluation of residual errors.
