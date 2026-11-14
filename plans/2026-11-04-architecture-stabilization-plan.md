# Bintanong Architecture Stabilization: Claude Code Execution Plan

**Date:** 4 November 2026  
**Repo/ref to recheck:** `bintanong420/Bintanong`, `p12-evaluation-harness`, reviewed SHA `3d6905c0c6210fdfe118b3bea3aae7269aab198c`.  
**Author:** independent assistant recommendation, **not an approved or implemented engineering change**.  
**Read first:** `INDEPENDENT_AUDIT.md`, `AGENTS.md`, `plans/INDEX.md`, `plans/plan_current_progress/current_progress.md`, owner decisions and the thesis architecture/scope/appendix material referenced in `AGENTS.md`.

## Hard truth / objective

Do not attempt to cure Bintanong's “amnesia” with more prompt examples or `if phrase == "I already said it"`. The application lacks a real dialogue ledger, and its tests currently reward a prerequisite-listing question being converted into an eligibility clarification. The project needs a **behavior-contract correction and a bounded conversation architecture**, not a general rewrite of the RAG or SWI-Prolog stack.

**Target outcome:** a student can ask fact-only questions about prerequisites, request an individualized eligibility check, answer follow-up questions, switch topics, refer to earlier answers, and recover from a redundant clarification; the system can reproduce this behavior from a server-owned thread without trusting past assistant text as institutional policy.

**Non-goals:** no LLM fine-tuning, unrestricted chat-to-vector memory, full Prolog rewrite, silent university-policy supplementation, stored institutional records from self-reports, automatic profile building, or new unapproved research-release activation.

## Engineering approaches and recommendation

| Option | Trade-off | Decision |
| --- | --- | --- |
| A. Continue extending `ConversationContext`/`PendingCheck` with one-off states | Small immediate diff; unbounded case coupling; cannot handle “why?” or two antecedents generically | **Reject** |
| B. Pass entire chat history from frontend each turn | Easy apparent fix; client-history authority, token growth, stale assistant text and injection/provenance confusion; restart divergence remains | **Reject as canonical design** |
| C. Server-owned thread ledger + typed working memory + bounded context compiler, staged from in-memory to durable store | More initial work and contract changes; explicit lifecycle, bounded cost, testable security and extensibility | **Recommend** |

**Important decision point:** no long-term personal academic retention by default. Implement an ephemeral server-owned thread first; a separate owner/privacy decision gates durable transcript storage. Existing 30-minute expiry may remain during the first slice provided the UI clearly reports context reset.

---

## Overall sequence (one bounded PR/commit family at a time)

| Phase | Deliverable | Gate before moving on |
| --- | --- | --- |
| 0 | Pin, reproduce, instrument, preserve baseline | Repro recorded with current deployed build + compiler ON/OFF; source-only uncertainty explicit |
| 1 | Correct fact-only prerequisite listing contract | `list prereqs` answers; eligibility still asks for unknown results |
| 2 | Thread/turn ledger and generic unresolved state (in-memory adapter) | “I already said it,” “why?”, multi-entity, topic switch and interrupted answers pass |
| 3 | Router ContextCompiler and typed state/status mapping | No `empty_clarification -> missing source` for dialogue repair; trust boundary intact |
| 4 | Frontend transport parity and lifecycle | Browser sends actual typed text; server owns thread; no hidden question replay |
| 5 | Persistence/privacy and restart recovery **only after policy signoff** | Authorized rehydrate, deletion, RLS/ownership, retention and privacy tests pass |
| 6 | Graduation source diagnosis and focused RAG correction | Root stage verified; no invented policy or phrase patch |
| 7 | Router/generation consolidation and held-out evaluation | Independent generalization and source-coverage metrics; regression gate clean |

## Phase 0 — Baseline freeze and independent reproduction

**Before touching code:**

```bash
pwd
git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline -20
git diff --stat
git worktree list
```

