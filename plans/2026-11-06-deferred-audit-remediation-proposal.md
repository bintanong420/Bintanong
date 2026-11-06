# Bintanong P12 — Audit-driven remediation and PR integration plan

**Planning baseline: 6 November 2026 (Asia/Manila)**  
**Repository:** `bintanong420/Bintanong`  
**Planning status:** Proposal for engineering review, **not proof that a fix passed tests**.  
**Operating principle:** Distinguish observed behavior, static-code risks, hypotheses and independently reviewed academic truth. No feature expansion is allowed to weaken source pinning, reviewed curriculum scope or candidate-only research restrictions.

## Executive decision

Do not merge nine unrelated fixes into one PR, and do not rewrite the architecture. Maintain **one immutable acceptance corpus**, one owner-maintained defect register, and multiple narrowly scoped PRs. Every PR must state which verified failures it closes; independent audits may contradict each other and must be reconciled against reproducible traces.

## Confirmed current branch graph

```
p12-post-gathering-fixes @ 730344e7bbb889c86ab5c94288455566a9248066
    |
    +-- PR #18 [draft, OPEN] audit/curriculum-symbolic-boundary-20261105
           HEAD @ 1f8ee4a47b59a630c04305521f98a9f9bb9e476f
           |
           +-- PR #19 [draft, OPEN] feature/fm05-bounded-compound-symbolic
                  HEAD @ 27ef19ec9cd565ced81c3c6746bb0ad225c18f7b

p12-evaluation-harness — preserve as a frozen evaluation/gathering reference.
```

PR links: https://github.com/bintanong420/Bintanong/pull/18 and https://github.com/bintanong420/Bintanong/pull/19. Neither head reported CI statuses when checked. **PR #19 depends on PR #18.** Do not cherry-pick the same files into both branches or push directly to the evaluation/gathering branch.

### PR ownership

- **#18, boundaries/evidence:** domain-owned catalog vs symbolic operations, honest unmatched-document-topic notices, conservative research retrieval promotion. Must run routing, adapter, retrieval, generation and Hybrid regressions. The allowlist alone **does not prove semantic interpretation**.
- **#19, multi-operation research prototype:** synthetic-only executor for exactly two independent prerequisite eligibility checks, per-part typed candidate evidence, fail-closed partial errors. The existing student-facing route still deliberately rejects compound requests. **Not a completed FM-05 fix**.
- **All future PRs:** branch from the latest validated integration base, not from another agent's dirty worktree. Stack only when there is an explicit API dependency. New failures should be reproduced before remediation.

## Ground truth and existing benchmark

The supplied PDF defines **24 question families × 3 language variants**: 10 symbolic and 14 policy/procedure, with English, Tagalog and Taglish forms. The user's CSV marks **47 `Y`, 8 `P`, 14 `N` and 3 blank** (72 variants total). These are owner-provided observations, not independently adjudicated ground truth; Bintu-1 baseline columns are blank. The blank variants in row 7 concern program selection and must be labeled *not tested / blocked by UI* rather than automatically counted correct or incorrect.

High-signal concrete reproduction candidates from the CSV and existing November 5 development run:

| Case | Observed symptom / audit hypothesis | Primary subsystem | First check |
|---|---|---|---|
| #2/#5/#6 | Explicit `not passed` premise re-asked as unknown | language/claim interpretation | trace claim span, fact state, symbolic inputs |
| #9 | Forensic 3/L gets generic subject clarification in all three variants | target/alias binding | resolve in selected BSCrim edition with approved catalogue |
| #10 | General simultaneous prerequisite/co-requisite question routed inconsistently | scope/mode classification | documentary rule vs named curriculum check |
| #13/#14 | Incorrect enrollment/add-change routing, transfer materials | RAG topic/claim selection | selected subject IDs and retrieved source records |
| #16 | INC coverage inconsistent across languages; one source contains deadline conflicts | evidence sufficiency / source limits | exact reviewed rule and conflicting-source handling |
| #17/#18/#19 | Taglish withholds or marks source missing while other variants answer | multilingual topic routing | compare identical claim mapping and source cards |
| #23 | Gate-pass answer omits actual steps though relevant chunks exist | part completeness | required reviewed fields vs cited answer |
| #24 | Facilities question routes to library service record | document-topic disambiguation | general facilities vs library facility scope |

Important: the benchmark questions sometimes contain different contextual information in the three language columns. Do not call every answer difference a language error; label *semantic equivalence* separately. Several PDF `Correct if...` entries explicitly say `verify`; independently confirm those against the appropriate prospectus before treating them as truth. The repository's separate 72-browser-run log measured 72/72 rendering, **not** 72/72 correctness.

