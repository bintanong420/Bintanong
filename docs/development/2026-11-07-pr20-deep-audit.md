# PR #20 — Deep Audit, Prior-PR Reconciliation and Evidence Boundaries

**7 November 2026** — static review only; no model, Python, UI, source-PDF or live-service tests were executed as part of this PR creation.

**Source baseline:** p12-dev at 21be2614fb082836a89df9ce1b0dfdf568c204c8.
**Destination:** feature/p12-unified-answer-pipeline to p12-dev (new draft PR #20).
**Source drafts:** PR #18 at 1f8ee4a47b59a630c04305521f98a9f9bb9e476f; PR #19 at 27ef19ec9cd565ced81c3c6746bb0ad225c18f7b.

## Updated conclusion after inspecting PRs #18 and #19

The fundamental defect is lack of a lossless, validated per-request-part contract from interpretation to tool execution, source evidence, verified claims, SSE and student-visible UI. A prompt-only change cannot fix lost documentary results, execute multiple Prolog operations or render per-part coverage that is not transmitted.

| Finding | Source PR candidate | Remaining work in #20 |
|---|---|---|
| H01 multiple structured operations | #19 adds compound.py candidate-only, two independent same-curriculum prereq checks | Keep research restriction until fully bound through orchestrator/generator/response; extend 2-symbolic + 1 document only after safe part-evidence contracts |
| H02 multi-topic document drop | Neither | merge_documents returns first non-OK; preserve independent supported topics and typed gaps, conflict/release gates stay fail-closed |
| H03-H05 frontend presentation | Neither | Versioned answer presentation, strict SSE/Zod/React mapping, per-part source IDs, safe legacy text |
| H06 selective Prolog routing | #18 adds host-owned domains catalog vs constraints | Actual model interpretation and negation still need independent gold and measured accuracy |
| H07 document calibration and topic selection | #18 adds exact research calibration gate and not-checked wording | Preserve safeguards; do not conflate no matching topic with no source coverage |
| H08-H11 dialogue/claim limit/context | p12-dev has bounded dialogue, ledgers, partial slots and safe Markdown | Fix client clarification replay, lifecycle indication and per-part supported claim mapping |
| H12 router compiler flag | p12-dev supports optional compiler, default OFF | Compare OFF/ON without enabling it blindly |

PR #19 is **stacked on #18**: three commits in #18 plus two additional commits in #19. Both drafts are open and unmerged. At inspection no submitted reviews or recorded CI checks were present. The old PR base and current p12-dev diverged by 51 newer p12-dev commits; cherry-pick by intent into #20, not naive merge into the evaluation harness.

## Binding repository rules and interpretations

- Input comprehension: **English, Filipino/Tagalog, Taglish**. Output: **English for English; Taglish for Filipino/Taglish** under 27 October owner decision. Internal fil tags are not a separate student reply language.
- Reviewed blank **prerequisite cell** is equivalent to no prerequisite under 4 November owner decision. Do not extrapolate to blank unreviewed fields, procedure steps, fees, approvals or grades.
- Course identifiers, curriculum/program edition, student assertions vs hypotheses, retrieval release/rule/source pins remain authoritative. Proposed 2025–26 prospectus is **not automatically operative policy**; taken is not passed.
- Undergraduates only within the thesis scope. Source acquisition, release, institutional approval, public deployment and autonomous university actions are out of scope. Freeze p12-evaluation-harness and its data-gathering service.
- Repository AGENTS.md requires thesis physical pages 17–18 and relevant governance/architecture context to be read **before implementation**. This static GitHub audit does not claim to have inspected those thesis pages itself.
- November 6 owner signoff had 72 Y marks but three inferred unexecuted cases and no single frozen run SHA; not proof of 72 independently executed passes.
- The detailed older audit below has 12 findings and 20 scenario patterns; its numbered multi-PR roadmap is superseded by the single #20 implementation plan at plans/2026-11-07-pr20-unified-answer-pipeline-plan.md.

---

## Detailed baseline audit (historical p12-dev source snapshot)

# Bintanong `p12-dev`: Deep Architecture Audit and Implementation Plan

**Audit date:** 7 November 2026  
**Repository:** `bintanong420/Bintanong`  
**Reviewed ref:** `p12-dev` — `21be2614fb082836a89df9ce1b0dfdf568c204c8`  
**Scope:** Behavior and request understanding; answer text structure and student-facing frontend presentation; Hybrid queries; cross-cutting conversation, correctness, performance, and evaluation.

## Evidence standard and boundaries

This is an independent **read-only source inspection** through the connected GitHub repository, reconciled with the repository's existing research and test reports. **I did not execute the backend, run the LLM, instrument live requests, inspect the owner's live secrets/services, or run tests independently.** Findings marked **Confirmed in current code** are static-code facts. **Reported observation** means another developer's recorded test/live run, not reproduced here. **Risk/hypothesis** needs a new reproduction.

The source-specific audit is for `p12-dev`, not the frozen `p12-evaluation-harness` or `p12-post-gathering-fixes`. `plans/2026-11-04-development-isolation-handoff.md` explicitly separates development from thesis data gathering and says the running gathering backend may predate recent fixes. Do not equate a Git branch SHA with the code serving a running endpoint. Archive separate source SHA, service SHA, model identity, rule-bundle version, retrieval-release ID, settings, and timestamps in each test.

## Verdict

Bintanong already has real safeguards and useful architecture: source-pinned documentary retrieval; Prolog-driven, curriculum-scoped symbolic operations; a model router with constrained schema and explicit course/result mentions; per-document-question slots and a support checker; a safe React-based Markdown parser; a newly added bounded, server-owned dialogue ledger; atomic turn commit; and typed non-answer reasons. **Do not rebuild these features.**

The key obstacle is the lack of one coherent, end-to-end semantic contract linking (1) requested tasks, (2) tool execution, (3) part-by-part coverage, and (4) student-facing presentation. This shows up in the confirmed one-symbolic-operation limit, the early all-or-nothing document merger, partial answers reported as generic `answered`, and free-text/line-filter presentation despite existing rich backend metadata. Prompt modifications alone cannot repair these structural mismatches.

## Finding matrix

| ID | Priority | Finding | Evidence | Impact | Suggested owner |
|---|---|---|---|---|---|
| H01 | **P1** | Hybrid dispatch executes at most one structured operation; a multi-op request triggers `compound_request` clarification | **Confirmed** | Student cannot ask two distinct course checks in the same request | Backend routing/orchestration |
| H02 | **P1, first to fix** | Multi-topic document aggregation returns the first non-OK result, throwing away other successful topics | **Confirmed + test** | A document answer that exists can be masked by a missing second topic | Retrieval/integration |
| H03 | **P1** | Partial coverage is tracked internally but publicly exposed mainly as `answered` plus unstructured prose | **Confirmed** | UI cannot accurately indicate which portions were answered and which lacked evidence | Backend API + frontend |
| H04 | **P1** | `render_text` assembles raw lines; `student_text()` strips and modifies them via text matching | **Confirmed** | Fragile layout, duplication removal and answer hierarchy; risky to add more prompt formatting | Backend presentation |
| H05 | **P1** | No public structured display blocks or per-part citation mapping; `planView` disabled pending strict Zod schema | **Confirmed** | Frontend cannot reliably render verdicts, caveats, sources and study plans as distinct components | API/frontend |
| H06 | **P1** | English/Taglish/Tagalog behavior and policy routing remain inconsistent in recorded live variants | **Reported observation** | Same underlying academic question can receive different confidence, route or answer | Understanding/evaluation |
| H07 | **P1/P2** | Frontend may prepend the original question to clarifications despite newly implemented server dialogue | **Confirmed** | Duplicated premises, misleading history and language/provenance drift are possible | Frontend/API |
| H08 | **P2** | In-memory dialogue retains up to 8 exchanges and projects up to 4 same-scope exchanges; restart/expiry loses history | **Confirmed** | Normal follow-up behavior can disappear without explicit lifecycle UI | Session/frontend |
| H09 | **P2** | Global eight-claim draft budget is shared by document parts, and procedure answers can be long | **Confirmed constraint + reported verbosity** | Multi-detail replies risk claim-budget pressure and poor readability | Generation/presentation |
| H10 | **P1 release quality** | Legacy 50-case score and narrow live variants do not verify multi-op, mixed evidence, cross-language semantic accuracy or whole UI contract | **Reported + code inspection** | A pass count can overstate supported capability | Evaluation |
| H11 | **P2 conditional** | Fact filtering may use explicitly requested scope before dialogue recovers scope | **Confirmed ordering, impact conditional** | A scope-omitting client could lose contextual facts | Context compiler |
| H12 | **P2** | `BINTANONG_ROUTER_COMPILE` remains default OFF; parallel router/guard/compiler paths add regression surface | **Confirmed** | Flag-dependent semantics; dangerous to enable without paired evaluation | Routing |

### H01 — The precise Hybrid boundary

- Router prompt: RAG = documentary explanation; Symbolic = prerequisite/course/study-plan computation; Hybrid = both. Request parts are bounded (up to eight); operations are bounded (up to four).
- But validator `validate_interpretation` tests `if len(p.operations) > 1: return result('compound_request')` before dispatch. It later constructs the `PredicateRequest` for `p.operations[0]` only.
- `IntegrationResult._result` requires `len(plan.operations) == 1` for a ready structured route.
- In the Orchestrator, Hybrid calls one `retrieve()` plus one `reason()` concurrently using `asyncio.gather`.
- Therefore the code is not silently executing the first of several checks; it **clarifies** when correctly parsed as multiple operations. The limitation is missing multi-operation capability, not necessarily a safety bypass.

**Immediate contract:** maintain the current safety guard until a trustworthy multi-op planner exists. Make the clarification explicit, e.g. “I can evaluate one course at a time here. Which should I check first?” rather than suggesting the document sources are missing.

**Full implementation option:** add an `ExecutionPlan` containing bounded operations with individually bound course/term targets and a `part_to_operation` mapping. Run maximum two **independent** structured operations in an initial milestone, each against the same pinned release, effective scope, and clearly scoped student facts. Keep results as typed per-op evidence and bind them to part IDs. Refuse or ask a precise clarification if the requested scope/grade premise is ambiguous, if the same printed code resolves differently, or if one operation's result cannot safely feed another. Add further dependency chaining only with explicit specifications; never let model-generated prose define Prolog goals.

**Files:** `backend/bintanong_routing/prompt.py`, `contracts.py`, `validation.py`, `wire.py`, `compile.py`; `backend/bintanong_orchestration/contracts.py`, `orchestrator.py`, `integration.py`; typed symbolic adapters; relevant routing/orchestration/generation tests.

### H02 — Multi-topic retrieval defeats partial-answer policy

`backend/bintanong_orchestration/orchestrator.py::merge_documents()` says the first non-`ok` result prevents integration. It returns that failed result immediately, rather than preserving successful other topics with their own statuses. `tests/test_orchestration_multi_topic.py::test_a_topic_without_evidence_leaves_the_whole_message_unanswered()` explicitly encodes this behavior.

But `tests/test_generation_part_slots.py::test_covered_part_is_answered_and_the_unavailable_part_is_named()` demonstrates a later, partially answered policy: if a supported first part and an unavailable second part reach generation, the answer status may be `answered` with ledger status `some_parts_unavailable`.

**This is a real cross-layer mismatch:** generator partial behavior cannot operate when the retrieval integration stage has discarded the successful evidence.

**Fix:** replace the single `DocumentResult` representing several topics with a typed `DocumentEvidenceBundle` / `PerTopicRetrieval` retaining each topic's status, source passages, gaps, release and source IDs, and part-to-topic mapping. Integrate successful topics and explicit missing topics **only when there is no unresolved conflict, unverified release, or source-safety condition that requires withholding**. Missing fee may permit a sourced office answer and an explicit “fee unknown”; a hard source conflict for the very same policy may still require withholding that part. Preserve current conservative conflict/release checks by design.

**RED tests:** one topic `ok` + other `insufficient_evidence` -> both per-topic facts retained, one `unavailable` part; one `conflicting_sources` -> no speculative policy conclusion; both missing -> insufficient evidence; unrelated topics with source ID duplication -> no duplicate passage; different release pins -> hard failure.

### H03 — An `answered` status does not necessarily mean every part was answered

`backend/bintanong_generation/ledger_contracts.py` expressly permits an `answered` CandidateAnswer with either `all_declared_parts_mapped` or `some_parts_unavailable`. The API's public SSE `data-answer` exposes `status`, `reason`, `conditional`, `language`, missing fields and a generic notice, but **not** the ledger entries, part IDs, their coverage states or source links per part. Frontend `answerMetadataSchema` has no such fields.

**Fix without breaking existing clients:** retain the current `status` while adding a versioned `coverageState: 'complete' | 'partial' | 'none' | 'uncertain'` and `parts: [{partId, requestedText, evidenceType, outcome, missingReason, sourceIds, blockIds}]`. Only expose host-validated metadata and source IDs already present in the candidate answer; map uncertain/failed checks separately from `not_in_evidence` or `source_gap`. Later, if product needs an explicit `partially_answered` status, migrate deliberately and version tests.

### H04/H05 — Presentation is backend-controlled string manipulation, not a design contract

- `generation/render.py::render_text` assembles `lines`, sometimes numeric scope diagnostics, prose, source excerpts and source citation references.
- `api/presentation.py::student_text` drops the research preview, internal check-scope lines, and duplicate eligible rule/explanation by comparing exact strings and replacing strings across the whole rendered text.
- `api/stream.py::answer_parts` delivers **one** full text delta after validation, then source parts and `data-answer`. This is SSE transport but not token-by-token public answer streaming.
- `frontend/lib/chat-markdown.ts` safely parses a restricted subset of Markdown, and `frontend/components/workspace/markdown-text.tsx` uses React nodes without raw HTML injection. That is a strong security boundary. It supports headings, bullets, simple nesting, bold, inline code, HTTPS links and tables, but not arbitrary Markdown semantics.
- `frontend/components/workspace/conversation.tsx` currently places the answer inside one Markdown component; sources are separate via a source-panel action.
- `api/stream.py` leaves `plan_view=False` until the strict public schema accepts it. A backend `plan_view` producer exists but the frontend feature is not contractually enabled.

**Recommended approach:** a typed, host-built **Answer Presentation Model**, not a second unconstrained LLM format prompt. The model generates claims only. The host constructs a presentation tree from validated claims, symbolic outputs, ledger entries and verified citation IDs. The frontend renders typed components, while the backend also emits a deterministic Markdown/plain-text fallback for copy, older clients and accessibility.

Proposed block types: `lead`, `verdict`, `requirements`, `section`, `step_list`, `course_table`, `unavailable_part`, `sources`, `notice`, `clarification`, `recovery_plan`. Typed blocks must have strict size bounds, non-overlapping IDs and text/evidence relationships; forbid arbitrary HTML and JSX; validate source references against candidate evidence.

Implement before adding more presentational markup to LLM prompts. Establish a consistent order:
1. **Direct result**: answer the student's question immediately with precise outcome or limitation.
2. **Basis**: distinguish user-reported results from verified printed institutional requirements.
3. **Breakdown by requested part**: one heading/section per independently answerable part.
4. **Conditions/unknowns**: preserved exceptions, co-requisites, source gaps and next required student fact.
5. **Sources and next action**: cited chunks or rules with source panel link; only administrative office/referral details established in reviewed material.

Avoid gratuitous headings on a one-sentence answer. Render a small clear card, not a wall of numbered lines.

**Sample v2 public payload (illustrative only):**

```json
{
  "schemaVersion": "bintanong-student-answer-v2",
  "status": "answered",
  "coverageState": "partial",
  "parts": [
    {"partId": "r1", "kind": "structured", "state": "mapped", "blockIds": ["b1"], "sourceIds": ["<verified-rule-id>"]},
    {"partId": "r2", "kind": "document", "state": "unavailable", "missingReason": "not_in_evidence", "blockIds": ["b2"], "sourceIds": []}
  ],
  "blocks": [
    {"id": "b1", "type": "verdict", "outcome": "ineligible", "title": "Eligibility check", "text": "One required course is not yet completed."},
    {"id": "b2", "type": "unavailable_part", "title": "Policy procedure", "text": "The reviewed sources do not state this step."}
  ],
  "fallbackText": "..."
}
```

`<verified-rule-id>` is a placeholder and must be replaced only by validated, pinned evidence. The existing public source pattern is `ev-<64-hex>`, not arbitrary user/model IDs. Never publish a block that carries an unsupported sentence.

### H06 — Behavior, understanding and language consistency

The router schema already distinguishes `list_course_prerequisites`, `check_prerequisite_eligibility`, and reverse `list_affected_courses`. It explicitly preserves passed/failed/not-taken/taken-unknown, hypothetical and reported facts. **The remaining problem is consistent application**, especially across languages, follow-up dialogue, source topic selection and many specialized deterministic guards.

`plans/2026-11-05-live-language-browser-results.md` reports a 24-question x three-language run. Within seven eligibility cases, English and Taglish each matched the expected verdict for 6/7; Tagalog 4/7. The report notes incorrectly re-asked facts, irrelevant shifting referrals, Taglish abstentions where other languages retrieved policy, a language metadata fallback, and lengthy raw-looking documentary replies. These are **small-sample recorded observations**, not a current general accuracy metric or a proof the latest running service is identical to the ref inspected here.

**Stabilization:** introduce a task-first `UnderstandingPlan` with a canonical array of independently answerable goals, explicit evidence requirements, required scope and user-stated assertions, and a single validated language/style decision. Let LLMs propose this plan, but require deterministic validation of all quoted entities, operation coverage, negation and source scope. Keep dialogue acts and answer style separate from authority to create facts. Instrument **first divergent stage** for each failed example: intent split -> scoped identity -> evidence need -> topic selection -> retrieval -> Prolog -> claim validation -> presentation.

**Router compiler:** `backend/bintanong_routing/router.py::compile_enabled()` uses `BINTANONG_ROUTER_COMPILE=1`, OFF by default. Do not toggle the flag for convenience. Run paired OFF/ON fixed and held-out corpus using the same release/model and commit; promote only if it improves independent reference intent/slot accuracy without false eligibility or policy overreach. Inventory the existing host guards before replacing any.

### H07/H08/H11 — Dialogue memory exists, but API/UI and scope must agree

The November 4 independent repository audit is historically valuable but partly outdated. Current `p12-dev` includes:
- `backend/bintanong_private_context/dialogue.py`: up to eight bounded exchanges and explicit unresolved turn;
- `backend/bintanong_private_context/context_compiler.py`: up to four relevant same-scope exchanges (16 KiB) plus pinned unresolved origin;
- `backend/bintanong_private_context/sessions.py::commit_turn_result`: atomic turn commit under lock and revision check;
- `backend/bintanong_orchestration/reasons.py`: `dialogue_unresolved` distinct from institutional `retrieval_coverage` and `source_incomplete`.

**Remaining confirmed issues:** in-memory session idle expiry ~30 minutes; no durable cross-restart history; `frontend/lib/student-clarification.ts::{clarificationReply,typedReply}` may concatenate the original question with clarification selections/typed response even though the backend now holds an originating turn; `frontend/components/workspace/workspace.tsx` calls this helper and the browser tests assert a concatenated string. This replay is intentional existing behavior, not evidence of every turn being doubled.

**Recommended migration:** add explicit `replyToTurnId`, `clarificationField`, `responseValue`/literal user text in a versioned request. The server validates ownership, revision, unresolved slot and compatible scope; it binds to the exact originating turn. Keep human-facing UI history of what the user actually typed. Feature-flag the removal of legacy frontend replay and add browser regressions for typed follow-up, selected options, multi-turn repair, scope switch, repeated message IDs, stale session and restart. Do not treat prior assistant prose as official evidence or prior candidate answers as grade facts.

If the frontend omits scope on document-only questions, ensure scope is resolved **before** filtering saved grade facts. Most current UI paths include selected scope, so the scope-loss severity is conditional, not a demonstrated frequent incident.

### H09 — Long answers, claim budgets and latency

The `AnswerDraft` has a maximum of eight claims. `part_schema()` distributes this budget across document parts, and `to_draft()` errors on more than eight claims. That is an intentional bounded-answer guard, not automatically a defect. However, many complete student-service procedures require several independent steps, actor/office conditions and citations, so the limit can compete with completeness. Avoid simply raising all token/claim caps: first establish a **per-part completeness and source witness** budget, a deterministic long-service formatter, and progressive “summary + steps/details” presentation. Preserve source completeness semantics even if the display is compact.

The Phase 12 v2 report recorded warm local median around 26.8 seconds / p95 36.8 seconds for the full pipeline; the November 5 browser variants recorded median local click-to-render ~14–15 seconds. These are different builds and measurement definitions, **not** evidence that every answer is now 14 seconds. Instrument router, topic selection, each retrieval, symbolic, generation, review, render, SSE and browser paint; optimize hot paths only after correctness and evidence gates pass.

### H10 — Evaluation validity

`docs/evaluation/phase12-evaluation-report.md` gives original v2 38/50 (76%), with 40 reused development cases and no full held-out intent/slot ground truth, retrieval Precision/Recall, unsupported-claim adjudication, repeated runs/blind ratings or full UAT. This benchmark predates later November fixes. `evaluation/conversations/run_conversations.py` scores status and literal text requirements, not complete causal claims. `evaluation/question_parts.py` provides stronger part mapping structures, but it is not a substitute for independently annotated end-to-end cases.

Use **two different suites**:
- **Regression characterization:** existing deterministic fixtures and prior incidents, retained but corrected when requirements are wrong; preserve RED->GREEN history.
- **Held-out acceptance:** independently authored questions using curricula, policies, conversation turns, languages, and missing-source scenarios not used to tune prompts. Freeze the suite before evaluation and track first incorrect stage. Report **accuracy**, **coverage**, **false acceptance**, **false abstention**, **partial-response honesty**, **presentation quality**, and **latency** separately.

## Suggested final design

```text
User message + server-owned dialogue scope + request-local facts
                              |
                     UnderstandingPlan
                 (r1..rN, typed asks, facts)
                              |
              validated execution planning
         +--------------------+-------------------+
         |                                        |
   Symbolic executor(s)                     Document retrieval
   release + curriculum scope               by topic and part
   bounded explicit op set                  per-topic results
         |                                        |
         +--------------------+-------------------+
                              |
                 Typed per-part evidence bundle
                      + coverage ledger
                              |
                 Claim-level support validation
                              |
                 Host AnswerPresentation builder
                              |
                  API schema v2 + fallback text
                              |
               React semantic blocks + source UI
```

**Invariants:** every answer part maps to an input span and explicit execution/evidence state; all executable structured requests use reviewed Prolog capabilities; every claim maps to pinned source/rule references; a mixed-route failure does not convert unexecuted checks into RAG guesses; a partial document result remains partial (unless a higher-priority conflict requires withholding); and the backend decides correctness while frontend decides visual appearance.

## Implementation plan: proposed PR sequence

### PR0 — Freeze, evidence, reproducibility (0.5–1 developer day)

- Pin exact `p12-dev` SHA, model, source release, symbolic rule bundle and settings. Record separate running gathering and development service SHAs. Do not restart or mutate gathering services.
- Capture 15–25 known failed/representative questions as red fixtures: multilingual, multi-document, Hybrid, multi-op, follow-up, curriculum switch, missing fee, ambiguous course. Store sanitized trace IDs, parts, route, topic statuses, evidence IDs and final presentation.
- Run existing affected tests in an isolated environment; capture baseline without relabeling old test failures as passes.

**Gate:** baseline reproduces actual outcomes and identifies first diverging layer; no thesis dataset contamination.

### PR1 — Preserve partial documentary evidence across retrieval (1–2 developer days)

- Add per-topic results and mapping to `DocumentResult` integration or new typed bundle. Update `merge_documents`, integration `assemble`, candidate evidence and generation input to accept safe partial topic bundles.
- Preserve release-mismatch/conflict priority. Do not soften exceptions without reviewed evidence.
- Build RED/GREEN tests: good office plus missing fee; both good; both missing; source conflict; missing continuation; duplicate same passage; cross-release mismatch.

**Gate:** any answerable part survives an unrelated missing topic, every unavailable part remains explicitly unavailable, no fabricated evidence or incorrect source pin.

### PR2 — Versioned answer presentation contract (1.5–3 developer days)

- Add `AnswerPresentationV2` host-built blocks and part metadata from already validated output; keep legacy text intact.
- Extend `backend/bintanong_api/stream.py` to emit `data-answer` metadata `coverageState`, `parts`, and `blocks`, guarded by feature flag or negotiated schema version.
- Extend strict Zod schema and React component mapping: `VerdictBlock`, `EvidenceSection`, `PrerequisiteTree`, `StepsBlock`, `UnavailablePart`, `AcademicPlanBlock`. Enable `planView` only with schema and regression parity.
- Maintain safe text-based fallback; escape all content; source IDs only from validated evidence; copy action produces coherent plain text; screen-reader headings and focus semantics.

**Gate:** 100% of validated question parts display with matched state, source IDs and scope; desktop and 390px viewport; raw HTML never interpreted; old clients unchanged.

### PR3 — Task-first behavior and dialogue/UI parity (2–3 developer days)

- Introduce explicit `UnderstandingPlan` tests for list prereq vs check eligibility vs reverse dependency, documentary procedure vs information, English/Filipino/Taglish mixed tasks.
- Reconcile frontend clarification replay with new server dialogue API using `replyToTurnId` and typed slots; remove string-concatenation only after parity gate.
- Add reason-specific clarification language. Distinguish valid clarification vs source gap, and an answered question vs an unexecuted requested part.
- Compare router compiler OFF/ON against same gold suite; retain current default until confidence is established.

**Gate:** a fresh topic is not misread as a continuation; a short follow-up resolves the intended previous turn; no user-supplied grade is silently promoted from taken to passed; no source-bounded claims are invented.

### PR4 — Multi-operation Hybrid v2, deliberately bounded (2–4 developer days)

- Change `RequestUnderstanding`, validated plan and integration evidence from single `PredicateRequest` to ordered `operations[]` and `part_operation_refs[]`.
- Start with independent operations only (max two): two distinct course checks in the same exact curriculum with self-reported facts, plus documentary part. Each execution carries its own target, result, rule witnesses, missing slots and exception state.
- Audit curriculum switch and courses with ambiguous aliases. No trust in model-generated goals, no ambiguous student states invented, no result chaining without explicit policy.
- Keep operation indices stable from router to generation and presentation; fail closed on partial operation outputs.

**Gate:** 2 structured + 1 documentary question produces 3 properly accounted parts or a precise, non-misleading clarification; no cross-edition or cross-course contamination. Do not deploy unbounded fan-out.

### PR5 — Evaluation, performance, safe rollout (1.5–3 developer days)

- Build a fixed held-out matrix by operation, part-count, route, source state, curriculum, input language, dialogue act and viewport. Score first-stage divergence.
- Include real curriculum and policy expert checks, not just substring assertions or model-written verdicts. Test Edge desktop/mobile, Firefox and WebKit/Safari if available (record environment-specific exclusions).
- Instrument per-stage warm/cold latency, calls per turn, payload size, retries and output validation. Compare against pinned PR0 baseline.
- Roll out only on isolated dev, then owner sign-off. Keep data-gathering branch untouched until explicit approved release window and regression evidence.

**Gate:** no false-positive curriculum eligibility or uncited rule claims in the held-out acceptance set; no request part silently dropped; partial gaps visibly indicated; latency budget measured and recorded rather than assumed.

**Total rough planning estimate:** 8–16 focused developer days, excluding the time needed for independent human source adjudication, model availability and full real-device/UAT testing. These are planning estimates, **not promised completion dates**. Begin with PR1 and PR2 for fastest student-visible impact; PR4 is a true architecture expansion and should not be mixed into a one-off prompt patch.

## Test matrix: mandatory cases

| ID | Student request pattern | Required behavior |
|---|---|---|
| T01 | “What are the prerequisites of IT 14/L?” | List reviewed rule, no personal grades asked merely to describe it |
| T02 | “I failed CC 4/L; can I take CC 5/L?” against BSCS **2018–2019** | Correct curriculum-specific Prolog decision, explicit supplied fact provenance |
| T03 | Same wording against BSCS **proposed 2025–2026** | Independent proposed-curriculum rules, no 2018/19 rule leakage; do not equate proposed with approved/current |
| T04 | “What subjects are affected if I fail CC 4/L?” | Reverse dependency, not named course's own requirements |
| T05 | “Can I take X and Y? I passed Z.” | Explicit two structured checks on v2 or accurate supported-limit clarification on v1; neither operation disappears |
| T06 | “Can I take X? What does the student handbook say about prerequisite approval?” | Hybrid one Prolog + documentary claim, each source separately bound |
| T07 | “Where do I file Form Q, and what is the fee?” with office evidence but no fee record | Return sourced office, mark fee unavailable, visible partial coverage |
| T08 | Same question with conflicting fee sources | Disclose conflict and withhold unsupported fee, never guess |
| T09 | “How do I enroll? What are the steps, documents and processing times?” | Ordered, complete **visible** source process; source gaps explicitly labeled |
| T10 | “I took CC 4/L” | `taken_unknown` — never silently `passed` |
| T11 | “Hindi pa pasado sa CC 4/L, pwede ba CC 5/L?” | Preserve negation; Taglish answer without English-only fallback |
| T12 | “Why?” after checked result | Bounded dialogue reference to exact originating check, not answer from model memory |
| T13 | “I already told you I failed it.” | Correct previous state or honest clarification, not institutional evidence gap |
| T14 | “Actually use the proposed 2025 curriculum.” | Change scope, rebind facts and recompute with correct release, no bleed |
| T15 | Blank prerequisite cell in source | Owner-reviewed blank prospectus prerequisite cells mean no prerequisite; other blank fields remain unresolved |
| T16 | Three separate policy topics, middle missing | Two supported sections survive and middle section explicitly unavailable |
| T17 | Long official procedure, multi-source | Limits, actors, conditions and ordered steps preserved within claim budget |
| T18 | Assistant output includes `<script>`, Markdown table, long URL and `|` in source quote | No HTML execution, safe wrapping, accessible table fallback |
| T19 | Multi-part answer at 390px and 1440px | Clear hierarchy, no horizontal overflow or orphan headings |
| T20 | Guest session expires/restarts before clarification | Explicit reset/context-lost message; no pretense of remembered scope |

**Curriculum test note:** The attached BSCS 2018–2019 curriculum lists `CC 5/L` prerequisites as `CC 3/L` and `CC 4/L`, while the **proposed** 2025–2026 curriculum lists `CC 3/L` and `CS 2`. These are different rule graphs and are especially valuable for detecting edition mix-ups. Neither document alone authorizes treating the proposed revision as operative university policy.

## Suggested project ownership

- **KR/Prolog developer:** curriculum identities, operation contracts, source witnesses, dependency and grade-state safety. Require sign-off on T02–T06, T10, T14–T15.
- **LLM/router developer:** task extraction, dialogue act, topic selection, failure reason and language parity; avoid accumulating case-specific regexes as the only fix. Require sign-off on T01, T07–T13.
- **Frontend/API developer:** typed presentation schema, React rendering, mobile/accessible hierarchy, stream metadata, clarification identity and stable copy. Require sign-off on T07–T09, T16–T20.
- **Evaluation owner:** independent gold annotations, benchmark isolation, exact source-release record, zero false eligible claims; consolidate stage traces and blocked tests without changing expected answers to flatter performance.

## Source index (reviewed at `p12-dev`)

- [Routing prompt](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_routing/prompt.py), [validation](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_routing/validation.py), [router](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_routing/router.py), [contracts](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_routing/contracts.py)
- [Orchestrator](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_orchestration/orchestrator.py), [integration](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_orchestration/integration.py), [candidate contracts](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_orchestration/contracts.py)
- [Generation](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_generation/generator.py), [part answers](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_generation/part_answers.py), [render](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_generation/render.py), [part ledger](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_generation/ledger_contracts.py)
- [Student presentation](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_api/presentation.py), [SSE](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_api/stream.py), [chat](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_api/chat.py)
- [Frontend markdown parser](https://github.com/bintanong420/Bintanong/blob/p12-dev/frontend/lib/chat-markdown.ts), [Markdown component](https://github.com/bintanong420/Bintanong/blob/p12-dev/frontend/components/workspace/markdown-text.tsx), [strict answer schema](https://github.com/bintanong420/Bintanong/blob/p12-dev/frontend/lib/student-contracts.ts), [conversation UI](https://github.com/bintanong420/Bintanong/blob/p12-dev/frontend/components/workspace/conversation.tsx), [clarification replay](https://github.com/bintanong420/Bintanong/blob/p12-dev/frontend/lib/student-clarification.ts)
- [Dialogue state](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_private_context/dialogue.py), [context projection](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_private_context/context_compiler.py), [sessions](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_private_context/sessions.py), [reason codes](https://github.com/bintanong420/Bintanong/blob/p12-dev/backend/bintanong_orchestration/reasons.py)
- [Multi-topic tests](https://github.com/bintanong420/Bintanong/blob/p12-dev/tests/test_orchestration_multi_topic.py), [part-slot tests](https://github.com/bintanong420/Bintanong/blob/p12-dev/tests/test_generation_part_slots.py), [Markdown tests](https://github.com/bintanong420/Bintanong/blob/p12-dev/frontend/tests/chat-markdown.test.mjs)
- [Phase 12 report](https://github.com/bintanong420/Bintanong/blob/p12-dev/docs/evaluation/phase12-evaluation-report.md), [November 5 72-variant live browser report](https://github.com/bintanong420/Bintanong/blob/p12-dev/plans/2026-11-05-live-language-browser-results.md), [November 6 publication signoff](https://github.com/bintanong420/Bintanong/blob/p12-dev/plans/2026-11-06-owner-signoff-publication.md), [development branch isolation](https://github.com/bintanong420/Bintanong/blob/p12-dev/plans/2026-11-04-development-isolation-handoff.md)

## Final engineering recommendation

**Do not begin with “make the prompt prettier.”** First fix partial evidence loss (PR1) and define exactly what an answer part and answer state mean across backend/API/frontend (PR2). Then tighten multilingual understanding and dialogue identity (PR3), and only then expand Hybrid to multiple structured operations (PR4). Re-run independent held-out acceptance after each boundary. Preserve the currently frozen evaluation build until the research owner deliberately approves a controlled promotion.