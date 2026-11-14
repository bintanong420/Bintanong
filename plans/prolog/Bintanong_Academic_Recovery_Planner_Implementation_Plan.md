# Bintanong — Cross-Program, Policy-Aware Academic Recovery Planner
## Implementation plan and acceptance criteria

**Status:** Proposed research feature; not implemented, activated, or institutionally approved  
**Baseline:** `bintanong420/Bintanong`, `feat/memory-eligibility` at `a18398be120e91e01fc1ddb3040da92dbc5fcb9b` (inspected November 4, 2026, Manila time)  
**Design objective:** Generate *conditional, evidence-backed* academic recovery pathways across reviewed Palawan State University undergraduate curricula, incorporating regular classes, off-semester offerings, midyear enrollment, special-class requests, and relevant grade-removal routes.

## 1. Scope, outcome, and non-negotiable boundaries

Bintanong's approved research framing is a **read-only undergraduate academic guide**, not an enrollment or academic-standing authority. The thesis explicitly contemplates explaining recovery after failure of CC4/L while using Prolog to validate prerequisite consequences. A multi-term recovery planner is a proposed extension of that use case, not evidence of an already-approved optimizer.

The system shall:

1. Resolve the student's **program, major/track, campus where relevant, and curriculum edition** using the reviewed release; never substitute the current academic year for the student's curriculum.
2. Reuse **student-stated or confirmed-uploaded facts** without interpreting “taken” as “passed”; preserve `5.0`, `4.0`, `INC`, `not_taken`, and unknown as distinct states.
3. Generate up to **three ranked conditional options** over a bounded horizon (initially four to six academic terms, including summer/midyear).
4. Show term-by-term **courses, proposed mode of offering, units, prerequisite reasons, policy constraints, approval dependencies, and source citations**.
5. Separate three outcomes: **prerequisite eligibility**, **possible return to the prescribed curriculum sequence**, and **formal regular-student/scholastic-standing determination**. Never claim the third without verified applicable criteria and official evaluation.
6. Support all **reviewed undergraduate curriculum configurations** through the same code. Where coverage is incomplete, return a partial pathway or an evidence gap, not a fabricated schedule.
7. Treat all future passing grades and unapproved offerings as **scenario assumptions**, never as actual grades, enrollment, or guarantees.

**Explicitly excluded from MVP:** actual SIS enrollment, COR issuance, writing institutional records, guaranteed special-class formation, timetable conflict resolution without authoritative section schedules, academic-calendar dates not in reviewed sources, fee amount prediction, automatic course substitution/equivalence, optimization for graduation honors, and definitive academic-standing certification.

## 2. Existing reusable implementation

| Existing component | Current role | Planner reuse |
|---|---|---|
| `backend/bintanong_routing` | LLM proposes structured intents; host validates scoped aliases and facts | Recognize an academic-recovery request and verify proposed parameters |
| `backend/bintanong_private_context` | Scoped session facts and pending check; currently memory-only with idle expiry | Read factual current state; keep projected state separate |
| `backend/bintanong_symbolic` | Pinned curriculum runtime, Prolog checks, course facts and dependencies | Authoritative *within reviewed rules* prerequisite/co-requisite checks |
| `backend/bintanong_orchestration/term_assessment.py` | `assess_term_prerequisites`: checks the curriculum's prescribed courses for **one** term; no ranking or recommendation | Reuse checking logic, extend candidate generation to off-term/special-class cases |
| `backend/bintanong_orchestration/adapters.py` | Fixed allowed-operation signatures; `MultiCurriculumSymbolicAdapter` | Curriculum-dispatched execution with one pinned release |
| `backend/bintanong_generation` | Checked explanation and output validation | Explain proposed options with fixed course/approval/constraint facts |
| `evaluation/memory_eligibility` | Offline, scenario, per-curriculum, and recorded-question gates | Preserve existing regression gates; add planner gates |

**Baseline warning:** The repository report notes unresolved full HTTP/browser checks, incomplete all-curricula and recorded-question gates, and research-mode release constraints. A passing planner test is not institutional activation. The repository's November 4 owner instructions additionally state that **reviewed blank prerequisite cells mean no prerequisite**; re-pin and verify this revised rule rather than copying older test assumptions that treated those cells as unknown.

## 3. Policy evidence model (required before suggestions)

Create a **separate versioned planning-policy ledger**. Do not bury policy logic in LLM prompts, BSCS-specific branches, or independently edited Prolog copies. Each policy record needs `policy_id`, `source_version_id`, `source_span`, `effective_period`, `audience`, `campus/college/program scope`, `constraint_kind`, parsed parameters, reviewer decision, and unresolved conflict markers. Respect applicability and supersession only after review.

