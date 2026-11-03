# Bintanong backend implementation plan for undergraduate curricula

**Student outcome** · A PalSU undergraduate can select their program, major or track and curriculum edition, tell Bintanong what they passed or are taking, and get an answer grounded in their own prospectus. Follow-ups reuse the facts already supplied in this chat. Bintanong asks the student for a missing result and identifies a gap in the prospectus when the source itself is incomplete.

**Baseline** · 3 November 2026. Reviewed `bintanong420/Bintanong`, branch `p12-evaluation-harness`, commit `395079c`. The research release records 39 undergraduate curricula, including separate tracks and two BSCS editions. Tasks 1–3 deliver single-course advising through the existing FastAPI, Bintu/Gemma and SWI-Prolog/Janus pipeline. Task 4 adds semester planning wherever the prospectus covers the requested term. [Inspected revision][revision] · [Release coverage][coverage] · [Thesis routing diagram][diagram]

## How the same code serves each program

| Decision | Implementation rule |
| --- | --- |
| Which curriculum applies? | Validate the program and curriculum IDs against `GET /curricula`. Major or track may already be encoded in the program ID. When “BSBA” matches multiple majors and no selection settles it, ask the student to choose from the reviewed matches. Reuse a valid selection on follow-ups. Clarify a conflict between the message and the picker. An unavailable campus or edition gets a coverage message. [API scope check][chat] · [Program aliases][programs] |
| Which course and rule apply? | Resolve the printed code, title or reviewed alias **inside the selected curriculum**. Use `build_multi_research_resources()` and `MultiCurriculumSymbolicAdapter` to execute against that curriculum’s pinned bundle. Generated verdicts and citations must match the same release member. Keep course codes, prerequisite pairs, term lengths and titles out of application branches and shared prompts. [Release builder][multi] · [Curriculum dispatch][adapter] |
| What can carry forward? | Remember `session_id`, `program_id`, `curriculum_id` and canonical `course_id`. A scope change cancels the pending question. Transfer credit, a shared GE code or a similar title cannot establish equivalence on its own. A later release must revalidate the course identity before reusing a fact. Always evaluate the current rules afresh. |
| How does another program join? | Review its prospectus, aliases, rules and year/term coverage, then link the versioned ledger to the research release. Add an independently reviewed example and one gap or ambiguity case. Existing rule types use the same runtime. An unrepresented requirement, such as an unreviewed minimum grade, stays unresolved until its semantics and evidence have been reviewed. [Release ledger loader][loader] · [Curriculum authoring][authoring] |

## First conversation using the original BSCS case

Assume the student selected BSCS 2018–2019. They have supplied no earlier result for CC 5/L.

| Turn | Student | Expected Bintanong reply |
| --- | --- | --- |
| 1 | “Natake ko na yung CC5/L. Can I take Information Assurance and Security na ba?” | “CC 5/L ang prerequisite ng CS 13/L – Information Assurance and Security. Naipasa mo ba ang CC 5/L?” |
| 2A | “Oo, pasado.” | “Oo. Pasok ka sa prerequisite ng CS 13/L – Information Assurance and Security, base sa sinabi mong naipasa mo ang CC 5/L.” |
| 2B, alternate reply | “Hindi ko pa napasa.” | “Hindi pa. Kailangan mong maipasa ang CC 5/L bago mo makuha ang CS 13/L.” |
| 3, after 2A and an unrelated question | “Pasok ba ako sa prerequisites ng CS 13/L?” | Recheck the rule using the earlier self-report. Give the conclusion without asking about CC 5/L again. |

Show the curriculum source beside the answer. Attribute the grade to the student. Wording can vary. The target, condition, verdict and provenance must agree.

| BSCS curriculum | Target | Required by the reviewed prospectus |
| --- | --- | --- |
| Effective SY 2018–2019 | CS 13/L · Information Assurance and Security | CC 5/L |
| Effective SY 2018–2019 | CC 5/L · Information Management | Both CC 3/L and CC 4/L |
| Proposed SY 2025–2026 | CS 13/L · Computer Security and Information Assurance | Both CS 6/L and CS 10/L |

