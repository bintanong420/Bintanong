# Candidate generation and output validation

The current Phase09 recovery candidate requires Interpretation v2,IntegrationResult
v2 and CandidateAnswer v2. Routing extracts exact requested parts BEFORE evidence;
orchestration binds original question SHA256,request,release and validated operation.
Generation rejects another question and accounts for every declared part in a bound
ledger. The EXISTING support call now maps document parts and checks source support;
matching host-rendered symbolic results cover structured parts. No classifier call
is added. Unknown/missing parts withhold a normal answer. The separate language call,
shared repair/deadline,complete source cards and institutional holds remain.

`understanding.py` integrates the shared review/ledger records. `ledger_contracts.py`
contains the single ledger-record definitions used by this candidate and the older
detached helpers. Ledger semantic completeness remains **unverified**;a wrong model
part/mapping can pass host checks. Software green is not actual-model accuracy or
latency. This v2 candidate has not passed a new actual-model gate or been promoted.
Historical observations below refer to their recorded earlier code/contracts.
Old payloads are rejected at the new runtime boundary;there is no silent empty plan.
The old covered experiment's whole-question verdict cannot satisfy v2 part accounting.

`parts.py` is a detached fixed-observation candidate,unconnected to Generator.
`await QuestionPartAnalyzer(transport).analyze(text,integration,draft)` validates
ready RAG input and supplied documentary claims,then uses at most two calls under
one deadline:quoted-part extraction and individual mapping/support review. The host
resolves unique exact quotes to original character offsets and rejects ambiguous
occurrences. Review schemas pin identities and allowed IDs;existing ledger guards
remain required. No repair,route change,Prolog check,answer generation or renderer
occurs. An `ok` PartAnalysis contains an assessed ledger,which can be unresolved;
semantic completeness always remains unverified. Fixed failure states omit unchecked
output and exception text. Per-stage seconds are nested component durations,not
browser or complete-answer latency. See the
[fixed observation plan](../../plans/2026-10-20-question-parts-observation-plan.md).
The single frozen8case actual-model batch FAILED:five source sentences were copied
instead of question quotes;three structured cases were classified unknown and
remained unresolved. Document-part review was not exercised. Keep this helper
detached/unselected,no correction sweep. The7.8-22.8s component durations do not
measure complete validated answers. [Results](../../plans/2026-10-20-question-parts-observation-results.md)
preserve outputs and the open limitations.

`requirements.py` retains detached authoring/assessment functions;the generator
reuses its review records,not its RAG-only helper path. `create_plan(text,integration,parts)` binds1-8 supplied exact original
question spans and their document/structured/unknown kinds to a release/query hash.
`review_identity(text,integration,plan,draft)` binds request,language,full source
cards,plan and draft;`assess_parts(...,review)` checks each supplied claim mapping
or unavailable/uncertain state,existing draft/support guards and replay identity.
Missing mappings,unmapped claims and failed support keep the ledger unresolved.
Structured/unknown requirements cannot be satisfied by this document-only helper.
The returned ledger is never an answer or runtime authorization. Even
`all_declared_parts_mapped` leaves `semantic_completeness=unverified`:an omitted
requirement or incorrect semantic mapping can still pass mechanically. Nested
records share their enclosing contract version. No extractor/model call,renderer,
new profile or runtime selection is introduced. See the
[bounded plan](../../plans/2026-10-20-question-parts-plan.md).

Phase09 is active after reopening the earlier offline milestone. The request grammar
binds the draft decision to its host-owned value,including null. The initial120s
baseline timed out9/9; a corrected three-language RAG follow-up at240s answered3/3.
Those are separate observations; default-budget and broader route performance
remain unresolved. See the [measured report](../../plans/2026-10-19-phase09-observation-status.md)
and [final handoff](../../plans/phase-09-handoff.md),
[research and Context alignment](../../plans/2026-10-19-orchestration-research-and-context-alignment.md).
The later [Symbolic/Hybrid observations](../../plans/2026-10-19-phase09-structured-generation-observations.md)
returned five answers and one fallback at240s. Three answers have agent-identified
scope/clarity concerns despite positive checker verdicts; all answers took over120s.

