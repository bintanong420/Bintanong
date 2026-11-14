# Evaluation Testing Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let the owner type the 72 benchmark queries into a gated dev page, see both top-3 kNN lists and the answer key, mark results, and produce Accuracy/Precision/Recall/F1 from the saved runs.

**Architecture:** A contextvar observer records what `RetrievalEngine` ranks, without changing the answer. A dedicated `/evaluation/*` router, mounted only by launcher configuration, runs each query through the unchanged `ChatTurns` and pipeline in an isolated session and appends JSONL records outside Git. An offline scorer turns records and keys into a report.

**Tech Stack:** Python 3.13, FastAPI, Next.js 16, TypeScript, node:test, pytest. No new dependencies.

**Spec:** [feasibility and decisions](2026-11-06-evaluation-testing-mode-plan.md); metric rules from master section 17.3. No PRD change: this is dev tooling implementing the approved master evaluation section, not product scope.

## Global Constraints

- Roster is exactly the 24 rows x 3 languages = 72 queries in `Context/The_Bintanong_Benchmark_Queries (4).pdf` (SHA-256 starts `be467633`).
- Top 3 only; `min_similarity=.25`; all-chunk list keeps undergraduate scope and pinned document versions, and drops only the topic filter.
- All-chunk results are display/scoring data and must never reach the generator.
- Mode is off unless `BINTANONG_EVALUATION_TOKEN` is set; off or wrong token returns 404. Never set it on main/gathering (3216/8021).
- Student `/chat`, `stream.py`, `student-transport.ts`, rate limit and session store behavior stay unchanged.
- Serial model use: every run takes a normal `AnswerAdmission` reservation.
- Answer keys and run logs are source-derived: keep them under ignored `C:/Coding-projects/bintanong_workspace/audit-evidence/evaluation-testing-mode-20261106/`; tracked tests use synthetic fixtures.
- Metrics are development results: report single-author judging, no refusal cases, and questions that informed earlier fixes.
- Python tests: `$PY=C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`, `$PY -B -m pytest -q -p no:cacheprovider --basetemp=<ignored dir>`. Frontend: `npm run test:ui`, `npm run typecheck` in `frontend/`.
- Commits follow `.agents/skills/conventional-commits/SKILL.md`, explicit staging, no attribution trailers (owner).

## Review Focus

1. Misrouted retrieval question (clarification or Prolog, so no topic search): all-chunk list still appears; topic-bound scores zero rather than being skipped. Tests in Tasks 1 and 3.
2. Question with several topics: each search stays separate on the page and scoring uses 3 x searches as k. Tests in Tasks 1 and 3.
3. Model outage during a run: saved as `infrastructure_error`, shown plainly, not scored; the next attempt counts. Tests in Tasks 1 and 3.
4. Typed text with a typo: run kept with `case_id: null`, page warns, scorer excludes and lists it. Tests in Tasks 1, 3 and 4.
5. Repeating a query after seeing a poor result: first completed run counts, later ones are listed. Test in Task 1.

---

### Task 1: Roster and metric scorer

**Files:**
- Create: `evaluation/benchmark/roster-72.json`, `evaluation/system_metrics.py`
- Test: `tests/test_evaluation_system_metrics.py`

**Interfaces:**
- Produces roster rows `{case_id, row, subset, language, question}`; `case_id` is `A01-EN|TG|TL` to `B24-EN|TG|TL` (A = rows 1-10, B = rows 11-24; EN English, TG Tagalog, TL Taglish).
- Produces `load_roster() -> list[dict]` and `normalize_question(text) -> str` (collapse whitespace, casefold).
- Produces `select_runs(records) -> SelectedRuns` with `.scored: dict[case_id, record]`, `.reruns`, `.unmatched`, `.failed`.
- Produces `retrieval_case_metrics(returned_ids: list[str], relevant_ids: set[str], searches: int) -> dict` with `hits, precision_at_3, precision_returned, recall_at_3, f1_at_3, hit_at_3`.
- Produces `route_metrics(pairs: list[tuple[str, str]]) -> dict` (pairs are expected, predicted) with `accuracy, per_class, macro_f1, macro_classes, confusion`.
- Produces `answer_metrics(rows: list[dict], partial_counts: bool) -> dict` with `accuracy, precision, recall, f1, n`.

