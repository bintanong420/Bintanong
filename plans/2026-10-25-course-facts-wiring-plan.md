# Course facts wiring Implementation Plan (Phase 11 step 2h item 4)

> **For agentic workers:** execute task-by-task with TDD (RED observed, GREEN, mutation check). Steps use `- [ ]`.

**Goal:** "What subjects are in first year BSIT?", "How many units is CC 5?" and a printed title instead of a code
are answered from the reviewed course facts, as host-written text, on the Symbolic route.

**Architecture:** The LLM router gets two operations: `course_facts` (target: a course mention) and
`list_term_courses` (target: a new `term` mention quoting e.g. "first year, second sem"). The host parses the term
quote deterministically, binds the inputs, and the symbolic adapter answers from `bintanong_symbolic/course_facts.py`
(no Prolog, no similarity). A `CourseFactsResult` travels through orchestration like `DependencyResult`; the
renderer writes en/fil/Taglish lines with the prospectus page. The model never writes these facts.

**Tech stack:** Python 3.13, pydantic contracts, existing routing/orchestration/generation packages. No dependency.

**Spec:** `plans/2026-10-24-course-facts-plan.md` (approved 25 Oct) + owner readings CF1-CF6 (`owner-decisions-ledger.md`).

## Global Constraints

- Values exactly as printed (CF1 "2/1"); no unit arithmetic; missing units stated as not printed, never 0.
- A curriculum without reviewed placement for every course: no listing (E1 "not in reviewed sources" referral).
- Reply language rule (AGENTS.md 21 Oct): English->English; Filipino->everyday Filipino; Taglish->Taglish; never
  deep Tagalog ("isusumite", "nakasaad"). New host wording is shown to the owner before the live run.
- Title aliases only when the printed title is unique within the curriculum (case-insensitive, spacing-normalized).
- Prompt examples are fictional; evaluation cases are not reused as prompt examples.
- Commits: Conventional Commits, no attribution trailers; explicit staging.

## Review Focus

1. "first sem" with no year -> clarify which year (never assume first year). Test in Task 1.
2. "second year" with no semester -> list every term of that year, grouped by printed term. Test in Task 4.
3. Year with no printed courses (e.g. 5th year of a 4-year program) -> "the prospectus lists no courses for that
   term", only when coverage is complete. Test in Task 4.
4. A title shared by two courses (e.g. "Accounting for Non-Accountants" in two curricula is fine; twice in one
   curriculum is not aliased) -> keep the "give the printed code" reply. Test in Task 5.
5. BSMid split units (LEC/RLE/LAB) and BSN Unit/s render without inventing a total. Test in Task 4.

---

### Task 1: Term mention parsing

**Files:** Create `backend/bintanong_routing/terms.py`; Test `tests/test_routing_terms.py`.

**Produces:** `parse_term(text: str) -> tuple[int, str] | None` returning `(year 1-5, 'first_semester' |
'second_semester' | 'summer' | 'any')`; `None` when no year is stated.

- [ ] Tests: "first year" -> (1,'any'); "1st yr 2nd sem" -> (1,'second_semester'); "second year, first semester" ->
  (2,'first_semester'); "unang taon" -> (1,'any'); "ikalawang taon, unang sem" -> (2,'first_semester');
  "3rd year summer" -> (3,'summer'); "4th year midyear" -> (4,'summer'); "first sem" -> None; "CC 5" -> None.
  The year word is the one attached to year/yr/taon, the semester word the one attached to sem/semester.
- [ ] RED, implement with one regex per role, GREEN, mutation check, commit `feat(routing): parse year and semester mentions`.

### Task 2: Interpretation and wire contracts accept term mentions and the two operations

**Files:** Modify `backend/bintanong_routing/contracts.py` (mention kind `term`, kept out of `CatalogEntry.Kind`;
`list_term_courses` targets a term mention, every other operation a course mention), `backend/bintanong_routing/wire.py`
(`term_index` beside `course_index`), `backend/bintanong_routing/validation.py` (`OPERATIONS` += both; term mentions
are "ignored" for catalog resolution but must parse with `parse_term`, else `unresolved_entity` clarify; bind
inputs). Tests: `tests/test_routing_validation*.py`, `tests/test_routing_wire*.py` (extend existing files).

