"""Ask mode drafts: the greedy prerequisite chain from one failed course (plan of action, Step 5; owner 4 Nov 2026).

Terms run in calendar order (first semester, second semester, summer, next year ...) from the start term. The failed
course and every course that needs it (the reviewed `list_affected_courses` list) are placed one term at a time in the
earliest term whose start-of-term state meets the reviewed prerequisite rule; the student's other prescribed courses
stay in their prescribed terms. When a summer cannot hold every unblocked course, the course that unlocks the most
later courses goes first (unlock weight, after Aurora, Lugones et al. 2026). Regular terms are not hard-capped: a load
above the prescribed total is a heads-up from `check_plan` (D5), never a block.

Variants: A regular offerings only (a course in its own prescribed semester of a later year); B also special-class
requests (a course outside its prescribed semester); C also summer within the reviewed summer load. Each variant is
run through `check_plan`; one that cannot work, or that comes out the same as an earlier one, is dropped with its
reason. Courses before the start term are assumed passed unless the student stated otherwise; the reply says so.
Nothing here enrolls, approves or stores anything, and nothing names a program or a course.
"""
from __future__ import annotations

import json
from pathlib import Path

from ..bintanong_symbolic.runtime import StudentFacts
from .checker import _request, _units, check_plan
from .contracts import (REQUESTED_MODES, Draft, DraftTerm, DroppedDraft, PlacedCourse, PlanCheckRequest,
                        RecoveryResult, RecoveryRoutes, TermRef)
from .policies import LoadPolicy, load_policy

SLOTS = ('first_semester', 'second_semester', 'summer')
LAST_YEAR = 5
RULES = Path(__file__).resolve().parents[2] / 'knowledge' / 'rules'


def palsu_recovery_sources() -> tuple[LoadPolicy, RecoveryRoutes]:
    """The reviewed PalSU load policy and the verbatim recovery-route clauses (Handbook pp. 35, 37)."""
    routes = RecoveryRoutes.parse(json.loads((RULES / 'palsu-recovery-routes-v1.json').read_text(encoding='utf-8')))
    return load_policy(RULES / 'palsu-load-policy-v1.json'), routes


class _Memo:
    """The same reviewed Prolog check, run once per course and per state of the courses its own rule names.

    Each check is a separate Prolog worker process (about 0.4 s), and the drafts repeat many identical checks. A
    result is reused only for the same predicate, course and the same passed/failed/enrolled states of every course
    in that course's reviewed requirement (read from the result itself); errors are never reused.
    """
    def __init__(self, runtime):
        self._runtime, self._refs, self._results = runtime, {}, {}

    def __getattr__(self, name):
        return getattr(self._runtime, name)

    def _key(self, request, course, facts):
        refs = self._refs.get(course)
        if refs is None:
            return None
        sets = (facts.passed, facts.failed, facts.enrolled, facts.not_enrolled)
        return request.predicate, course, tuple((r, *(r in s for s in sets)) for r in refs)

    def check(self, request, facts):
        course = next(i.value for i in request.inputs if i.name == 'course_id')
        key = self._key(request, course, facts)
        if key in self._results:
            return self._results[key]
        result = self._runtime.check(request, facts)
        if result.decision.outcome in ('eligible', 'ineligible', 'unknown') and result.requirement is not None:
            refs, stack = set(), [result.requirement]
            while stack:
                node = stack.pop()
                refs.update([node.course_id] if node.course_id else [])
                stack.extend(node.items)
            self._refs[course] = tuple(sorted(refs))
            self._results[self._key(request, course, facts)] = result
        return result


class _Drop(Exception):
    def __init__(self, reason, **detail):
        super().__init__(reason)
        self.reason, self.detail = reason, detail


def _next(key):
    year, slot = key
    return (year, slot + 1) if slot < 2 else (year + 1, 0)


def _ref(key):
    return TermRef(year=key[0], semester=SLOTS[key[1]])