## Defect register: required row per coding agent finding

Minimum fields:

```
Finding ID | failure mode | claim source (CSV/repo/live trace/agent hypothesis)
base/head commit SHA | config flags | release_id | program_id | curriculum_id
user input + intended meaning | expected route, part IDs and operation targets
actual normalized interpretation | retrieval subject/claims | symbolic request/result
expected source spans, page and edition | observed result/status
reproduction command / fixture | severity (P0/P1/P2) | owner | PR | verdict
```

Classify each: **CONFIRMED**, **CODE-LEVEL RISK**, **HYPOTHESIS**, **FIXED-UNVERIFIED**, or **VERIFIED**. Deduplicate findings by underlying root cause, not by symptom. Prevent grading a refusal as equivalent to a wrong positive decision. Keep user/student grade data out of public traces and commits.

## Implementation sequence and PR gates

### Gate 0 — Audit freeze and baseline instrumentation (PR-AUDIT)

**Owner:** integrator/test lead. **Target:** `p12-post-gathering-fixes` or its latest approved descendant, with independent tests-only changes.

1. Freeze original 72 queries and expected source identities, preserving the original PDF and CSV as private artifacts. Normalize distinct `Y`, `P`, `N`, `not tested`, `unknown gold` labels; avoid retroactively changing the original benchmark.
2. Build a **new held-out corpus** with verified intent, program, curriculum edition, normalized facts, target, selected route/operation, source spans and expected conclusion. It must include compound requests; the original 72 does not.
3. Capture sanitized per-stage traces: router interpretation and repairs, selected topic, retrieved IDs/coverage, Prolog operation and outcome, generation coverage, server build SHA and flags. Attach run IDs to all agent findings.
4. Create CI jobs or a reliable explicit local gate for Pydantic/unit suite, Pytest integration, source/provenance integrity, and tagged e2e. The checked branch currently has no `.github/workflows` directory; distinguish the absence of checks from a passing check.
5. Run a frozen baseline on the original P12 candidate before modifying correctness expectations. Save all old results for comparison.

**Exit:** at least one independently reproducible case per high-priority root cause, plus an unchanged benchmark manifest/hash.

### Gate 1 — Stabilize and merge PR #18

**Owner:** routing+evidence maintainer. **Scope:** FM-01 domain guard, FM-03 fallback accuracy, FM-07 conservative calibration.

- Run the documented targeted tests plus routing/RAG/Hybrid integration checks on the actual development venv. Inspect false abstentions from stricter retrieval promotion before adjusting it.
- Show policy-only → zero symbolic calls; catalog facts → lookup (no constraint rule); eligible checks → only registered prerequisites; unavailable/conflicting RAG → no falsely complete answer.
- Regression-test missing information vs unavailable topic vs defective source vs incomplete evidence as **different** conditions.
- Compare `BINTANONG_ROUTER_COMPILE` OFF/ON; do not assume either profile performs identically.

**Exit:** tests and reviewed behavior pass; #18 merged first. Recheck PR #19's base/commit graph afterward before rebasing or retargeting.

### Gate 2 — Routing semantic accuracy and multilingual normalization (PR-ROUTE)

**Owner:** router maintainer; QA independently labels expected intent. **Scope:** FM-01, FM-02 and FM-08; FM-06 only when reproduced.

- Use `backend/bintanong_routing/{prompt,wire,compile,validation,router,topic_selection,claim_evidence}.py`; preserve host-owned capability signatures and source scope.
- Enforce question-part coverage and target identity; distinguish `list_course_prerequisites` from `check_prerequisite_eligibility` and reverse-dependency operations.
- Verify that explicit `not_passed`, `failed`, `not_taken`, `taken_unknown`, `passed` and hypotheticals are not promoted into one another.
- Bind explicit program and curriculum edition consistently at request start and on follow-ups; ambiguous editions ask clarification, never guess the latest prospectus.
- Test English/Tagalog/Taglish negation and morphology, alias/case/slash variants, #9 Forensic target, and topic-switch/carryover cases with *the same intended meaning*.
- Keep model semantic evaluation distinct from schema-valid JSON or exact string matching.

**Exit:** no **false eligible** outcomes in independently source-verified adversarial gate, all exact target/edition labels pass required fixtures, and no regression in source-only routing.

### Gate 3 — RAG subject selection, retrieval sufficiency and complete procedures (PR-RAG)

**Owner:** retrieval+knowledge maintainer; separate source reviewer. **Scope:** FM-03, FM-07.