Read `AGENTS.md`, scope controls, owner decisions for blank prerequisite cells, architecture sections (as instructed by the repository), and `plans/2026-11-03-memory-eligibility-results.md`. Identify active local unpushed changes and the actual server's version/pin/flag. Do not discard dirty changes or land directly on the busy `p12` worktree without coordination.

**Add explicit reproduction cases** in a new fixture file, with no positive institutional claim beyond what the reviewed ledger establishes. Use synthetic IDs for focused unit tests; for live BSIT IT 14/L, pin the exact reviewed curriculum, source hash and version.

- C01: `Ano ang prerequisites ng IT 14/L?` / selected `bsit-2018-2019`. Current behavior to diagnose: lists IT 3/L then asks “naipasa mo ba?”. Expected new behavior: `answered` with requirement and citation/structured provenance; no grade question.
- C02: `Can I take IT 14/L?` with no completion facts. Expected: conditional/clarification_needed asking about IT 3/L if necessary; no invented eligibility.
- C03: `Can I take IT 14/L? I passed IT 3/L.` Expected: checked result and attribution to user statement, not registrar certification.
- C04: `how to apply for graduation?` Expected **not predetermined**: trace source coverage; answer only if applicable reviewed procedure exists, else a precise evidence-gap response.
- C05: a reproduced generic assistant clarification followed by the user utterance `huh i already said it`. Expect generic dialogue-reference recovery if original subject is available, otherwise explicit honest context-loss, never blanket missing-source claim.
- C06: `Compare CC 4/L and CC 5/L` then `the other one?`; preserve two antecedents or clarify which; never guess.
- C07: an already answered question then `why?`; re-evaluate from pinned source/Prolog, do not cite the prior assistant as primary evidence.
- C08: a graduation question after a prerequisite question; topic switch should not inherit old course or `PendingCheck`.

**Capture one row per stage** using opaque IDs and sanitized values:

```text
head_sha / config flag / release_id / curriculum_id
session_id_hash / conversation_id / turn_id / revision
actual_client_text_hash / effective_router_text_hash (differ? why?)
prior_memory_summary / unresolved_state_kind / prior_completed_turn_count
router_operation / route / diagnostic / guards_applied
selected_topics / retrieved_source_ids / coverage_status
symbolic_predicate / outcome / unknown_conditions
generator_status / failure_reason / UI_status
```

No transcript/grade content in persistent logs; raw fixture inputs stay in local test artifacts with restricted access.

**Gate:** reproduce current behavior at pinned HEAD (or explain why deployed build differs), record with compiler OFF and ON. Do not claim both flags behave the same without a run. New feature specs should fail RED on old behavior.

---

## Phase 1 — Fix prerequisite-listing versus eligibility semantics

### Contract decision

Formalize three distinct user intents:

1. **`list_course_prerequisites`**: “Ano ang prerequisites ng IT 14/L?” The operation returns reviewed prerequisite/co-requisite structure without needing the student's academic record.
2. **`check_prerequisite_eligibility`**: “Can I take IT 14/L?” Evaluate the student's provided/confirmed facts; request missing results only when necessary.
3. **`list_missing_prerequisites`**: “Which prerequisites am I missing?” Personalized gap check, conditional on supplied records and rule semantics.

Name is a recommendation; maintainers can pick a different explicit identifier if it better fits current contracts, but **the semantic distinction is non-negotiable**.

### Touch points

- `backend/bintanong_routing/contracts.py`, `wire.py`, `prompt.py`, `validation.py`, `compile.py`, `router.py`: request/schema and interpretation, including companion/repair paths; semantic router must distinguish “what are the prerequisites” from “can I take.”
- `backend/bintanong_contracts/symbolic.py`, `backend/bintanong_orchestration/adapters.py`, `backend/bintanong_symbolic/runtime.py` / existing generic rule evaluator: read-only requirement-description capability with canonical rule tree and provenance, not a second hand-coded copy of course prerequisites.
- `backend/bintanong_generation/decision_reply.py`, `render.py`, `generator.py`: an `answered` result for reviewed requirement-only queries. Absence of completion fact does not force a question.
- `tests/test_generation_prerequisite_list.py`, `evaluation/conversations/cases.json`: replace the incorrect expected `clarification_needed` for fact-only queries; keep separate eligibility tests that still expect clarification when required.