- [ ] **Step 1: Write failing tests**

```python
def test_roster_is_exactly_24_rows_by_3_languages():
    rows = load_roster()
    assert len(rows) == 72 and len({normalize_question(r['question']) for r in rows}) == 72
    assert {r['row'] for r in rows} == set(range(1, 25))

def test_retrieval_example_and_single_chunk_ceiling():
    m = retrieval_case_metrics(['a', 'x', 'b'], {'a', 'b', 'c', 'd'}, searches=1)
    assert (m['precision_at_3'], m['recall_at_3']) == (2/3, 1/2) and round(m['f1_at_3'], 2) == .57
    one = retrieval_case_metrics(['a'], {'a'}, searches=1)
    assert one['precision_at_3'] == 1/3 and one['precision_returned'] == 1 and one['f1_at_3'] == .5

def test_no_search_scores_zero_not_skipped():
    m = retrieval_case_metrics([], {'a'}, searches=0)
    assert (m['precision_at_3'], m['recall_at_3'], m['hit_at_3']) == (0, 0, False)

def test_two_searches_use_k_of_six():
    assert retrieval_case_metrics(['a', 'b', 'c', 'd', 'e', 'f'], {'a'}, searches=2)['precision_at_3'] == 1/6

def test_unkeyed_empty_relevant_set_has_undefined_recall():
    assert retrieval_case_metrics(['a'], set(), searches=1)['recall_at_3'] is None

def test_macro_f1_uses_classes_with_gold_and_keeps_predicted_only_in_confusion():
    m = route_metrics([('RAG', 'RAG'), ('RAG', 'Hybrid'), ('Symbolic', 'Symbolic')])
    assert m['accuracy'] == 2/3 and 'Hybrid' not in m['macro_classes'] and m['confusion']['RAG']['Hybrid'] == 1

def test_answer_precision_recall_definitions():
    rows = [dict(expected='answer', given=True, mark='correct'),
            dict(expected='answer', given=True, mark='wrong'),
            dict(expected='answer', given=False, mark='wrong'),
            dict(expected='clarification', given=False, mark='correct')]
    m = answer_metrics(rows, partial_counts=False)
    assert (m['accuracy'], m['precision'], m['recall']) == (1/2, 1/2, 1/3)

def test_partial_is_wrong_in_strict_and_right_in_lenient():
    rows = [dict(expected='answer', given=True, mark='partial')]
    assert answer_metrics(rows, partial_counts=False)['accuracy'] == 0
    assert answer_metrics(rows, partial_counts=True)['accuracy'] == 1

def test_first_completed_run_counts_and_failures_or_unmatched_do_not():
    selected = select_runs([run('r1', 'B11-EN', 'infrastructure_error'), run('r2', 'B11-EN'), run('r3', 'B11-EN'), run('r4', None)])
    assert selected.scored['B11-EN']['run_id'] == 'r2'
    assert [r['run_id'] for r in selected.reruns] == ['r3']
    assert [r['run_id'] for r in selected.unmatched] == ['r4'] and [r['run_id'] for r in selected.failed] == ['r1']

def test_mixed_commit_or_release_is_refused():
    with pytest.raises(ValueError, match='mixed_runs'):
        select_runs([run('r1', 'B11-EN', commit='a'), run('r2', 'B12-EN', commit='b')])
```

- [ ] **Step 2: Run and confirm failure** (`$PY ... tests/test_evaluation_system_metrics.py`; expected: import error for `evaluation.system_metrics`).
- [ ] **Step 3: Transcribe the roster and implement the functions.** Copy exact wording, including typos. Empty `returned_ids` gives zeros; `precision_at_3` is hits / (3 x max(searches, 1)); F1 of zero precision and recall is 0.
- [ ] **Step 4: Check every roster word against the PDF.** Run a one-off check that each question's tokens appear in `pdftotext` output. Expected: no missing tokens.
- [ ] **Step 5: Add the CLI and test it.** `python -m evaluation.system_metrics --runs <jsonl> --keys <json> --out <dir>` writes `report.json` and `report.md`: route, retrieval (separately for each list, by language and overall, including `precision_returned`), and strict/lenient answer metrics, plus key disagreements, reruns, unmatched, failures and the disclosures from Global Constraints. Unkeyed rows take relevance from owner marks across that row's language runs and label recall "pooled". For keyed rows the key decides and disagreements are listed.
- [ ] **Step 6: Run tests; expected pass.**
- [ ] **Step 7: Commit** `feat(evaluation): add benchmark roster and metric scorer`.

