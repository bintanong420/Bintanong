# Phase07 functionality audit against the runtime diagram

20October2026. Owner asks whether Phase07 skipped functionality. Checked master12,
the actual routing PNG, Phase07 plan/handoff/closeout, routing implementation and
its tests. The question is about completeness, not permission to start Phase10.

| Requirement | Delivered path and limit |
| --- | --- |
| Original query and minimal cleanup | contracts.prepare_query validates sizes/Unicode and preserves original text; NFC/whitespace cleanup only. |
| Bintu tokenization before routing | LlamaTransport calls the model's apply-template/tokenize endpoints and checks actual context headroom, including bounded repair. SEA-LION tokenization is separate in QueryEncoder when retrieval runs. |
| Language, intent and entities | Router asks the actual LLM for strict Interpretation; a second call independently interprets response style. Host checks literal quoted spans and reviewed, exact, curriculum-scoped aliases. |
| Negation, time and fact meaning | Original wording is retained in the LLM prompt; claims distinguish asserted/hypothetical/reported states. NormalizedQuery carries negation/time annotations. Literal grounding/annotations do not prove semantic understanding; the LLM can still misread the question. |
| LLM adaptive route | RAG/Symbolic/Hybrid remains selected by the model with supported capability descriptions. Host validates scope, signatures and inputs; it does not replace semantic routing with keyword classification. |
| Missing/ambiguous/unsupported requests | Clarification, unsupported_scope and evidence_unavailable controls; unresolved editions, unknown audiences, unsupported operations and conflicting facts withhold dispatch. Multiple requested operations currently need clarification, rather than silently dropping one. |
| Safe Prolog dispatch data | Only three reviewed operation families, fixed typed arguments and scoped identities. Actual Janus execution belongs to Phase06/08; routing alone does not execute or authorize institutional rules. |
| Request/session consistency | RequestContext rejects foreign-session/mismatched-scope facts. Establishing authenticated ownership/expiry is the caller's later session boundary, not a delivered login feature. |
| Preferred final language | Phase07 returns response_style metadata. Phase09 generation consumes it; correct final language still needs its own evaluation. |

No missing core router code path was identified in this audit. This does **not**
mean all intended question types, language quality or later-phase functionality
are finished. In particular:

- The retained synthetic evaluation has15/15fresh route/effective results, but
  only13/15exact reused response-style labels. Two Taglish cases still select
  Filipino. That is a known requirement failure, not successful functionality.
- These are five fictional families, not the accepted75institutional variants,
  a final evaluation or language-wide accuracy. Host quote anchoring is observable
  and is not evidence of perfect raw spans/negation interpretation.
- Arbitrary multi-operation plans, extra policy-rule families and exact structured
  course-fact operations are not registered by this initial router. The current
  three operations are prerequisite eligibility, missing prerequisites and affected
  courses; unknown capability coverage cannot become an answer by similarity.
- Private PDF/photo extraction, authenticated session lifecycle, student HTTP/UI
  and institutional source/release loading are separate undelivered boundaries.
  The gap confirmed by the [architecture audit](2026-10-20-runtime-architecture-implementation-audit.md)
  is the missing demonstrated real-service composition, now being built in p09.

Preserve the frozen routing/style prompts and their disclosed failures under the
[standing decision](2026-10-19-prompt-engineering-and-validation-decision.md).
This audit does not justify another open-ended prompt sweep or reinterpret the
formal offline handoff as a fully usable student system.