### RED / GREEN / REFACTOR acceptance

**RED tests:** two unrelated synthetic curricula plus BSIT reviewed fixture; ask English, Filipino, Taglish; assert operation identity, no completion fact required, correct rule shape, source/ref, no decision outcome for mere listing, and `answered` status where source review is complete. Cover blank reviewed cell, explicit None, a printed but unresolved condition, co-requisite, `any_of` and `all_of`. Verify request to *list missing* still computes missing student results.

**GREEN gate:** eligibility tests unchanged; user-reported facts and Prolog exact scope not weakened; unrelated curriculum outcomes not copied; all source gaps remain accurately qualified.

**REFACTOR gate:** remove the old normative expectation, not the negative fixture. Document why it changed, with the screenshot as evidence. Do not make the wording change only; change the operation/intent contract.

---

## Phase 2 — Add a server-authoritative dialogue ledger (ephemeral first)

### Recommended abstractions

```python
@dataclass(frozen=True)
class ConversationTurn:
    turn_id: str
    conversation_id: str
    role: Literal['user', 'assistant']
    text: str
    status: Literal['accepted', 'completed', 'failed', 'cancelled']
    created_at: datetime
    source_refs: tuple[str, ...] = ()  # validated refs, not source text

@dataclass(frozen=True)
class UnresolvedDialogue:
    originating_user_turn_id: str
    assistant_question_turn_id: str | None
    requested_operation: str | None
    missing_slots: tuple[str, ...]
    candidate_entities: tuple[str, ...]
    status: Literal['waiting', 'resolved', 'abandoned']

@dataclass(frozen=True)
class ConversationMemory:
    scope: AcademicScope | None
    active_entities: tuple[EntityRef, ...]
    focused_entity_id: str | None
    unresolved: UnresolvedDialogue | None
    referenced_turn_ids: tuple[str, ...]
    revision: int
```

The types are conceptual—adapt to existing Pydantic contracts and repo conventions. **Do not put student-provided grades or personal secrets into `ConversationMemory` as truth**; keep `ScopedFact` in its existing validated store and reference its IDs when necessary.

### `ConversationStore` API

```python
class ConversationStore(Protocol):
    create(owner_identity, scope) -> Conversation: ...
    get_owned(owner_identity, conversation_id) -> Conversation: ...
    get_recent_turns(conversation_id, *, limit: int) -> tuple[ConversationTurn, ...]: ...
    get_memory(conversation_id) -> ConversationMemory: ...
    commit_turn_result(conversation_id, expected_revision, result: TurnCommit) -> Conversation: ...
    delete_owned(owner_identity, conversation_id) -> None: ...
```

Start with an in-memory implementation for deterministic unit/integration tests. Its primary purpose is to make **thread semantics explicit**, not to claim durability. Define a bounded total turn count/text budget, ownership checks, duplicate-turn/idempotency handling and a revision for concurrent requests.

### Commit boundary

The current `ChatTurns.run()` commits facts/pending check and subsequently calls `set_conversation()` as a separate operation. Replace this with one **atomic logical `TurnCommit`** that includes completed assistant response metadata, updated facts, unresolved-state update, and expected conversation revision. If the backing store spans two physical stores temporarily, use an explicit compensating strategy and test it; do not pretend atomicity exists.

A cancelled/failed turn must not enter history as a successful answer. A declined/abstained answer can be retained as *what the assistant said*, but must not be marked as an authoritative verified academic claim.

### Gate