### Task 2: Retrieval observer and all-chunk search

**Files:**
- Create: `backend/bintanong_retrieval/observation.py`
- Modify: `backend/bintanong_retrieval/engine.py`
- Test: `tests/test_retrieval_observation.py`

**Interfaces:**
- Produces context manager `observe_retrievals() -> Iterator[list[dict]]`; entries `{query, subject_id, requested_claims, candidates, emitted_chunk_ids}`.
- Produces `RetrievalEngine.search_all_chunks(request: RetrievalRequest, top_k: int | None = None) -> list[dict]`, returning raw RPC rows; `top_k` must be 3, 5 or 8 (the RPC's allowed values).

- [ ] **Step 1: Write failing tests**

```python
def test_observer_records_ranked_candidates_and_what_was_sent_on():
    with observe_retrievals() as seen:
        engine.retrieve(request, subject_id='topic', requested_claims=('claim',))
    assert seen[0]['query'] == request.query and seen[0]['subject_id'] == 'topic'
    assert [row['chunk']['chunk_id'] for row in seen[0]['candidates']] == ['a', 'b', 'c']
    assert seen[0]['emitted_chunk_ids'] == ['a']

def test_observation_crosses_the_adapter_worker_thread():
    async def scenario():
        with observe_retrievals() as seen:
            await RetrievalAdapter(engine, research=True).retrieve(request, subject_id='topic', requested_claims=('claim',))
        return seen
    assert asyncio.run(scenario())

def test_no_observer_means_identical_response():
    assert engine.retrieve(request) == baseline_engine.retrieve(request)

def test_all_chunk_search_drops_only_the_topic_filter():
    engine.search_all_chunks(RetrievalRequest('q', 'release-test', scope=('audience:undergraduate',), document_version_ids=('v',)))
    assert 'p_chunk_ids' not in client.params and client.params['p_scope'] == ['audience:undergraduate']
    assert client.params['p_top_k'] == 3 and client.params['p_min_similarity'] == .25 and client.params['p_version_ids'] == ['v']

def test_all_chunk_search_cannot_change_a_later_answer():
    before = engine.retrieve(request, subject_id='topic', requested_claims=('claim',))
    engine.search_all_chunks(request)
    assert engine.retrieve(request, subject_id='topic', requested_claims=('claim',)) == before
```

- [ ] **Step 2: Run and confirm failure** (import error for `observation`).
- [ ] **Step 3: Implement.** Use a `ContextVar` holding the list. `asyncio.to_thread` copies context, so the list reaches the worker. In `engine.retrieve`, record candidates immediately after the RPC `status` and release checks so early policy returns are still seen; set `emitted_chunk_ids` beside the existing `_trace` call. A storage failure in `search_all_chunks` raises to the caller.
- [ ] **Step 4: Run new tests plus `tests/test_retrieval_engine.py tests/test_retrieval_evidence_policy.py`; expected pass.**
- [ ] **Step 5: Commit** `feat(retrieval): observe ranked candidates for evaluation`.

### Task 3: Evaluation service and gated router

**Files:**
- Create: `backend/bintanong_api/evaluation.py`
- Modify: `backend/bintanong_api/app.py`, `backend/bintanong_api/research.py`, `backend/bintanong_api/research_app.py`
- Test: `tests/test_api_evaluation.py`

**Interfaces:**
- Consumes `observe_retrievals`, `search_all_chunks`, `load_roster`, `normalize_question`.
- Produces `evaluation_from_env(pipeline, releases, curricula, course_labels) -> EvaluationService | None`, reading `BINTANONG_EVALUATION_TOKEN`, `_LOG`, `_KEYS`, `_COMMIT`. No token gives `None`; a token with any other value missing, or a log path inside a Git checkout, raises `ValueError` at startup.
- Produces `ApiServices.evaluation: object = None`; `create_app` mounts `evaluation_router` only when set.
- Routes, all requiring header `x-bintanong-evaluator`: `GET /evaluation/cases`, `POST /evaluation/run {question}`, `GET /evaluation/runs`, `POST /evaluation/runs/{run_id}/judgment {chunk_marks, answer_mark, note}`.
- Record: `{schema_version:'bintanong-evaluation-run-v1', run_id:'run-<16 hex>', code_commit, release_id, case_id, question, outcome:'completed'|'infrastructure_error', error, route_label, topics, answer:{status, language, text, sources}, searches:[{query, topic_bound:[row], all_chunks:[row]}]}`; row is `{rank, chunk_id, similarity, text, source_label, pages, section_path, sent_to_writer, attached_count}`.

- [ ] **Step 1: Write failing tests** with a fake pipeline and fake engine, covering:
  - `test_off_by_default_and_wrong_token_are_404`: no service gives 404; wrong header gives 404, compared in constant time.
  - `test_partial_configuration_refuses_startup`: token without log path raises `ValueError`.
  - `test_log_inside_git_checkout_refuses_startup`.
  - `test_run_returns_both_lists_answer_and_key`: for B11-EN, `searches[0]` has both lists, `sent_to_writer` is set, key returned.
  - `test_control_reply_still_gets_all_chunk_list`: no topic search gives `topic_bound == []`, three `all_chunks`, query is the normalized text.
  - `test_two_topics_give_two_searches`.
  - `test_each_run_has_a_fresh_session`: the second run's context has no first-run dialogue or facts.
  - `test_pipeline_failure_is_saved_as_infrastructure_error`: HTTP 200 with that outcome and empty searches.
  - `test_unmatched_text_is_kept_with_null_case`.
  - `test_run_uses_admission_but_not_student_quota`: held slots give 503 `answers_busy`; `question_limit` unchanged.
  - `test_judgment_is_appended_and_survives_reload`: a new service on the same log returns the mark.
  - `test_unknown_run_or_invalid_mark_is_rejected`: `answer_mark` must be `correct`, `partial` or `wrong`.
  - `test_student_chat_stream_is_unchanged`: same parts with evaluation mounted and not.
- [ ] **Step 2: Run and confirm failure** (import error).
- [ ] **Step 3: Implement `EvaluationService`.** Own a private `SessionStore` and `ChatTurns`; wrap the pipeline only to capture the routed value. Issue and delete one session per run. Wrap the turn in `observe_retrievals()`. `route_label` is `decision.route or decision.control`. Afterward build one all-chunk search per observed query, or from `routed.query.normalized_text` (falling back to `prepare_query(question)`) when none was observed, using `await releases.pin()` for release, scope and versions; run it through `asyncio.to_thread`. Row `text` is `chunk['source_text'] or chunk['text']`, matching `context.py`. Keys are read at startup; a run returns the key entry covering its `case_id`, or `key_status:'human_judged'`.
- [ ] **Step 4: Implement the router and wire both factories.** Take `admission.reserve(account_id='evaluator')`, enter `reservation.running(...)`, release in `finally`. Do not call `question_limit`. Keep the existing `authorize` dependency. Append one JSON line per record under a lock.
- [ ] **Step 5: Run new tests plus `tests/test_api_stream.py tests/test_api_chat_turns.py tests/test_api_research_factory.py tests/test_api_research_composition.py`; expected pass.**
- [ ] **Step 6: Commit** `feat(api): add gated evaluation runs`.

### Task 4: Proxy and evaluation page

**Files:**
- Modify: `frontend/lib/student-proxy.ts`
- Create: `frontend/app/dev/evaluation/page.tsx`, `frontend/app/dev/evaluation/evaluation.module.css`, `frontend/lib/evaluation-client.ts`
- Test: `frontend/tests/student-proxy.test.mjs`, `frontend/tests/evaluation-client.test.mjs`, `frontend/tests/browser/evaluation-mode.mjs`

**Interfaces:**
- Consumes the Task 3 routes and record.
- Produces `matchCase(text, cases) -> case | null`, `runEvaluation(question, passcode)`, `saveJudgment(runId, marks, passcode)`, `listRuns(passcode)`.

- [ ] **Step 1: Write failing tests.** Proxy: the four evaluation paths and methods are allowed; `x-bintanong-evaluator` reaches the API only on those paths and is stripped from `/chat`; other `/evaluation/*` paths return 404. Client: `matchCase` ignores whitespace and case, and returns null for a typo.
- [ ] **Step 2: Run `npm run test:ui`; confirm failure.**
- [ ] **Step 3: Implement proxy allowlist and client.** Passcode is held in React state only, never stored.
- [ ] **Step 4: Implement the page.** Passcode field; all 72 queries listed on the page, grouped by row and language, with done/failed status; clicking one fills the question box, which can also be typed in, with a "not in the 72, will not be scored" warning; Run button with waiting state. Result: route, topics, answer, sources; answer key panel, or "No answer key: your marks decide"; two columns, Topic-bound and All chunks, per search (stacked at phone width), each row showing rank, similarity, source, page, sent-to-writer badge, key badge and relevant yes/no. Answer mark buttons, note, progress `n/72` and a saved-run list that reloads from the server after refresh. An off or wrong passcode shows "Evaluation mode is off or the passcode is wrong."
- [ ] **Step 5: Add a browser check** using a fake API: run, mark, reload, see marks; no horizontal scroll at 375 px.
- [ ] **Step 6: Run `npm run test:ui`, `npm run typecheck`, the browser check; expected pass.**
- [ ] **Step 7: Commit** `feat(frontend): add evaluation testing page`.

### Task 5: Draft answer keys with the owner

**Files:**
- Create (ignored): `audit-evidence/evaluation-testing-mode-20261106/answer-keys.json`, draft script beside it.

**Interfaces:**
- Produces entries `{key_id, case_ids, expected_route, expected_outcome:'answer'|'clarification', key_status:'keyed'|'human_judged', relevant_chunk_ids, expected_facts, source_note}`.

- [ ] **Step 1: Set expected routes.** Rows 1-6, 8, 9 `Symbolic`; row 7 `clarify`; rows 10-24 `RAG` unless owner review shows a part needs Prolog.
- [ ] **Step 2: Build pools for rows 10-24.** Union the reviewed topic's chunks with `search_all_chunks(top_k=8)` across each row's three wordings. Candidate = chunk text states a fact needed for the answer.
- [ ] **Step 3: Show the owner short batches inline** (row, question, exact printed text, source page, proposed relevant or not). Apply `plans/source-gap-policy.md`: a gap stays a gap. Where no acceptable key exists, record `human_judged`. Rows 12-15, 18 and 20 get per-language keys where wording differs.
- [ ] **Step 4: Validate.** All 72 cases covered exactly once; every chunk id exists in the release; record the file's SHA-256 in current progress. Freeze before the owner's full run.
- [ ] **Step 5: Commit plan/progress notes only** `docs(plans): record frozen evaluation answer keys`.

### Task 6: Pilot, full run and report

**Files:**
- Modify: `docs/evaluation/phase12-evaluation-report.md` (section 7), `plans/plan_current_progress/current_progress.md`
- Create: `plans/<run date>-evaluation-metrics-results.md`

- [ ] **Step 1: Run the full Python and frontend suites on the candidate commit**; report totals. Commit nothing new after this point except docs.
- [ ] **Step 2: Start the dev API (8022) and web (3217) with the four evaluation variables**; confirm 8021 returns 404 for `/evaluation/cases`.
- [ ] **Step 3: Agent pilot with 5 cases** (A01-EN, A07-EN, A10-TL, B15-TL, B20-TL), serial. Expected: lists as designed, row 7 asks for a program. Delete the pilot log before the owner's run; fix defects with a regression test and refreeze.
- [ ] **Step 4: Owner types all 72 and marks them.** Agent spends no tokens here.
- [ ] **Step 5: Run the scorer.** Expected: 72 scored or each exception listed.
- [ ] **Step 6: Write results, replacing "not measured" for only the metrics actually measured.** State commit, release, key hash, disclosures and remaining unmeasured items (RAGAS, BATAYAN, Bintu-1 baseline).
- [ ] **Step 7: Commit** `docs(evaluation): report benchmark metrics`.
