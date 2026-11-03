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

- Show the owner the exact printed clauses (summer nine units and the graduating-student exception; overload limit
  and the scholastic-delinquency bar; any regular-semester load rule) with page and wording, in short batches.
- Record each accepted reading as a versioned policy record (source span, audience, parameters, unresolved markers);
  generate the runtime rule from it. A clause not accepted stays unused, and a load question then says the limit is
  not available and refers the student to the Registrar.
- Exit: a policy fixture whose every executed number traces to a reviewed span; unreviewed readings are held.

### Step 2 — Check my plan

- Input: the student's curriculum, stated results, and a proposed sequence of terms with courses (e.g. "special class
  CC 4/L now; CS 4/L and CS 6 in summer; CC 5/L in 1st sem"). Router operation `check_plan`, curriculum-scoped.
- For each term in order: prerequisite check on the start-of-term state; assumed passes from earlier terms added only
  as request-only assumptions (never stored as grades); unit total against the reviewed load rule for that term type.
- Output per term: works / blocked (which course, which prerequisite or limit) / unknown (missing rule, unit or
  policy); plus the conditions it depends on (special class requested, not approved; summer offering not confirmed).
- Tests first: the BSCS four-term scenario from the owner plan (§6, 24-vs-21 load flagged, not approved), a denied
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

## Next action

Owner answers D1–D4; on D1 "go", start Step 1 by showing the load clauses for review.