def plan_recovery(runtime, curriculum_id, failed_course_id, affected, facts, stated_term, policy, routes,
                  *, regular_asked=False) -> RecoveryResult:
    """affected: the reviewed list_affected_courses ids; facts: the student's stated results (course_id, state);
    stated_term: (year, semester) the student named, or None; policy: a reviewed LoadPolicy or None."""
    runtime = _Memo(runtime)
    listings = [runtime.look_up(_request('list_term_courses', curriculum_id, year_level=str(y), semester='any'))
                for y in range(1, LAST_YEAR + 1)]
    if any(listing.status != 'complete' for listing in listings):
        raise ValueError('curriculum_not_listed')
    printed = {c.course_id: c for listing in listings for c in listing.courses}
    if failed_course_id not in printed:
        raise ValueError('failed_course_not_placed')
    order = {course: i for i, course in enumerate(printed)}
    key_of = {c: (p.year, SLOTS.index(p.term)) for c, p in printed.items()}
    units = {c: _units(p) for c, p in printed.items()}
    failed_key = key_of[failed_course_id]
    stated = {course: state for course, state in facts}
    stated_key = (None if stated_term is None or stated_term[1] not in SLOTS
                  else (int(stated_term[0]), SLOTS.index(stated_term[1])))
    term_stated = stated_key is not None and stated_key >= failed_key
    start = stated_key if term_stated and stated_key > failed_key else _next(failed_key)
    if start[0] > LAST_YEAR:
        raise ValueError('no_term_after_the_failed_course')
    blocked = [failed_course_id] + [c for c in affected if c in printed and c != failed_course_id
                                     and stated.get(c) != 'passed']
    blocked.sort(key=order.get)
    assumed = [c for c in printed if key_of[c] < start and c not in blocked and c not in stated]
    base_facts = [(c, 'passed') for c in assumed] + [(c, s) for c, s in facts if c in printed]
    if failed_course_id not in stated:
        base_facts.append((failed_course_id, 'failed'))  # "if I fail X": the drafts are for that case
    weights = {}

    def weight(course):  # unlock weight: how many later courses need it (reviewed dependency listing)
        if course not in weights:
            weights[course] = len(runtime.list_affected_courses(_request('list_affected_courses', curriculum_id,
                                                                         course_id=course)).course_ids)
        return weights[course]
    calendar = []
    key = start
    while key[0] <= LAST_YEAR:
        calendar.append(key)
        key = _next(key)
    last_prescribed = max(key_of.values())

    def eligible(course, passed, enrolled):
        others = set(printed) - set(enrolled) - {course}
        facts = StudentFacts(passed=tuple(sorted(passed)), failed=tuple(sorted(set(printed) - passed)),
                             enrolled=tuple(sorted({*enrolled, course})), not_enrolled=tuple(sorted(others)))
        return runtime.check(_request('check_prerequisite_eligibility', curriculum_id, course_id=course),
                             facts).decision.outcome == 'eligible'

    def mode(course, key, variant):
        own = key_of[course][1]
        if key[1] == 2:
            return 'summer' if own == 2 or variant == 'C' else None
        if key[1] == own:
            return 'retake' if course == failed_course_id else 'prescribed'
        return 'special_class_request' if own != 2 and variant in ('B', 'C') else None

    def draft(variant):
        if variant == 'C' and policy is None:
            raise _Drop('no_summer_policy')
        passed = set(assumed) | {c for c, s in facts if s == 'passed'}
        placed, terms = {}, []
        for key in calendar:
            if len(placed) == len(blocked):
                break
            kept = [c for c in printed if key_of[c] == key and c not in blocked]
            enrolled, moved = list(kept), []
            room = None
            if key[1] == 2 and variant == 'C':
                room = policy.summer_normal_units - sum(units[c] or 0 for c in kept)
            waiting = [c for c in blocked if c not in placed and mode(c, key, variant)]
            if room is not None and len(waiting) > 1:  # only a capped term needs the tie-break
                waiting.sort(key=lambda c: (-weight(c), order[c]))
            changed = True
            while changed:  # a co-requisite pair can both enter once one of them is in the term
                changed = False
                for course in waiting:
                    if course in placed:
                        continue
                    size = units[course] if key_of[course][1] != 2 else 0  # a prescribed summer course is its own
                    if room is not None and (size is None or size > room):
                        continue
                    if eligible(course, passed, enrolled):
                        placed[course] = key
                        enrolled.append(course)
                        moved.append(PlacedCourse(course_id=course, mode=mode(course, key, variant)))
                        room = None if room is None else room - size
                        changed = True
            if enrolled:
                terms.append((key, moved, kept))
            passed |= set(enrolled)
        missing = [c for c in blocked if c not in placed]
        if missing:
            raise _Drop('not_placed', course_id=missing[0])
        return terms, placed

    def checked(variant, terms):
        plan = [dict(kind='summer' if key[1] == 2 else 'regular',
                     year_level=None if key[1] == 2 else key[0], semester=None if key[1] == 2 else SLOTS[key[1]],
                     courses=[dict(course_id=c, mode='summer' if key[1] == 2 else 'prescribed') for c in kept]
                     + [p.model_dump(mode='json') for p in moved])
                for key, moved, kept in terms]
        try:
            request = PlanCheckRequest.parse(dict(schema_version=PlanCheckRequest.SCHEMA_VERSION,
                curriculum_id=curriculum_id, facts=[dict(course_id=c, state=s) for c, s in base_facts], terms=plan))
        except ValueError:
            raise _Drop('too_long') from None
        result = check_plan(request, runtime, policy)
        for verdict, (key, _, _) in zip(result.terms, terms):
            if verdict.outcome == 'blocked':
                reason = next(r for r in verdict.reasons if r.kind == 'unmet_prerequisite')
                raise _Drop('blocked', course_id=reason.course_id, missing=reason.missing, term=_ref(key))
        return [DraftTerm(term=_ref(key), moved=tuple(moved), kept=tuple(kept), verdict=verdict)
                for verdict, (key, moved, kept) in zip(result.terms, terms)]

    drafts, dropped, shapes = [], [], {}
    for variant in ('A', 'B', 'C'):
        try:
            terms, placed = draft(variant)
            shape = tuple((key, tuple(moved)) for key, moved, _ in terms if moved)
            same = next((v for v, s in shapes.items() if s == shape), None)
            if same is not None:
                raise _Drop('same_as', same_as=same)
            shapes[variant] = shape
            drafts.append((sum(p.mode in REQUESTED_MODES for _, moved, _ in terms for p in moved),
                           max(placed.values()), Draft(variant=variant, terms=tuple(checked(variant, terms)),
                           requests=sum(p.mode in REQUESTED_MODES for _, moved, _ in terms for p in moved),
                           beyond_curriculum=max(placed.values()) > last_prescribed)))
        except _Drop as drop:
            dropped.append(DroppedDraft(variant=variant, reason=drop.reason, **drop.detail))
    # Stated order (plan of action, Step 5): fewest unconfirmed requests, then the earliest last delayed course.
    drafts.sort(key=lambda item: item[:2])
    next_offering = next((k for k in calendar if k[1] == failed_key[1]), None)
    return RecoveryResult(schema_version=RecoveryResult.SCHEMA_VERSION, synthetic=runtime.synthetic,
        curriculum_id=curriculum_id, failed_course_id=failed_course_id, failed_term=_ref(failed_key),
        start_term=_ref(start), term_stated=term_stated,
        next_offering=None if next_offering is None else _ref(next_offering), regular_asked=regular_asked,
        clauses=routes.clauses, drafts=tuple(d for *_, d in drafts), dropped=tuple(dropped),
        policy_id=None if policy is None else policy.policy_id)
