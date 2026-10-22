# Document evidence calibration implementation plan

> **For agentic workers:** Use executing-plans inline, retaining the existing
> isolated worktree. One final independent review of the completed experiment;
> no reviewer per input-preparation step. Owner direction already authorizes
> continuation; do not ask again about accepted wordings or execution method.

**Goal:** Assess the remaining document-evidence retrieval trade-offs without
expanding prerequisite questions into unnecessary RAG experiments.

**Architecture:** Keep all 75 accepted variants, but separate 39 document-evidence
probes, 18 scoped curriculum probes reserved for structured reasoning, and 18
existing early-stop controls. Reuse saved evidence and vectors. Only D3/D4's six
new document questions need encoding in this slice; D1/D2 stay accepted for later
structured lookups and are not encoded here.

**Tech stack:** Existing Python 3.13 environment, pinned local encoder/tokenizer,
unchanged context/subject/claim helpers and saved JSON/JSONL artifacts.

**Spec:** [Accepted packet](2026-10-16-development-calibration-proposal.md),
[architecture clarification](2026-10-16-curriculum-symbolic-routing-clarification.md),
AGENTS.md curriculum section, master sections 10/11/13. Baseline `f812f35`,
unchanged product `232a418`. This plan narrows the earlier proposed 75-case sweep
after the owner's architecture correction; it changes no wording or expectation.

## Global constraints

- All 75 strings remain accepted. Preserve prior 63 observations, vectors, original
  sources and seals. No whole-curriculum conversion, source intake or repeated review.
- Use the existing 27-candidate corpus and compatible saved vectors/configuration;
  no document or old-query re-encoding. Existing models remain in external MODELS.
- No install/download/dependency change, SQL/API/runtime change, Prolog execution,
  source activation or Phase 06 advancement. Candidate-only, advisory, undergraduate.
- Missing source claims/currentness and unknown student facts remain unresolved.
  Report field availability separately from answer sufficiency, which is unassessed.
- Raw inputs/scripts/results live in a new ignored workspace audit-evidence root;
  tracked material is curated text only. Explicit staging and Conventional Commits.

## Review focus

- A curriculum dependency or exact prerequisite lookup must not be rerouted into
  new retrieval sweeps to improve a headline score: verify disjoint purpose sets.
- Source absence can coexist with relevant context: retain limits regardless of
  emitted context, never convert relevance into price/billing/currentness support.
- Unknown curriculum/entity/audience must stop before a substituted answer:
  reuse recorded controls; raw negative matches cannot bypass their gate.
- Corpus/register versions and raw/filtered/emitted stages must remain distinct:
  verify exact vector payloads, provenance and metric denominators before combining.
- P50 application payment and P20,000 example require complete reviewed source
  groups: verify direct-fact reviews, source references and unchanged original claims.

## Task 1 — Freeze purpose sets and compatible inputs

**Files:** ignored `p05-document-evidence-calibration-20261016/` inputs and manifest;
tracked checkpoint/current progress and this plan pointer. No backend changes.

**Consumes:** sealed trace `requests.json` (63 exact identities), accepted packet at
`d2abc8d` and its actual approval receipt, current 27 candidates and saved vector
paths from the temporal preflight. **Produces:** `accepted-purpose-roster.json`,
`document-development-cases.json` and a hash-bound `readiness.json`.

- [ ] Join all 75 exact IDs/strings, three languages per group. Classify purposes
  by explicit existing group IDs, not keyword guessing or automatic route labels.
  Expected disjoint counts: document39 / structured18 / early-stop18, total75.
- [ ] Document groups: six original policy groups; U1/U2; T1/T2/U3; D3/D4.
  Structured reservation: Architecture/Nursing/Criminology/Tourism plus D1/D2.
  Early stops: two unknown-BSCS groups, S1/S2/A1/P1. Preserve their exact reasons.
- [ ] Check all 27 saved document-vector IDs/payloads/configurations and the 33
  old document-query vectors. Bind exact input hashes. Confirm only six accepted
  D3/D4 IDs lack a query vector in the current slice; do not encode D1/D2.
- [ ] Independently reconstruct these sets/counts/strings from the immutable inputs,
  verify no overlap or edited old identity, record readiness and commit the verified
  architecture/plan/preflight increment. No model or ranking work in this task.

## Task 2 — Bind complete document claims and source reviews

**Files:** ignored `source-inputs.json`, `source-review-register.json`,
`caller-annotations.json`, `metric-labels.json`, `input-bindings.json`.

