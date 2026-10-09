# Evaluation preparation

Protocol preparation only. No final institutional questions have been verified by this document. Keep private inputs, gold institutional passages and evaluation output outside Git. This protocol implements the planning requirements of master §§6.3 and 16 and the [Phase 1 plan](../plans/phase-01-source-governance-contracts-plan.md).

## Sets and grouping

Maintain separate development and sealed final sets. Assign a stable scenario-family ID before paraphrasing; English, Tagalog, Taglish and near-identical variants of that family stay in one split. Group by the underlying decision scenario, not just query spelling. The source corpus may be shared; final queries, gold answers and outcomes must never tune prompts, thresholds or rules. Record and detect family and near-duplicate overlap before sealing the final set.

Target at least 50 independently verified final Taglish questions: at least ten each for enrollment procedures, prerequisite eligibility, grade policies, academic standing and disciplinary policies. This is a target, not an observed count. Missing verified scope or source authority keeps the corresponding final cases pending. Synthetic development fixtures may test contracts without establishing institutional policy.

## Implemented case and protocol contracts

[case.schema.json](case.schema.json) defines the `bintanong-evaluation-case-v1` JSON contract; [case.py](case.py) supplies `case_findings`. The executable [missing-prerequisite development cases](cases/dev/grp-missing-prereq-grade.json) show all required fields and the actual `group_id`, `dev` split and `synthetic` status. Exactly one route or control is set; a Symbolic route requires an expected outcome. Synthetic cases have an explicit invented `synthetic_policy`, empty `gold_spans`/`gold_rules`, null review evidence and no institutional applicability.

[protocol.py](protocol.py) supplies `load_cases`, `validate_case_set`, deterministic `derive_split`, `make_freeze` and `coverage`. [rubrics.py](rubrics.py) supplies `score_case`, `summarise` and `RunRecord`. See [the Task 5 decision record](../docs/decisions/phase-01-evaluation.md) for tested defaults and limitations.

A synthetic label cannot become source-backed verification by removing its flag. Institution-backed final cases require exact version/digest/page/locator spans, applicability, a fixed reviewed answer, reviewer evidence and review version. Five symbolic outcomes remain `eligible`, `ineligible`, `unknown`, `unsupported`, `error`; answer-envelope status and router control are separate fields.

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

## Pending-source traceability exercise

`py -3.13 -m evaluation.traceability evaluation/examples/traceability-synthetic.json` checks one document version, one chunk, one synthetic rule draft and one existing synthetic development case. The executable example uses fictional source bytes/text. It replaces the earlier descriptive chain. The checker pins source spans, chunk id/content hash, rule id/bundle/draft digest, and case id/digest; exact binding comparisons preserve JSON number types.

The separate external BSBA-HRM exercise uses a copied cached Docling JSON and records a maintainer check against the chunk's own extracted cells. Original PDF bytes were hashed, but the legacy cache has no conversion byte identity, so the cache-to-PDF association and source verification remain pending. The per-chunk `content_check` never changes the register's content-review or approval state. The printed passage does not support the invented COURSE-A/B rule. The case stays synthetic with empty gold spans/rules, no applicable institutional scope and no verified-final coverage. See [the Task 4 decision record](../docs/decisions/phase-01-traceability.md).
