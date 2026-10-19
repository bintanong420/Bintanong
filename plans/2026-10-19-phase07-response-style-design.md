# Phase07 response-style interpretation correction

Owner continuation resumes98aa714 within accepted Phase07 scope. Student capability:
match English, Filipino and Taglish conversation style without altering evidence routing.
Existing actual v6:15/15routes/meaning,10/15style (all Taglish labeled fil). Native
thinking only corrected one of two selected Taglish cases. Do not repeat those probes.

Current integration uses two independent calls to the same Bintu model; the later
separation section supersedes the original combined-call hypothesis below.

## Original combined-call hypothesis (retired)

Hypothesis:an ISO-like language label conflates Filipino language with Taglish response
style. Make style interpretation observable in the SAME Bintu structured call, before
route/action fields. Model quotes short literal English and Filipino conversational
fragments, then selects english_only/filipino/taglish/unknown. Course codes, acronyms
and quoted source titles alone do not establish English conversation. No host language
dictionary, word-ratio threshold, translation pipeline or second classifier is added.

Wire proposal v2 replaces language with a style object. Disjoint style schemas require
English evidence for english_only, Filipino evidence for filipino, both for taglish;
unknown remains available with both fragment arrays empty. Each known fragment is1-160characters,
at most four per language. Exact case-sensitive substring containment applies,
without normalization, trimming or offset/uniqueness requirements; mixed-word
substrings remain valid. Nonblank validation is separate from literal grounding.
Backend validates bounded nonblank fragments and literal
containment in ORIGINAL text, then maps the model-selected style losslessly to existing
en/fil/taglish/unknown metadata. This validates provenance/consistency, not linguistic
truth. Canonical Interpretation v1, scoped operations and evidence guards remain stable.
Wrong style evidence never causes RAG substitution or symbolic dispatch.

First test the concrete wire design on five EXISTING synthetic questions:
procedure-en/procedure-fil/procedure-taglish/prerequisite-taglish/greeting-taglish.
Full existing routing prompt/context/catalog/guards, default non-thinking inference.
This is an interface hypothesis check, not another wording/temperature sweep. Retain
raw wire output and actual prompt/schema/model identities; no gold enters the call.
If it resolves those labels without route/meaning loss, implement strict decoding and
observable evidence with focused RED/GREEN, review and full15-case evaluation. If not,
record the concrete failure and do not claim style handling complete.

## Implementation contract

decode_model_proposal(data) -> (canonical Interpretation, StyleEvidence).
Schema/type/count failures get the existing one format repair. Literal-style grounding
fails without semantic retry, before any dispatch. Existing unique quote anchoring for
course claims/mentions stays unchanged. Extra/legacy/conflicting wire keys are rejected;
no v1 model-output fallback can bypass required style evidence. Canonical-domain v1 is
unchanged for trusted internal use. Wire schema shares its style definition by ref to
avoid multiplying token overhead across routing branches. Enforce the real context budget.

Builder check completed:implementable in accepted scope. Adopt its precise grounding,
Python/schema parity, immutable result observability and failure-metadata points.
Unknown style preserves current precedence:explicit excluded audience still returns
unsupported_scope; an in-scope unknown style clarifies. On rejected style grounding,
accepted response_style is unknown; never propagate the rejected style as trusted.

## Verified component and actual prototype

New style-contract tests RED32(module absent), then GREEN75across style/contracts/
router,2.21s,exit0. style-contract-red.log/style-contract-green.log. Component is
not integrated into Router yet. Decoder-schema/strict-Python count combinations are
tested independently; Python additionally rejects whitespace-only fragments. Literal
grounding remains a separate host check. Canonical v1 is not changed.

Fixed five-case prototype:style5/5,route/effective4/5,claim/operation collections5/5.
All three procedure variants and mixed greeting work. Prerequisite-taglish incorrectly
selected Hybrid while its reason describes ONLY a prerequisite check. This is a
route regression, not a pass hidden by a guard. style-evidence-prototype/ preserves
all raw wire captures/report/identities; no production adoption claim.

Focused correction:clarify existing route semantics:an eligibility/prerequisite
check alone stays Symbolic; explaining its symbolic result alone does not require
RAG. Hybrid still handles a question needing a document explanation/procedure as
well. A fixed two-case check reuses prerequisite-taglish and affected-procedure-
taglish to test BOTH sides before integration/full15evaluation. No host route
override or expected-label change; not a temperature/wording sweep.

