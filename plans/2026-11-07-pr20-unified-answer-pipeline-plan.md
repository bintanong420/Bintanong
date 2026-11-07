# PR #20 — Unified Answer Pipeline: Implementation and Verification Plan

**Repo:** `bintanong420/Bintanong`  
**Source:** `p12-dev` at `21be2614fb082836a89df9ce1b0dfdf568c204c8` (fetch latest before execution)  
**Integration branch:** `feature/p12-unified-answer-pipeline`  
**PR base:** `p12-dev`  
**Existing source PRs:** #18 `1f8ee4a4` and #19 `27ef19ec`  
**State on creation:** **planning-only draft. No implementation, Python/frontend tests, model queries, or institutional deployment have been performed by this PR creation.**

## 1. Product contract / reason for this PR

A student may ask a compound academic question such as “I passed CC 4/L; can I take A and B? What does the handbook say I should do next?” Bintanong must (a) understand each requested subtask in context; (b) decide which tasks require version-scoped structured/Prolog evidence and which need reviewed documentary evidence; (c) run only eligible bounded tools against the correct source/curriculum; (d) avoid dropping a successful independent part because another part lacks evidence; (e) validate claims and source provenance; and (f) display *what was answered and what was not* with comprehensible, accessible layout.

A prompt cannot fix an orchestrator that discards results, a one-operation execution contract, or a frontend that lacks per-part status. PR #20 owns the cross-layer integration; PRs #18/#19 contribute implementation source, not separate releases.

**Goal:** One reviewable PR with a lossless `question_part -> required evidence -> execution result -> validated answer -> UI block/source` chain. **No increase in unsupported claims or false-positive eligibility.**

## 2. Nonnegotiable constraints

- Read `AGENTS.md`, `plans/INDEX.md`, `plans/plan_current_progress/current_progress.md`, `plans/undergraduate-scope-policy.md`, `plans/source-gap-policy.md`, `plans/2026-10-27-english-taglish-response-decision.md`, relevant master/architecture, and thesis physical pages 17–18 before code change. Preserve source/version decisions, owner-approved prerequisite blank-cell exception and the owner-approved curriculum route architecture.
- Research is **PalSU undergraduate academic affairs**. Graduate, professional Medicine/Law and staff-only procedures are excluded unless an undergraduate-applicable component is independently reviewed; source data is preserved rather than fabricated.
- Input languages: English / Filipino / Taglish. Reply language: English for English input; Taglish for Filipino or Taglish input. Keep explicit code names, formal terms and citations accurate. Internal legacy `fil` is not a third reply locale.
- Institutional source/review release, curriculum edition, course target, student grade state, operating rule version and source pin are immutable proof constraints. A proposed curriculum is not official policy. “Took” is not “passed”; a blank *reviewed prerequisite cell* is no prerequisite under the 4 Nov owner exception, but blank document/fee fields are not zero.
- Keep symbolic operations to registered curriculum/catalog operations. Policy and student procedure are documentary unless they independently request a supported curriculum operation. No arbitrary model-generated Prolog goals.
- Do not change `p12-evaluation-harness`, frozen gathering services, shared real data, model assets, `.env` secrets, published release flags or authoritative source bundles. Development tests use separate resources/ports; research candidate remains candidate-only.
- Preserve `BINTANONG_ROUTER_COMPILE` default OFF unless gold evaluation and owner sign-off justify change. Reuse dialogue and safe Markdown renderer; do not duplicate subsystems.

## 3. Source PR inventory and import policy

PR #18 adds `bintanong_routing/domains.py`; modifies router prompt, validation, routing, adapters, orchestrator and text rendering; adds source/research notes and domain/calibration tests. PR #19 adds `bintanong_orchestration/compound.py`, its research notes and `tests/test_compound_symbolic.py`. PR #19 is **stacked on #18**, not an independent copy. The 3+2 source commits in order:

```text
bd904be829c274c8359454123428479a136c3a63  refactor: curriculum-only symbolic boundary, topic-mismatch distinction
c835d862710a35662503a7c711f559803d0320ec  docs: Aurora comparison and architecture
1f8ee4a47b59a630c04305521f98a9f9bb9e476f  fix: research calibration gate
4c61e6cb83c85e0d9a5a93bbf8505de1f84ecf46  feat: bounded two-check research executor
27ef19ec9cd565ced81c3c6746bb0ad225c18f7b  feat: candidate-only routed research entrypoint
```

**Import after branch snapshot:** Start from latest `origin/p12-dev`; cherry-pick these exact commits using `-x` one at a time and resolve conflicts semantically, not via `-X theirs` wholesale. `p12-dev` is ~51 commits ahead of the shared old source base, so expect conflicts/overlap. If a commit has become redundant, explicitly document the equivalent target SHA and skip *only with evidence*. Import #19's two commits once; do not merge the entire #19 branch after importing #18. Keep older PRs open until parity, and then close them **unmerged/superseded** with a pointer to PR #20; no force-push or deletion required.

Commit gate: all intended #18/#19 code and tests are present or intentionally superseded. `git diff origin/p12-dev...HEAD` contains only integration/audit changes. No ordinary student-facing multi-op dispatch enabled as an accidental side effect.

## 4. Work packages, in one PR / in commit order

### A — Integrate prior work, preserve current P12 behavior

**Affected:** `backend/bintanong_routing/{domains,prompt,validation,router}.py`, `backend/bintanong_orchestration/{adapters,orchestrator,compound}.py`, `backend/bintanong_generation/render.py`; corresponding tests/docs. **Explicitly retain** current `compound_request` guard in the student path until section D's tests pass.

- Confirm all nine operations belong to exactly one host allowlisted domain (`curriculum_catalog` vs `curriculum_constraints`) and the execution adapters agree with the domain registry.
- Ensure policy-only procedural questions—even if they mention courses—do not induce Prolog.
- Preserve PR #18's strict conditions before research-calibration promotion: only sole calibration gap, exact requested reviewed claims, bound source fields that are nonblank and in emitted passages. Later sufficiency validation is still mandatory.
- Use PR #18's *topic not checked* wording only where no reviewed topic was matched; don't call it a corpus absence finding.
- Keep PR #19 synthetic-only, two independent same-curriculum `check_prerequisite_eligibility` operations, distinct targets and part IDs, and bounded sequential executor. Verify it remains outside student answer flow.

**Exit:** focused regression green, no capability broadened, provenance recorded.

### B — Fix multi-document partial-evidence drop (H02)

**Confirmed baseline:** `backend/bintanong_orchestration/orchestrator.py::merge_documents` returns the first non-OK document result, discarding successful independent topics. `tests/test_orchestration_multi_topic.py` currently endorses the global hold, while generation ledger supports `some_parts_unavailable`.

**Design:** Introduce or reuse a typed `DocumentTopicOutcome` and `DocumentEvidenceBundle`: `part_id(s)`, reviewed `subject_id`, requested claims, retrieval status, source/release ID(s), passages/claim coverage and exact gaps. Do *not* globally coerce all results to `ok`. Use an explicit combination policy:

| Topic conditions | Allowed aggregation |
|---|---|
| All `ok`, consistent release/source | Complete evidence |
| One clean supported, one independent insufficient/not-in-evidence | Partial evidence; preserve successful part, mark second unavailable |
| All unsupported | Withhold / honest insufficiency |
| Conflict affecting one part | Withhold that part and avoid contradicted claims; globally hold if conflict/scope impacts shared assumptions |
| Release mismatch / untrusted or invalid source | Hard hold for the mismatched data; no cross-release merging |
| An unselected/not-checked topic | Distinct not-checked status; not falsely described as source absence |

Bind documentary part ID to selected topic(s) before retrieval and preserve mapping through `integration.py` and `generation/part_answers.py`; bounded claim ledger remains authoritative. Never let one successful part authorize a missing fee, step, grade or approval condition.