- New Chat creates a new `conversation_id` but preserves the person/quota identity.
- Multiple course entities can remain in working memory; no arbitrary `pop()` reduction to one.
- Clear topic switch resets focus appropriately without deleting unrelated confirmed facts by accident.
- Two tabs cannot silently overwrite the same thread revision.
- A new `SessionStore` instance with the same in-memory conversation adapter (or an explicitly injected persistent one later) behaves according to the documented lifecycle.
- Existing source/private-upload isolation tests remain green.

---
## Phase 3 — A bounded ContextCompiler and honest dialogue-status contract

### ContextCompiler

Build exactly one server-side context compiler, invoked before routing:

```python
class CompiledConversationContext:
    current_user_text: str
    recent_relevant_turns: tuple[ConversationTurn, ...]
    active_scope: AcademicScope | None
    active_entities: tuple[EntityRef, ...]
    unresolved: UnresolvedDialogue | None
    student_fact_refs: tuple[str, ...]
    token_budget_used: int
```

Select by **relevance and recency**, not just last successful `course_id`. Start with last 2–4 relevant completed exchanges plus working memory; preserve original unresolved user question and the assistant clarification until resolution or explicit abandonment. At larger lengths, a compact summary may be introduced only if source/grade provenance and untrusted classification remain intact; do not summarize away the original target/negation/condition.

Maintain strict partitions:

```text
TRUSTED system/router instructions
UNTRUSTED recent dialogue and summaries (interpretive context only)
SCOPED student statements/confirmed upload facts (not official grades)
TRUSTED pinned institutional source/Prolog rule results (final answer evidence)
```

Never allow prior assistant text to seed Prolog or be cited as institutional evidence. For `why?`, use the prior answer only to recover the question/claim under discussion; re-check it against pinned source/Prolog.

### Generic repair and clarification

Model conversational acts that require no immediate institutional retrieval:

```text
ASK_NEW_TOPIC
REFINE_PREVIOUS_REQUEST
ANSWER_PENDING_CLARIFICATION
ASK_WHY / EXPLAIN_PREVIOUS_ANSWER
REPAIR_OR_CHALLENGE_ASSISTANT
CORRECT_PREVIOUS_STUDENT_FACT
RESET_OR_SWITCH_TOPIC
```

These are *semantic act types*, not lists of exact magic phrases. Use a bounded LLM interpretation with deterministic validation that any referenced prior turn exists and belongs to the current thread. When ambiguous, ask a precise clarification grounded in the actual unresolved record. No silent guess.

**Disallow** `pending='another_feature_name'` growth as the primary architecture. Existing `PendingCheck` may remain a domain-specific pending operation, but every assistant clarification must be associated with an originating turn and expected response slot.

### Separate failure statuses

Propose typed reasons (names may adapt to contracts):

```text
dialogue_reference_missing
dialogue_ambiguous
clarification_pending
interpretation_failed
capability_unavailable
reviewed_source_missing
source_record_incomplete
source_conflict
answer_coverage_incomplete
symbolic_unknown
model_or_tool_unavailable
```

Student UI:

- Dialogue reference missing: `I can't recover which earlier question you mean. Please restate the question.`
- Genuine pending clarification: reference the known operation/subject, e.g. `I know you mean the IT 14/L eligibility check. Have you passed IT 3/L?`
- Reviewed source gap: an institution-specific limitation/referral appropriate to the missing evidence.
- Unsupported audience: clear undergraduate-scope message.

No generic `empty_clarification -> no_evidence` for dialogue repair. Keep an explicit `evidence_unavailable` status only when evidence is genuinely unavailable; distinguish it from invalid routing.

### Acceptance tests