For Lawrence’s question, “Can I take CC 5/L if I haven’t passed CC 3/L and CC 4/L?”, the old-curriculum answer is “No. Under that assumption, you are missing both prerequisites for CC 5/L.” If the student is posing a what-if, a later question about their actual record must still start from the facts they reported as true.

The attached prospectuses show these rows. The older PDF matches the repository’s recorded source hash. The proposed PDF shows the same CS 13/L row but has a different file hash. Use the release-pinned source for executable tests. [2018–2019 review][old] · [Proposed 2025–2026 review][proposed]

## Cross-program acceptance cases

**Run the same engineering question in two fresh chats.** In each, independently state “I passed Math 11/L. Hindi ko pa napapasa ang Math 12/L, pero naka-enroll ako sa Math 12/L this term. Can I take Phy 11/L this term?” The reviewed 2018–2019 editions require opposite answers.

| Selected program | Must already have passed | May have passed or be taking in the target term | Expected conclusion |
| --- | --- | --- | --- |
| BS Civil Engineering | Math 12/L | Math 11/L | **Prerequisite unmet.** The student explicitly has not passed Math 12/L. [Civil Engineering review][civil] |
| BS Mechanical Engineering | Math 11/L | Math 12/L | **Prerequisites met.** The student passed Math 11/L and is taking Math 12/L in the same term as Phy 11/L. [Mechanical Engineering review][mechanical] |

Run the following through the same `/chat` route, memory store and answer validator. Treat these as expected outcomes for the proposed work.

| Curriculum | Scenario | Acceptance criterion |
| --- | --- | --- |
| BS Architecture 2018–2019 | “Natake ko na ang ACAD-1/L. Pwede na ang ACAD-2/L?” Then “Oo, pasado.” | Ask about passing ACAD-1/L once. Resume the ACAD-2/L check and give a positive prerequisite verdict using the printed codes. [Architecture review][architecture] |
| BS Nursing 2018–2019 | For NCM 15-103 the student reports passing NCM15-101A, NCM15-101B and NCM15-102A. | Ask only about NCM15-102B. Confirming a pass completes the four-part rule. Keep A and B as distinct course records. [Nursing review][nursing] |
| BSBA, Business Economics 2018–2019 | “Can I take BE 2001? I haven’t taken GE-PC yet.” | Return **prerequisite unmet** and identify GE-PC. Also test the genuinely different case of BAC 5, whose reviewed cell explicitly says “None.” [Business Economics review][business] · [Recorded regression][samples] |
| BSEd, Mathematics 2018–2019 | A student asks about FS 2, whose requirement refers to all professional education and specialization courses. | Explain the printed condition. The bundle does not establish the complete required set, so withhold a positive verdict even if the student says they passed several named courses. [Mathematics Education review][education] |
| BS Midwifery 2019–2020 | “What can I take in second year, first sem?” | State that the reviewed prospectus covers only years three and four. An empty year-two lookup cannot establish that no courses exist. The student can still ask about a covered course, such as Mid Res 1 after passing Biostat 1. [Midwifery review][midwifery] |

## What the backend does today