- Work in `backend/bintanong_retrieval/{candidate_subject,evidence_policy,engine,context_selection}.py`, orchestration `_topic_intents`, and `backend/bintanong_generation/{part_answers,understanding,validation}.py` as needed.
- Diagnose #13/#14/#23/#24 by logging subject candidates, requested claims, selected chunks, section/page locators, and omitted required fields; compare against original handbook/charter.
- Do not treat semantically similar passages, source ID existence or an LLM's confidence as proof the requested procedure is covered. Require per-claim reviewed fields and per-part coverage; preserve gap taxonomy.
- Avoid an unrestricted “retrieve everything” fallback; use bounded query expansion/secondary subject retrieval only on independently verified insufficient-coverage signals.
- For a multi-part query, do not discard the unsupported portion. Answer supported parts and name held ones when the evidence contract permits; do not falsely claim the institution lacks rules.

**Exit:** verified source spans for every required procedural step of selected cases; held/uncertain gaps remain explicit; no off-topic document promoted to a supported answer.

### Gate 4 — PDF → reviewed catalog → Prolog truth audit (PR-KB)

**Owner:** source/KR reviewer plus independent academic reviewer. **Scope:** FM-04, source component of FM-02 and FM-06.

- For each target curriculum, maintain source identity: original PDF bytes hash, printed page/cell, edition, normalized course record, prerequisite expression, rule ID, review decision and immutable release/bundle version.
- Compare Docling/Markdown-to-catalog records with the original PDF and resulting Prolog representation; separately label scanned ambiguity, blank prerequisites, `None`, conjunction/disjunction, corequisites, alternatives, and year-level restrictions.
- Use manually reviewed fixtures from multiple programs/editions (not just BSCS). A deterministic engine may be perfectly internally consistent and still faithfully execute an incorrectly extracted rule.
- Fail closed on unresolved printed conditions; no inferring a rule from OCR/layout guesses. Do not alter the university's rules to improve a test score.

**Exit:** independently adjudicated source-to-rule consistency report with discrepancy register, regenerated candidate release and zero silent unreviewed-rule promotion on acceptance set.

### Gate 5 — Complete FM-05 (PR #19 plus follow-up PR-MULTI)

**Owner:** orchestration+generation lead. **Scope:** FM-05, Hybrid composition.

**Part A, currently in #19:** two distinct eligibility checks, same edition, typed per-part candidate evidence, isolated partial failures; no user-facing activation. First run the synthetic tests; repair any actual failures.

**Part B, new dependent PR only after Part A passes:**
- Version the request plan as a bounded sequence of up to 4 question/operation bindings. Each part has unique `part_id`, `operation_index`, typed predicate request, bound target and curriculum scope.
- Orchestrate bounded operations sequentially against the existing Janus worker (respect `_BoundedWorker` lock) or through an explicitly verified queue. Do not call the same Prolog runtime concurrently without reworking admission semantics.
- Validate source release and type of **every** structured result. Do not let the first result silently fill `CandidateEvidence.symbolic` for every part.
- Introduce **per-part evidence and verdicts** in `CandidateEvidence`, `IntegrationResult` and generation `PreparedEvidence`, `CandidateAnswer` and per-part ledger. Preserve old single-result schema/API via a clear versioned migration or adapter; do not silently change current serializations and hashes.
- Render final student output deterministically from per-part host-verified outcomes, citing each independently. `unknown` stays unknown; a failed sub-operation is reported without invalidating an independently successful result.
- Test two eligibility checks; eligibility + dependency list; printed catalog fact + eligibility; two symbolic checks + one RAG policy; one timeout + one success; duplicate targets; cross-edition disagreement; negative/completion fact; multiple source gaps; source-release mismatch.

**Exit:** full end-to-end browser/API answer contains exactly the requested independently supported parts; no dropped question and no unverified eligibility. Keep an explicit disabled-by-default feature flag until this passes.

### Gate 6 — Dialogue memory and follow-up lifecycle (PR-MEMORY)

**Owner:** session/transport lead. **Scope:** related architecture audit findings A02/A04/A05/A06/A08 and FM-06 follow-up facts.

- Existing `ConversationContext` + `PendingCheck` must not be mistaken for a general transcript or verified grade record. Introduce an ephemeral server-owned thread/turn ledger first, with bounded typed state and a context compiler.
- Track original user question, assistant clarification, answered/held parts, previously pinned source/rule result, scope and unresolved fact requests separately. Do not store university-policy truth from prior LLM prose.
- Add multi-antecedent, “I already said it”, “why?”, interrupted request, topic switch, and session-expiry tests. Changes to durable storage or retention require owner privacy signoff.
- Ensure UI sends actual typed message and structured thread/turn IDs; avoid client-side rewriting that diverges from the server-owned dialogue.