**Consumes:** task 1's39 document identities and existing confirmed source groups.
**Produces:** separate source-field, caller-context and evaluation-only label inputs.

- [ ] Freeze complete source groups before joining question claims. Reuse existing
  source reviews. Add only the direct V01 application-payment review from its two
  already-confirmed readings; D4 reuses the existing F01/F08/F09 example facet.
  No new source-content approval or whole-procedure correctness is inferred.
- [ ] Bind exact reviewed fields/events/limits, current catalogue/register and
  primary/required-neighbor sets. Preserve first-step derivative history and every
  earlier registration version. Hold any new ambiguous reading for focused review.
- [ ] Keep explicit trusted subject/context annotations separate from metric labels;
  labels never enter ranking/filter inputs. Preserve U1/U2/T1/T2/U3 unestablished
  claims, Charter cutoff and handbook timing conflict. Verify complete versus
  empty/partial/wrong-subject contexts with existing helpers and direct field audit.

## Task 3 — Compare only the remaining document-evidence configurations

**Files:** ignored `new-query-vectors.jsonl`, rankings, context archives, decisions,
claim reports and metrics. Reuse historical scripts as references, never rerun
their exclusive writers in sealed roots. No product interface extension planned.

**Consumes:** tasks1/2, 27 existing document vectors and33 saved query vectors.
**Produces:** six new query vectors, 39-case conditional comparisons and limitations.

- [ ] Verify existing local asset hashes/configuration, then encode only six D3/D4
  questions. Check finite normalized vectors and compatibility; compute cosine
  scores from saved vectors for any missing current-27-corpus comparison. Preserve
  old 21-candidate observations under their original corpus identity.
- [ ] Compare k3/5/8, thresholds0/.25/.5/.75/.9, budgets2048/4096, all-primary versus
  longest-gap-free-prefix, retaining complete required-neighbor groups. Reuse
  compatible measurements. No fresh curriculum sweeps, controls encodings or NLP.
- [ ] Use unchanged `select_candidate_subject(catalogue, chunks, subject_id=...)`,
  `build_context_selection_report(candidates, budget, count_tokens,
  primary_limit=..., shared_citations=True, shared_group_metadata=True)` and
  `build_candidate_claim_report(catalogue, chunks, subject_id=...,
  requested_claims=..., emitted_chunk_ids=..., claim_reviews=...)`.
  Gold labels remain external. Separate raw ranking, trusted-filter primary and
  emitted-context results; null selection remains null, never successful emptiness.
- [ ] Report fixed-k and returned-primary precision, expected-primary recall,
  complete field-group recovery, gaps and source-claim status by language/category.
  Empty/unknown denominators are N/A where appropriate; no answer-success aggregate.
  Reuse18 early-stop controls separately. Report structured18 as reserved, not failed
  retrieval cases. Neither assembly cleanliness nor cosine proves claim coverage.
- [ ] Reject candidate policies that drop limitations, bypass gates or default
  unknown facts. Report trade-offs or no justified winner; never force a scalar
  cutoff or silently promote these conditional inputs into runtime interpretation.

## Task 4 — Verify, review once and hand off

**Files:** ignored independent verifier/logs/seal; curated document-evidence report,
INDEX, active checkpoint/current progress and CLI/blocked handoffs.

- [ ] Independently recompute new cosine scores and relevant saved comparisons;
  verify exact contexts/tokens/citations/dependencies/claim results and all preserved
  input hashes. A helper replay is distinct from an independent field audit.
- [ ] Run appropriate existing focused tests and documentation/phase-ledger checks
  using the readiness venv, `-B -p no:cacheprovider` and external basetemp. Only an
  actual product defect justifies a separate focused RED/GREEN code correction;
  do not repeat unchanged full/native suites or add mirror tests for preparation.
- [ ] One final independent review after results exist, resolve material findings,
  seal raw evidence, explicitly stage verified text and commit. Record actual
  language/category results, development exposure, unresolved limits and exact
  remaining Phase 05 exit requirements. No blind/generalization or phase-exit claim.

## Stop condition

This slice is complete when the39 document comparisons and existing controls have
verified, source-bound results and an explicit calibration conclusion, including
“no justified policy” if warranted. Do not add another sidecar layer or parameter
grid simply because some cases remain unassessed. Record any required new
capability against its intended structured/RAG/Hybrid path and formal phase gate.
Full Phase 05 completion still requires the standing exit/governance checks.
