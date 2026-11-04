"""Pure chat-entry helpers; the router supplies reviewed scope and the current term."""
from dataclasses import dataclass
from typing import Literal
from ..bintanong_contracts.source import SourceSpan
from ..bintanong_contracts.symbolic import DecisionScope
import re
from ..bintanong_routing.contracts import prepare_query
from ..bintanong_routing.terms import parse_term
from ..bintanong_symbolic.runtime import StudentFacts
from .checker import _request
from .contracts import PlanCheckRequest, TermRef
from .recovery import SLOTS, _Memo, _next


def parse_plan_terms(text, catalog, curriculum, *, start_term=None, facts=()):
    """Parse explicit colon-separated term lines; missing years need caller-supplied term context."""
    prepare_query(text)
    aliases = {}
    for entry in catalog:
        if entry.kind == 'course' and entry.curriculum_id == curriculum:
            for alias in entry.aliases:
                aliases.setdefault(prepare_query(alias).casefold(), set()).add(entry.entity_id)
    terms, previous_key = [], None
    year_context = start_term
    for line in re.split(r'[;\n]+', text):
        if not line.strip():
            continue
        header, sep, content = line.partition(':')
        if not sep:
            raise ValueError('plan_line_requires_colon')
        term = parse_term(header, year_context)
        if term is None or term[1] == 'any':
            raise ValueError('term_required')
        year, semester = term
        key = year, SLOTS.index(semester)
        if previous_key is not None and key <= previous_key:
            raise ValueError('terms_not_in_order')
        previous_key, year_context = key, term
        courses = []
        for item in content.split(','):
            mode = 'summer' if semester == 'summer' else 'prescribed'
            match = re.search(r'\s+(special class|off[- ]semester|retake)\s*$', item, re.I)
            if match:
                if semester == 'summer':
                    raise ValueError('summer_mode_conflict')
                mode = {'special class':'special_class_request', 'off-semester':'off_semester_request',
                        'off semester':'off_semester_request', 'retake':'retake'}[match[1].lower()]
                item = item[:match.start()]
            ids = aliases.get(prepare_query(item).casefold(), set())
            if len(ids) != 1:
                raise ValueError('course_ambiguous' if ids else 'course_unresolved')
            courses.append(dict(course_id=next(iter(ids)), mode=mode))
        terms.append(dict(kind='summer' if semester == 'summer' else 'regular',
            year_level=None if semester == 'summer' else year,
            semester=None if semester == 'summer' else semester, courses=courses))
    return PlanCheckRequest.parse(dict(schema_version=PlanCheckRequest.SCHEMA_VERSION, curriculum_id=curriculum,
        facts=[dict(course_id=c, state=s) for c,s in facts], terms=terms))


@dataclass(frozen=True)
class EarliestTermResult:
    curriculum_id: str
    course_id: str
    start_term: TermRef
    term: TermRef | None
    status: Literal['found', 'unknown']
    assumed_passes: tuple[str, ...]
    reason: str | None = None
    scope: DecisionScope | None = None
    rule_ids: tuple[str, ...] = ()
    rule_spans: tuple[SourceSpan, ...] = ()


def earliest_term(runtime, curriculum_id, course_id, facts, start_term):
    """Earliest regular prescribed offering under explicit request-local assumed passes; never availability."""
    start = TermRef(year=start_term[0], semester=start_term[1])
    runtime = _Memo(runtime)
    listings = [runtime.look_up(_request('list_term_courses', curriculum_id, year_level=str(y), semester='any'))
                for y in range(1, 6)]
    printed = {c.course_id:c for listing in listings for c in listing.courses}
    rule_ids, rule_spans, scope = {}, {}, None
    def cite(checked):
        nonlocal scope
        if scope is not None and checked.scope != scope:
            raise ValueError('earliest_rule_release_mismatch')
        scope = checked.scope
        rule_ids.update(dict.fromkeys(checked.rule_ids))
        for span in checked.rule_spans:
            rule_spans.setdefault(span.model_dump_json(), span)

    def result(term=None, assumed=(), reason=None):
        return EarliestTermResult(curriculum_id, course_id, start, term, 'found' if term else 'unknown',
                                  tuple(assumed), reason, scope, tuple(rule_ids), tuple(rule_spans.values()))
    if any(x.status != 'complete' for x in listings) or course_id not in printed:
        return result(reason='curriculum_or_course_not_reviewed')
    keys = {c:(p.year, SLOTS.index(p.term)) for c,p in printed.items()}
    key = start.year, SLOTS.index(start.semester)
    stated = {}
    for c,s in facts:
        if c in stated and stated[c] != s:
            raise ValueError('conflicting_course_results')
        if c not in printed:
            raise ValueError('fact_not_in_curriculum')
        stated[c] = s
    passed = {c for c,s in stated.items() if s == 'passed'}
    assumed = [c for c in printed if keys[c] < key and c not in stated and c != course_id]
    passed.update(assumed)
    while key[0] <= 5:
        offered = [c for c in printed if keys[c][1] == key[1] and keys[c] <= key and c not in passed]
        if course_id in passed:
            return result(reason='course_already_passed')
        complete = offered
        checks = {}
        while complete:
            enrolled = complete
            complete = []
            for c in enrolled:
                checked = runtime.check(_request('check_prerequisite_eligibility', curriculum_id, course_id=c),
                    StudentFacts(passed=tuple(sorted(passed)), failed=tuple(sorted(set(printed)-passed)),
                        enrolled=tuple(enrolled), not_enrolled=tuple(sorted(set(printed)-set(enrolled)))))
                checks[c] = checked
                if checked.decision.outcome == 'eligible':
                    complete.append(c)
            if complete == enrolled:
                break
        for c in complete:
            cite(checks[c])
        if course_id in complete:
            return result(TermRef(year=key[0], semester=SLOTS[key[1]]), assumed)
        passed.update(complete)
        assumed.extend(c for c in complete if c not in assumed)
        key = _next(key)
    return result(assumed=assumed, reason='prerequisite_chain_unresolved_within_five_years')
