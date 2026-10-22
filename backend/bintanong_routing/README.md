# Offline multilingual LLM routing

This Phase07 module interprets English, Filipino and Taglish with a supplied local
LLM. It returns the routing proposal, independently grounded style evidence and a
separately validated shared RoutingDecision. Two calls use the SAME Bintu model:
routing and style interpretation remain separate; style receives only the
original question and cannot emit routes, audiences, operations or policy.
It does not retrieve documents, execute Prolog, generate student answers, publish an
API or activate institutional data. The historical API BintuClient/Direct adapter
remains separate and cannot dispatch through this module.

`await Router(transport, ...).route(text, RequestContext(...))` preserves original
text and minimally normalizes it. Interpretation is strict JSON with grounded
program/curriculum/course mentions, claims and proposed operations. Course aliases
resolve only against explicitly injected reviewed records and known curriculum;
explicit program/curriculum mentions may resolve scope through their own aliases.
There is no fuzzy equivalence or curriculum inference from a course code.
The full reviewed alias catalog stays in the host resolver after literal extraction;
it is not included in either router profile's model-visible payload. Scope/facts
and available operation names retain their existing model-input boundaries.

The model-facing bintanong-interpretation-wire-v2 uses {text,occurrence} quotes.
The model declares part_count and parts before operations/route. Count must match
the list;the host never adds or deletes parts to make it match. This count remains
untrusted and cannot prove semantic completeness. Wire-v1 packets are rejected.
Occurrences are zero-based exact matches in original text,including overlapping
matches. Operations and claims reference the identical quoted course mention;
the model supplies neither character offsets nor numeric course-reference indices.
wire.normalize_interpretation constructs host-owned spans and indices,then existing
Interpretation v2/alias/scope/mode/dispatch validation runs unchanged. Missing,
invented,duplicate or uncontained references reject within the existing shared
format-repair budget. There is no legacy model-packet fallback or fuzzy/first-match
guess. Internal Python spans retain exclusive ends;offset_corrections is zero
because these spans are constructed,not repaired. No text/state/meaning is rewritten.
Claim spans must include the corresponding course mention. These
checks establish textual provenance, not semantic truth: the LLM can still misread
negation or attach the wrong meaning. Actual model evaluation must measure that.
ScopedFact is a trusted application's request-local user assertion, not an official
grade record. The application must establish session ownership before constructing
RequestContext; this module checks consistency, not authentication or session expiry.
Session/request/fact identifiers stay host-side; the model sees only applicable
program/curriculum scope and course-state assertions. Evaluation scenario names
must never be encoded into model-visible request identifiers.
No transcript completeness, pass threshold or equivalence rule is invented.

Only the three Phase06 operation names are recognized, with fixed course_id and
curriculum_id bound inputs validated against CapabilityRegistry. EMPTY_REGISTRY
remains the default. Nonempty synthetic registry injection requires explicit
synthetic=True; institutional execution remains held. A dispatchable result is
validated routing data for a future executor, not permission to publish a decision.
documents_available defaults false. Source release authorization belongs to the
future evidence-loading layer, not to a model assertion or injected alias label.

RAG/Hybrid/Symbolic specify evidence needs. Clarification, greeting, excluded scope
and unavailable evidence are controls. Missing curriculum, ambiguous aliases,
compound operations, conflicting assertions and nonasserted hypothetical/reported
facts withhold dispatch. Missing unmentioned grades remain unknown; no full
transcript is required simply to name a supported operation.

Decoder branches match existing host audience precedence: excluded/unrelated
audiences require unsupported_scope with no operations/claims; unknown requires
clarify and can preserve compound details. Bintu still selects the audience from
the question. Host checks retain contradictory proposals from nonconforming
transports for inspection and withhold dispatch without a semantic retry.

The router-v9 prompt clarifies that context helps interpret requested work without
adding tasks. Social-only greetings use their control; explaining a symbolic result
alone does not add document retrieval. A combined structured and documentary task
still requires Hybrid. The audience decoder, host validation and style prompt
remain separate from this guidance.

The selected response_style is en, taglish, fil or unknown. Bintu quotes literal
English/Filipino fragments and selects a conversational style. The host checks
bounded structure/count consistency and exact original-text containment, then maps
that selection losslessly to language metadata. The model picks the style; the only
host override is an owner-approved floor (22 October 2026): an `english_only` label on a
question containing an everyday Filipino function word (ang, sa, ko, po...; all-caps
acronyms such as BA/MA ignored) becomes `taglish`, its literal words added as Filipino
fragments and `style_floor_applied` set. The host never chooses between fil and taglish.
Literal provenance cannot prove the fragment's language; model evaluation remains
necessary. The original routing proposal's language remains observable, while query
hints/accepted response_style come from the style interpretation. English requests should
receive English, Taglish natural Taglish, Filipino predominantly Filipino with
useful English technical terms. Language does not change evidence routing.
This metadata carries the preference to later generation; no final-language quality
claim is established here. Image attachments and private-file parsing are later work.

