# Aurora primary-source comparison — Bintanong P12 architecture boundary
Date: 2026-11-05. This is an **engineering design review**, not a reproduced Aurora benchmark or a validation of Bintanong's live deployment.

## Primary sources (pinned)
- Paper: Lugones et al., *Aurora: Neuro-Symbolic AI Driven Advising Agent*, arXiv:2602.17999v1, sections 3 and 4.6: https://arxiv.org/html/2602.17999
- Aurora GitHub: `Damrl-lab/Aurora` at `d40e98558e079bbe091f963f14afe643b82a53c7`:
  - `backend/README.md`
  - `backend/services/intent_ner/src/main.py`
  - `backend/services/router_api/src/main.py`
  - `backend/services/prolog_kb/validator.py`
  - `backend/services/pipeline_api/gateway.py`
  - `backend/services/deepseek_llm/server.py`
- Bintanong reviewed baseline: `p12-post-gathering-fixes` @ `730344e7bbb889c86ab5c94288455566a9248066`, plus revised diagram from `p12-evaluation-harness`.

## Paper: intended division of labor
1. Intent recognition / entity extraction determines the advising request.
2. BCNF PostgreSQL catalog and SQL filtering select candidate curricular records.
3. SWI-Prolog enforces prerequisites, co-requisites, credit caps, term constraints and degree plans; for long-term plans, the paper describes a heuristic greedy scheduler.
4. The controller fills 5W+1H and COURSE_FACT/PREREQ_CHAIN blocks from validated facts.
5. The LLM communicates the verified recommendation, rather than inventing an eligibility decision.
6. The paper's evaluation used 20 questions over four simulated programs, five runs per query. These do not establish performance on Bintanong's mixed institutional-document domain.

Crucially, Aurora's active retrieval is **structured SQL**, not vector similarity. Aurora's `backend/README.md` says `embedding_svc` is a future extension and currently unused. Thus its description of RAG is not interchangeable with Bintanong's SEA-LION/pgvector retrieval of Handbook, Charter or student-government policies.

## GitHub: important implementation differences from the paper's claims
### Confirmed static defect: prerequisite lookup can return optimistic eligibility
`backend/services/router_api/src/main.py`, `check_prerequisite`, uses `await httpx.post(...)` even though `httpx.post()` is synchronous. Its broad `except Exception: pass` suppresses errors; when the prerequisite list remains empty the code computes `eligible = all(p in taken for p in prereqs)`. Since `all([])` is true, the endpoint contains a *code-level path* to false eligibility. Not runtime reproduced.

### Confirmed static risk: candidate validation fails open
The helper `prolog_ready` within `candidate_ids` catches all errors from the Prolog HTTP request and returns the unfiltered candidate `subset`. A validator outage therefore may allow unverified courses into recommendations. This directly weakens the paper's categorical narrative about hard-constraint validation.

### Concrete scope differences
- Aurora's gateway calls `intent_ner` and passes its advising envelope to the LLM. `intent_ner` uses bounded intent patterns and dispatches course-focused tasks to SQL/Prolog. It does **not** implement Bintanong's policy-document Q&A as a separate vector RAG domain.
- Prolog HTTP endpoints are limited to academic requirements, prerequisite checks, credit/term validation and planning. Aurora also uses Prolog as a course-title fallback; copying that catalog coupling is unnecessary for Bintanong.
- Aurora's LLM prompt trusts upstream facts, but this does not itself verify the entire response; Bintanong's host-owned validation is a stronger place to enforce final claims.

## Consequences for Bintanong
**Keep:**
- Database-backed, curriculum-edition-specific program and course identities.
- Bounded, typed, versioned constraint operation registry; no model-authored arbitrary Prolog goals.
- Explicit separation of catalog fact lookups from actual symbolic rule evaluation.
- Verified evidence and official-curriculum provenance before answer generation.
- Deterministic plans/eligibility outcomes and the LLM as explanation layer.

**Do not port:**
- Universal SQL -> Prolog -> LLM for documentary questions.
- Treating absent source/grade evidence as an affirmative eligibility result.
- Fail-open symbolic recommendations when a worker or retrieval request errors.
- Generalizing Aurora's 20-query synthetic benchmark to Bintanong's 39 curricula and separate institutional sources.
- Aurora's freeform goal-string assembly or broad exception handling.

## Test gates
1. RAG-only procedure/fee request -> zero curriculum or Prolog operations, documentary citations.
2. Printed curriculum catalog lookup -> reviewed catalog facts; no Prolog rule execution.
3. Prerequisite eligibility -> scoped selected-curriculum rule evaluation; incomplete grade/prerequisite evidence yields **unknown**, not eligible.
4. Prolog worker unavailable or invalid output -> held/error answer; never promote unvalidated candidate courses.
5. Mixed prerequisite + document request -> independently executed parts, provenance and per-part completeness; no documentary policy assertion presented as a rule verdict.
6. Mismatched editions and user-stated vs verified grades -> no rule or fact leakage.
7. Independent human-reviewed PDF expectations -> compare against both catalog representations and generated Prolog outputs.
8. Compare compile routing ON/OFF in isolated live model runs, checking *selected operation and target*, not only effective guarded route.

## Status
This review adds primary-source justification to draft PR #18. The initial `domains.py` port is deliberately a routing contract, **not** proof that every runtime path enforces domain ownership or that LLM interpretation is semantically correct. No tests or model inference were executed by this documentation change.
