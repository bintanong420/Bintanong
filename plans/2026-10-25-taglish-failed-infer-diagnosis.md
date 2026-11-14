# One-case Taglish failed-infer diagnosis

Student capability: answer a supported requirements-and-steps question without an
unexplained temporarily-unavailable result. Evidence path: existing semantic router
-> reviewed inactive source retrieval -> per-part generation/validation. Phase11
simple-query/quality exit remains open. Unresolved question: did the previously
observed tool_error mean output truncation, timeout or another transport failure?

Saved6b47449 packets omit failed inference because logging occurred only after a
successful return. Server768-token observation is suggestive, not conclusive.
One instrumented attempt of the same Taglish question is authorized technical
diagnosis under the owner's autonomous-work direction: write input/schema before
infer, record fixed RuntimeFailure.code on exception, retain successful raw packets.
No retries, prompt/model/default changes, extra checker experiment or output-budget
increase. One case, ordinary router/generator repair caps only, then stop and report.
Use explicit inactive local80-record package; no hosted reads/writes or activation.

Current production/test tree593de5f passed full6749 +1595 subtests,6skip2xfail6warnings,
1297.74s,exit0. No full-suite rerun for this ignored harness/logging-only diagnosis.
No change to product behavior; validation is packet capture and actual failure code.
Raw evidence stays ignored in workspace/audit-evidence/p11-taglish-infer-20261025.
Source-quotation presentation choice remains pending; diagnostic output is not an
accepted language-quality result. If the error does not reproduce, report that
limit and stop; do not try equivalent replays without a new bounded question.

The case reproduced temporarily_unavailable/tool_error at PartExplanation66.957s.
Instrumentation defect: RuntimeFailure has no .code attribute; the logger stored
unclassified instead of its fixed args[0] reason. Input/schema were captured before
infer, so the exact failed request is available. One extra generation-only replay
is justified to correct that measurement error: same saved messages/schema/768 cap,
capture the raw completion response before the transport raises, and read args[0].
No repeated routing/retrieval, parameter changes or further retry. This is an
explicit one-call extension to the original bound, not a successful first capture.

Result: exact generation-only replay37.321s, one completion, RuntimeFailure
truncated_output; raw finish_reason=length, completion_tokens768, prompt_tokens3636.
The output ends inside its last canonical citation ID. No partial answer rescued.
Counterfactual tokenizer-only replacement of four COMPLETE IDs:766->539 prefix
tokens (227 saved); prose/partial final ID unchanged. This is not an answer/latency
quality result. No further completions in this diagnosis. Production/tests unchanged.

## Bounded implementation after diagnosis

Reuse the20Oct approved short-reference design in the current per-part interface.
Default stays canonical; add opt-in reference_profile=short for parts only. Other
scoped/guarded/covered restrictions stay. No output cap/model/source/default change.

1. RED tests for strict short per-part wire contracts, full source/question/coverage
   preservation, canonical restoration before cutoff/fraud/coverage/style checks,
   ordinary review with full provenance, repair/unknown/duplicate/private/rule-ref
   rejection, request isolation and runtime settings. Do not replace prose strings.
2. part_answers.py owns typed short slots/schema and draft-message ID encoding;
   use existing EvidenceReferences request-local labels; decode to PartExplanation
   before to_draft. Generator/application allow only this new opt-in composition.
   Checker messages, ledger identities and final citations remain canonical.
3. Focused/broad tests, scoped independent review, verified commit; one full suite
   on frozen final code. No further model completion this increment; default
   selection needs separately bounded actual-model quality evidence. No activation.
4. Save exact evidence and compact handoff; presentation answer still pending.

Implementation verification: initial9 RED at the unsupported constructor gate;
first GREEN8/1 exposed a fixture question-binding mismatch, repaired without
weakening that guard. Broad752 passed24.50s. Added unavailable-slot placeholder
regression RED1/13; fixed decoding to retain canonical ignore-placeholder semantics.
Final selected broad753 passed; independent scoped review no blockers/14 passed1.12s.
Strict private/rule/unknown/duplicate refs, repair, request binding/isolation, source
content/coverage preservation and cutoff integration verified. Default canonical;
no further completions or actual-model quality claim for short per-part composition.