**Produces:** `PredicateRequest` for `list_term_courses` with inputs `curriculum_id`, `year_level` ("1".."5"),
`semester` (as Task 1); for `course_facts` inputs `curriculum_id`, `course_id`.

- [ ] Tests: term-target operation validates; course operation aimed at a term mention -> `invalid_course_mention_reference`;
  unparseable term quote -> clarify; units question (`course_facts`) no longer becomes `unsupported_requirement`;
  existing 3 operations unchanged. RED, implement, GREEN, routing selection green, commit `feat(routing): ...`.

### Task 3: Adapter and result contract

**Files:** Modify `backend/bintanong_symbolic/course_facts.py` (add `CourseFactsResult` contract: `predicate`,
`inputs`, `synthetic`, `status` in complete|not_reviewed|not_found, `courses: tuple[PrintedCourse, ...]` with
course_id, code, title|None, units as ((field, printed value as text), ...), year_level, semester (printed),
`page`, `version_id`); `backend/bintanong_orchestration/adapters.py` (SymbolicAdapter answers both operations
from its runtime's reviewed ledger); `backend/bintanong_runtime/research.py` (OPERATIONS/CAPABILITIES += both,
per-operation capability signatures). Tests: `tests/test_symbolic_course_facts.py`, `tests/test_orchestration_adapters.py`.

- [ ] Tests: adapter returns the listing for bound inputs; scope mismatch rejected as for prerequisite checks;
  research/synthetic label kept. RED, implement, GREEN, commit.

### Task 4: Orchestration, integration evidence and host-rendered reply

**Files:** Modify `backend/bintanong_orchestration/{orchestrator,contracts,integration}.py` (accept
`CourseFactsResult` like `DependencyResult`), `backend/bintanong_generation/{evidence,contracts,render,validation}.py`
(pack field `course_facts`; render lines per language). Tests: generation render/orchestration tests.

**Rendered text (en; fil/taglish analogues, owner-checked):** heading "First year, first semester courses
(<program> <curriculum years> prospectus, p. N):", then one line per course "CC 1/L Introduction to Computing
- 2/1 units"; BSMid "LEC 2, RLE 1"; no units "units not printed"; `any` groups by printed term; empty complete
term "The prospectus lists no courses for that term."; `course_facts`: "CC 5/L (Data Structures and Algorithms):
2/1 units, first year, second semester (prospectus p. N)."; `not_reviewed` -> existing E1 referral.

- [ ] Tests for each line shape in en/fil/taglish, Review Focus 2/3/5, no digits computed (sum never appears).
  RED, implement, GREEN, selection (routing/orchestration/generation/api/evaluation) green, commit.

### Task 5: Title aliases in the catalog

**Files:** Modify `backend/bintanong_runtime/research.py::research_catalog`; Test `tests/test_runtime_multi_curriculum.py`
or the research catalog test file.

- [ ] Tests: unique printed title resolves to its course; a title printed twice in one curriculum is not an alias;
  a title equal to another course's code form is not added. RED, implement, GREEN, commit.

### Task 6: Router prompt

**Files:** Modify `backend/bintanong_routing/prompt.py` (operation list, `term` mention rule, one fictional
example; units/title/subject-list questions are Symbolic). Tests: prompt tests that pin operation names.

- [ ] Update prompt tests first (RED), edit, GREEN, commit. Then owner check of the new host wording (Task 4).

### Task 7: Live verification (after the hosted upload, item 5)

- [ ] Live R5/R6/R10 + "What subjects are in first year BSIT?" in en/fil/Taglish; roster run 18 vs 17 (status/decision
  changes must be explained); multi-turn run; full suite. Record results in a dated report and the checkpoint.

## Open (not in this plan)

- CF6 clipped-title gap is recorded in the authoring report only; the reply does not yet say a title is cut off.
- Course-unit totals per term are not shown (CF5).
