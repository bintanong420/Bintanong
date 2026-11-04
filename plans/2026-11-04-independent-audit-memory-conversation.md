# Bintanong: Independent Repository Architecture and Failure Audit

**Audit date:** 4 November 2026 (Asia/Manila)  
**Repository:** `bintanong420/Bintanong`  
**Examined ref:** `p12-evaluation-harness`  
**Pinned SHA:** `3d6905c0c6210fdfe118b3bea3aae7269aab198c`  
**Previous reference:** `bca60a8cf35999c89c8d8a85be98f04208ec4f33` (141 commits behind examined SHA)  
**Review type:** independent static source review using the connected GitHub repository; selected tests, plans, configurations and user-supplied UI screenshots. **No local repository runtime, live model inference, SQL migration, frontend browser test, or CI run was executed by this auditor.** Reported test counts from repository notes are *author-reported*, not independently reproduced.

**Purpose:** identify why a natural academic conversation fails, provide an evidence-based architecture assessment, and supply a remediation baseline for Claude Code. This is not a security certification, institutional validation or exhaustive inspection of every source file. It covers the user-facing runtime's major trust, data and control pathways with focused code review.

## 0. Verdict

Bintanong has a defensible reviewed-source/Prolog foundation but currently **does not possess a complete conversation subsystem**. It has: (a) a tiny single-previous-turn routing context, (b) a separate store of student-supplied course outcomes, (c) one resumable eligibility/term check, and (d) frontend reconstruction of prior questions for particular clarification flows. None is a first-class ledger of dialogue turns and assistant responses.

Separately, **the expected output for prerequisite-listing queries is wrong**: the evaluation suite requires a clarification for a question asking only to *list* prerequisites. This makes the screenshot behavior a test-supported failure, not merely a model regression. The `empty_clarification -> no_evidence -> insufficient_evidence` mapping also misreports an interpretation failure as an institutional-source gap.

**Do not rewrite the entire thesis system.** Separate factual memory from dialogue memory; distinguish listing a course's requirement from checking eligibility; correct the status taxonomy; isolate source coverage failures; and require genuinely independent multi-turn evaluation before expanding more runtime correction branches.

### Severity matrix

| ID | Priority | Finding | Evidence class |
| --- | --- | --- | --- |
| A01 | **P0** | Prerequisite listing is conflated with eligibility | Confirmed: implementation + asserted tests |
| A02 | **P0** | Conversation history is not represented or sent to the backend | Confirmed: frontend + chat API + tests |
| A03 | **P0** | Clarification-understanding failure can be mislabeled insufficient institutional evidence | Confirmed mapping; exact screenshot trace unverified |
| A04 | **P0** | UI history and server context diverge; frontend replays reconstructed questions | Confirmed: source |
| A05 | **P1** | Academic-fact memory is not general dialogue memory | Confirmed: source |
| A06 | **P1** | Session is volatile; expiry/reset is silent | Confirmed: source + tests |
| A07 | **P1** | Stale/partial conversation update semantics | Confirmed code pattern; concurrency severity needs reproduction |
| A08 | **P1** | Context holds only one course/subject; prior answer absent | Confirmed: model schema + capture code |
| A09 | **P1** | Router/compiler correction stack is extensive; compiler OFF by default | Confirmed: source; author-reported ON test failures |
| A10 | **P1** | Dialogue evaluation is incomplete and partly encodes bad expectations | Confirmed: cases + runner |
| A11 | **P1** | Graduation-procedure failure not attributable to memory without a trace | Open hypothesis requiring runtime diagnosis |
| A12 | **P1** | Recovered scope is applied after initial fact filtering | Confirmed ordering; impact conditional on no-scope callers |
| A13 | **P2** | No explicit chat/thread ID or durable conversation lifecycle | Confirmed: source |
| A14 | **P2** | Operational admission and rate limiting are process-local | Confirmed: source; multiworker risk conditional |
| A15 | **P2** | Blank prerequisite policy changed materially on November 4 | Confirmed owner instruction; institutional correctness not verified |
| A16 | **P2** | Instrumentation lacks a safe, end-to-end conversation-recovery diagnostic contract | Source-design inference; adequacy needs operational examination |
| A17 | **P2** | Potential frontend/backend curriculum-lock contract mismatch | Confirmed difference; whether intentional needs owner check |
| A18 | **Strength** | Scoped facts, source pinning, reviewed release restrictions, isolated uploads | Positive code design; not a security proof |

