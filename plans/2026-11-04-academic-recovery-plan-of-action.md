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

- Up to three drafts over the next two or three terms, produced by trying the documented routes and keeping only
  plans that pass the Step 2 checker. Ordered by a stated, simple rule (fewest unconfirmed approvals, then earliest
  return to the prescribed sequence), never called "best" or "optimal".
- Every draft headed: "Draft, not approved. Show this to your program adviser." with each required approval listed.
- A student's "approved na ng adviser" is recorded as student-reported, not as an institutional fact.
- Disclosure: an extension beyond the thesis objectives unless the owner adds it to Chapter 3; kept out of the formal
  baseline comparison unless so added.

### Step 6 — evaluation

- Re-run `evaluation/memory_eligibility` offline/scenarios/curricula/recorded and the 116 sample queries; report
  numerators per curriculum. Add plan-check cases per program (owner plan §7, ARP-01…10, as check cases).
- Measure warm backend time for plan checks separately from Gemma and browser time.

## Not in this plan

Automatic enrollment, COR, grades or standing; confirmed offerings, sections, schedules or professors; fees beyond the
printed special-class rate; course substitution or equivalence; ranked "optimal" schedules; certification of regular
standing.

## Decisions needed (owner)

- D1: approve Steps 1–4 and 6 as in scope (thesis-bounded).
- D2: Step 5 drafts — yes / later / no; if yes, inside Chapter 3 or as a disclosed extension.
- D3: replace `Context/bintanong_thesis_for_context.pdf` with the newer external copy.
- D4: numbered phase or a bounded task list on `p12-evaluation-harness`.
- D5: reading of the maximum-load clause: the semester's prescribed total units is the ceiling for any mix of courses
  (a mix above it gets the major warning), or only the prescribed courses themselves.
- D6 (decided, owner 4 Nov 2026: "yes go ahead, just print the discrepancy"): the removal period is the succeeding
  term (3.2, Resolution 279, 2018; 3.7). Every answer that uses it also prints the discrepancy: the same section
  also says "within one year" (3.3, 3.7).
- D7: what counts as an `advance course` (a course prescribed for a later term than the student's year level?), or
  cite the restriction without checking it.

## Next action

Owner answers D1–D7; on D1 "go", start Step 1 by showing the Check clauses for review.