## Transport

LlamaTransport uses /props, /apply-template, /tokenize and /v1/chat/completions.
The p07-greedy-no-prefix-cache-v1 profile fixes temperature0/seed0,
reasoning_effort=none and cache_prompt=false in each generation request.
reasoning_effort is a requested setting,not proof that no thinking was generated.
The pinned Gemma JSON grammar permits thoughts;the sealed actual observation
reported reasoning despite that request. No zero thinking budget is selected.
See the [bounded design](../../plans/2026-10-20-router-correction-diagnosis-and-design.md).
Metadata records these overrides separately from an allowlisted subset of server-
reported sampling defaults, including sampler order when available. Missing defaults
are not invented; arbitrary prompt/grammar/stop text is excluded. Batch/thread/model
startup configuration still belongs in the external evaluation evidence. Disabling
prefix reuse changes evaluation conditions and can increase latency; it does not
guarantee determinism or improve accuracy. Prior implicit-cache outputs cannot be
presented as fresh inference under this profile. Semantic prompts remain unchanged.
It reserves max_output_tokens plus eight tokens within actual n_ctx for the whole
chat, including any repair. The model's tokenizer/template is used, not SEA-LION.
JSON-schema decoding is the default; explicit constrained=False uses JSON-only
decoding with the same strict backend validation. There is no automatic downgrade.
The routing decoder has disjoint route/control branches; style has its own strict
versioned schema.
Proceeding RAG decoder output has no operations; Symbolic/Hybrid has exactly one.
Clarification can retain multiple requested operations. The downstream guard still
withholds compounds if a transport ignores the schema; no operation is dropped.
Exactly one format/schema repair is SHARED across both calls:
normal two calls, maximum three. A persistent invalid reference (shown to the student
as a clarification) gets one unrepaired style call so the clarification matches the
student's style; if it fails, style stays unknown. attempts counts routing calls, style_attempts counts
style calls, inference_calls counts both, repair_attempts counts repairs alone.
Repair reanchors the original question. Grounding/capability holds
do not cause semantic retry or a cheaper RAG route. HTTP bodies are bounded and
errors expose only fixed operational codes. No module logs raw queries or grades.

Verified local research runtime: existing Gemma GGUF in owner-corrected
C:/Coding-projects/bintanong_workspace/MODELS/GEMMA_4_E4B. Official image download
explicitly authorized; image digest/build/model/template identities are recorded
in the Phase07 checkpoint/report. The weights remain mounted read-only in place.
The configured Gemma is the supplied Bintu inference model for this research;
this does not prove a separately fine-tuned Bintu-1 checkpoint.

## Synthetic development evaluation

The default `separate` profile keeps route and style in two normal calls with one
shared repair, at most three calls. Trusted `--routing-profile combined` selects an
experimental one-packet candidate, at most two calls with one whole-packet repair.
Both nested contracts retain their original schemas and host validation. No
request/model field can select a profile or silently fall back between profiles.
The candidate **failed multilingual promotion**: three greeting-route errors and
four new style regressions on the existing15fictional variants. Keep separate as
the default. See [results and recovery](../../plans/2026-10-20-combined-routing-results.md);
combined is not selected for student use and establishes no full-chain speed gain.

`python -B -m backend.bintanong_routing.evaluation INPUT.json --output PATH.json`
reads an explicit object containing catalog, cases and metadata. It uses a synthetic
registry and never executes it. Inputs are synthetic development questions, not
institutional source rules; new institutional benchmark labels/wordings retain
their review requirements. Evaluation rejects final split, duplicate IDs and
inconsistent equivalent-family labels. Expected labels never enter router calls.

The CLI defaults to localhost18087; --url/--timeout configure an existing runtime.
Output must stay under --evidence-root (default workspace/audit-evidence). Reports
contain normalized synthetic interpretations after quoted-reference resolution;
keep them ignored. Proposed route/control semantics stay as selected by the
model. Explicit diagnostic probes may retain original raw model output separately.
The report separately
scores proposed evidence/control labels, effective guarded labels, canonical
entities, scoped operation names/targets, claim meaning and response style.
Each case requires expected_operations (empty for no operation); bindings use
operation:curriculum_id:course_id. Invalid/failing outputs stay in every
relevant denominator. Report v2 adds style prompt/schema identity, grounded style
evidence and explicit per-stage/call/repair counts. Equivalent-family consistency and per-language counts are
separate from accuracy. A safe guard cannot make a wrong proposal correct.
evaluation_kind=mock proves only test/harness behavior, never model accuracy.

Use the existing Python3.13 readiness environment for this workstation's tests.
All focused tests are generic synthetic fixtures. No installs, source promotion,
institutional result, final benchmark or whole-project-green claim is implied.
