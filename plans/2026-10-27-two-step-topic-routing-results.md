# Two-step topic routing — candidate implementation and observations

Implemented at `f726e72`;[plan](2026-10-27-two-step-topic-routing-plan.md).
The opt-in candidate fits the observed prompts and preserves guard behavior, but
**fails semantic quality checks**. It is not enabled in the live composition.
Expanded465 remains inactive;corrected78 and all source/runtime pins are unchanged.

## Delivered behavior and verification

`Router(topic_selection=True)` selects at most eight current-menu subjects only
when there are more than eight. Selection uses the same local model/transport.
Strict JSON/ID/duplicate/ambiguity checks bind complete original topic objects;
the existing router receives the unchanged question/context and selected menu.
No selector-generated fact,route,eligibility result or prose becomes evidence.
Invalid selection/transport failure withholds without full-menu fallback. A
candidate document part without a subject cannot dispatch. Exact existing
template/token guards cover selector,detail,style and repairs;no truncation.
Selection counts are separate from routing/style/repair counts. Current small
menus and the default path retain their previous inference messages and schema.

Synthetic TDD:baseline89passed;RED28missing-option failures;GREEN28. Oversized
pytest parameter initially broke Windows' environment-variable limit;short ID
repaired the harness before the valid RED run. New existing-transport integration
tests cover8192exact fit (7416input+768output+8margin) and one-token overflow at
each stage,including a larger repair. Accounting RED1missing selection_calls,
then GREEN. Concurrent/sequential request isolation and style repair covered.

Routing/topic-orchestration/docs/phase-state checks:**477passed/14subtests39.22s**.
Independent final review:**47selector/evaluation tests passed2.62s**,no blocking
finding;minor evaluation-accounting finding fixed before the implementation commit.
Project suite:**6929passed/1595subtests,6skipped,2xfailed,6warnings,1500.25s,exit0**.
It started before the final accounting-only reporting change and three additional
coverage tests;focused477includes those final changes. Final selector/evaluation/
docs check:**57passed2.46s**. Full-suite command:sharedPython3.13 `-X utf8 -B -m
pytest -q -p no:cacheprovider tests --basetemp=<A>/full-suite`;TEMP/TMP under A.
Six skips independently rechecked with `-rs`:four Windows symlink privilege
restrictions,one missing CUDA/ocr-gpu extra,one historical external dataset absent.
The two existing expected failures are refused photo-row layouts (far-left label
tilts sparse row;tight row/box jitter ambiguity). Six warnings concern deprecated
Starlette/httpx/Docling options and the unregistered root-level gpu marker;unchanged.
No dependency/lock change. Ruff/Black/mypy/Bandit unavailable in the shared env;
not installed. Pytest imports/type contracts and manual diff/security review apply,
not a claim of static-type/lint/security-tool success. Phase/diff validation passes.

## Twelve bounded actual-model observations

Eight expanded-menu development cases;four small-menu control observations (two
questions with the switch off/on). These are author-inspected probes,not accepted
new benchmark wording,a final evaluation or a student accuracy rate. No retrieval,
answer generation,checker,answer pipeline,Prolog execution or hosted write occurred.

| Expanded-menu request | Selector seconds | Total routing seconds | Observed result |
| --- | ---: | ---: | --- |
| Another TOR copy,English | 26.08 | 53.17 | Correct TOR-copy subject/printed-fields claim;English |
| Same task,Filipino | 5.88 | 19.76 | Correct TOR-copy subject/printed-fields claim;Filipino |
| Same task,Taglish | 3.38 | 14.51 | TOR subject/claim retained;**Filipino style miss** |
| Passing grade | 4.30 | 24.67 | Grading subject;**eight selected rows omit3.0boundary** |
| Borrow book and another TOR copy | 4.47 | 27.36 | Two parts retained;**wrong requisition subject/limit and TOR instruction-only claim** |
| Graduate admission | 4.03 | 16.54 | Selector suggests admission subjects;semantic router correctly refuses excluded scope |
| CC5 prerequisites in BSCS | 3.30 | 20.37 | Selector suggests policy topic;semantic router keeps structured request,clarifies unresolved entity |
| “What is step1?” after TOR | 3.28 | 18.91 | Prior TOR subject retained;**empty_clarification withholds** |