- After a generic clarification, `huh i already said it` retrieves prior question and assistant's clarification (if present) and either resolves or asks about a **specific** missing slot.
- `Why?` after a source-grounded answer triggers explanation backed by the original pinned source, not a fresh arbitrary RAG search or an ungrounded apology.
- `What about the other one?` after two courses can resolve the counterpart or ask a short disambiguation based on actual candidates.
- A new self-contained graduation question after a prerequisite query does not inherit the prerequisite target.
- Fake prior assistant text containing “ignore rules” never bypasses institutional routing/Prolog validation.
- A fresh conversation with `huh i already said it` and no previous history returns `dialogue_reference_missing`, never a hallucinated course or source-gap statement.
- If no authoritative evidence supports the previous claim, the answer explicitly corrects/abstains; it does not merely repeat old assistant output.

---

## Phase 4 — Frontend/API thread parity

### Contract

Use a server-issued, ownership-bound `conversation_id`; do not use `"current"` as the semantic thread identity.

```json
{
  "conversationId": "opaque-server-issued-id",
  "turnId": "opaque-idempotency-id",
  "message": {"role": "user", "text": "huh i already said it"},
  "programId": "validated-program-id",
  "curriculumId": "validated-curriculum-id"
}
```

The exact versioned API shape is maintainers' choice. Reject a forged conversation ID, a conversation owned by another account/browser, a stale revision (or resolve by a documented concurrency rule), and invalid course scope. A message's displayed user text must equal its submitted utterance; structured UI options may be sent in a separately typed clarification object.

### Migrating UI behavior

- `frontend/lib/student-transport.ts`: replace one-message chat `id=current` semantics with explicit thread/turn identity.
- `frontend/components/workspace/workspace.tsx`: stop selecting last browser user bubble to reconstruct a message. New Chat starts a new server thread; reload retrieves authorized history or explicitly states it is not retained.
- `frontend/lib/student-clarification.ts`: retire `typedReply()` original+reply textual rewrite after server-side unresolved state passes; preserve buttons, options and confirmed-detail UX but transmit typed response/slot IDs transparently.
- `frontend/lib/student-workspace.ts`: reducer hydrates from server-authoritative completed turn history, with consistent interrupted/failed states and a clear context-expired banner.
- `backend/bintanong_api/chat.py`, `app.py`, `stream.py`: generate/authenticate thread ID, include final turn status and reason, update ledger on an explicit completion boundary, provide safe history retrieval and delete endpoints.

**Compatibility strategy:** implement a temporary versioned adapter for existing UI transport; instrument any rewritten input, then remove the adapter after a full green migration. Do not accept an unbounded client-supplied transcript as an authoritative server history.

### Acceptance tests

- The wire request contains exactly `"huh i already said it"` while the backend can still reference earlier turns via conversation ID.
- Prior typed text and UI-visible user bubble match (no surprise concatenation).
- Refresh/re-auth behavior is explicit. Session expiry never presents an old continuous UI thread with a secretly empty backend state.
- Guest and signed-in threads cannot cross-read; `DELETE /session`/New Chat does not reset the anonymous browser quota cookie.
- Cancel/retry, regenerate, rate-limit waits and busy admission preserve idempotency and final-turn consistency.
- Frontend feature flags and backend scope requirements agree; document whether document-only questions require choosing a curriculum.

---

## Phase 5 — Durability, privacy, identity, lifecycle (separate approval gate)

**Do not implement long-term retention automatically.** For the first milestone an ephemeral thread store is sufficient to prove correct conversational semantics; it may still reset on server restart, but the UI must then say so honestly.

When durable, authenticated threads are approved, propose versioned Supabase/PostgreSQL migrations such as:

```sql
-- Logical schema, not production-ready SQL
conversations(
  conversation_id uuid primary key,
  account_id uuid null,
  guest_owner_hash text null,
  curriculum_id text null,
  revision bigint not null,
  created_at timestamptz not null,
  updated_at timestamptz not null,
  expires_at timestamptz null,
  deleted_at timestamptz null
);
conversation_turns(
  turn_id uuid primary key,
  conversation_id uuid not null references conversations,
  ordinal bigint not null,
  role text not null,
  text text not null,
  status text not null,
  evidence_refs jsonb not null default '[]',
  created_at timestamptz not null,
  completed_at timestamptz null
);
conversation_memory(
  conversation_id uuid primary key references conversations,
  memory_json jsonb not null,
  revision bigint not null
);
```