**Tests:** 2 OK; 1 OK + 1 missing; all missing; unsupported topic; contradictory source; mismatched releases; duplicated chunk IDs; ordered service steps; conditional source fields; unrelated claims never gain evidence.

### C — Define and render `AnswerPresentationV2` (H03–H05, H09)

**Producer:** post-validation deterministic host mapping, not raw model-generated display instructions. **Consumer:** FastAPI SSE metadata and strict TypeScript Zod schemas with safe React UI. Keep legacy `student_text()` validated text as a backwards-compatible fallback.

Suggested contract (refine against actual existing Pydantic schemas; do not copy speculative names blindly):

```json
{
  "schemaVersion": "bintanong-answer-presentation-v2",
  "coverageState": "partial",
  "parts": [
    {
      "partId": "r1",
      "label": "Can I take course A?",
      "evidenceNeed": "structured",
      "state": "answered",
      "blocks": [{"type": "verdict", "text": "Not eligible under the selected curriculum."}],
      "sourceIds": ["ev-<64-lowercase-hex-digest>"]
    },
    {
      "partId": "r2",
      "label": "What is the fee?",
      "evidenceNeed": "document",
      "state": "unavailable",
      "blocks": [{"type": "limitation", "text": "The fee is not established by reviewed evidence."}],
      "sourceIds": []
    }
  ]
}
```

Use genuine source IDs in implementation/tests, not the illustrative placeholder above. Other states distinguish `unknown`, `clarification_needed`, `not_checked`, `withheld`, and `answered`; keep finite union and state-specific invariants. Recommended block variants: `summary`, `verdict`, `explanation`, `steps`, `limitation`, `source_notice` with bounded lengths, steps and IDs. Only validated claims or fixed host-approved notices enter blocks. No arbitrary HTML, JS, CSS or unsupported Markdown directives. Display `conditional` as a student-fact qualifier, not a university certification badge. Evidence ID references must exist in released citations; source cards must not duplicate unnecessarily.

**SSE:** Continue text-start/text-delta/text-end and existing `source-document` ordering; add a versioned, optional typed `data-answer.presentation` (or negotiate a separate event) after successful validation. Update `frontend/lib/student-contracts.ts` Zod **and** actual frontend parser/transport, `frontend/components/workspace/conversation.tsx` renderer and UI tests together. The existing `planView` feature stays disabled until explicitly supported by a separately validated typed contract.

**Visual hierarchy:** concise result first; individual part headers/status, prerequisites/conditions, ordered steps, citations and source limits adjacent; fallback safe Markdown, no raw HTML injection, 390px and desktop overflow/accessibility tests.

**Exit:** every displayed supported claim traces to one result/part and exact source; partial never shown as fully answered; old text-only and error streams still parse; stream is never unvalidated draft text.

### D — Wire bounded two-check and mixed Hybrid path (H01)

Import and reuse PR #19's validated research executor, **do not reimplement it**. After per-part evidence and presentation are ready:

1. Add a versioned `ExecutionPlan` composed from validated request parts and verified scope, with part-to-operation mapping. Supported initial modes: `1 Symbolic`, `1 Symbolic + N bounded document topics` (existing), `2 independent Symbolic`, `2 independent Symbolic + 1 document topic` (new).
2. Preserve `plan_two_eligibility_checks` constraints: exactly two registered `check_prerequisite_eligibility` operations; one program, one curriculum, same pinned release, distinct targets, distinct question-part IDs, no grade completion guesses, no dependent operation chaining.
3. For mixed Hybrid, reuse the exact per-part safety and tool-result typing. 2 eligible + 1 missing document is **partial**, not total failure and not a fabricated policy outcome.
4. For 3+ operations, different curricula, unsupported operation combinations, missing scope/grades or ambiguous course mentions, explicitly clarify/withhold; never silently run the first operation only.
5. Execute bounded symbolic calls sequentially if needed for worker admission. Avoid arbitrary parallel model/tool saturation. Keep per-stage latency logs and cancellation propagation.
6. Gate student-facing capability behind an explicit default-OFF development feature; synthetic research route remains available without feature escalation. Activation requires witnessed acceptance and owner approval.

