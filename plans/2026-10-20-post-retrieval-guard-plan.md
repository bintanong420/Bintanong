# Post-retrieval decision guard implementation plan

20 October 2026; Phase09, existing p09 worktree; baseline4022711. Execute inline
using executing-plans/TDD and one independent final whole-change review.

**Goal:** withhold a structured answer when the initial RAG route omitted the
required structured check. **Spec:** master12.4/13/14, thesis17-18/39-44 and routing
PNG; undergraduate/source-gap policies and owner's accuracy-first direction.
**Capability:** avoid unsupported student eligibility, dependency or structured
course-fact conclusions after retrieval. **Evidence path:** existing semantic
router, complete retrieved documentary cards, explicit LLM guard, host withholding
or unchanged documentary generation/checking. **Exit:** Phase09 decision scope.
**Question:** can one bounded assessment catch the omitted structured requirement
without blocking ordinary documented services or inferring missing conditions?

## Design and constraints

Add an explicit post-retrieval LLM assessment for ready scoped-profile RAG only.
It sees the original question and complete documentary cards as untrusted data.
Its strict release-bound result is document_only, structured_required or uncertain.
Only document_only proceeds to existing documentary drafting/support checking.
Other results, malformed output or wrong release yield a fixed localized withheld
response, no generated claims or conclusion. Timeout/tool failure remains temporary
unavailability. No assessment repair or hidden reroute; existing request/generation
deadline includes the guard. Symbolic/Hybrid already have typed structured results;
nonready controls and explicit legacy developer profile retain their behavior.

Record one guard observation with host-measured seconds and result in the candidate
answer; evaluation reports include guard prompt hash and distinguish guard-only
from host-only outputs. Historical missing observation remains null. The semantic
assessment is fallible, not an accuracy guarantee. No keyword routing, new rules,
source truncation, cache, training, downloads, dependencies, DB changes or activation.
All private references/source holds/version and unknown semantics remain in force.

## Tasks, interfaces and verification

1. [x] Write focused tests in tests/test_generation_guard.py; observe RED.
   Create generation/guard.py for strict Assessment, schema, full-evidence prompt
   and prompt digest. Add host GuardObservation in generation/contracts.py;
   optional CandidateAnswer.decision_guard retains historical parsing. Integrate
   Generator once before scoped RAG drafting. Update render/validation for fixed
   withheld response and host checks. Cover all languages, required/uncertain,
   malformed/extra/duplicate/wrong-release output, cancellation/errors/deadline,
   no extra attempts/rerouting, full source/privacy boundaries, pass-through repairs,
   concurrent isolation and non-RAG/control/legacy bypass. Observe GREEN.
2. [x] Update evaluation metadata/mode and developer guide; adjust existing scoped
   RAG mocks for explicit guard call. Verify focused plus relevant regressions and
   commit the cohesive implementation. Record failures and commands honestly.
3. [x] Once only, reuse existing nine fictional multilingual generation questions
   (RAG documents, Symbolic and Hybrid) and force the existing Symbolic eligibility
   questions onto document-only prepared RAG evidence to test withholding. These
   are synthetic software probes, not new institutional benchmark wording. Review
   every result before reporting latency; no seed/prompt sweep. If quality fails,
   record the failure and leave selection/Phase09 exit unresolved.
   After a passing prepared check, run the existing English actual-service RAG
   request once through resident encoder/local Supabase to verify composition and
   outer/inner/guard timing. Reuse the existing startup/readiness timer;do not rerun
   unchanged actual-service Symbolic/Hybrid paths or claim browser/full-cold time.
4. [x] Independent whole-change review; TDD any important findings in one pass,
   explicit regression gate, dated results and compact progress/checkpoint pointers.
   Preserve raw workspace/audit-evidence/p09-post-retrieval-guard-20261020 receipts.
   No Phase10 advancement, push, merge or deployment.

Existing Python3.13 readiness interpreter, -B pytest -q -p no:cacheprovider;
external TEMP/TMP/basetemp. Reuse resident CUDA18088 and owner workspace/MODELS.
Report guard time inside generation/outer pipeline time without double counting;
reuse completed response-time research and measurement contract. Full-system cold,
browser/API/queue/hosted timings remain unmeasured and in their applicable phases.

## Review focus

- Model output/injection cannot manufacture an approved decision or bypass a check.
- Ambiguous/missing student facts require withholding, not a negative conclusion.
- Legitimate documented services stay answerable; a course word alone is no rule.
- Guard failure/deadline cannot fall through to drafting or consume a repair.
- Reports cannot label guard inference as host-only or hide its timing/call cost.

## Observed failure and one correction boundary

Initial12case run completed at48307b8:original9appropriate;forced EN withheld,
FIL incorrectly document_only/answered unrelated FormQ,Taglish uncertain/withheld.
Independent reviewer confirms one P2,no fabricated eligibility observed. Requested
reporting of an allegedly existing/supplied check needs explicit handling:the
question is not evidence a check occurred. Full-runtime dependent observation held.

One bounded correction is authorized by the existing accuracy-first task: add this
semantic distinction to the guard instructions,without copying evaluation wording,
keywords,routing substitution,new fields or changed source. Write an actual-model
regression against saved FIL failure and observe RED;then rerun ONLY unchanged
3forced questions plus3ordinaryRAG controls once under the corrected prompt.
Store new source/prompt/input/output receipts separately in raw correction/.
If this gate fails,leave the safeguard/Phase09 exit unresolved;no further sweep.
This is the single reviewer-fix pass. Re-grade and report the finding honestly.

Correction gate failed:EN withheld,FIL tool_error at768completion tokens,Taglish
document_only/answered unrelated service. Saved-output regression2failed/4passed.
No further model observation;the full-runtime quality prerequisite did not pass.
Reject the correction and restore original instructions for reproducibility.
Retain the failed guard only as explicit `explanation_profile='guarded'`,with
canonical references. Selected default scoped/canonical/separate remains unchanged.
Selection isolation RED2/GREEN209tests3.75s;CLI help wrapping failure corrected
without changing behavior. This is quarantine of a known failure,not a semantic fix.

Final ruling:reviewer P2 remains open in the explicit experiment;do not promote it
or close Phase09. Cost:misrouted structured requests remain an unmet safeguard in
the selected pipeline. No faster inaccurate route is approved. Next work must
reassess evidence/task coverage before another generation/routing experiment.

Delivery:isolated productd2d1131;explicit53-selection gate2048passed/66subtests
89.43s,exit0;155raw files sealed. [Results](2026-10-20-post-retrieval-guard-results.md)
preserves both failed quality gates and the open P2. Bounded experiment complete;
the required capability and Phase09 exit remain unfinished. No further inference.