The schema is an illustration; Claude must perform threat modeling, choose appropriate RLS/service-role controls and approved retention, and keep sensitive student assertions separately scoped with deletion semantics.

**Ownership identities must remain separate:** account UUID / guest pseudonymous owner / session credential / conversation ID / selected program+curriculum / request ID / rate-limit key. No conversation ID can reset the five-questions-per-five-minute person quota. Browser cookie deletion may currently reset guest quota by policy; do not accidentally change it without owner decision.

**Required decisions before DB migration:** whether raw user/assistant transcript retention is approved; guest TTL; authenticated retention/explicit deletion; what “New Chat” forgets; whether confirmed academic facts can persist beyond one chat; what a change of account or curriculum should invalidate; access audit/RLS; archival/backups and expiry deletion.

**Persistence gate:** simulate server restart and lost session credential; authorized recovered thread keeps correct scope/turn history; unauthorized owner gets 404/403; guest expiry signals reset; all private facts/uploads are erased according to retention and deletion policy; no raw secrets in logs or model prompts.

---

## Phase 6 — Graduation source/coverage diagnosis, not another phrase patch

Trace `how to apply for graduation?` **as a standalone query**, both after a prerequisite turn and in a fresh thread.

1. Pin the actual active research release and document/ledger hashes.
2. Inspect selected document topics, specifically whether `handbook_graduation` covers the *application process*, not merely residence/eligibility/length-of-study.
3. Inspect source claim fields, not-stated limits, selected chunks, semantic retrieval scores/filters and `record_coverage`.
4. Determine whether the router emitted `RAG`, `clarify` or `evidence_unavailable`, and whether a deterministic guard changed it.
5. If evidence was available, identify the first loss: topic shortlist, claim selection, retrieval, integration, checker completeness or rendering.
6. If evidence was **not** available, preserve a clear limitation; do not fabricate application steps or silently infer an official office/process.
7. Add an independent “requirements to graduate” versus “application process for graduation” contrast test. They are not equivalent intents.

**Gate:** produce a trace-based root-cause statement with source IDs, version, claimed missing fields and a direct link to the exact code responsible. A new phrase regex alone does not satisfy this phase.

---

## Phase 7 — Routing/generation consolidation + evaluation hardening

This phase begins **after** the memory and intent contracts pass. Do not combine it with their first implementation PR.

### Rule inventory

Create a table of each post-October-30 override (`router.py` guards; `topic_selection.py` companions; `generation/*_reply.py`; checker overrides), identifying:

- trigger / source of truth / exact user request family;
- original failure / current correction / trust boundary;
- general missing primitive / whether the rule is source-driven or test-case-driven;
- two unrelated curricula and two unseen paraphrases proving it generalizes;
- deletion/refactor candidate / owner-approved research limitation.

Consolidate into general mechanisms where defensible:

```text
LLM interpretation -> typed intent / requested detail
reviewed source metadata -> evidence dependency graph
ambiguous source fragments -> provenance-aware reconstruction
source-checker instability -> deterministic extractive coverage verification
policy rules -> declarative versioned requirements, not hardcoded student phrasing
```

Keep deterministic source and Prolog guards. The goal is not “remove all if-statements”; it is **eliminate test-specific corrective behavior masquerading as architecture**.

### Separate characterization from true evaluation