`await Generator(transport).generate(text,integration)` consumes a candidate
`IntegrationResult`. `await AnswerPipeline(orchestrator,generator).run(text,context)`
composes routing/evidence and generation under one request deadline. Both retain the
default institutional release hold; there is no student endpoint or activation.

| File | Responsibility |
| --- | --- |
| `contracts.py` | Strict model drafts/support reports and host-only candidate output; typed scope and claim mappings |
| `evidence.py` | Revalidate integration, create source cards and copy safe canonical target/curriculum/edition/bundle context |
| `references.py` | Optional request-local short wire labels; restore canonical hashes before validation/rendering |
| `scope.py` | Selected document-only explanation contract and per-claim documentary checking; structured decisions remain host-owned |
| `guard.py` | Experimental one-call post-retrieval assessment; failed multilingual gate and remains unselected |
| `coverage.py` | Unselected RAG question-coverage experiment; failed actual multipart request despite successful prepared probes |
| `prompt.py` | Versioned draft/support instructions and constrained schemas; question/source/repair text remain untrusted data |
| `validation.py` | Release/language/outcome/reference checks, complete support verdicts and final assembly checks |
| `render.py` | Localized preview/control templates, canonical decision rendering and per-claim source markers |
| `generator.py` | At most two drafts/two support calls, one repair, fallbacks, cancellation and remaining request deadline |
| `evaluation.py` | Bounded synthetic dev observations; mock versus real-model label; human language/support reviews remain separate |

The host copies `DecisionOutcome`, target inputs and `DecisionScope`; private
`fact_ref` values are removed. A held Hybrid result can retain a structured
observation for inspection but cannot render its positive/negative conclusion.
Control clarifications retain typed `missing_facts` and name the missing program
or curriculum version in the requested language. Final validation checks those
fields; private namespace references are rejected before preparation.
RAG/Hybrid require documentary explanation, not merely a rule-only cited claim.
Each rendered prose claim retains its own evidence markers and typed references.

Draft JSON, wrong release/outcome/language, invented citations, incomplete/negative
support verdicts and private namespace references are rejected. A failed draft gets
one repair with unchanged evidence. Failure then returns a deterministic grounded
fallback; no unchecked tokens are streamed. Controls and non-ready evidence skip
inference. Router repair counters remain in integration events, separate from
answer repairs. Unexpected tool errors expose no exception body.

`Generator(..., explanation_profile='legacy', reference_profile='short')` is an explicit experimental token
reduction; the default is `canonical`. Short drafts use a separate strict schema
and e1..e32 labels, mapped only within that request. Full source text and metadata
remain. The host restores canonical hashes before existing validation, then uses
the same labels for the separate support check. Final claims/citations retain full
canonical IDs. No prose replacement, source truncation or checker bypass occurs.
See the [bounded plan](../../plans/2026-10-20-short-evidence-references-plan.md).

`Generator(..., explanation_profile='scoped')` is the selected offline accuracy candidate described
in the [scoped plan](../../plans/2026-10-20-scoped-explanations-plan.md). It renders
ready pure Symbolic answers entirely from their validated typed result, with no
generated claim to check. RAG/Hybrid still generate and separately check documentary
claims, using complete document cards; the host alone constructs decision fields.
Each checker item receives only that claim's cited documents. It cannot borrow
Prolog results to justify an unstated documentary purpose. Free prose remains
fallible. Scoped is now default after the bounded actual quality gate. Legacy is an
explicit developer comparison with known scope limitations. Scoped currently
requires canonical reference IDs; it does not select the rejected short-ID profile.