| Component | Verified behavior | Change needed |
| --- | --- | --- |
| Chat and session | `ChatTurns.prepare()` reads the last user message. `capture()` retains identifiers for a course or topic and supports a pending transfer-direction question. Confirmed upload rows can become session facts. The project’s multi-turn report explicitly records that chat-stated grades do not carry. | Carry a student’s explicit course results and the exact prerequisite question awaiting a reply. [Chat][chat] · [Conversation context][conversation] · [Multi-turn findings][observations] |
| Routing and rules | The model proposes typed operations. The host grounds claims and passes asserted facts to the symbolic adapter for this request. The router currently maps “not yet passed” and “not taken” to the internal `failed` bucket. Prolog already distinguishes an explicit unmet condition from missing evidence. | Preserve what the student actually said before storing it. Reuse the existing engine and versioned rules. [Routing prompt][prompt] · [Orchestrator][orchestrator] · [Prolog engine][engine] |
| Answer generation | A ready `Symbolic` result returns from `Generator.generate()` before a final model inference. The student view converts condition codes into phrases. The repo’s recorded BSCS example still says “conditions” and then lists the course result. | Let Bintu compose the student-facing explanation from checked evidence. Keep the verdict fixed. [Generator][generator] · [Student presentation][presentation] · [Recorded replies][samples] |
| Semester lookup | `list_term_courses()` returns reviewed curriculum placement. The router rejects multiple proposed operations in one turn. `list_affected_courses` identifies potential dependencies. | Add one bounded operation that checks each candidate’s prerequisites. A dependency list alone cannot answer what the student can take. [Term lookup][term] · [Route validation][routing] |

## 1. Capture exactly what the student said

- [ ] Start with a parameterized failing test in `tests/test_routing_validation.py`. Run the same “natake ko na” exchange for fictional courses with a number, a hyphenated lab suffix and an A/B pair. Then replay the source-backed BSCS and Architecture examples on the research release. Even if the model proposes `passed`, the host must require evidence of a pass. Match reviewed aliases within scope and ask when more than one course fits.
- [ ] Extend `backend/bintanong_routing/{contracts,wire,prompt,validation}.py` to distinguish explicit pass, explicit failure, not yet passed, never taken and taken with result unknown. Keep enrollment as a separate dimension. Resolve the source phrase to one course in the selected program and curriculum. Bind the negation and speaker to each course in multi-course sentences. A bare number or INC stays unresolved without an applicable reviewed interpretation.
- [ ] In `backend/bintanong_orchestration/adapters.py`, project only the facts a rule can use. An explicit pass satisfies a completion check. An explicit failure, “not yet passed” or “never taken” establishes noncompletion for that check. A bare “took it” supplies neither outcome. Keep the original distinction so the answer never calls a student’s unattempted course a failure.
- [ ] Support a standalone statement such as “I passed CC 5/L” even when it contains no question. Acknowledge the scoped fact. A quotation about a friend contributes no fact about the speaker. For an explicit what-if, pass the hypothetical premise only to that check, label the answer conditional and discard the premise afterward. When “if” introduces a genuine past self-report, use the meaning of the clause. Ask if ownership or timing is unclear.

**Exit check** · “I failed CC 3/L and CC 4/L” produces two explicit negative facts. “If I failed both…” produces zero remembered facts. “I passed CC 3/L but haven’t taken CC 4/L” preserves both statuses and their respective courses. Run the same contrasts in English, Filipino and Taglish.

## 2. Remember facts and complete pending checks in the active chat

- [ ] Extend `backend/bintanong_private_context/{sessions,conversation}.py` and `backend/bintanong_api/chat.py`. Keep two things in session memory. One is the set of student-supplied facts across turns. The other is the pending question, with its original operation, target course, missing prerequisite, question type and scope. For the demo, the target is **CS 13/L** and the missing result belongs to **CC 5/L**.
- [ ] Key each fact by session, program, curriculum edition, course and fact dimension. Attach the applicable academic period to a concurrent-enrollment fact. “Taking it this term” cannot satisfy a next-term co-requisite without evidence for that term. A completed pass can still apply in a later term under the same edition. Retain a source kind (`user_statement` or `private_upload`) and an opaque turn or confirmation reference. Discard the raw text after validation. Under the session lock, read fresh state and commit accepted facts and pending context with turn completion. Use stable message identity for retries and regeneration. Keep the 256-fact limit and 30-minute idle expiry. Apply the same scoped merge to upload confirmations and chat corrections. [Session store][sessions] · [Existing privacy contract][privacy]
- [ ] Bind “Oo, pasado” only to a single pending positive completion question in the same scope. For “Are you taking Math 12/L this term?”, bind a bare yes to **enrollment in that term**. If two courses could be meant, ask which one. After an unrelated turn or scope change, retire the old question as a target for bare “yes.” Keep earlier explicit facts available for later named questions in their own scope. A direct correction can replace an earlier self-report. Conflicting statements or a disagreement with a confirmed upload require clarification before using the disputed fact. Re-run the check after resolution.
- [ ] Cover cancellation, failed checks, duplicate sends, regeneration, expiry, New chat, and switching account or curriculum. A failed or cancelled turn commits no partial memory. A deleted or expired session stays deleted. Deduplicate facts resent by the existing clarification UI. A normal typed follow-up must also work when the client sends only its new message. Update any UI copy that describes which previously supplied details can influence an answer. [Existing clarification client][client]

