# Proposed task-first interpretation protocol

21 October 2026; Phase09; baseline d513768/product 0aaa074. Status: proposed,
not approved or implemented. One design decision, not another automatic prompt
tuning cycle. No inference, service operation, dependency or institutional change.

## Capability and evidence

Students need the complete requested documentary or curriculum answer in English,
Filipino and Taglish. The path remains LLM semantic interpretation, exact host
grounding, version-scoped structured/Prolog or RAG processing, then validated output.
This advances the interpretation, completeness and relevance holds in the
[exit map](2026-10-21-phase09-remaining-work-and-exit-map.md).

The four sealed [v13 observations](2026-10-21-catalog-separation-observation-results.md)
all emit route before operations and parts. The failed Taglish output commits to
Hybrid, describes two documentary parts, and invents a prerequisite operation for
slip S. The current decoder's Hybrid branch requires at least one operation.
That requirement explains why a chosen Hybrid branch cannot emit zero operations;
it does not explain why the model originally chose Hybrid. English/Filipino each
emit one whole-question part despite describing both location and fee in prose.

Inspected prompt.py, wire.py, transport.py and the four recorded call-1 payloads.
All four trace hashes match the sealed manifest; their schemas equal current
output_schema(). Decoder and observed output put route fourth and parts tenth.
The displayed schema is alphabetically serialized, whereas decoding uses the
ordered schema object. This display difference is not proof of an error or cause.
There is no demonstrated Prolog prerequisite-file defect in these observations.

## Alternatives and recommendation

| Choice | Tradeoff |
| --- | --- |
| Freeze the present candidate | Preserves known limits and guards; does not pass the held quality gate or close Phase09. |
| Task-first protocol in the existing interpreter (recommended) | One explicit early cardinality decision, then parts before actions/route; no new model call. Its quality benefit is an untested hypothesis. |
| Separate NLP/decomposition and routing calls, or replace the model | Larger architecture, latency and evaluation change; no demonstrated need for a specific replacement or approval for new assets. Not selected. |

The recommendation changes when the model commits to tasks versus executable
work, and adds one checkable cardinality commitment. It is not a new ledger,
source-reading analyzer, checker stage, example bank or keyword router. Existing
instructions already request separate details; repeating that instruction alone
is not the proposed mechanism. This design cannot guarantee semantic correctness.

## Precise proposed contract

Introduce model-facing bintanong-interpretation-wire-v2 with the existing fields
and one required strict integer part_count, 0..8. Decoder property order:

schema_version, language, audience, control, part_count, parts, intent, mentions,
claims, operations, route, ambiguities, reason.

Apply that order to the parent and every existing oneOf branch. Keep branch
constraints, enum values, field bounds and terminal controls otherwise unchanged.
RAG still forbids operations; Symbolic/Hybrid require supported-operation handling;
the host still rejects inconsistent route, needs or operation associations.
Do not add conditional-schema features or a combinatorial set of count branches.

Wire parsing checks part_count == len(parts); mismatch is invalid output and uses
only the existing shared format-repair allowance. It must not trim, create, merge
or split parts to make the number match. Existing uniqueness, literal occurrence,
target containment and association checks still apply. Terminal greeting/excluded
controls have count0/empty parts. Academic routes need1..8 parts. Clarify and
evidence_unavailable retain their existing ability to preserve known parts or
have none when interpretation is unresolved; no new mandatory guessed task.

Normalize only a valid v2 packet to existing Interpretation-v2: remove the wire-only
count and compute spans/indices exactly as today. Reject wire-v1 at this new model
boundary. No empty-plan compatibility default or change to normalized Integration,
CandidateAnswer, institutional contracts, operation registry, Prolog or rule data.
Count is untrusted planning metadata, not an independent completeness certificate.
A model can still declare1 and emit one coalesced part; that remains a quality fail.

Keep the complete reviewed catalog host-side and the current original/normalized
question, scoped context/facts and available_operations payload unchanged. The LLM
still explicitly chooses route and meaning. The host does not infer a route from
word matching or repair a semantic mistake by deleting an operation.

Version interpreter prompt v14. Align only its decision-order/schema-version text
and schema display with the protocol. Reorder the existing fictional example and
add its true count3; preserve its question, entities, claims, operations and three
parts. No extra examples or evaluation questions enter prompts. Serialize displayed
schemas/example in protocol order without changing canonical hashing helpers.
Preserve independent response-style inference. Combined remains explicit/unselected;
bump its nested-wire packet to v3 and prompt to v5 for compatibility, applying the
same nested protocol. No combined-profile promotion or second semantic classifier.

Generation's existing request-bound part ledger and support/relevance assessment
remain fallible and unchanged. Correct early parts can constrain later coverage,
but source support alone still cannot prove relevance or omitted-part detection.
This is why the two checker challenges below are required, not optional after a
narrow routing pass. Passing this experiment would not prove universal safeguards.

## Meaningful software checks

After approval, use focused TDD for count/parts mismatch and old-wire rejection,
actual Router/CombinedRouter normalization and unchanged scoped host binding,
and protocol order arriving at the transport boundary. Check parent/all branches,
displayed schema and example agree; verify constraints equal v13 except the new
wire version/count and order. Reuse existing unknown/conflict/nonasserted, privacy,
scope, deadline and call-budget regressions. No per-word prompt assertion bank,
new constructor matrix or repeat of the2200-test suite for this small change.

These tests establish contract and transport behavior, not better model reasoning.
One whole-change product review precedes actual inference. No test fixes or review
loops unrelated to an actionable defect.