Explicit `explanation_profile='guarded'` adds one release-bound LLM assessment against the original
question and complete documentary cards. Only `document_only` proceeds to drafting
and support checking. `structured_required`, `uncertain` and invalid output return
a localized `decision_withheld` abstention without generated claims. Timeout/tool
failure returns temporary unavailability. No assessment repair, route change or
new rule execution occurs. The existing generation/request deadline includes this
call; Symbolic/Hybrid and nonready controls do not add it. See the
[guard plan](../../plans/2026-10-20-post-retrieval-guard-plan.md). Assessment remains
semantically fallible; schemas and mocks cannot establish missed-decision recall.
The [actual results](../../plans/2026-10-20-post-retrieval-guard-results.md) failed
both initial and single corrected multilingual gates. Guarded remains an explicit
developer experiment;default scoped does not run it. The rejected prompt correction
is preserved in ignored evidence;the initial prompt is retained for reproducibility.
The missing post-retrieval safeguard remains an unresolved Phase09 requirement.
`explanation_profile='covered'` is a separate unselected experiment in the
[coverage plan](../../plans/2026-10-20-question-coverage-plan.md). Its ready RAG
review requires complete question coverage plus every existing support/language/
scope check. Supported claims about a different subject cannot pass on entailment
alone. Partial/none/uncertain coverage returns a fixed localized insufficient-
evidence response with no claims/citations and no answer repair. Other review or
support failures retain the one-repair limit and unchanged evidence/deadline.
The same review call produces both judgments;these are not independent models.
Hybrid keeps the original documentary checker and host result;this coverage claim
is RAG only. `question_coverage` records the reviewed draft and combined review
seconds,already included in generation/pipeline time. It is null for historical
and other paths. No semantic guarantee or default selection follows from mocks.
The six prepared probes passed,but the actual-service question asked for both
location and fee. The model released location only and incorrectly judged complete
coverage despite the fee being present in its source. Keep scoped selected;covered
failed its quality gate. The27.3s live response is an incomplete-answer duration,
not supported complete-answer latency. No correction or further model sweep follows
this bounded experiment. [Results](../../plans/2026-10-20-question-coverage-results.md)
preserve the open P2 and exact limitations.
`CandidateAnswer.decision_guard` records result and elapsed seconds (one assessment,
including transport preflight/connection work). It is null for historical reports
and paths with no guard. Its time is already inside generation/pipeline timing.

The prose checker uses the supplied Bintu transport and can be wrong. Grammar/schema
success, source ID presence or a positive checker verdict is not a guarantee of
entailment, complete policy coverage or correct conversational language. Human
assessment and actual-model observations remain required. The inherited namespace
scanner is not a general PII detector. Candidate text is plain text; future frontend
code must render it safely. Never log full prompts, answers, facts or source cards.

This candidate contract does not replace institutional EvidenceBundle/AnswerEnvelope.
Institutional loading/source authority, privacy/session ownership, Phase10 private
files and Phase11 web/API integration retain their boundaries. No model training,
new framework, automatic acquisition or permanent student-record storage is added.

## Verify

From repository root with the prepared Python3.13 environment and external
TEMP/TMP/--basetemp under workspace/audit-evidence:

```powershell
python -B -m pytest -q -p no:cacheprovider --basetemp=C:/Coding-projects/bintanong_workspace/audit-evidence/p09-generation-tests/run tests/test_generation_evidence.py tests/test_generation_validation.py tests/test_generation_loop.py tests/test_generation_pipeline.py tests/test_generation_evaluation.py
```

Mock fixtures prove guard/control mechanics, not model quality. Observation reports
record effective explanation/reference profiles and matching prompt hashes;host-only
rendering and guard-only inference are identified separately from actual generation.
The guard prompt hash is recorded for the guarded profile. The observation
report records effective per-case support hashes. Covered has a null top-level
support hash because RAG uses coverage review and Hybrid uses the original checker;
its coverage policy hash and pending human question-coverage review stay explicit.
CLI accepts only explicit synthetic dev cases (1–30), rejects duplicate IDs/final
split and writes only under the supplied evidence root. It starts no model/server:

```powershell
python -B -m backend.bintanong_generation.evaluation C:/Coding-projects/bintanong_workspace/audit-evidence/p09-generation-20261019/synthetic-dev-cases.json --output C:/Coding-projects/bintanong_workspace/audit-evidence/p09-generation-20261019/actual-observations.json --evidence-root C:/Coding-projects/bintanong_workspace/audit-evidence/p09-generation-20261019 --url http://127.0.0.1:18087 --timeout 120
```

Run that only when the existing authorized runtime is available; preserve existing
reports and choose a new output path for any justified follow-up. The nine-case
baseline and targeted follow-up are complete. Inspect each claim, condition, language
and fallback; annotate pending human review separately from model-checker acceptance.
See the [observation report](../../plans/2026-10-19-phase09-observation-status.md).