---

## 1. Direct analysis of the screenshots

### Screenshot 01: prerequisites and graduation

Visible messages:

- Student: `Ano ang prerequisites ng IT 14/L?`
- Bintanong: IT 14/L requires IT 3/L, then asks whether IT 3/L was passed and returns a clarification-type reply.
- Student: `how to apply for graduation?`
- Bintanong: reviewed-source information incomplete/unavailable.

**S01 is a proven semantic-contract bug (A01).** The student asked *what prerequisite is listed*. There is no grade premise to evaluate. A deterministic source-grounded `describe/list prerequisites` answer should not be conditional on the student's prior pass/fail outcome. A second, explicitly requested *eligibility* question would use the symbolic check and request missing student facts.

**S02 is unproven as a memory bug (A11).** An independent graduation application question can fail because the source does not contain a procedure, because the selected document topic lacks the required claim, because retrieval missed the right record, or because the generation coverage checker withheld the answer. Neither the screenshot nor this static audit identifies the actual live route. Inspect the trace before writing a graduation-specific fix.

### Screenshot 02: clarification and conversational repair

Visible messages:

- Bintanong: `Could you tell me which subject or topic you mean?`
- Student: `huh i already said it`
- Bintanong: `This information is not in Bintanong's reviewed sources yet...`

**S03 exposes absence of a general clarification protocol.** The assistant text is a generic fallback; there is no guaranteed server-held unresolved request or assistant question for the next utterance to reference. The screenshot does not show every earlier turn, so it cannot establish precisely what the original subject was.

**S04 illustrates a plausible mapping fault (A03).** A message objecting to a redundant clarification is a dialogue-repair act, not an institutional-source query. The exact model proposal is unavailable. However, the source explicitly maps `empty_clarification` to `no_evidence` and then to the student's `insufficient_evidence` copy. Reproduce with a route diagnostic to prove the live transition.

**Artifacts:** `screenshots/01-prerequisite-and-graduation.png` and `screenshots/02-clarification-and-amnesia.png`. Their visible messages are observations, not proof of internal routing state.

---

## 2. Current effective architecture

```text
Browser React workspace
  state.messages[] (client-side history)
  ├─ normal query: current text only
  └─ special clarification: rewritten original question + typed/selected reply
        ↓
frontend/lib/student-transport.ts  ->  one last user message, id="current"
        ↓
POST /chat  ->  ChatTurns.prepare() uses request.messages[-1]
        ↓
SessionStore (RAM)
  ├─ ConversationContext: previous one-course/one-topic/operation snapshot
  ├─ ScopedFacts: confirmed/uploaded or acknowledged user assertions
  └─ PendingCheck: one missing completion/enrollment/term answer
        ↓
follow_up_context() -> RequestContext
        ↓
Router -> optional topic selector -> LLM interpretation
        ↓
multiple deterministic host corrections -> validation
        ↓
Orchestrator -> pinned reviewed RAG / version-scoped SWI-Prolog
        ↓
Generator -> supported answer or source/clarification/failure status
        ↓
end_turn(facts, pending check) then set_conversation(captured route)
        ↓
Validated student-facing SSE answer / local React message append
```

No persistent, server-authoritative sequence of user + assistant turns is constructed. `ConversationContext` itself says "session memory only, never text or grades." The routing prompt signals only abstract previous-turn IDs, availability and operation parameters; it cannot condition on the prior assistant clarification or exact previous claims.