**Exit:** two independent results present with their real provenance, or explicit safe unknown/abstention; document part separately grounded; no existing single-operation flow regression.

### E — Task understanding, language and dialogue parity (H06–H08/H11/H12)

- Tune router instructions only to guide existing validated task/operation/part schema; no reliance on text-only prompt compliance for policy safety. Distinguish `what prerequisites are` (catalog) vs `am I eligible` (rule) vs `what should I file` (document) vs compound request.
- Add small independent EN/Filipino/Taglish gold fixtures for semantic equivalence including negation and `took`/`passed` distinction, program/curriculum scope, policy vs Prolog, and mixed part ordering; measure routed parts and final semantics separately.
- Reuse existing `backend/bintanong_private_context/dialogue.py`/`context_compiler.py`/`sessions.py` bounded dialogue. For clarifications, plan a host-validated `replyToTurnId` / requested slot(s) contract so `frontend/lib/student-clarification.ts` does not masquerade an appended old question as new user text. Preserve session/revision checks and expiry fallback.
- Preserve English/Taglish reply policy across fixed notices, errors, parts, source limitations and response streams; do not mistake `fil` raw evidence label for desired output.
- Report compile flag OFF/ON as comparative evaluation **without altering the default**.

**Exit:** no repeated clarifications from stale client-generated question composition; response language and semantic route correct under approved gold, with stated failures retained as failures.

### F — Freeze verification evidence, review and closure

**Before marking ready for review:** run targeted tests, full feasible Python suite, TS, UI tests, Next build; maintain a test evidence matrix with exact SHA/runtime/model/release/flag and pass/fail/blocked reasons. Use private human-adjudicated original PDF-backed tests in isolated development environment without committing raw files. Avoid claiming 72/72 from November 6 export; 3 marks were inferred. Compare baseline and candidate latency under the same run protocols; warm backend and browser click-to-render are not interchangeable metrics.

New PR must show:
- Imported source PR #18 and #19 file/commit parity (or documented superseded equivalent).
- No source release mismatch, cross-edition data leak, unknown-grade-as-passed, unreviewed procedure asserted as complete, or unsupported source citation.
- Full task coverage for supported shapes; explicit partial/withheld for unsupported shapes.
- Separate developer-only and student-visible gates; candidate-only remains default.
- No changes to evaluation-harness, public deployment, credentials, real data, or institutional approval state.
- Reproducible code/test commands and attached/referenced results. If local runtime is inaccessible, record **NOT RUN** and leave draft.

**Only after PR #20 is reviewably complete:** close PR #18 and PR #19 as superseded **without merging**. Link exact historical commits and preserve discussions. Owner controls subsequent merge/promotion; this PR is not approval for university deployment.

## 5. Mandatory regression/acceptance matrix