The uploaded **PalSU Student Handbook 2021** (BOR-approved in 2020) supplies *candidate review evidence*, including:

| Handbook section / printed page | Candidate constraint requiring verification of current applicability |
|---|---|
| Course Requirements / p. 30 | Prerequisites and sequencing normally mandatory; narrowly limited waiver route for qualifying graduating students upon Dean approval |
| Academic Load / pp. 34–35 | Regular-semester load based on the prescribed curriculum; normal summer load **9 units**; conditional higher summer limit for graduating students |
| Classification of Classes / p. 36 | Off-semester regular classes need stated minimum enrollment and available faculty; special-class requests require faculty availability, fee, and maximum **15 students** |
| Scholastic Delinquency / pp. 39–40 | Restrictions on advance courses for students with scholastic delinquency; priority for previously failed required courses |
| Removal and Completion / pp. 45–46 | `4.0` and `INC` have removal/completion procedures; a failed `5.0` is not the same route |
| Classification / p. 35 | Regular/non-regular classification is not the same as probation/scholastic delinquency |

**Never assume:** a special class has been approved, a faculty member is available, a student qualifies for overload, a section exists, a course will be available during summer, a fee is known, or a graduating-student exception applies. Where a policy is missing or supersession is unresolved, the planner marks `policy_unverified` and asks for an authorized decision.

## 4. Planning entities and invariants

Add typed, validated contracts in `backend/bintanong_planning/contracts.py` (new package):

```text
PlanningRequest
  release_id, program_id, curriculum_id, starting_term, horizon
  goal: rejoin_sequence | resolve_deficiencies | compare_options
  stated_fact_refs, scenario_assumptions, preferred_modes

ClassOption
  course_id, term, mode: prescribed_regular | off_term_regular
                                | special_class_request | summer | removal
  prerequisite_verdict, unit_load, offering_status, faculty_status
  approval_status, estimated_fee_status, evidence_refs

PlanTerm
  term_id, class_options, total_units, hard_violations
  unresolved_conditions, hypothetical_end_term_passes

RecoveryPathwayResult
  request_id, release_id, curriculum_id, scenario_id
  alternatives[], each with terms[], reasons[], source_refs[]
  status: verified_constraints | conditional | unsupported
  on_sequence_projection, formal_standing_status: unknown | review_required
```

**Invariants:**

- Student facts remain scoped to session, program, curriculum and fact origin. A what-if is scenario-only. No hypothetical pass is stored as a real pass.
- At term start, prerequisites require previously earned credit unless the reviewed rule specifically permits co-requisite enrollment. The simulator updates projected completion only **after** an assumed successful term.
- `all_of`, `any_of`, same-term rules, and broader requirements retain reviewed semantics. Missing rule coverage remains an explicit unknown except where a reviewed policy decision resolves it.
- Required units come from the reviewed ledger (`units.total` or an approved authoritative mapping); missing or ambiguous numbers block load verification.
- Every program-specific outcome must arise from selected curriculum/policy data, not hard-coded degree names or course codes.
- A special class may be **requested**, **tentatively offered**, **confirmed available**, **denied**, or **unknown**. `requested` is never synonymous with `approved`.
- Any invalid or stale release binding, conflicting student evidence, absent policy approval, or unmet prerequisite prevents a definitive claim.

## 5. Implementation work packages (sequential)

### WP0 — Freeze the baseline and policy review

- Pin the commit and release member used for tests. Capture branch status, source hashes and scope evidence (thesis printed pp. 16–17; research implementation pp. 82–84).
- Catalogue all existing prerequisite, dependency and term-check contracts; capture current tests and known failures separately from new regressions.
- Review handbook clauses above for undergraduate applicability, academic periods and possible newer amendments; hold unknowns and conflicts explicitly.
- Choose one source-backed BSCS historical scenario plus cross-program synthetic/real cases, with expected outcomes approved by a human reviewer.

**Exit:** A versioned policy fixture (possibly partially held), complete provenance map, and a reproducible baseline test report.

### WP1 — Separate factual and hypothetical planning state

- Add immutable `PlanningRequest`, `ScenarioState` and `RecoveryPathwayResult` contracts.
- Project accepted session facts into a request-local planning copy; never change the session facts when a scenario advances.
- Support student corrections and “special class denied” / “I passed it” follow-ups. Actual corrections follow the existing evidence and session lifecycle; scenario revisions do not impersonate actual grades.
- Add a distinction between **on-sequence target** and **institutionally confirmed standing**.

**Exit:** Tests prove what-if passes, requested offerings and another student's facts never become real student completion facts.

### WP2 — Generate class and recovery actions

