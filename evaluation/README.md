# Evaluation preparation

Protocol preparation only. No final institutional questions have been verified by this document. Keep private inputs, gold institutional passages and evaluation output outside Git. This protocol implements the planning requirements of master §§6.3 and 16 and the [ready Phase 1 plan](../plans/phase-01-source-governance-contracts-plan.md).

## Sets and grouping

Maintain separate development and sealed final sets. Assign a stable scenario-family ID before paraphrasing; English, Tagalog, Taglish and near-identical variants of that family stay in one split. Group by the underlying decision scenario, not just query spelling. The source corpus may be shared; final queries, gold answers and outcomes must never tune prompts, thresholds or rules. Record and detect family and near-duplicate overlap before sealing the final set.

Target at least 50 independently verified final Taglish questions: at least ten each for enrollment procedures, prerequisite eligibility, grade policies, academic standing and disciplinary policies. This is a target, not an observed count. Missing verified scope or source authority keeps the corresponding final cases pending. Synthetic development fixtures may test contracts without establishing institutional policy.

## Case template

```json
{
  "case_id": "synthetic-prerequisites-001",
  "scenario_family_id": "synthetic-missing-required-grade",
  "split": "development",
  "category": "prerequisites",
  "synthetic": true,
  "query": "Pwede ba akong kumuha ng COURSE-B kung wala pa ang grade ko sa COURSE-A?",
  "scope": {"institution": "fictional", "edition": "synthetic-v1"},
  "expected_route": "Symbolic",
  "expected_control": "clarify",
  "expected_symbolic_outcome": "unknown",
  "missing_facts": ["verified prerequisite rule", "confirmed COURSE-A result"],
  "gold_source_spans": [],
  "allowed_claims": ["Required facts and applicable rule coverage are missing."],
  "verification_state": "synthetic_only",
  "reviewer": null
}
```

The route/control pair is illustrative planning data; settle exact control vocabulary against the shared routing contract before implementing a harness. A synthetic label cannot become source-backed verification by removing its flag. Institution-backed final cases require exact version/digest/page/locator spans, applicability, a fixed reviewed answer, reviewer evidence and review version. Five symbolic outcomes remain `eligible`, `ineligible`, `unknown`, `unsupported`, `error`; answer-envelope status and router control are separate fields.

## Annotation rubrics

| Axis | Required annotation and failure |
|---|---|
| Route/control | Expected required evidence path and clarification/refusal; an unavailable Symbolic/Hybrid component cannot silently become RAG |
| Evidence | Exact locator, source version/release, applicable scope, sufficient conditions/exceptions and conflict coverage; a citation alone does not prove support |
| Symbolic result | Correct five-outcome status, typed facts, supported predicate and traceable rules; missing coverage cannot produce eligible/ineligible |
| Answer correctness | Supported explanation in the requested language, preserved negation/numbers/exceptions, explicit uncertainty and limited decision scope |
| Unsupported claims | Count invented policy, office, fee, date, prerequisite or approval claims; report critical errors separately from average quality |

Annotate disagreements and adjudication evidence explicitly. Tune on development cases only. Include missing facts, wrong edition, unknown course, conflicting sources, incomplete coverage, unsupported requests, operational failure and private-session isolation. Language variants must preserve the scenario meaning, negation and temporal qualifiers.

## Reproducibility and release gates

Record `code_version`, `prompt_version`, `model_revision`, `quantization`, `embedding_config`, `knowledge_release_id`, `rule_bundle_version`, decoding settings, evaluation-set version and grouping assignment. Exact embedding token counts include prefixes and special tokens; the prospectus `estimate-v1` count is review metadata.

Before claiming a final benchmark: verify case/category totals, disjoint family assignments, source-backed independent review, frozen references and complete run metadata. Report per-category and per-language results, abstentions, critical/unsupported claims and operational errors. A missing final set or unrun evaluation is pending/NOT RUN, never a passing result.