**Exit check** · Drive the BSCS and Architecture exchanges through `POST /chat` as a guest and in a signed-in session. The original chat remembers the result. A fresh chat asks again. In a separate test, switch curricula between the clarification and a bare “yes.” Zero facts may transfer across the switch. Include `tests/test_api_chat_turns.py`, `tests/test_private_context_conversation.py` and `tests/test_private_context_isolation.py`.

## 3. Give Bintu the Prolog result and return a clear conclusion

- [ ] Reuse `DecisionOutcome`, `RequirementView` and `PreparedEvidence` in `backend/bintanong_contracts/symbolic.py` and `backend/bintanong_generation/evidence.py`. Resolve the target’s printed code and title, prerequisite labels, satisfied/unmet/missing conditions, source span, release and student-fact origin. Allow only a registered operation with bound arguments. This gives developers an inspectable record of which facts and rules produced the answer. Keep that record request-local. Only scoped facts and identifiers carry into later checks. Persistent diagnostics can count outcomes, fallbacks and timings. Exclude raw chat, student grades and model chain-of-thought from persistent logs and institutional storage.
- [ ] Preserve the reviewed rule structure when explaining a decision. Use “both” for `all_of`, “either” for `any_of`, and “passed or taking in the same term” for a co-requisite. A blank, a missing referenced course and an explicit reviewed “None” must stay distinguishable. Generate wording from these rule types so the same explanation works for Engineering, Education and Nursing. [Generic rule evaluator][engine]
- [ ] Add a bounded post-Prolog Bintu call for personal prerequisite answers in `backend/bintanong_generation/generator.py`. Handle both the ready decision and the current early-return path for a checked `unknown`. Give it the checked evidence and reply language. It should choose which verified conditions explain the verdict and how to ask for any missing fact. Use English for English input and natural Taglish for Filipino or Taglish input. For document procedures mixed into the same question, retain the existing Hybrid route and its independent citations.
- [ ] In `backend/bintanong_generation/{render,validation}.py` and `backend/bintanong_api/presentation.py`, put the scoped conclusion first. Bind course names, verdict polarity, condition states and citation identities to the evidence. Constrain the model’s selectable reasons and next actions to those supplied by the host. Reject even a schema-valid draft whose wording reverses a condition or promises enrollment. If wording fails validation or times out, render the same verified facts in plain English or Taglish. If Prolog itself failed, return unavailable. A missing student result triggers a targeted question. Missing rule coverage gets a source-gap explanation.

**Exit check** · In `tests/test_generation_pipeline.py` and `tests/test_api_presentation.py`, verify the post-Prolog model input and the first sentence actually streamed to the student. Test `eligible`, `ineligible`, `unknown`, `unsupported` and `error`. Inject an opposite verdict and a fabricated prerequisite into otherwise valid drafts. Neither may reach the student. Use the existing conditional-answer metadata and source cards. [Evidence preparation][evidence] · [Final validation][validation] · [Chat stream][stream]

## 4. Answer “What can I take next sem?”