| ID | Scenario | Evidence expected | Must not happen |
|---|---|---|---|
| A01 | Policy-only question mentions a course | RAG-only request | Spurious Prolog execution |
| A02 | Separate curriculum catalog fact | Pinned structured lookup | Grade clarification for a catalog lookup |
| A03 | “I took CC 4/L” then eligibility | Unknown completion until expressly stated | Treat taken as passed |
| A04 | “I failed CC 4/L; CC 5/L?” under BSCS 2018–19 | Reviewed prereq relationship and facts | Wrong edition |
| A05 | Same wording under *proposed* BSCS 2025–26 | Distinct proposed scope, proper unknown when other prereqs unreported | Treat proposal as operative or automatically eligible |
| A06 | Owner-reviewed blank prerequisite cell | Reviewed none under owner exception | Extend to blank fees/unreviewed fields |
| A07 | Two distinct prerequisite checks | Two separate truthful result states | Drop second check / invent pass |
| A08 | One check lacks grade, another ready | Partial with unknown grade | Unknown becomes eligible |
| A09 | Two checks + a reviewed procedure | Two Prolog parts + one document part, or bounded safe hold | Lose any part or fabricate source |
| A10 | One documentary topic supported, another missing | Supported claim survives; missing part visibly unavailable | Entire reply collapses |
| A11 | Documentary source conflict | Withhold contradicted claim, identify limits | Invent tie-breaker |
| A12 | Release/version mismatch | Hard hold | Cross-release evidence blending |
| A13 | Topic menu no match | “Not checked” | “Not in corpus” without checking |
| A14 | “Hindi pa pasado...” | Taglish with correct negation | English-only or opposite eligibility |
| A15 | Multi-turn “Why?” after a check | Explanation tied to previous result | New invented source/fact |
| A16 | Stale/expired clarification | Explicit reset or safe re-ask | Pretend server remembers |
| A17 | 3+ structured operations | Precise unsupported-limit clarification | Silent operation dropping |
| A18 | Long procedure with source gaps | Ordered verified steps + caveat | Omitted official conditions or unsupported steps |
| A19 | Legacy SSE client | Valid verified text + existing metadata | Schema break |
| A20 | Structured UI at 390px and desktop | Visible part states, keyboard/screen reader, safe text | Raw HTML execution, hidden horizontal overflow |
| A21 | Router compiler OFF vs ON | Parallel gold comparisons | Silent default flip |
| A22 | Restricted staff/graduate question | Scope exclusion | Unsupported university advice |

**Metrics:** route/intent accuracy per input language, operation count/target correctness, exact curriculum/source pin, per-part coverage, claim support, false-positive eligibility count (critical), extra/missing part count (critical), stream validation, UI correctness, stage and end-to-end latency. Track denominators and exact executed SHA; owner signoff alone is not independently observed run evidence.

## 6. Command-level verification gates

```powershell
# Repository root. Python 3.13 and required backend/API/test extras must be installed.
python -m pytest tests/test_routing_domains.py tests/test_retrieval_calibration_gate.py tests/test_compound_symbolic.py tests/test_routing_validation.py tests/test_routing_operation_coverage.py tests/test_routing_compile.py tests/test_orchestration_pipeline.py tests/test_orchestration_multi_topic.py tests/test_orchestration_adapters.py tests/test_orchestration_research_evidence.py tests/test_generation_pipeline.py tests/test_generation_part_slots.py -q
python -m pytest tests -q

# From repository root:
cd frontend
npm ci
npm run typecheck
npm run test:ui
npm run build

# Back at root:
git diff --check
git status --short
git merge-base --is-ancestor origin/p12-dev HEAD
```

Run live inference/PDF-backed source validation **only** with explicit model/service window and isolated resources. For failures distinguish code vs missing local data or source governance. Never mark blocked as passed.

## 7. Reviewable evidence checklist

- [ ] `origin/p12-dev` SHA freshly snapshotted; branch still current or updated by normal merge/ff.
- [ ] #18 source changes integrated with no inadvertent policy permissions.
- [ ] #19 two-check prototype integrated, still synthetic-only before wiring.
- [ ] Per-topic evidence propagation and conflict precedence tested.
- [ ] V2 presentation schema, SSE, Zod and React aligned; text fallback works.
- [ ] Compound and mixed Hybrid feature flagged and validated; unsupported cases clarify.
- [ ] Dialogue and language rules pass accepted gold fixtures.
- [ ] Full feasible unit/integration/frontend gates actually executed with logs.
- [ ] Private source evidence remains private and unchanged.
- [ ] Frozen evaluation worktree/services unchanged.
- [ ] PR #18 and #19 supersession documented only when code parity is demonstrated.
- [ ] Merge/release explicitly **not performed** without owner review.

**Status on PR creation:** All implementation and verification boxes are unchecked. Creating the plan is not implementing it.