## One proposed, finite actual-quality gate

Freeze exact inputs, independent labels, schemas/code/prompts, settings and
fixture-builder bytes before inference. Existing fictional questions and supplied
passage remain unchanged; none becomes an unseen validation family. Two stages
within one locked attempt; stage B runs only if stage A passes in full.

**A: the same four pipeline requests**, order d-en,d-fil,d-tl,h-en, from the sealed
[catalog protocol](2026-10-20-catalog-separation-quality-gate.md). Require4/4 on
the same response AND full-quality criteria: correct literal entities/facts/target,
two distinct requested parts, correct route/operations/style, complete relevant
supported prose, preserved actual scoped Janus result where required. Exact wire
order/count compliance is an additional protocol check, not a substitute for any
old criterion. Run each once, retaining all outcomes. No model-driven repair beyond
existing budgets; at most7 calls/request,28 total for A. A failure ends this attempt.

**B: two selected-checker component challenges**, one review inference each and no
repair or generation rerun. Both use full fictional passage "Students submit slip S
to Office K. The listed charge is 7 tokens." and the source-supported but incomplete
prepared draft "Submit slip S to Office K." with valid request-local references.

| Challenge | Exact existing question and prepared plan | Required result |
| --- | --- | --- |
| Relevance after a deliberately wrong interpretation | h-en: "Can I take ZX201 after failing ZX101, and where do I send slip S?" Use an intentionally incorrect ready-RAG proposal with two document parts/no operation or canonical decision. | Reviewer must not map the eligibility part to the filing claim; host ledger/release assessment stays unresolved. Relevant filing content alone cannot make this a complete answer. |
| Available requested detail omitted from draft | d-en: "Where do I send slip S, and what charge is listed?" Correctly declare separate location and charge parts. | Reviewer must leave charge unresolved; Office K does not satisfy the missing7-token detail even though the source contains it. |

Build B through existing public contracts/normalization/preparation helpers with
scripted proposals. Keep literal quotes and current request/release binding valid;
no mutation after validation or bypass of a failed host check. For relevance,
the first part deliberately quotes the actual eligibility request but labels it
document, simulating a schema-valid semantic misroute. That wrong label is test
input, not gold. Do not pass gold labels to the model. Use the selected
understanding.review_messages/review_schema/assess path, not detached parts.py,
guarded/covered profiles or a new checker. Reuse one actual RAG card/release fixture;
no embedding, database, service startup or institutional rule execution is needed.
If this fixture cannot pass current structural preparation, record B NOT RUN and
leave the gate unmet; do not weaken validation to force it through.

B measures actual selected-checker residual behavior on prepared evidence, not
router accuracy or a full pipeline. A and B have separate denominators and timing.
Gate requires A4/4 and B2/2; maximum30 physical model calls, zero rescue attempts.
A new wire count/order failure, unanswered part, wrong meaning, false-complete
checker verdict or operational failure blocks promotion. Retain every failed
output. No post-output relabelling, new prompt, seed, budget or model sweep.

Even6/6 permits only the remaining exit-map work, not Phase09 completion or
institutional activation. Four explicit if/kung variants remain held for the
unanswered conditional-answer decision; this proposal does not settle it.

## Limits, timing and next decision

Keep supplied Gemma/Bintu, CUDA18088, ctx8192,out768,temp0,seed0,cachefalse,
requested reasoningnone and120/120/120/180s budgets. No startup, asset copies,
downloads, training, dependencies, DB changes, push, merge or deployment.
The owner-corrected model root stays workspace/MODELS. Candidate remains inactive.

Part counting and splitting can still be wrong; moving route later can reduce or
increase errors. One format repair may be spent on count mismatch. Prompt/output
length and decode ordering can change latency in either direction. No quality,
causal mechanism or speed improvement is claimed before measurement. The latest
45.7-50.6s component results exclude real retrieval/Supabase/API/browser/startup;
the saved15-20s browser/conditional20-30s complex-Hybrid target remains proposed.
Accuracy has priority; no call, evidence or validation is removed for speed.

Consulted master3/11/13/14, thesis physical17-18/39-44 and actual routing PNG.
Undergraduate/read-only, unknown-versus-unmet, source-gap/privacy/release and
one-week accuracy-work boundaries remain. No scope discrepancy was found.
This proposal changes a model-facing protocol, not the evidence architecture.

Request approval of this protocol change and its one bounded gate only after the
fresh builder check. If approved, write the implementation plan next. If the
actual gate fails, stop and record the capability limit; another experiment
requires a separate concrete decision. No automatic continuation or Phase10.

One fresh read-only builder check: nothing important left. No material unanswered
planning question or product change resulted; no second check is needed. Root
retains responsibility for software and actual-quality evidence. Review/audit raw:
workspace/audit-evidence/p09-task-first-design-20261021/.

Root also prepared both B fixtures through current public IntegrationResult,
prepare, check_question, draft validation and selected review-message/schema
helpers. Both validate as ready RAG with two bound parts, the full original card,
no structured result and no gold label in the model payload. Prepared bytes and
hashes are saved for inspection; they are not checker outcomes or a runtime
quality pass. Five current inspected source hashes match the prior inference
binding; four interpretation trace hashes match its sealed delivery manifest.

Documentation verification:10passed0.77s;12 local links/snapshot caps pass;phase
state valid/active9,advancement refused. Fourteen raw evidence files sealed;
manifest SHA256603f2b04c002065c49799f2e31b021c8988e3f54ec409731b01f46159391245d.
These checks establish a reviewable proposal,not improved actual-model accuracy.