- [ ] Add one proposed host operation, `assess_term_prerequisites`, to the router’s term operations and capability registry. If the target year level or semester is missing, ask only for the missing piece and retain the stated failures while waiting. An explicit year and semester in the same chat can fill the gap. An entry cohort alone cannot identify an irregular student’s next term.
- [ ] In `backend/bintanong_orchestration/{orchestrator,adapters}.py`, enumerate reviewed candidates with `list_term_courses()`. For each candidate, run `check_prerequisite_eligibility` with the same pinned release, edition and scoped student facts. Add the typed term result to the existing orchestration, generation and API contracts. Keep one term per request, one model explanation for the list and the existing request deadline. Make any partial coverage or timeout visible. [Research capability registry][registry] · [Symbolic adapter][adapter]
- [ ] Before enumerating, verify the requested year and term against reviewed source coverage for that edition. Record covered terms or a known source gap alongside the ledger during review where the existing release metadata is insufficient. `list_term_courses()` can return `complete` with an empty list when all cataloged rows are placed but a whole year is absent from the supplied document. Only say that a term lists no courses if the complete source for that term establishes it. Use fifth-year and summer terms where printed. Keep lecture, lab and RLE units as labeled, and withhold unit totals when the source does not reconcile. [Term lookup][term] · [Midwifery coverage][midwifery]
- [ ] Group results by **prerequisites met**, **blocked by a known prerequisite**, and **needs information or source review**. Show the reason beside each course. Separate already-passed courses from recommendations. Identify this as the prospectus list for the requested term. For an irregular student, label earlier failed courses separately as possible retakes, check their own prerequisites, and flag unverified availability. Actual section offerings, seats, waivers and overload approval require their own evidence.

**Exit check** · Use the older BSCS curriculum and a student who explicitly failed CC 3/L and CC 4/L. For second year, second semester, CC 5/L must be blocked. CS 4/L is also blocked by CC 4/L. GE-PS has a blank prerequisite cell in the reviewed source and must remain unresolved. Test a synthetic course with a verified satisfied rule to exercise the positive group. Add `tests/test_term_prerequisite_advising.py` for this operation and a regular chat API test for the two-turn version. [Old BSCS review][old]

## Verification and handoff

| Gate | Evidence required before calling it complete |
| --- | --- |
| Single-course demo | The opening conversation works through the regular chat API and student view. A prior pass survives a topic change. A correction changes the next verdict. A vague assertion never produces eligibility. |
| Curriculum isolation | Switching to proposed BSCS 2025–2026 and supplying only a CC 5/L pass cannot clear CS 13/L. Ask about CS 6/L and CS 10/L. Run the Civil/Mechanical pair in fresh sessions, then repeat after a mid-chat switch. Passing requires the correct source and outcome in both programs, zero facts carried into the other scope and zero verdicts based on another term’s enrollment. |
| Every release member | Discover the roster from `GET /curricula` and reconcile it with the pinned ledger manifest. For each member run a source-reviewed multi-turn case and a negative or unknown case through `POST /chat`. Use an expected answer independently read from the prospectus or its review. Where coverage is absent, verify that limitation and report the scope as limited. Report numerator, denominator and failures per curriculum. A skipped curriculum cannot count as passing. Re-run the table above for its distinct rule and coverage cases. [Release report][coverage] · [Multi-curriculum tests][multi-tests] |
| Adding another program | Load a synthetic ledger with unfamiliar course IDs and an existing rule type via the release builder. Verify the program appears in `GET /curricula`, the regular chat resolves a two-turn check and the citation points to that ledger. Adding this fixture must require no edit to the router prompt, Prolog evaluator or response templates. |
| Rule and answer integrity | Preserve all-of, any-of, co-requisite, unknown and conflict behavior. Test a what-if followed by a real question, a failed tool, an invalid explanation and a deadline. Require zero false eligibility decisions, cross-session transfers or verdict reversals in the agreed cases. |
| Regression and cost | Keep the recorded 113 prerequisite questions across 39 curricula as a single-turn comparison. Each Psychology track had only one such question. Exercise the original BusEco negative, even though the UI replaced that sample. Add held-out multi-turn cases independent of prompt examples. Distribute English, Filipino and Taglish across the live runs. Report extraction, carry-over, verdict, wording and warm student-visible latency separately from the older results. [Recorded baseline][samples] |

