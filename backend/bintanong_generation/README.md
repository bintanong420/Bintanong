# Candidate generation and output validation

Phase09 implementation is active; actual-model evaluation is **NOT RUN** because
automatic approval review rejected starting the existing offline container. Do not
infer language/support accuracy or phase completion from passing mocked tests.
[Plan/checkpoint](../../plans/phase-09-checkpoint.md),
[research and Context alignment](../../plans/2026-10-19-orchestration-research-and-context-alignment.md).

`await Generator(transport).generate(text,integration)` consumes a candidate
`IntegrationResult`. `await AnswerPipeline(orchestrator,generator).run(text,context)`
composes routing/evidence and generation under one request deadline. Both retain the
default institutional release hold; there is no student endpoint or activation.

| File | Responsibility |
| --- | --- |
| `contracts.py` | Strict model drafts/support reports and host-only candidate output; typed scope and claim mappings |
| `evidence.py` | Revalidate integration, create source cards and copy safe canonical target/curriculum/edition/bundle context |
| `prompt.py` | Versioned draft/support instructions and constrained schemas; question/source/repair text remain untrusted data |
| `validation.py` | Release/language/outcome/reference checks, complete support verdicts and final assembly checks |
| `render.py` | Localized preview/control templates, canonical decision rendering and per-claim source markers |
| `generator.py` | At most two drafts/two support calls, one repair, fallbacks, cancellation and remaining request deadline |
| `evaluation.py` | Bounded synthetic dev observations; mock versus real-model label; human language/support reviews remain separate |

The host copies `DecisionOutcome`, target inputs and `DecisionScope`; private
`fact_ref` values are removed. A held Hybrid result can retain a structured
observation for inspection but cannot render its positive/negative conclusion.
RAG/Hybrid require documentary explanation, not merely a rule-only cited claim.
Each rendered prose claim retains its own evidence markers and typed references.

Draft JSON, wrong release/outcome/language, invented citations, incomplete/negative
support verdicts and private namespace references are rejected. A failed draft gets
one repair with unchanged evidence. Failure then returns a deterministic grounded
fallback; no unchecked tokens are streamed. Controls and non-ready evidence skip
inference. Router repair counters remain in integration events, separate from
answer repairs. Unexpected tool errors expose no exception body.

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

Mock fixtures prove guard/control mechanics, not model quality. The observation
CLI accepts only explicit synthetic dev cases (1–30), rejects duplicate IDs/final
split and writes only under the supplied evidence root. It starts no model/server:

```powershell
python -B -m backend.bintanong_generation.evaluation C:/Coding-projects/bintanong_workspace/audit-evidence/p09-generation-20261019/synthetic-dev-cases.json --output C:/Coding-projects/bintanong_workspace/audit-evidence/p09-generation-20261019/actual-observations.json --evidence-root C:/Coding-projects/bintanong_workspace/audit-evidence/p09-generation-20261019 --url http://127.0.0.1:18087 --timeout 120
```

Run that only when the existing authorized runtime is available. The current nine
synthetic inputs are prepared but unexecuted. Inspect each claim, condition, language
and fallback; annotate pending human review separately from model-checker acceptance.
See the [pending observation report](../../plans/2026-10-19-phase09-observation-status.md).