No catalogue was supplied for these routing-only probes,so the structured case
does not establish real entity resolution or Prolog success. There were32physical
inference calls,zero repairs/transport errors/overflows. Selector inputs2864–2879;
expanded detailed-router inputs4076–4487;style inputs822–833. All observed calls
fit8192with768output+8margin. This is not a universal long/multipart-input proof.

The two seven-topic controls were passing-grade and exam-cheating requests.
Default/enabled pairs had byte-identical messages,schemas,raw responses and parsed
interpretations;both retained RAG/English/two calls. This verifies path preservation,
not complete accepted-roster accuracy. Total routing times23.98/12.95s(default),
15.38/11.21s(enabled);different cache residency prevents attributing the variation
to the switch. No speed improvement or answer-quality gain is claimed.

## Timing and runtime identity

Single sequential observations;existing resident model,one slot,prefix cache on.
First observed selector26.08s is reported separately;inference/kernel/cache
warmness was not controlled. Later selector calls3.28–5.88s. Timers include local
HTTP/connection,props,template/token preflight,inference and JSON parsing within
the stated stage;total routing includes selection,semantic routing and style.
The project suite ran concurrently on the host,so these are diagnostic timings,
not isolated throughput,percentiles or browser end-to-end latency. Startup,
Supabase,retrieval,Prolog,generation/checker,API/session/admission/queueing and
browser/rendering are unmeasured/excluded. Accuracy-first latency contract applies.

Same Gemma4E4B `gemma-4-E4B-it-UD-Q4_K_XL.gguf` under workspace/MODELS;
llama.cpp `b11723-31288c9c6`;container image
`sha256:f66a5229a3e0586339d16155e9fe09c37834d7a7f4134bbdee7360b5a1f2546d`.
Chat template SHA256`74a88f94c57c14e22dcdbe08e94127f42b87c6f584cb73838e73e32126f3f6b3`.
Profile`p09-greedy-prefix-cache-v1`,8192context,768output,120s timeout,temp0/seed0,
reasoning none/thought opener banned,constrained JSON. No restart/download/upgrade.

## Decision and next gate

Keep the candidate inactive. Compact source IDs made the menu fit but failed to
distinguish book borrowing from resource requisition;detailed claim selection
also chose a limitation/instruction instead of the requested process. The grading
claim subset and follow-up/style errors remain visible. Do not call validated
RAG/schema decisions correct answers or tune an unbounded prompt sweep.

Next:repair source-labelled service/claim discrimination using the actual reviewed
headings and field context,alongside the pending independent service/image
structural bindings. Preserve original words/limits and existing approvals;pause
only for new consequential source ambiguity under delegated-review rules.
Metadata diagnosis:the retained borrowing record already contains the approved
`service_title_and_description` value “5. BORROWING OF BOOKS Students and other
stakeholders requesting books from the library.” TOR uses `service_context`.
`_reviewed_topic_context` recognizes `service_title`/`description`/numbered clauses,
so these legacy names produce no source context. The compact selector currently
projects IDs only;changing the context mapper alone would not repair its labels.
The requisition record's printed title has a recorded malformed-source-condition
hold tied to a copied description;do not globally relax that guard to show labels.
Use reviewed field bindings for a bounded heading projection and separately
preflight its exact prompt;do not invent semantic aliases or truncate limitations.
After that,rerun these exact saved failures and focused accepted regressions before
expanded answer observations. Per-request retrieval budgets,hosted normalized
draft synchronization,governed release and full answer-quality gates remain.
No frontend integration,source promotion,activation,school approval or phase advance.

## Recovery evidence

Ignored root:`C:/Coding-projects/bintanong_workspace/audit-evidence/p11-two-step-routing-20261027`.
`red-clean.log`,`accounting-red.log`,`focused.log`,`verified.log`;`observe_routing.py`,
12raw JSON receipts,`observations.log`,`observation-summary.json` retain all
messages/schemas/raw outputs,timings and per-call runtime metadata. Public source
probes only,no private uploads/grades. Full-suite log/exit receipt retained there.
Reproduce with sharedPython3.13 `-X utf8 -B -m pytest -q -p no:cacheprovider` and
external basetemp;exact focused selector is all `tests/test_routing_*.py`,
`test_orchestration_document_topics.py`,`test_orchestration_multi_topic.py`,
`test_docs_hygiene.py` and `.agents/skills/bintanong-phase-handoff/tests/test_phase_state.py`.