For each task, start with a failing synthetic case, observe the specific failure, make the smallest change, then rerun it and the related regressions. Use Python 3.13 and the existing locked environment. From the repo root, this PowerShell command exercises the single-course baseline in an isolated temporary directory.

```powershell
$runDir = Join-Path ([System.IO.Path]::GetTempPath()) ("bintu-memory-" + [guid]::NewGuid())
python -B -m pytest -q -p no:cacheprovider --basetemp=$runDir tests/test_routing_validation.py tests/test_api_chat_turns.py tests/test_private_context_conversation.py tests/test_private_context_isolation.py tests/test_symbolic_queries.py tests/test_generation_pipeline.py tests/test_api_presentation.py tests/test_api_curricula.py tests/test_runtime_multi_curriculum.py tests/test_runtime_hosted_curricula.py
```

**First team demo** · Run the BSCS two-turn clarification and its fresh-chat reset, then give the identical `Phy 11/L` question to Civil and Mechanical Engineering. Show which printed rule explains each answer. Take up semester planning after these checks pass through the student-facing chat.

[revision]: https://github.com/bintanong420/Bintanong/tree/395079c16e3f3850a37a66949c37edb0bbf7e68c
[diagram]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/Context/bintanong_full_runtime_routing_architecture.png
[old]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/plans/2026-10-23-bscs-old-prerequisite-review-01.md
[proposed]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/plans/2026-10-23-bscs-proposed-prerequisite-review-01.md
[chat]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_api/chat.py#L68-L125
[conversation]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_private_context/conversation.py
[observations]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/plans/2026-10-23-multi-turn-observation-results.md
[prompt]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_routing/prompt.py#L103-L129
[orchestrator]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_orchestration/orchestrator.py#L219-L251
[engine]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/algorithms/curriculum_runtime.pl
[generator]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_generation/generator.py#L93-L130
[presentation]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_api/presentation.py
[samples]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/Context/sample-query-results-20261103.md
[term]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_symbolic/course_facts.py#L96-L104
[routing]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_routing/validation.py#L246-L332
[sessions]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_private_context/sessions.py
[privacy]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/plans/master_implementation_plan_original_long.md#232-privacy-and-cost-constraints
[client]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/frontend/lib/student-clarification.ts
[evidence]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_generation/evidence.py
[validation]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_generation/validation.py
[stream]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_api/stream.py
[registry]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_runtime/research.py#L307-L327
[adapter]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_orchestration/adapters.py
[coverage]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/docs/evaluation/phase12-evaluation-report.md
[multi]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_runtime/research.py#L317-L369
[loader]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_runtime/hosted_curricula.py
[programs]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/frontend/lib/programs.ts
[authoring]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/backend/bintanong_symbolic/authoring.py
[multi-tests]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/tests/test_runtime_multi_curriculum.py
[civil]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/plans/2026-10-24-bsce-prerequisite-review-01.md
[mechanical]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/plans/2026-10-24-bsme-prerequisite-review-01.md
[architecture]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/plans/2026-10-22-bsa-prerequisite-review-01.md
[nursing]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/plans/2026-10-24-bsn-prerequisite-review-01.md
[business]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/plans/2026-10-23-bsba-buseco-prerequisite-review-01.md
[education]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/plans/2026-10-24-bsed-math-prerequisite-review-01.md
[midwifery]: https://github.com/bintanong420/Bintanong/blob/395079c16e3f3850a37a66949c37edb0bbf7e68c/plans/2026-10-24-bsmid-prerequisite-review-01.md