- Retain existing `evaluation/conversations/cases.json` as historical coverage, correct demonstrably wrong expected statuses and document the revised semantic requirement.
- Add independent held-out sets: source-present vs absent, phrase paraphrases not seen in prompts, 3–8 turn conversations, long-gap reference, correction, topic switch, reversed course names, unknown grade, mixed Taglish, contradictory statements, two programs sharing a code, untrusted prompt-injection in history, and restart/expiry.
- Require independent answer checks against source/Prolog outcomes; literal substring matching alone is insufficient.
- Score by stage and by first divergence, not just final pass/fail. Record status confusion matrix, evidence entailment, false certainty, unsupported acceptance, false refusal, language correctness, latency.
- Evaluate compiler OFF vs ON on the **same** reproducible cases and pinned model/release; do not enable ON by default unless the change passes existing routing guard tests and held-out gates.
- Performance: measure model calls per turn, source selection/retrieval, symbolic execution, warm backend and visible browser time. Report the one-runner/four-waiting limits; never claim a response-time SLA from backend-only timing.

**Gate:** no new confirmed false-positive eligibility, source-overreach, cross-curriculum bleed, or failed transparency tests; independent held-out memory and intent cases meet owner-accepted thresholds; no new unreviewed institutional rule claims.

---

## Suggested PR / commit boundaries

1. `test(conversation): pin screenshot reproductions and trace reasons` — diagnostics/test-only; no behavior change.
2. `feat(symbolic): distinguish listed prerequisites from eligibility` — operations/Prolog adapters/generation/test spec; no conversation persistence.
3. `feat(conversation): server thread ledger and in-memory working state` — backend-only with RED/GREEN tests and no RAG/Prolog rewrite.
4. `feat(conversation): bounded context compiler and typed dialogue reasons` — router boundary; validated history is untrusted interpretive data only.
5. `feat(frontend): server conversation IDs and remove synthetic question replay` — UI/backend contract migration with browser test suite.
6. `feat(conversation-storage): explicit durable retention and deletion` — **requires separate approved privacy policy**; optional until approved.
7. `fix(rag): verified graduation source or selector error` — only after trace proves the need.
8. `refactor(router-generation): consolidate guard families` — separate architectural cleanup.

For each PR, provide: baseline SHA; files touched; RED test output; GREEN test output; unchanged trust invariants; new warnings; manual screenshot/HTTP test; rollback steps; environment flags; reviewer signoff. Keep worktrees separated and avoid direct hotfixes to serving branch.

---

## Non-negotiable release acceptance scenarios

| ID | Input/exchange | Expected outcome |
| --- | --- | --- |
| M01 | `What are the prerequisites of IT 14/L?` | State IT 3/L from applicable reviewed rule and **answer**, not ask student grade |
| M02 | `Can I take IT 14/L?` with no facts | Ask for missing relevant result; no false yes/no |
| M03 | `I passed IT 3/L` after an eligible pending check | Re-check using scoped self-report; label the premise |
| M04 | `I took IT 3/L` | No assumption that taken means passed |
| M05 | Correct a previously reported result | Newer same-scope asserted correction supersedes old statement, preserving upload conflict rules |
| M06 | `I failed CC 4/L—what's affected?` | Prolog dependency path and cited curriculum, not fabricated recovery advice |
| M07 | `What about the other course?` after two named courses | Resolve the alternative or ask precise disambiguation |
| M08 | `Why?` after an answer | Explain previous answer using validated current evidence/rules |
| M09 | Assistant asked redundant clarification; user: `huh i already said it` | Recover referent from thread or report explicit context loss; never source-gap claim |
| M10 | Fresh thread: `huh i already said it` | Report unavailable prior thread/context, no invented antecedent |
| M11 | Switch from prerequisites to graduation | No stale prerequisite target or fact question; independent source routing |
| M12 | Graduation *application procedure* not in reviewed sources | State precise absence/limit, not make up steps |
| M13 | Graduation application process present in approved records | Answer with actual applicable source, section/page, limits |
| M14 | New Chat | New thread; user quota identity unchanged; documented fact-retention behavior |
| M15 | API restart after saved thread | Recover only if persistence approved/enabled; otherwise clearly signal reset |
| M16 | Explicit curriculum switch to other track | No cross-curriculum fact leak or code-equivalence assumption |
| M17 | Concurrency/cancel/retry | No double completed assistant turn or partial state corruption |
| M18 | Old assistant hallucination quoted as prior context | Never trusted as institutional claim; repair/check rather than repeat |