- From the chosen curriculum release, enumerate remaining courses, their prescribed terms, units and source spans. **Do not restrict candidates to a single term's prescribed list**; the current `assess_term_prerequisites` intentionally does.
- Produce actions: normal prescribed course, off-term regular offering (conditional), special-class request (conditional), approved summer offering when known, retake, and grade `4.0`/`INC` removal when applicable.
- Filter or mark each action against prerequisite rules, unit totals, summer limits, applicable advancement restrictions and required approvals.
- For unknown class offerings, return **request candidate** or **unverified offering**, never confirmed availability.

**Exit:** One set of candidate-generation rules works without edits for synthetic programs with unfamiliar identifiers and for distinct real undergraduate curricula.

### WP3 — Bounded multi-term solver

- Implement in `backend/bintanong_planning/solver.py` a host-controlled search over calendar-order terms (e.g., 2nd semester → midyear → next 1st semester).
- Generate possible class combinations, apply Prolog checks against an immutable start-of-term snapshot, and reject hard-policy violations.
- Branch separately on conditional approvals and projected passes; never treat them as facts. Provide a fallback when a special class is denied.
- Search a small configured horizon (initial cap **6 terms**) using bounded beam search; enforce deterministic beam width, evaluation count, deadline and memory caps. Report truncation explicitly.
- Lexicographically rank: **zero verified violations** → earliest conditional rejoining of prescribed sequence → fewer required approvals/unknown offerings → lower load/cost/risk. Do not call an alternative “optimal” without exhaustive or certified optimization.
- Cache repeated request-local checks by `(release, curriculum, facts hash, course, term, co-enrollment set)`; benchmark Janus worker overhead before implementing a fixed batch endpoint.

**Exit:** At least two distinct correct conditional pathways are produced for a source-backed recovery test, plus a correctly blocked result when prerequisites or load policies rule them out.

### WP4 — Integrate with current Bintanong flow

- Extend `backend/bintanong_routing/{contracts,prompt,validation}.py` with a **curriculum-scoped** `plan_academic_recovery` operation. Existing operation targets assume course/term mentions; do not fake a course target for a program-wide question.
- Extend `backend/bintanong_orchestration/{adapters,orchestrator,contracts,integration}.py` to dispatch the planner with an immutable release pin and fixed operation signature.
- Preserve research vs institutional authorization barriers. Reuse the reviewed ledger loader and Prolog runtime; do **not** let the LLM emit arbitrary Prolog or bypass the allowed-operation registry.
- When a user asks both “what can I take?” and “how do I request a special class?”, use a **Hybrid** evidence path where the structural result comes from the planner and the procedure comes from reviewed documentary evidence.
- Extend generation with bounded host-rendered tables/sections: per-term selections, eligibility reasons, requests/approvals, constraints, citations and a plain-language explanation from Bintu. Reject unsupported fees, projected approvals and false academic-standing claims.

**Exit:** A multi-turn chat can request a plan, clarify curriculum/facts, receive alternatives, then revise an approval or availability assumption without losing scope or altering real grades.

### WP5 — UI and student actions

Display three sections per alternative: **Proposed plan**, **What must be confirmed**, and **Why this plan works**. For each course, show term, mode, unit count, prerequisite state and a distinct label: `reviewed`, `conditional request`, `offering unverified`, `blocked`, or `source gap`.

Allow a scenario choice such as *“Special classes unavailable”*, *“Midyear unavailable”*, or *“Limit my load”* to cause a new server-side check. The frontend must never reclassify a conditional action as approved.

**Exit:** Accessibility, source links and status text are verified in the actual `POST /chat` stream and browser, not only an in-process demo.

### WP6 — Cross-program tests, regression and release gates

1. Run source-backed Prolog tests and synthetic fixtures before involving Gemma; keep model language understanding as a separate gate.
2. Use English, Taglish and Filipino inputs, with English/Taglish responses per the current repo policy.
3. Test BSCS older/proposed editions; Civil vs Mechanical engineering; Architecture; Nursing; BSBA Business Economics; BSEd Mathematics; Midwifery missing-term coverage; and at least one *unfamiliar synthetic* program.
4. Repeat each source-backed case with a denied special class, no available midyear option, a 9-unit summer boundary, an ordinary load overrun, and a missing approval. Expected result is an alternative or explicit inability to verify—not an invented exception.
5. Exercise release mismatch, conflicting grades, scope switch, private upload isolation, failed turns, scenario deletion, and repeated/cancelled requests.
6. Re-run existing `evaluation/memory_eligibility` **offline/scenarios/curricula/recorded** gates; report numerator/denominator for all **39** reviewed curriculum configurations and **113** recorded questions, including any untested/held cases. Run actual HTTP/browser and mixed RAG/Prolog flow tests.
7. Measure latency separately for Prolog, solver, Gemma, whole backend, and browser-visible response. If necessary, optimize approved fixed batching rather than weakening correctness checks.