## Addendum — Intended LLM reasoning role, symbolic evidence and conversation memory

**Requested clarification · 3 November 2026.** The desired behavior is for Bintu/Gemma to actively interpret the student's question, identify the relevant checks, use Prolog's rules and query results as evidence, and generate the final contextual answer. The model should explain how the requirements relate to the student's reported situation and determine what information to request next. This addendum expands Tasks 1–4 and their acceptance criteria; it describes intended work, not a claim that the branch already implements it.

### Responsibility of each component

| Component | Responsibility |
| --- | --- |
| Bintu/Gemma before symbolic execution | Interpret English, Filipino or Taglish; identify target courses, explicit results, enrollment periods and hypothetical conditions; propose an existing typed operation and any needed clarification. |
| Host/backend | Validate the interpretation against the student's statement, resolve course identities within the selected curriculum, merge accepted scoped facts, and execute only registered operations with validated arguments. |
| Prolog | Apply the reviewed curriculum rules to the supplied facts and return the checked outcome and supporting satisfied, unmet or unknown conditions. |
| Bintu/Gemma after symbolic execution | Analyze the supplied evidence, connect the findings to the student's question, explain relevant dependencies, synthesize semester results, and ask for missing information. Generate a natural answer whose conclusion agrees with the checked evidence. |
| Answer validator | Verify course identities, verdict, reasons, rule structure and citations. Reject unsupported claims or reversed conditions and use the existing safe fallback when necessary. |

The student or a confirmed uploaded record supplies evidence of course completion. Prolog does not independently discover grades. The LLM must not infer that all unmentioned subjects were passed. Curriculum rules remain explicit and source-backed; course-specific answers must not be hard-coded into shared prompts or application branches. A reusable evaluator should derive decisions from the selected curriculum and current facts.

### Evidence-based reasoning and temporary memory

Use the existing memory subsystem in Task 2 rather than introducing a second conversation store. Carry validated facts and the pending check across turns so the model can use earlier information when deciding what to check or ask next. Preserve the distinction between failed, not yet passed, never taken, passed and taken with an unknown result. Keep enrollment and its academic period separate from completion.

For each request, assemble a structured evidence record containing:

- The selected program, curriculum edition, release and requested course or term.
- Accepted student facts, their origin references and any request-only hypothetical assumptions.
- The registered operation and grounded query arguments.
- Relevant prerequisite or co-requisite rules, their structure and source references.
- The checked outcome and satisfied, unmet, disputed or missing conditions.
- Host-approved clarification options and next actions that the LLM may explain.

This record supports an inspectable explanation of **facts → rules checked → results → conclusion**. It is an evidence trace, not the model's private chain of thought. Keep the full trace request-local. Persist only the scoped facts and pending-question identifiers allowed by Task 2, with its existing 256-fact limit, 30-minute idle expiry, isolation, correction and cancellation rules. Discard raw prompt text after validation as already specified. Persistent diagnostics must exclude raw chat, grades and private model reasoning.

A prior explicit pass may be reused in its original scope, but the applicable rules must be evaluated afresh. A curriculum switch must not transfer facts or bind a pending bare “yes” across scopes. Hypothetical assumptions apply only to the current check and must not alter the student's remembered actual record.

### Example A — A personal prerequisite question

**Input:** Selected BSCS 2018–2019; “Can I take CC 5/L if I haven't passed CC 3/L and CC 4/L?”

1. Identify CC 5/L as the target and noncompletion of CC 3/L and CC 4/L as the stated premise. Determine whether this is a hypothetical scenario or an actual self-report; clarify if the distinction is ambiguous.
2. Resolve all three courses inside the selected edition. Query the reviewed rule for CC 5/L.
3. Prolog checks the rule requiring both CC 3/L and CC 4/L to be passed and returns that both conditions are unmet under the premise.
4. Provide Bintu with the target, rule, two unmet conditions, premise status and citation. Bintu generates the answer and explains why both prerequisites matter.

