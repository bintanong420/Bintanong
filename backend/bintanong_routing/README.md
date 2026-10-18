# Offline multilingual LLM routing

This Phase07 module interprets English, Filipino and Taglish with a supplied local
LLM. It returns a model proposal and a separately validated shared RoutingDecision.
It does not retrieve documents, execute Prolog, generate student answers, publish an
API or activate institutional data. The historical API BintuClient/Direct adapter
remains separate and cannot dispatch through this module.

`await Router(transport, ...).route(text, RequestContext(...))` preserves original
text and minimally normalizes it. Interpretation is strict JSON with grounded
program/curriculum/course mentions, claims and proposed operations. Course aliases
resolve only against explicitly injected reviewed records and known curriculum;
explicit program/curriculum mentions may resolve scope through their own aliases.
There is no fuzzy equivalence or curriculum inference from a course code.

Text offsets are Python Unicode character offsets into the original text, with
exclusive ends. A model can quote exactly but count incorrectly. The backend
anchors a quote only if it occurs exactly once; corrections are reported separately.
Correct explicit offsets can distinguish repeated text; bad offsets on repeated or
missing quotes remain unresolved. No text/state/meaning is rewritten.
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

The selected response_style is en, taglish, fil or unknown. English requests should
receive English, Taglish natural Taglish, Filipino predominantly Filipino with
useful English technical terms. Language does not change evidence routing.
This metadata carries the preference to later generation; no final-language quality
claim is established here. Image attachments and private-file parsing are later work.

## Transport

LlamaTransport uses /props, /apply-template, /tokenize and /v1/chat/completions.
It reserves max_output_tokens plus eight tokens within actual n_ctx for the whole
chat, including any repair. The model's tokenizer/template is used, not SEA-LION.
JSON-schema decoding is the default; explicit constrained=False uses JSON-only
decoding with the same strict backend validation. There is no automatic downgrade.
The decoder schema has disjoint route/control branches. Exactly one format/schema
repair is allowed; it reanchors the original question. Grounding/capability holds
do not cause semantic retry or a cheaper RAG route. HTTP bodies are bounded and
errors expose only fixed operational codes. No module logs raw queries or grades.

Verified local research runtime: existing Gemma GGUF in owner-corrected
C:/Coding-projects/bintanong_workspace/MODELS/GEMMA_4_E4B. Official image download
explicitly authorized; image digest/build/model/template identities are recorded
in the Phase07 checkpoint/report. The weights remain mounted read-only in place.
The configured Gemma is the supplied Bintu inference model for this research;
this does not prove a separately fine-tuned Bintu-1 checkpoint.

## Synthetic development evaluation

`python -B -m backend.bintanong_routing.evaluation INPUT.json --output PATH.json`
reads an explicit object containing catalog, cases and metadata. It uses a synthetic
registry and never executes it. Inputs are synthetic development questions, not
institutional source rules; new institutional benchmark labels/wordings retain
their review requirements. Evaluation rejects final split, duplicate IDs and
inconsistent equivalent-family labels. Expected labels never enter router calls.

The CLI defaults to localhost18087; --url/--timeout configure an existing runtime.
Output must stay under --evidence-root (default workspace/audit-evidence). Reports
contain synthetic interpretations after exact quote anchoring, plus offset-correction
counts; keep them ignored. Proposed route/control semantics stay as selected by the
model. Explicit diagnostic probes may retain original raw model output separately.
The report separately
scores proposed evidence/control labels, effective guarded labels, canonical
entities, scoped operation names/targets, claim meaning and response style.
Each case requires expected_operations (empty for no operation); bindings use
operation:curriculum_id:course_id. Invalid/failing outputs stay in every
relevant denominator. Equivalent-family consistency and per-language counts are
separate from accuracy. A safe guard cannot make a wrong proposal correct.
evaluation_kind=mock proves only test/harness behavior, never model accuracy.

Use the existing Python3.13 readiness environment for this workstation's tests.
All focused tests are generic synthetic fixtures. No installs, source promotion,
institutional result, final benchmark or whole-project-green claim is implied.