**Evidence:** [transport L72–89](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/frontend/lib/student-transport.ts#L72-L89), [chat L1–3, L64–98](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_api/chat.py), [session store](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_private_context/sessions.py), [router prompt L281–305, L308–341](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_routing/prompt.py#L281-L341).

---

## 3. Root-cause findings, with independently inspected evidence

### A01 — Wrong prerequisite-listing semantics [P0, confirmed]

- The application supports `check_prerequisite_eligibility` and `list_missing_prerequisites`. The latter concerns **missing prerequisites for the student's situation**, not a fact-only description of requirements. There is no independent `list_course_prerequisites` capability in the inspected operation registry.
- `render.py` comments state that a prerequisite check with no passed/failed fact will list requirements **and ask which were passed**. `test_generation_prerequisite_list.py::test_no_stated_fact_asks_about_the_single_prerequisite_directly` asserts that clarification. The `evaluation/conversations/cases.json` entry `course-bsit-prereq` explicitly expects status `clarification_needed` for `What are the prerequisites of IT 14/L?`.
- This is why even a correctly implemented memory module cannot fix the screenshot.

**Change:** introduce a distinct read-only prerequisite description capability or an equally explicit typed mode where describing the requirement tree is disjoint from eligibility decisions. **Recommended:** add `list_course_prerequisites` returning reviewed rule structure, source/version and unresolved status; no `ScopedFact` requirement. Preserve `all_of`, `any_of`, co-requisites and printed/unreviewed conditions. Keep `list_missing_prerequisites` for personalized gaps. Re-specify evaluation first.

Evidence: [evaluation fixture](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/evaluation/conversations/cases.json), [generator test](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/tests/test_generation_prerequisite_list.py), [render L52–60](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_generation/render.py#L52-L60), [validation operations](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_routing/validation.py).

### A02 / A08 — Missing first-class dialogue ledger; lossy antecedents [P0/P1, confirmed]

- Frontend sends the current message only. Chat API deliberately reads only the last user message; the test suite enforces this.
- `ConversationContext` contains one `course_id`, one `subject_id`, a pending transfer flag, a detail, and a previous operation/year/semester. There is no list of entities, previous user utterance, previous assistant message, summary, unresolved dialogue record, answer propositions or citation refs.
- `capture()` stores the course only when one is selected; multiple courses yield no course focus. Its previous-turn prompt offers the model `course_available=true` rather than a complete discourse context.
- `tests/test_routing_follow_up_memory.py::test_memory_holds_no_text` explicitly enforces the no-text schema.

**Change:** server-authoritative per-thread turn ledger plus bounded working memory; context compiler explicitly selects relevant turns/claims while **never using chat as institutional evidence**. A transcript alone is not an academic fact database.

Evidence: [chat](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_api/chat.py), [contracts L58–75](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_routing/contracts.py#L58-L75), [capture](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_private_context/conversation.py), [tests](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/tests/test_routing_follow_up_memory.py).

### A03 — Invalid status taxonomy for dialogue repair [P0, confirmed mapping]

Three code layers cause an interpretation failure to masquerade as a source gap:

```text
Router validation:
  empty clarification lacking operation/claim/reference
  -> diagnostic: empty_clarification, control: evidence_unavailable

Orchestrator:
  _ROUTING_FAILURES['empty_clarification'] = 'no_evidence'

Generator/render:
  fallback_status('no_evidence') = 'insufficient_evidence'
  -> "This information is not in Bintanong's reviewed sources yet..."
```

A true missing institutional clause and a failed discourse reference should not share the same reason. The application currently has generic wording for clarification even when no typed missing field was identified.

**Change:** separate **dialogue resolution**, **route interpretation**, **capability availability**, **retrieval coverage**, **source incompleteness**, **validation failure**, and **system error** into stable machine-readable reason codes. Render student wording appropriate to each and pass typed `unresolved_dialogue` in metadata. Make generic clarification recover prior question or declare missing conversational context explicitly; no source-office referral for plain conversational repair.

Evidence: [validation L361–368](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_routing/validation.py#L361-L368), [orchestrator L25–38](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_orchestration/orchestrator.py#L25-L38), [render L7–21 and L163–171](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_generation/render.py#L163-L171).

### A04 — Frontend fabricates conversational context [P0, confirmed]

`workspace.tsx::prepareSend()` obtains the last visible user bubble and passes it to `typedReply()`. `student-clarification.ts` explicitly says the server keeps IDs only, so the reply alone loses what was asked. It constructs `original + "\n\n" + reply`, and sometimes selects scope based on a typed program name. This is an integration workaround, not transparent dialogue state.

**Risks:** the text shown as the student request can differ from what they typed; the reconstructed string can re-trigger old intent, contaminate evaluation, exceed input caps, or be interpreted as a new composite request. A correct server conversation should need only the actual typed utterance plus a bound thread ID; structured clarification options should be typed metadata, not rewritten pseudo-transcripts.

Evidence: [workspace L114–135](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/frontend/components/workspace/workspace.tsx#L114-L135), [clarification L54–90](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/frontend/lib/student-clarification.ts#L54-L90).

### A05 — New fact memory is useful but narrow [P1, confirmed]

`private_context/memory.py` is genuinely new and useful. It handles reported pass/fail/not-taken/enrollment facts and one `PendingCheck` for a single unknown result or term. It deliberately stores IDs/states/codes, **never raw dialogue**. `pending_from()` requires exactly one waiting course/dimension. `bind_reply()` matches bounded short result words and replaces them with a newly formulated prerequisite question. `end_turn()` retires the prior pending check when a different completed turn occurs.

This supports `"Oo, pasado"` when one eligibility check is awaiting a result. It does **not** support `"why?"`, `"I already said it"`, reference to the assistant's last reason, or general multi-entity discourse.

**Change:** preserve `ScopedFact` and `PendingCheck` as domain-specific components, but place them under a broader dialogue-state/ledger abstraction. Do not rename this code to imply it stores general memory.

Evidence: [memory.py](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_private_context/memory.py), [session end_turn](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_private_context/sessions.py), [memory tests](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/tests/test_private_context_memory.py).

### A06 — Session expiry and restart silently destroy state [P1, confirmed]

`SessionStore` uses a process-local dictionary, `IDLE_SECONDS = 30 * 60`, and no shared backing database. `require_session()` issues a fresh session when a cookie is absent, expired or unrecognized; it does not alert the frontend that a visually intact conversation has lost server context. The existing tests intentionally assert new-process loss. The current research app constructs `ApiServices(sessions=SessionStore(), ...)`.

**Change:** make thread identity and persistence explicit; short-term, surface a `context_reset` signal to avoid false continuity. Long-term, recover authorized, retained threads from shared storage. Retention is an academic privacy decision and must be approved/documented before persisting raw text or personal academic assertions.

Evidence: [sessions.py](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_private_context/sessions.py), [session L40–53](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_api/session.py#L40-L53), [research_app.py](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_api/research_app.py), [session tests](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/tests/test_private_context_sessions.py).

### A07 — Turn completion and conversation capture are separate updates [P1, confirmed structure]

`ChatTurns.run()` commits facts and the `pending_check` with `end_turn(completed=True)`, then computes a routing-derived `capture()` and calls `set_conversation()` separately. These are not one atomic transaction. Also, capture depends on the route's validation rather than whether the final student-facing result was substantively answered. If `capture()` returns `None`, the older `conversation` remains.

This can preserve stale prior focus after a failed interpretation; after a fully completed but not substantively answered route it can also store context whose assistant reply was an abstention. With concurrency/restart, fact and conversation state may diverge.

**Change:** define an explicit atomic `TurnCommit` containing the final status, actual user/assistant turn records, fact changes, focus changes, unresolved-state changes, expected revision, and a cancellation/idempotency marker. No implicit `capture() is None -> keep old context` contract.

Evidence: [chat.py run()](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_api/chat.py), [capture.py](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_private_context/conversation.py), [test_clarification_turn_keeps_the_earlier_context_for_the_reply](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/tests/test_api_chat_turns.py#L85-L92).

### A09 — Multiple interpretation/correction engines; compiler is not generally enabled [P1]

`router.py::guarded()` chains procedure/heading/topic/name/not-stated, attendance, graduation, transfer, fee/detail and check-repeat overrides. `topic_selection.py::add_companions()` injects additional documents. The new 577-line `compile.py` rebuilds an interpretation from LLM meaning but only runs when `BINTANONG_ROUTER_COMPILE=1`; default is OFF. The repository's compiler continuation report says **719 pass, 11 fail** with compiler ON in a targeted routing suite, and live ON/OFF validation remained an open gate at the report's checkpoint. These are *author-reported* outcomes, not independently executed here.

**Change:** avoid switching the compiler ON casually. Run the same deterministic and live test corpus under both flags, record regression reasons, and decide whether to promote it only after full parity + measured improvement. Separately inventory correction families for later consolidation; **do not perform a large routing rewrite in the memory PR**.

Evidence: [router L26–28, L525–645](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_routing/router.py#L525-L645), [topic_selection.py](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_routing/topic_selection.py), [compile.py](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_routing/compile.py), [compiled-routing continuation](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/plans/2026-11-04-compiled-routing-continuation.md).

### A10 — Evaluation suite checks superficial properties, and pending cases don't gate [P1, confirmed]

`evaluation/conversations/cases.json` has 35 scenarios of 1–3 turns. The `course-bsit-prereq` example enshrines the wrong expected status. No case reproduces `"huh i already said it"` or `"how to apply for graduation?"`. `run_conversations.py::check()` verifies status, required/forbidden substrings and non-emptiness; it does not inspect reasoning provenance, source applicability, failure cause or adversarial contamination. Cases tagged `pending` are deliberately excluded from the exit status. The README describes that behavior.

**Change:** keep this suite as a characterization set, but do not treat passing it as evidence of conversational competence. Create independent withheld natural multi-turn cases, separate requirement/eligibility labels, use semantic/evidence correctness grading, and score `wrong_dialogue_status` separately from `missing_source` and `unsupported_scope`.

Evidence: [cases.json](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/evaluation/conversations/cases.json), [runner](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/evaluation/conversations/run_conversations.py), [README](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/evaluation/conversations/README.md).

### A11 — Graduation source coverage is not resolved by this audit [P1, open]

The runtime contains a `handbook_graduation` topic and a correction for *how many years to graduate*, but that is not proof that an application **procedure** is among the reviewed source records. The screenshot does not expose the route, selected claim, evidence counts or final checker reason. The user needs a route/evidence trace; do not infer that the answer is definitely available or missing.

**Change:** reproduce with current release pin, record `topic_selection`, proposed claims, retrieval coverage (`record_coverage`, source IDs), reason for `insufficient_evidence`, and source-vs-question mismatch. Only add data if a verified authoritative undergraduate procedure exists and source governance allows it.

Evidence: [topic_selection.py L85–116](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_routing/topic_selection.py#L85-L116), [runtime topic menu](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_runtime/research.py), [orchestrator retrieval](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_orchestration/orchestrator.py).

### A12 — Fact scope filtering precedes scope recovery [P1, conditionally consequential]

`follow_up_context()` filters private facts by the explicit `(program_id, curriculum_id)` passed by the current request. Later routing validation can inherit the previous-turn scope. If a caller omits scope, the facts were already dropped. The current selected-program frontend generally passes both IDs; direct/API/legacy clients may not.

**Change:** derive a single canonical effective scope before filtering facts; fail closed on ambiguity. Test omitted scope, explicit switch, conflicting scope, two editions of same program and shared GE-code identities.

Evidence: [conversation.py follow_up_context()](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_private_context/conversation.py), [validation.py L229–241](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_routing/validation.py#L229-L241).

### A13 / A17 — Thread identity and scope policy need explicit API contracts [P2]

Frontend uses `chatId: "current"` and constructs its visible `messages[]` locally. No `conversation_id` or thread revision is part of normal chat request. React workspace initializes `messages: []` and has no server history rehydration. Separately, the frontend refuses chat without a chosen curriculum, but `ChatTurns.checked_scope(..., required=False)` permits missing scope (especially for document-only questions). Confirm whether the latter is intentional for public/no-program policy questions.

**Change:** introduce a stable thread ID, server-verifiable ownership, explicit start/new/delete lifecycle, history fetch, revision, and a documented program-selection policy applied consistently. Keep program/course scope separate from person identity.

Evidence: [transport L72–89](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/frontend/lib/student-transport.ts#L72-L89), [workspace reducer L19–31](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/frontend/lib/student-workspace.ts#L19-L31), [chat.py prepare()](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_api/chat.py).

### A14 — Per-person queue/rate limits are per-process [P2, conditional]

`AnswerAdmission` uses an asyncio semaphore and in-memory admitted/account counters; `QuestionRateLimit` uses an in-memory deque per account/guest-browser identity. This fits the current one-process `--parallel 1` research stack. It does not provide global correctness across two Uvicorn workers, restarted processes, or multiple replicas. The guest identity cookie intentionally survives New Chat, while the session cookie does not.

**Change:** document single-process constraint now; only distribute limiter/admission under an explicit multiworker deployment requirement. Never use `conversation_id` as quota identity. Avoid IP-only limits on shared university networks.

Evidence: [admission.py](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_api/admission.py), [rate_limit.py](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_api/rate_limit.py), [app.py](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_api/app.py).

### A15 — November 4 blank-prerequisite decision changes semantics [P2, governance risk]

`AGENTS.md` now explicitly states that a **blank prerequisite cell** in a *reviewed prospectus* is treated as "no prerequisite" as of an owner decision on 4 November 2026, superseding earlier blank -> unknown behavior. This is an owner-approved research policy, not automatically a university-endorsed equivalence for every unreviewed document or ambiguous field. Separately printed non-course conditions remain unresolved when unreviewed.

**Change:** tag the authoring rule/policy version; validate that the cell was *reviewed and truly blank* rather than extraction-truncated; preserve source page and review provenance. Measure answer deltas across this change. Do not expand the rule to missing cells or missing pages.

Evidence: [AGENTS.md source-gap section](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/AGENTS.md), [ledger policy](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/plans/owner-decisions-ledger.md).

### A16 — Need bounded, privacy-safe causal observability [P2, architecture recommendation]

`Orchestrator` already emits coarse stage events with duration, route and evidence IDs, a positive starting point. However the screenshots require reconstructing which prompt context existed, what unresolved dialogue state was available, which route and selected claim were proposed, which guard changed them, which retrieval records were returned, and why the response became insufficient. Without a consistent request/turn-level trace, developers may keep guessing.

**Change:** add opt-in local/research diagnostics using opaque IDs and redacted/sanitized values: `conversation_id`, `turn_id`, `session_recovered`, `context_revision`, `router_diagnostic`, `intent/operation`, `guard_applied`, `selected_topics`, `retrieval_coverage`, `integration_status`, `generator_validation_reason`, `user_visible_status`. Do not log raw uploads, grades, model chain of thought, credentials or student transcripts by default.

Evidence: [orchestrator.py stage instrumentation](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_orchestration/orchestrator.py), [CandidateAnswer validation fields](https://github.com/bintanong420/Bintanong/blob/3d6905c0c6210fdfe118b3bea3aae7269aab198c/backend/bintanong_generation/generator.py).

---

## 4. Independent subsystem review

| Subsystem | Assessment | Independent observations | Follow-up |
| --- | --- | --- | --- |
| Institutional source governance | **Preserve** | Research pin validates sealed artifacts and allowed audience/research-only state; topic menu contains reviewed subject/claim IDs, source gaps. | Test currentness, version conflict, unreviewed field holds; no fabricated procedures. |
| Prolog / structured curriculum | **Preserve with targeted semantics change** | Release-specific catalog, capability registry and symbolic dispatch; scoped facts are explicitly not official grades; planner additions are substantial. | Add rule-description operation; validate all-of/any-of/co-requisite/unknown and cross-curriculum release IDs. |
| RAG retrieval | **Needs incident trace** | Document path uses source-aware, pinned release and topic claims; insufficient-evidence can arise at multiple stages. | Trace graduation question; separate retrieval failure from absent policy. |
| LLM router | **High maintenance cost** | Guard chain overrides model choices, topic selection may inject companions; compiler flag off by default. | Freeze case-specific patches; abstract after memory and semantics are stable. |
| Generation/coverage | **Mixed** | Strong evidence-validation intent; many host-rendered special answers and checker fallbacks. | Inspect semantic vs literal coverage, checker non-determinism and source-quote bypasses in a later phase. |
| Dialogue memory | **Critical design deficit** | Single prior routing snapshot + `PendingCheck`; no turn ledger. | First-class server thread + bounded context compiler. |
| Student factual memory | **Useful but scoped** | Merge supports user-statement precedence and conflicts with private upload; one missing check resumable. | Preserve explicit user assertion and conflict semantics; do not treat memory as verified institutional grades. |
| Frontend | **Split-brain** | Local history; constructed reply input; `current` ID; no server rehydration. | Make actual typed utterance equal submitted text, apart from typed metadata. |
| Authentication/session | **Good boundaries; lifecycle gap** | Verified Supabase account UUID, restrictive-origin cookies, server credential hash, deliberate guest distinction. | Add server-owned thread with explicit expiry/rehydration; do not conflate account and thread. |
| Student upload parsing | **Positive isolation design** | Byte caps, type sniffing, child process parser, explicit row confirmation before `ScopedFact`. | Regression-test untrusted input and memory persistence; no inferred grade acceptance. |
| Runtime/operations | **Research-limited** | One model slot, four waiting, five questions/5 min, all per-process; latency documentation is detailed. | Re-run with live model, browser, and network; do not promise unmeasured SLA. |
| Evaluation | **Strong characterization, incomplete validity** | Many tests and recorded failure fixtures; live conversation runner checks literal substrings/status. | Separate specification, test fixture, held-out semantics and independent source review. |

Security note: reviewing a few authentication, origin, cookie and upload paths does **not** establish full security or privacy compliance. The account/guest trust boundaries are promising design choices, not a penetration-test result.

---

## 5. Evaluation validity and overfitting risks

1. **A green suite can ratify a poor user outcome.** The IT 14/L example demonstrates it: `clarification_needed` is written as an expected success.
2. **The current conversation benchmark is narrow.** Thirty-five short scripted sessions do not measure multi-turn reference, assistant self-correction, failed clarification recovery, long-gap memory, or cross-source continuation adequately.
3. **Phrase-specific host corrections risk test contamination.** QA failures repeatedly became patches and named tests; this is legitimate for characterization, but not equivalent to evidence of generalization. Preserve an unseen holdout made from independent user phrasing and unseen curricula.
4. **The compiled-routing flag needs a genuine randomized-on/off gate.** Do not compare outputs only against expectations written for the old path; score verified correct answer, proper abstention, source entailment, conversation resolution and latency.
5. **Correctness needs multiple independent dimensions.** Measure intent, scope, rule selection, Prolog outcome, source provenance, natural-language answer, factual/conditional wording, dialogue continuity and refusal calibration separately.
6. **Defects must be traceable to the first wrong boundary.** A final wrong sentence is not enough. Record first-stage divergence (UI, memory, routing, topic selection, retrieval, symbolic, generation/checker, presentation).

**Recommended metric groups:** (a) objective factual correctness; (b) prerequisite-listing vs eligibility intent accuracy; (c) dialogue reference resolution/clarification recovery; (d) correct uncertainty and abstention; (e) evidence/version grounding; (f) cross-curriculum isolation; (g) restart/expiry safety; (h) warm/cold/browser latency. No invented passing results.

---

## 6. Controls to preserve (do not regress)

- Student assertions are **user-reported and scoped**, never authoritative registrar grades. Preserve distinctions `passed`, `failed`, `not_passed`, `not_taken`, `taken_unknown`, `enrolled`, `not_enrolled`, hypothetical/reported and conflicting upload results.
- Exact course identity is valid **only in a selected, versioned curriculum**. A shared code/title does not prove equivalence, especially across tracks or old/proposed BSCS editions.
- Prolog receives only validated, bounded typed facts and reviewed rule bundles. Conversational text does not become a Prolog clause or institutional source.
- Reviewed document claims and release/source hash metadata remain the only documentary evidence for policy; do not vector-search private chat as institutional policy.
- Honest source uncertainty: malformed, clipped, superseded, non-applicable and missing documents remain distinct from absence of a rule. The narrowly owner-approved blank-prerequisite-cell exception requires reviewed provenance.
- Retain English/Filipino/Taglish understanding with English/Taglish student replies as the repository currently specifies.
- Preserve authentication, guest handling, origin checks, per-person quota identity, private upload row confirmation, cancelled-turn no-commit behavior and research-only release gates.
- Keep the existing fixed regression corpus, but **correct wrong normative assertions** and document changes rather than silently deleting tests.

---

## 7. Causal investigation matrix for the two screenshot cases

| Probe | Inspect | Required proof | Possible outcome |
| --- | --- | --- | --- |
| `Ano ang prerequisites ng IT 14/L?` | router proposed operation, Prolog result and generator status | Show actual operation and rule tree; confirm source/version for IT 3/L | Semantic operation wrong vs right operation with wrong answer contract |
| `how to apply for graduation?` | topic candidates, selected claims, retrieval `record_coverage`, generation checker | Exactly which source was missing/unavailable or why checker withheld | Genuine source gap vs retrieval/selector/coverage defect |
| Generic `which subject or topic?` | router diagnostic, `missing_facts`, capture and structured `ConversationContext` | Which ambiguity actually existed and what was retained | Empty/invalid clarification vs justified ambiguity |
| `huh i already said it` | exact submitted text; prior assistant reply; stored context; route; final status mapping | Find first stage where prior exchange unavailable or discarded | Dialogue failure followed by incorrect source-gap mapping |
| Session restart/expiry | session cookie and issued ID, `SessionStore` existence, UI messages | Whether context reset silently during visually continuous thread | Separate lifecycle defect, not assumed screenshot cause |
| Compiler ON/OFF | `BINTANONG_ROUTER_COMPILE`, same release/model/input | Both route diagnostics and first differing guard | Configuration-dependent regression vs fundamental history deficit |

**Run conditions to record:** pinned HEAD, Docker image/model digest, prompt version, research release pin, source/ledger hashes, environment flag, selected curriculum ID, pseudonymous session/turn IDs, API uptime, full staged status and observed student output. Store raw student screenshots only in the controlled audit workspace; not in production logs.

---

## 8. Independent verification boundaries

**Confirmed from code:** the absence of a dialogue transcript/ledger; narrow new fact-memory scope; the incorrect prerequisite-listing expectations; static error/status conversion; default-OFF compiled router; process-local sessions; 30-minute idle expiry; frontend question reconstruction; per-process quotas; explicit student assertion boundaries; separate threadless UI state; selected tests' behavior.

**Evidence-supported but not reproduced live:** screenshot response mechanisms; router test counts and compiler ON failures reported by contributors; the actual missing source/selected claim behind the graduation answer; possible state races; effects of test changes on the deployed API and thesis evaluation.

**Not audited:** every migration and source file; active unpushed local worktrees; current production server process/environment/logs; actual Prolog execution against the screenshot user's BSIT ledger; Gemini/Gemma model transcript; Supabase RLS configuration, transaction guarantees and retention policy; security penetration tests; university validation of handbooks/prospectuses; thesis appendix-by-appendix scientific verification.

**Material warning:** public/pushed HEAD `3d6905c` may be behind the active local tree or hosted app. Claude Code must `git status`, `git rev-parse HEAD`, identify the serving process's commit/flag and compare diffs before assuming any screenshot reflects this SHA.

---

## 9. Final assessment and recommended direction

The system's deepest issue is not simply "the LLM forgot." **The backend has no general representation of the conversation to provide.** It remembers academic facts and a restricted prior operation, but cannot recall an actual assistant clarification or an earlier claim. Meanwhile the evaluation suite expects a wrong prerequisite intent result and the error taxonomy conflates discourse failure with source absence.

**Recommended work order:** (1) freeze and instrument, (2) correct prerequisite-listing contract, (3) install an in-memory server-authoritative turn ledger and context compiler, (4) make unresolved dialogue and status updates explicit, (5) remove frontend pseudo-question replay, (6) add persistence/lifecycle only after retention policy is settled, (7) isolate graduation retrieval failure, (8) refactor correction stack as a separate task, (9) run honest held-out evaluation.

See `IMPLEMENTATION_PLAN.md` for concrete modules, test names, acceptance gates, rollback conditions and Claude Code execution instructions.
