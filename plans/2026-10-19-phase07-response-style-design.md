# Phase07 response-style interpretation correction

Owner continuation resumes98aa714 within accepted Phase07 scope. Student capability:
match English, Filipino and Taglish conversation style without altering evidence routing.
Existing actual v6:15/15routes/meaning,10/15style (all Taglish labeled fil). Native
thinking only corrected one of two selected Taglish cases. Do not repeat those probes.

## Design and bounded question

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

Implementation uses existing Python/Pydantic/runtime only. No installs, weights,
institutional data, final answers, API or Phase08 work. New tracked tests remain synthetic.
Context scope pages17-18 and routing PNG refreshed; master12 permits shared-call logical
interpretation/routing stages. Prior architecture/scope decisions stay settled.
