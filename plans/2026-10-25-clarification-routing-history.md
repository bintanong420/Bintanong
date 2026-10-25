# Grade clarification: frontend/API trace and backend reproduction

Owner requires investigation before changing the backend; confirmed that the English
answers were selected in the popup and submitted as a new message. No product code,
database contents, model configuration or release pin was changed in this investigation.

## Questions and findings

1. Does the client lose an answer, scope or session? No in the exercised current path.
   Actual clarificationReply -> installed AI SDK transport -> actual proxy preserves
   the original question, both selected statements, scope and synthetic session cookie.
   Actual ChatTurns preserves text/scope and passes stored course context to its pipeline.
   The running3215 public bundle serves the current formatter without old dialog headings.
2. Is a new message itself wrong? No: POST /chat intentionally consumes only the latest
   user text, with session identifiers for context. The popup resubmits the question with
   answers, as required by that contract. Separately typed grade-only messages do not
   retain the pending question or become persistent facts; that is a separate limitation.
3. Can the failure occur without the frontend? Yes: existing load_research_app composition,
   active19-chunk/39-curriculum release, seven document topics, real model, real Prolog,
   and an isolated in-memory session reproduce it through ChatTurns/ResearchPipeline.

## Full pipeline observation

| Turn | Result |
| --- | --- |
| Original CC5 prerequisite question | Symbolic/list_missing_prerequisites; returns printed prerequisite list and two actual completion questions. Stores CC5 course context. |
| Current popup reply | Both supplied completion statements become claims, but the model also creates a second requested part with evidence_need=unknown. |
| Owner's English IM wording plus the two synthetic completion statements | Same invented unknown part and generic clarification, with the previous CC5 context present. |

For both follow-ups, normalization succeeds. validation.py returns unknown_requirement
(lines259–261) with control=clarify and missing_facts=(). The orchestrator exits before
Prolog; the renderer emits the generic clarification sentence. The client displays that
canonical response. This is different from the earlier router-only invalid_reference
probe, which lacked the active release's topic menu. That component observation remains
valid but is not the exact full-pipeline cause. A new reference-repair hint would not
address this reproduced path: there is no normalization exception to trigger its retry.

Deterministic replay asserts unknown_requirement for both captured outputs. Removing
only the invented unknown part in a counterfactual model packet changes both routing
results to validated while preserving both claims unchanged. No runtime repair was added.
The --expect-ready check deliberately fails, preserving a fast RED reproduction.

## History and ownership

- 5b483ad (20Oct): introduced grounded requested parts and unknown_requirement handling.
- 71be2fd (20Oct): introduced quote/operation-target containment checks.
- 8060c7b (21Oct): made the model declare counted question parts before actions.
- c8a25f5 (21Oct): added specific reference-repair hints and persistent-reference clarification.
- Guided frontend68b70e1 (24Oct) added question headings to its follow-up, a real client
  defect removed by af119ad. The generic invented details dialog was also removed there.
- Router/prompt/wire/validation, API chat/research_pipeline and generation renderer files
  at HEADaf119ad are byte-identical to backend357aa80. The merge did not alter this path.
  Historical wire replay from frontend1525dc6 and HEAD rejects the earlier captured
  invalid-target packets identically. This does not date the first model misinterpretation.

## Verification and boundaries

17 clarification/transport/proxy tests and47 chat/context/follow-up/reference tests PASS.
Full-pipeline model observations above used synthetic premises, not official grades.
Direct-router checks also found not-yet-passed misclassified as not_enrolled; full-path
packets use failed. Claim-state semantics remain unresolved; no correction is inferred.
The direct-router English IM case validated without topics but failed with the full menu,
demonstrating why component probes cannot stand in for the actual research composition.
No complete historical deployment bisect or exact first-bad-model commit is claimed.
Orca automation reports no tabs; the owner's browser memory/network was not inspected.
Current public bundle and isolated transport/API seams were checked instead.

Evidence root: C:/Coding-projects/bintanong_workspace/audit-evidence/p11-20261025/clarification-loop/.
Scripts/results: trace_client_api.mjs/client-api-boundary.json; trace_api_context.py/
api-context-boundary.json; check_served_client.py/served-client.json;
trace_live_context.py/live-context-results.json; trace_full_pipeline.py/
full-pipeline-results.json and full-*-captured.json; replay_full_routing.py/
full-routing-replay.json; replay_history.py/history-replay.json. Replay commands use
py -3.13 -X utf8 -B and need no model or credentials after capture.

Next: review these findings before choosing a correction. Backend remains unchanged;
the previously proposed reference-repair hint is insufficient for the observed full path.