**Illustrative output:** “Under BSCS 2018–2019, you do not meet the prerequisites for CC 5/L if you haven't passed CC 3/L and CC 4/L. Both must be passed first.”

The wording may vary. The answer must retain the conditional wording when hypothetical, identify both unmet requirements and show the curriculum source. An actual report may become scoped memory; a what-if must not.

### Example B — Failures followed by semester planning

**Input:** “I failed CC 3/L and CC 4/L. What can I take next sem?”

1. Extract two explicit failures and retain them through the existing validated memory flow.
2. Establish the selected curriculum and requested year/semester. If the term is missing, ask for it while retaining the accepted failures. Do not infer an irregular student's target term from entry cohort alone.
3. Execute Task 4's bounded semester operation. The host enumerates the reviewed term courses and checks each candidate through Prolog using the same release and student facts.
4. Give Bintu the checked list, reasons, unknowns and coverage limitations. The model synthesizes an answer explaining which prerequisites are met, which courses are blocked and what remains unresolved.
5. Separate already-passed courses and possible retakes. Do not present a prerequisite result as confirmation of actual course availability or enrollment approval.

For the older BSCS curriculum and second year, second semester, retain the plan's expected evidence: CC 5/L is blocked by CC 3/L and CC 4/L; CS 4/L is blocked by CC 4/L; GE-PS remains unresolved because the reviewed prerequisite cell is blank. Other courses require their own checked evidence before appearing in the positive group.

**Illustrative output:** “Based on the failures you reported, CC 5/L is blocked because it requires both CC 3/L and CC 4/L. CS 4/L is also blocked because it requires CC 4/L. I cannot confirm GE-PS from the reviewed prerequisite entry because it is blank.” Show the requested term's full checked list and any targeted follow-up alongside this explanation.

### Implementation integration and acceptance checks

- [ ] **Task 1:** Verify the model's proposed interpretation against the statement. Test both failures in one sentence, mixed pass/fail results, unknown outcomes and conditional statements. Never fill unspecified results with assumed passes.
- [ ] **Task 2:** Reuse the scoped memory and pending-question subsystem. Test reporting failures, answering a term clarification, receiving the checked list, correcting a result and obtaining a freshly evaluated answer. Retain only validated facts under the existing lifecycle.
- [ ] **Task 3:** Ensure normal successful personal prerequisite answers actually invoke the post-Prolog LLM with the structured evidence, including checked unknown outcomes. Verify that the explanation uses the relevant reasons and preserves all-of, any-of and co-requisite meanings. Keep fallback responses for invalid drafts, timeouts or unavailable checks.
- [ ] **Task 4:** Keep semester evaluation bounded within the proposed registered operation. The LLM interprets and synthesizes; the host runs the candidate checks. This does not require arbitrary Prolog code generation or an unrestricted autonomous query loop.
- [ ] Run paraphrases of both examples in English, Filipino and Taglish. The verdict and supporting facts must remain stable while the wording may vary.
- [ ] Test a missing student result separately from missing source coverage. The former should produce a targeted student question; the latter should explain the source gap.
- [ ] Inject a generated answer that reverses the Prolog verdict, invents a prerequisite or assumes an unreported pass. Reject it before display.
- [ ] Verify no hypothetical facts survive into an actual-record question, and no facts transfer to another chat or curriculum.
- [ ] Demonstrate the normal LLM explanation path and its validated fallback separately. Record extraction accuracy, memory carry-over, verdict correctness, explanation fidelity and added latency. Do not treat a natural-sounding answer as proof of correct reasoning.

**Expected outcome:** Bintanong can understand a student's situation across turns, use validated memory to avoid repeated questions, obtain curriculum-specific symbolic evidence and generate a clear answer that explains the resulting decision. The LLM participates in interpretation, clarification and evidence synthesis; Prolog provides the authoritative evaluation of the reviewed rules under the supplied facts.