**Release gate:** No source-backed false eligibility, hidden overload violation, invented approval, cross-curriculum fact leak, or silently unverified offering in acceptance cases; no new regressions in prerequisite checks. Feature remains a research candidate pending applicable governance and authorization.

## 6. Primary retrospective acceptance scenario: BSCS 2018–2019

**Scenario seed:** Student reports CC4/L failed; all other passed courses must be explicitly supplied. Starting in second-year second semester; goal is to rejoin the prescribed third-year second-semester course sequence. Treat the following historical route as **a candidate to discover**, not a schedule hard-coded into the engine:

| Period | Candidate action | Planner obligation |
|---|---|---|
| 2nd year / 2nd sem | Take eligible prescribed courses + **request CC4/L special class** | Confirm prerequisites and semester load, mark faculty/approval/fee unknown until evidence exists |
| Midyear | Take **CS4/L and CS6** after conditional completion of CC4/L | Verify prerequisite timing; reconcile actual units with the **9-unit normal summer load**; verify offerings |
| 3rd year / 1st sem | Eligible prescribed courses + **request CC5/L special class** | Verify CC3/L and CC4/L, plus total load; **if 21 prescribed + 3 CC5/L = 24**, flag apparent excess instead of treating special class as overload approval |
| 3rd year / 2nd sem | Return toward the prescribed curriculum course sequence | Validate downstream prerequisites and remaining deficiencies; **do not guarantee official regular standing** |

The solver must also explore a **midyear redistribution** alternative if a different eligible course could fit within summer load and thereby free room in third-year first semester. It must not select such a course unless curriculum placement, advancement restrictions, prerequisites and actual offering/approval constraints are checked. Another scenario removes special-class availability; the output must change rather than copy the historical pathway.

**Key success criterion:** The exact BSCS scenario is produced by the *general* action/solver logic operating on the reviewed ledger and policies, with no BSCS-specific code, and the system flags unresolved administrative conditions.

## 7. Acceptance matrix: one engine, different programs

| ID | Program/edition | Expected distinction |
|---|---|---|
| ARP-01 | BSCS 2018–2019 | Special CC4/L → midyear follow-on courses → potential special CC5/L; load and approvals reported |
| ARP-02 | BSCS proposed 2025–2026 | Uses its own different prerequisite structure; never borrows older BSCS rules |
| ARP-03 | BS Civil Engineering | `Phy 11/L` respects its own Math prerequisite structure |
| ARP-04 | BS Mechanical Engineering | Same reported Math facts may yield a different outcome from Civil Engineering |
| ARP-05 | BS Architecture | `ACAD-1/L` and `ACAD-2/L` follow checked sequence, not course-name similarity |
| ARP-06 | BS Nursing | Multi-part NCM requirements preserved; unknown clinical/RLE offering restrictions block certainty |
| ARP-07 | BSBA Business Economics | GE-PC dependency contrasted with reviewed `None` requirement |
| ARP-08 | BSEd Mathematics | Broad “all professional education and specialization” requirement remains unresolved without full reviewed set |
| ARP-09 | BS Midwifery | Absent second-year coverage yields an explicit gap, not a fake empty semester |
| ARP-10 | Unfamiliar synthetic curriculum | New codes, placements and policies work with unchanged prompts and solver |

## 8. First coding ticket / execution challenge

**Write tests first for one pinned, BSCS 2018–2019 four-period simulation** (second-year second semester → midyear → third-year first semester → third-year second semester). Tests must check actual prerequisite semantics, `special_class_request` status, summer load, a flagged potential 24-vs-21 load, projected-versus-reported grades, source references, and a denied-special-class fallback.

Then implement `contracts.py`, `actions.py`, `policies.py`, and `solver.py` in that order, keeping the router and UI unchanged until the pure planner passes. After that, make the same tests pass against **Civil and Mechanical Engineering** without adding a program-specific condition.

### Source references

- **Bintanong development thesis**, Chapter I Scope and Limitations (printed pp. 16–17); Chapter III Research Implementation (printed pp. 82–84).
- **Palawan State University Student Handbook 2021**, Book I, printed pp. 30, 34–40, 45–46; original university policy applicability and later supersession require review.
- Repository: <https://github.com/bintanong420/Bintanong/tree/feat/memory-eligibility>
- Existing implementation evidence: `plans/2026-11-03-memory-eligibility-results.md`, `backend/bintanong_orchestration/term_assessment.py`, `backend/bintanong_orchestration/adapters.py`, `backend/bintanong_symbolic/runtime.py`, and root `AGENTS.md`.