## Revised separation after observed interference

The pair gives2/2proposed routes/styles but only1/2effective outcomes:the Hybrid
case adds an unrequested eligibility operation to list_affected_courses. Preserve
that failed combined-wire experiment; do not adopt it or add another wording patch.

Builder implementation choice:use two independently observable calls to the SAME
Bintu model, as master12.1permits. Keep verified routing prompt/schema/messages
unchanged (v6,canonical interpretation-v1). A separate style-only structured call
receives original_text and cannot emit routes, audiences, operations or policy.
Its response is versioned bintanong-response-style-v1 wrapping StyleEvidence.
This separates language-style output from routing-token generation, not a new
trained classifier. The combined wire-v2 adapter is retired before integration.

Run routing interpretation first, then style; neither executes an evidence tool.
After grounding, project ONLY the model-selected style into canonical language
metadata for validation; retain the original routing proposal separately. Return
immutable style evidence alongside accepted response_style/query hints. Unknown
style clarifies in-scope requests; excluded audiences still take precedence.
Style/schema failures share ONE format-repair allowance with routing:normal2calls,
maximum3total. Grounding failures never retry semantically and expose accepted
style unknown. Count routing/style calls and repairs explicitly in evaluation.

Reuse already completed routing captures ONLY when exact prompts/messages/schema
and generation configuration match. Fresh style calls plus current deterministic
composition can validate the same15cases without repeating15identical routing
inferences. Report reuse provenance; this is not a live latency benchmark. Also
verify fresh full two-stage execution on selected cases before closure. No new
question wording, scope/registry/source change or Phase08 work.

Revised-stage TDD:RED35failed/18passed, then GREEN127across all six routing suites,
1.34s,exit0. Four stale test-helper references were corrected before final GREEN;
no change to the production routing prompt/schema. style-stages-red.log,
style-stages-green.log and style-stages-final-green.log retain exact results.
Shared-budget, grounding failure, unknown precedence, style-only input privacy and
independent accepted style versus original routing-language metadata are covered.
The abandoned combined-wire projection/decoder was removed; no legacy style-output
fallback is introduced. Independent stage review found no P1/P2 and reran127tests,
1.30s. Actual full15-case composition keeps routes/entities/claims/operations15/15
and five consistent families, but style13/15. Procedure and excluded Taglish outputs
quote the entire mixed utterance as Filipino, leaving English fragments empty.
All15 routing captures match exactly;15style calls are fresh,30logical calls,
zero repairs. No end-to-end latency claim. style-stages-full/ retains raw evidence.

Promptv2 addresses that observed span-selection failure:inspect embedded phrases,
quote language-specific spans, and do not equate Filipino sentence frame with an
unmixed utterance. No host vocabulary or semantic override. RED is the two actual
failed development cases above. Fixed check:those same two plus procedure English,
procedure Filipino and Taglish greeting controls. Only a passing bounded check
permits the remaining full-case evaluation; no new gold or parameter sweep.
The five-case check returned style3/5, with both same errors unchanged; do not
adopt promptv2 or repeat equivalent wording changes. Raw:style-stages-v2-bounded/.

The next bounded test addresses a different mechanism:decoder field order. Both
failures first emit an empty English array, which forces the later label to
filipino under the disjoint schema. Move preferred_response_style before both
evidence arrays and ask the model to choose it from the complete utterance before
supporting it with quotes. This is a causal hypothesis, not an established root
cause. Keep all schema/count/grounding/repair rules and routing inputs unchanged.
Same fixed five cases; no new gold, host classification or generation settings.
Promptv3/schema-order candidate passes127routing tests,3.38s. Actual fixed check
passes5/5routes,entities,claims,operations and styles; zero repairs. Both previously
failed Taglish cases now choose taglish and quote an actual English fragment.
Raw:style-stages-label-first/, including the exact uncommitted product.patch over
ac00ac9. This supports adopting the combined prompt/order change; it is not an
isolated causal proof that schema order alone explains the previous failures.
Broad24-file gate for the stage implementation:1555passed/11subtests,179.81s,
exit0 (style-stages-regressions.log). Two inherited Docling failures still apply.

Implementation uses existing Python/Pydantic/runtime only. No installs, weights,
institutional data, final answers, API or Phase08 work. New tracked tests remain synthetic.
Context scope pages17-18 and routing PNG refreshed; master12 permits shared-call logical
interpretation/routing stages. Prior architecture/scope decisions stay settled.