**Exit:** controlled multi-turn cases pass across restarts where supported; no invented student grades, cross-session leakage or stale scope on topic switch.

### Gate 7 — Deployment parity, comprehensive evaluation and release gate (PR-RELEASE)

**Owner:** release lead / evaluator. **Scope:** FM-09 and all unresolved interaction risks.

- Capture Git SHA, test manifest SHA, model identifier/weight hash (where possible), router/compiler flags, retrieval configuration, source/review release, Prolog bundle and frontend/backend version on every candidate run.
- Re-run original 72 cases for comparability **without silently revising their original labels**. Separately score newly adjudicated gold cases and FM-05 compound cases; report English/Filipino/Taglish both per-family and per-language.
- Use explicit outcome classes: correct / incorrect / incomplete / unsupported-by-source / correct abstention / unnecessary clarification / operational failure / untested. Require source evidence for every eligibility verdict and institutional procedure.
- Run ablations (baseline LLM; RAG only; structured catalog; full hybrid/Prolog) under comparable conditions; report curriculum reasoning and policy-document tasks separately.
- Verify candidate deployment with `BINTANONG_ROUTER_COMPILE` effective value, exact source pin, real model and an independent acceptance set. No automatic institutional activation; owner approval required.

**Exit:** repeatable, sourced release report; no critical silent-wrong-answer regressions; documented residual limitations and thesis-claim alignment.

## Suggested ownership and sequencing (parallelizable, not a mandate for team size)

| Workstream | Can work in parallel with | Must wait for |
|---|---|---|
| Baseline/ground-truth audit | all coding work (read-only fixtures) | initial SHA freeze |
| #18 stability | source audit, dialogue design | nothing |
| Semantic routing | source-KB review, RAG retrieval audit | agreement on fixtures/contract surface |
| RAG/completeness | KR review, dialogue design | #18 evidence gate contract |
| KB proof | all others (mostly independently) | original approved PDF/review records |
| #19 executor unit tests | all non-orchestration work | #18 dependency pinned |
| FM-05 final generation integration | non-overlapping evaluation/KR | #19 tests + versioned part contract |
| Conversation ledger | RAG/KR review | typed state + frontend protocol signoff |
| Release qualification | none of the active code mutations | all accepted PRs on one candidate SHA |

## Git protocol for coding agents

1. Each agent reads `AGENTS.md`, `INDEPENDENT_AUDIT.md`, project owner decisions, relevant thesis appendices and source policies before changing behavior. Report any contradictions in the source instead of inventing reconciliation.
2. One worktree and feature branch per failure family. Name branches `fix/p12-<family>-<short-description>`; do not edit shared worktrees or active gathering services.
3. Each PR description: pinned base SHA, confirmed case IDs, root cause, exact changed files, negative/positive tests, model and curriculum pins, observed RED → GREEN result, risk of regressions, and intentionally unaddressed cases.
4. No green claim without the actual command, environment and test output. A local model gateway/API session must not be exercised concurrently with another agent unless a dedicated inference window is agreed.
5. The integration owner deduplicates agent patches, resolves conflicting diagnoses, and merges reviewed, dependency-ordered PRs. Merge #18 first; rebase/retarget #19 only after checking its ancestry. Unrelated changes should target the latest stable base, not pile onto #19.
6. After each merge: run affected regressions and a short smoke suite. After the final merge: a **new frozen acceptance run** with the exact deployed configuration, not assorted outcomes from different branch heads.

## Immediate 5-step assignment

1. Mark PRs #18/#19 as **draft / not yet regression-cleared** and record their exact heads.
2. Have each coding agent return **only reproduced issues and proposed minimal diffs** first; do not merge their fixes unreviewed. Group issues by one root cause and triage P0/P1/P2.
3. Convert the CSV failures #2, #5, #6, #9, #13, #14, #16, #23, #24 into independent source-reviewed fixtures. Add at least four real compound-query fixtures absent from the original PDF.
4. Run #18 targeted suite; then #19 suite on its stacked branch, both compiler settings where relevant. Record any test failure and baseline regression.
5. Approve contract ownership for routing vs orchestration vs generation before coding the full FM-05 integration. Do not delete the `compound_request` guard until the end-to-end per-part answer pipeline has passed.

**Final release criterion:** A checked answer must be tied to the right question part, course, program/edition, session facts and reviewed source/rule version. Any unsupported part must be labeled as unresolved rather than omitted, guessed, or represented as institutional truth.
