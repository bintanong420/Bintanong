# Academic recovery — plan of action (4 November 2026)

Proposed sequence for the owner's Academic Recovery Planner plan, bounded by the thesis
([ingestion record](2026-11-04-academic-recovery-planner-ingestion.md)). Owner direction, 4 Nov: backport the useful
functions of the automatic scheduler; suggestions are acceptable only as drafts that actual university people approve.
Each step needs the owner's "go"; nothing here starts a phase, approves a policy reading or activates a release.

## Principle

Bintanong **checks**; the student and the university **decide**. The student proposes a plan (or, in Step 5, receives
labelled drafts); Bintanong verifies it against reviewed curriculum rules and reviewed Handbook policy, cites sources,
and names every approval or offering that is not confirmed. It never claims availability, approval, a future grade
or academic standing (thesis Scope/Limitations, printed pp. 16–17; Research Implementation, printed pp. 82–83).

## Handbook rules that govern recovery (reviewed release text, 4 Nov read)

Quoted from the reviewed Student Handbook topics in `p12-research-faqsplit-20261030` (release pages). "Check" = a
structured rule in Step 1/2 after owner review; "Cite" = explained with the source in Step 4; "Caveat" = stated,
never determined.

| Rule (topic, page) | Printed effect | Use |
| --- | --- | --- |
| Maximum academic load (`handbook_unit_load`, 35) | "The maximum academic load per semester is the load prescribed for the semester in the curriculum. Students who enroll in more than the prescribed load ... will not be given credit for the excess units." | Check (reading D5) |
| Summer load (`handbook_summer_load`, 35) | Normal nine (9) units; graduating students up to twelve (12) with prior Dean approval | Check |
| Overload (`handbook_overload`, 36) | Only a graduating student, better-than-average record, last semester, +6 units, total ≤ 28, Dean approval; none after scholastic delinquency in the preceding semester | Check |
| Prerequisites and waiver (`handbook_prerequisite_policy`, 31) | No credit without passing the prerequisite; waiver only for graduating students in meritorious cases who fully attended the course before, taking both simultaneously on Dean approval; if the prerequisite is failed, the higher subject gets no credit | Check + Cite |
| Advance courses (`handbook_standing`, 39–41) | Students with scholastic delinquency "shall not be allowed to take advance courses during regular semesters" | Check only if the student states a delinquency (reading D7); Cite |
| Warning / probation / dismissal (`handbook_standing`, 39–41) | 25–49% failed units → warning; 50–75% → probation; >75% → dropped; 100% → permanent disqualification; probation removed by passing >50% next semester | Caveat (never computed as the student's standing) |
| Special class (`handbook_class_types`, 37) | Not prescribed that term, requested by students, subject to faculty availability and a special-class fee, maximum fifteen (15), regular class hours | Cite; always "requested, not confirmed" |
| Off-semester regular class (`handbook_class_types`, 37) | Needs at least 35 students (lecture) / 25 (laboratory) and an available faculty | Cite; "not confirmed" |
| Removal of 4.0 / INC (`grade_completion`, 46–47) | Removal within the succeeding term; one re-examination for "4" (pass → 3, fail → 5); removal exams for prerequisites of next-semester subjects must be taken before enrollment; re-enrolling forfeits the right to remove; unremoved 4.0 → 5.0, INC → NC | Check (timing, forfeiture) + Cite (reading D6) |
| Cross-enrollment elsewhere (`handbook_cross_enrollment`, 34) | Allowed when the subject is not offered at PalSU, with Dean and Registrar approval (conditions continue in the source) | Cite |
| Substitution (`handbook_substitution`, 44–45); curriculum change (`handbook_curriculum_change`, 45) | Substitution when a required subject is not offered or the curriculum is superseded; students follow the curriculum they started with | Cite; the checker keeps the student's own curriculum |
| Change of section/subject (`handbook_change_sections`, 44) | Allowed for lack of prerequisite or conflict of schedule, with instructor consent and Dean approval | Cite |
| Maximum residence (`handbook_residence`, 42) | Degree requirements within 1½ times the prescribed program length | Caveat on long plans |
| Leave of absence (`handbook_leave`, 38–39) | Written, before the semester, at most one academic year, Dean approval | Cite |
| Classification and year level (`handbook_student_classification`, 36; `handbook_year_levels`, 37–38) | "Regular" means pursuing a program of study, full load or not; year level follows completed units (25/50/75/85%) | Caveat: "back on the prescribed sequence" is not the Handbook's "regular" |

Consequences for the owner plan (owner 4 Nov: a major warning, not a blocker): the BSCS 3rd-year-1st-semester special
CC 5/L on top of a full prescribed load stays in the plan, with a major warning that quotes the maximum-load clause
(excess units over the semester's prescribed load earn no credit) and names who decides (Dean / Registrar). The plan's
"regular-student" outcome is not the Handbook's "regular" classification and stays a caveat.

## Steps

| Step | Delivers | Builds on | Rough size | Owner gate |
| --- | --- | --- | --- | --- |
| 0 | Decisions D1–D4 below; pre-phase research record if this becomes a phase | ingestion record | short | required |
| 1 | **Load policy as reviewed structured data** | release topics `handbook_summer_load` (p.35), `handbook_overload` (p.36), `handbook_standing` (p.39) | 1 review batch | owner reviews each reading |
| 2 | **Check my plan** (core) | `assess_term_prerequisites`, what-if assumptions, Step 1 | 1–2 days | go |
| 3 | **Earliest term for a course** and **what gets delayed** | `list_affected_courses`, ledger placements | 0.5–1 day | go |
| 4 | **Recovery options, unranked, cited** (Hybrid) | reviewed `handbook_class_types` (p.37), `grade_completion` (p.47), `handbook_prerequisite_policy` (p.31), special-class fee host reply | 0.5–1 day | go |
| 5 | **Suggested drafts for adviser review** | Steps 1–4 | 2–3 days | separate go; outside the thesis as written |
| 6 | Evaluation and disclosure | memory/eligibility gates, sample queries | 0.5 day + run time | go |

### Step 1 — load policy as reviewed data

- Show the owner the exact printed clauses marked Check in the table above (maximum semester load, summer load,
  overload, prerequisite waiver, advance-course restriction, removal timing and forfeiture) with page and wording,
  in short batches.
- Record each accepted reading as a versioned policy record (source span, audience, parameters, unresolved markers);
  generate the runtime rule from it. A clause not accepted stays unused, and a load question then says the limit is
  not available and refers the student to the Registrar.
- Exit: a policy fixture whose every executed number traces to a reviewed span; unreviewed readings are held.

### Step 2 — Check my plan

- Input: the student's curriculum, stated results, and a proposed sequence of terms with courses (e.g. "special class
  CC 4/L now; CS 4/L and CS 6 in summer; CC 5/L in 1st sem"). Router operation `check_plan`, curriculum-scoped.
- For each term in order: prerequisite check on the start-of-term state; assumed passes from earlier terms added only
  as request-only assumptions (never stored as grades); unit total against the reviewed load rule for that term type.
- Output per term: works / works with a major warning (e.g. units above the semester's prescribed load, quoting
  the clause and who decides) / blocked (an unmet prerequisite) / unknown (missing rule, unit or policy); plus the conditions it depends on (special class requested, not approved; summer offering not confirmed).
- Tests first: the BSCS four-term scenario from the owner plan (§6; the 24-vs-21 term carries a major warning
  for excess units, quoting the clause, not a block; D5), a denied
  special class, a 9-unit summer boundary, Civil vs Mechanical (Phy 11/L), and one synthetic curriculum with unfamiliar
  codes; no program-specific code. Exit: all pass offline, then live through `POST /chat`.
- **Ask mode (owner 4 Nov 2026):** a plain question must be enough, e.g. "Hala, bagsak ako sa DSA, paano na yung major
  subs ko? Ano pwede ko itake para maging regular load ako agad? Ano pwede options ko?" The router reads it as one
  recovery request (failed course, goal "back on the prescribed sequence", wants options) and the reply combines, in
  order: what gets delayed (Step 3), the recovery routes (Step 4), and the greedy chain draft (Step 5) already run
  through this checker. The student does not have to type a term-by-term plan; a typed plan is still checked as is.
  "Regular load" in the student's words means back on the prescribed sequence, and the reply says so without
  claiming the Handbook's "regular" classification.

### Step 3 — earliest term and what gets delayed

- Earliest term: walk the reviewed prerequisite chain from the student's results; answer "the term after you pass
  CC 4/L (and CC 3/L)", never a calendar date or offering.
- Delayed courses: the existing affected-courses list joined with each course's prescribed term.

### Step 4 — recovery options

- For a failed or INC course, list the documented routes with their printed conditions and sources: retake at the
  next regular offering; off-semester regular class (minimum enrollment); special-class request (maximum fifteen,
  assessment fee, approvals); summer within the load rule; removal/completion where the grade allows it.
- Unranked; every route marked as needing confirmation by the office named in the source.

### Step 5 — suggested drafts (only after Step 2 is in use and a separate owner go)

- **Method: the greedy prerequisite chain (owner 4 Nov 2026, the BSCS DSA example).** Start from the failed course
  and walk its reviewed dependency chain. Place each blocked course in the **earliest term** its prerequisites allow,
  term by term: first the failed course itself (next regular offering, or a special-class request, or summer), then
  each course it unlocks as soon as everything it needs is (assumed) passed, e.g. CC 4/L → CS 4/L and CS 6 → CC 5/L
  → later CS courses. Keep the student's other prescribed courses in their terms. Each term is then run through the
  Step 2 checker (prerequisites, D5 load warning, 9-unit summer). Greedy means "as early as possible, one term at a
  time", not a search for the best plan; it is explainable step by step.
- Variants, at most three, each a small change to the same greedy chain: (A) retake at the next regular offering
  only; (B) with a special-class request; (C) with summer used where the load allows. A variant whose route is
  unavailable (special class denied, no summer) is dropped and the reply says why.
- Ordered by a stated, simple rule (fewest unconfirmed approvals, then earliest return to the prescribed sequence),
  never called "best" or "optimal".
- **Precedent: Aurora** (Lugones et al., 2026, arXiv 2602.17999; code github.com/Damrl-lab/Aurora, no license shown),
  already the thesis's central related work (external copy pp. 45, 62, 69, 112–113). Its long-term roadmap is a
  greedy planner (Algorithm 1): each term it takes the remaining courses whose prerequisites are met, ranks them by
  "unlock weight" (how many later courses each unlocks) and packs them up to the term's credit cap; Prolog enforces
  prerequisites, co-requisites, credit caps and term availability; the LLM only phrases the verified plan and answers
  INSUFFICIENT_CONTEXT when data is missing. Bintanong adopts the unlock weight as the tie-break when a term cannot
  hold every unblocked course (e.g. CC 4/L first, since it unlocks the most). Differences kept on purpose: Bintanong
  plans recovery from a failed course rather than filling every term, keeps the student's prescribed courses, uses
  the Handbook routes (special class, summer, removal) with their conditions, warns instead of hard-capping load (D5),
  and labels every draft for adviser approval. Aurora has no approval step (adviser override is its future work),
  does not treat failed courses or retakes, and was evaluated on synthetic data with 20 queries. No Aurora code is
  copied (no license shown); only the published method is followed and cited.
- Every draft headed: "Draft, not approved. Show this to your program adviser." with each required approval listed.
- A student's "approved na ng adviser" is recorded as student-reported, not as an institutional fact.
- Disclosure: an extension beyond the thesis objectives unless the owner adds it to Chapter 3; kept out of the formal
  baseline comparison unless so added.

### Step 6 — evaluation

- Re-run `evaluation/memory_eligibility` offline/scenarios/curricula/recorded and the 116 sample queries; report
  numerators per curriculum. Add plan-check cases per program (owner plan §7, ARP-01…10, as check cases).
- Measure warm backend time for plan checks separately from Gemma and browser time.

## Thesis leader's list (sent to the owner, 4 Nov 2026)

| Leader item | Where it is handled | State |
| --- | --- | --- |
| Partial unreviewed data, possibly missed items | Prerequisite review GUI (`feat/p11-prereq-queue`): 241 open cells (219 unresolved references, 19 unreadable, 3 or/exception); then decisions into the ledgers and the hosted release | GUI ready; owner review pending; ledger update step not built |
| Follow-up clarification | Follow-up memory (`723416de` … `837646b3`); remaining: a bare program name still says "temporarily unavailable"; "how about the hotel track?" without a term | Mostly done; two gaps |
| Conversationality testing | A fixed multi-turn Taglish/English conversation set (follow-ups, corrections, topic switches) run through the GUI route, plus an owner GUI round | Not started |
| Curriculum planning | This plan, Steps 1–6 | Planned; decisions open |
| Shifting/switching courses → refer to the appropriate office (NEW) | Answer from Handbook 4.1 and FAQ 8 (already fetched together), end with the offices the source names (Dean of both colleges, OSAS/Guidance, Registrar); never evaluate credits or approve the shift | Partly done (answer); referral wording to add |

## What can run in parallel

One GPU serves the model, so live runs (gates, probes, GUI testing) happen one at a time; offline code and tests,
and the owner's review work, can overlap freely. `backend/bintanong_routing/{router,prompt,validation}.py` is shared
by several tracks, so changes there go one track at a time.

| Track | Work | Runs alongside | Waits for |
| --- | --- | --- | --- |
| A — owner review | Prerequisite review GUI (241 cells); Step 1 load-clause review | everything | nothing |
| B — planner core | Step 2 checker (new `bintanong_planning` package, offline tests) | A, C-offline, D-authoring | D1 |
| B2 | Step 3 (earliest term, delayed) and Step 4 (recovery options) | B (different files) | D1 |
| B3 | Step 5 greedy chain drafts and Ask mode | — | B, B2, D2 |
| C — conversation fixes | bare program name reply; shifting referral wording; "how about the hotel track?" | A, B (not the routing files at the same time) | — |
| D — testing | author the conversation test set (offline) | everything | — |
| D-live | gates, 116 sample queries, conversation set, owner GUI round | A only | the code it tests |
| E — ledger update | apply reviewed prerequisite decisions to the ledgers and hosted release | — | A |

Suggested order: start A, B, C and D now (after D1); B2 when B's contracts exist; one D-live run after each merged
step; B3 only after D2; E after A finishes.

## Not in this plan

Automatic enrollment, COR, grades or standing; confirmed offerings, sections, schedules or professors; fees beyond the
printed special-class rate; course substitution or equivalence; ranked "optimal" schedules; certification of regular
standing.

## Decisions needed (owner)

- D1 (decided, owner 4 Nov 2026: "go"): Steps 1–4 and 6 approved as in scope.
- D2 (taken from the owner's "go" on the recommendation, 4 Nov 2026): Step 5 drafts are built and belong in Chapter 3,
  with Aurora (Lugones et al., 2026) as the precedent; the owner may still revise this.
- D3 (decided, owner 4 Nov 2026): complement, not replace. `Context/bintanong_thesis_for_context.pdf` stays the
  thesis-leader-approved copy; the newer external copy is a working draft used as supplementary context, cited by
  hash (`614f9e21…`). Where they differ, the approved copy governs scope.
- D4 (owner: "ikaw bahala"; chosen): a bounded task list on `p12-evaluation-harness`, not a numbered phase. Phase 13 is
  cancelled and no next phase is authorized; this keeps the work in small committed steps without implying phase
  advancement. If the owner later wants it as a phase, AGENTS.md's pre-phase research record comes first.
- D5 (decided as a working assumption, owner 4 Nov 2026: "we can safely do this as a working assumption, just
  communicate it in a friendly student way"): the semester's prescribed total units is the ceiling for any mix of
  courses; a plan above it is shown with a major warning, not blocked. Wording proposed (owner may edit):
  - en: "Heads-up: this semester comes to 24 units, but your curriculum lists 21 for it. The Student Handbook says units
    above the prescribed load may not be credited (p. 35). It's worth checking with your Dean or the Registrar before you
    enroll."
  - taglish: "Heads-up: 24 units ang sem na 'to, pero 21 lang ang nakalista sa curriculum mo. Ayon sa Student Handbook,
    puwedeng hindi ma-credit ang sobrang units (p. 35). Mas okay kung i-check mo muna sa Dean o sa Registrar bago ka
    mag-enroll."
- D6 (decided, owner 4 Nov 2026: "yes go ahead, just print the discrepancy"): the removal period is the succeeding
  term (3.2, Resolution 279, 2018; 3.7). Every answer that uses it also prints the discrepancy: the same section
  also says "within one year" (3.3, 3.7).
- D7 (taken from the owner's "go" on the recommendation): the advance-course restriction is quoted, not checked:
  a student who states a warning or probation is told the rule and to ask the Dean which subjects count.
## Next action

Tracks A, B, C and D started 4 Nov 2026 (owner "go").