**Add negative cases** for quoted false pass statements, friend-reported grades, hypothetical conditions, out-of-scope graduate/Law/Medicine, absent review version, adversarial history instructions and source conflicts.

---

## Claude Code working instructions (paste into the project)

> You are implementing an architecture stabilization, not a feature-expansion or full rewrite. Read `INDEPENDENT_AUDIT.md` and this plan; inspect repository `AGENTS.md`, current HEAD, worktree state, active deployment SHA, release pin and `BINTANONG_ROUTER_COMPILE`. Do not assume the reviewed SHA equals a teammate's unpushed worktree. Read thesis physical scope/architecture sections and appendices referenced by repository instructions before changing rules.
>
> First reproduce the user's supplied screenshot questions with current build and gather a privacy-safe step-by-step trace. Establish three separate root causes: prerequisite-intent contract, missing dialogue history/clarification binding, and the graduation RAG evidence path. Label unconfirmed hypotheses; do not patch them as facts.
>
> Then implement **Phase 1 only** in a dedicated worktree, RED first. Do not change the expected status for `What are the prerequisites of IT 14/L?` by wording alone; introduce a proper non-personalized requirement-list operation. Preserve Prolog/source trust boundaries and all-of/any-of/co-requisite semantics. Run focused and broad tests, report results, and stop for code review before the next phase.
>
> For Phase 2 onward, design one server-owned conversation ledger with generic unresolved dialogue state and bounded context compiler. Never introduce more `pending='some_feature'` variants or frontend concatenation of prior question + reply as a permanent solution. Prove that `huh i already said it` and `why?` work without exact-phrase whitelists. Do not persist raw user histories until the owner approves retention and deletion policy.
>
> Every change must include the original failing test, first incorrect pipeline boundary, fixed behavior, reason for preserving/replacing tests, and independent holdout case. Do not turn compiler ON by default without OFF/ON regression results. Do not claim a live test passed unless it actually ran.

---

## Stop conditions / rollback triggers

Stop and escalate rather than improvise if any of these occurs:

- The live serving commit or configuration differs materially from the reviewed code and the screenshot cannot be reproduced.
- A planned operation would require inventing an unreviewed prerequisite rule, source fragment or university procedure.
- Conversation history or LLM text begins to enter institutional RAG/Prolog fact stores.
- Authenticated or guest private facts cross scope/identity boundaries.
- Source gap semantics/blank-cell classification changes without reviewing `AGENTS.md` and the authoring decision.
- Tests pass only after weakening evidence validation, disabling negative cases or deleting incorrect-behavior characterization without replacement.
- Extra LLM routing calls exceed practical latency/capacity without measured accuracy gain.
- A storage change would retain academic/educational data without an approved retention policy.

**Rollback:** preserve working prior commit and flag-off behavior; feature-toggle newly introduced context compilation when practical; revert only the affected PR; keep independent tests and traces so reverting does not erase the observed defect.

## Definition of done

This plan is satisfied only when user-visible prerequisite questions are correctly distinguished from eligibility checks, dialogue continuity survives ordinary natural follow-ups, the server can truthfully describe its memory loss, frontend and backend represent the same thread, and the held-out evaluation demonstrates no regression in academic evidence/Prolog safety. Durable cross-restart history is a separate gate that cannot be called delivered until privacy policy, storage, ownership and restart tests are verified.

**Requested implementation is not yet performed.** This is an independently authored handoff against the pinned pushed SHA; Claude Code must revalidate on its actual working tree and run the tests.
