"""Check a student's proposed sequence of terms (academic recovery plan of action, Step 2).

Each term is checked in order against the start-of-term state with the existing reviewed prerequisite rules
(`CurriculumRuntime.check`; all_of/any_of/co-requisite and blank-cell semantics stay the runtime's). Within a planned
term, a co-requisite counts as taken only when it is in the same term. After a term, its courses become assumed
passes for later terms of this request only: a course whose check was met counts as passed, one whose check could not
be decided becomes unknown, and a blocked course counts as not completed (no credit without its prerequisite). The
request and the session facts
are never changed. Units are the printed `units.total`; the load is compared with the reviewed load policy, and every
course that needs an offering or approval is listed as requested, not confirmed.
"""
from __future__ import annotations

import hashlib
import json

from ..bintanong_contracts.runtime import PredicateRequest
from ..bintanong_orchestration.adapters import student_facts
from ..bintanong_symbolic.runtime import StudentFacts
from .contracts import (REQUESTED_MODES, AssumedPass, LoadCheck, PlanCheckRequest, PlanCheckResult, PlanReason,
                        PlanWarning, TermVerdict, UnconfirmedCondition, plan_request_digest)
from .policies import NOT_REVIEWED, LoadPolicy

MAX_SPANS = 24
_MISSING = {'ineligible': ('not_completed:', 'not_enrolled:'),
            'unknown': ('completion_unknown:', 'enrollment_unknown:', 'identity_unreviewed:')}


def _request(predicate, curriculum, **inputs):
    return PredicateRequest.parse({'predicate': predicate, 'inputs': [
        {'name': 'curriculum_id', 'value': curriculum, 'fact_ref': None},
        *({'name': name, 'value': value, 'fact_ref': None} for name, value in inputs.items())]})


def _units(printed_course):
    value = dict(printed_course.units).get('units.total')
    return None if value is None else float(value)


def _ids(conditions, prefixes):
    return tuple(dict.fromkeys(c.split(':', 1)[1] for c in conditions if c.startswith(prefixes)))


def check_plan(request: PlanCheckRequest, runtime, policy: LoadPolicy | None) -> PlanCheckResult:
    """runtime: a CurriculumRuntime for the request's curriculum; policy: a reviewed LoadPolicy, or None."""
    request = PlanCheckRequest.parse(request.model_dump(mode='json'))
    policy = None if policy is None else LoadPolicy.parse(policy.model_dump(mode='json'))
    curriculum = request.curriculum_id
    every = [runtime.look_up(_request('list_term_courses', curriculum, year_level=str(y), semester='any'))
             for y in range(1, 6)]
    if any(listing.status == 'not_found' for listing in every):
        raise ValueError('curriculum_mismatch')
    # Every placed course of the curriculum, so a co-requisite outside a planned term reads as "not taken then".
    all_ids = ({c.course_id for listing in every for c in listing.courses}
               if all(listing.status == 'complete' for listing in every) else set())
    stated = student_facts(request.facts)  # the same projection the session uses; enrollment is per planned term
    passed, failed = list(stated.passed), list(stated.failed)
    assumed, spans, rule_ids, scope, verdicts = [], {}, {}, None, []

    def cite(result):
        nonlocal scope
        scope = scope or result.scope
        for span in result.rule_spans:
            spans.setdefault(json.dumps(span.model_dump(mode='json'), sort_keys=True), span)
        rule_ids.update(dict.fromkeys(result.rule_ids))

    for index, term in enumerate(request.terms):
        in_term = [c.course_id for c in term.courses]
        facts = StudentFacts(passed=tuple(passed), failed=tuple(failed), enrolled=tuple(in_term),
                             not_enrolled=tuple(sorted(all_ids - set(in_term))))
        reasons, units, outcomes = [], [], {}
        requests = {c.course_id:c.mode for c in term.courses if c.mode in REQUESTED_MODES}
        for course in term.courses:
            found = runtime.look_up(_request('course_facts', curriculum, course_id=course.course_id))
            if found.status != 'complete':
                kind = 'not_in_curriculum' if found.status == 'not_found' else 'units_missing'
                reasons.append(PlanReason(kind=kind, course_id=course.course_id, detail=f'course facts {found.status}'))
                outcomes[course.course_id], units = 'unknown', units + [None]
                continue
            scope = scope or found.scope
            if (term.kind == 'regular' and course.mode in ('prescribed', 'retake')
                    and found.courses[0].term != term.semester):
                requests[course.course_id] = 'off_semester_request'
            units.append(_units(found.courses[0]))
            if units[-1] is None:
                reasons.append(PlanReason(kind='units_missing', course_id=course.course_id,
                                          detail='units not printed in the reviewed curriculum'))
            checked = runtime.check(_request('check_prerequisite_eligibility', curriculum,
                                             course_id=course.course_id), facts)
            cite(checked)
            decision = checked.decision
            outcomes[course.course_id] = decision.outcome
            if decision.outcome == 'ineligible':
                reasons.append(PlanReason(kind='unmet_prerequisite', course_id=course.course_id,
                                          missing=_ids(decision.violated_conditions, _MISSING['ineligible'])))
            elif decision.outcome == 'unknown':
                requirement = checked.requirement
                printed = requirement.reason if requirement is not None and requirement.kind == 'unresolved' else None
                reasons.append(PlanReason(kind='prerequisite_unknown', course_id=course.course_id,
                                          missing=_ids(decision.missing_facts + decision.unknown_conditions,
                                                       _MISSING['unknown']), detail=printed))
            elif decision.outcome != 'eligible':
                reasons.append(PlanReason(kind='rule_error', course_id=course.course_id,
                                          detail=decision.error_code or decision.outcome))
        load, warnings = _load(term, runtime, curriculum, units, policy)
        verdicts.append(TermVerdict(
            index=index, reasons=tuple(reasons), warnings=tuple(warnings), load=load, assumed=tuple(assumed),
            unconfirmed=tuple(UnconfirmedCondition(course_id=c.course_id, kind=requests[c.course_id],
                                                   text='requested, not confirmed')
                              for c in term.courses if c.course_id in requests),
            outcome=_outcome(reasons, load, warnings)))
        for course_id, outcome in outcomes.items():  # request-local: only later terms see these
            failed = [c for c in failed if c != course_id]
            passed = [c for c in passed if c != course_id]
            assumed = [a for a in assumed if a.course_id != course_id]
            if outcome == 'ineligible':  # planned but blocked: no credit in this plan
                failed.append(course_id)
            elif outcome == 'eligible':
                passed.append(course_id)
                assumed.append(AssumedPass(course_id=course_id, from_term=index))
    policy_id = None if policy is None else policy.policy_id
    policy_sha256 = None if policy is None else hashlib.sha256(json.dumps(
        policy.model_dump(mode='json'), sort_keys=True, separators=(',', ':'), ensure_ascii=False,
        allow_nan=False).encode('utf-8')).hexdigest()
    return PlanCheckResult(schema_version=PlanCheckResult.SCHEMA_VERSION, synthetic=runtime.synthetic,
                           checked_request=request, policy_sha256=policy_sha256,
                           request_sha256=plan_request_digest(request, policy_id, policy_sha256),
                           curriculum_id=curriculum, terms=tuple(verdicts),
                           policy_id=policy_id, scope=scope,
                           rule_ids=tuple(rule_ids), rule_spans=tuple(spans.values())[:MAX_SPANS])


def _outcome(reasons, load, warnings):
    if any(r.kind == 'unmet_prerequisite' for r in reasons):
        return 'blocked'
    if reasons or load.status == 'unknown':
        return 'unknown'
    return 'works_with_warning' if warnings else 'works'


def _load(term, runtime, curriculum, units, policy):
    total = None if None in units else sum(units)
    if policy is None:
        return LoadCheck(status='unknown', units=total, ceiling=None, reason=NOT_REVIEWED), []
    if total is None:
        return LoadCheck(status='unknown', units=None, ceiling=None, reason='units not printed for every course'), []
    if term.kind == 'summer':
        ceiling, kind, clause = policy.summer_normal_units, 'summer_above_normal', policy.clause('summer')
    else:
        listing = runtime.look_up(_request('list_term_courses', curriculum, year_level=str(term.year_level),
                                           semester=term.semester))
        prescribed = [_units(c) for c in listing.courses]
        if listing.status != 'complete' or not prescribed or None in prescribed:
            return LoadCheck(status='unknown', units=total, ceiling=None,
                             reason='prescribed semester total not available in the reviewed curriculum'), []
        ceiling, kind, clause = sum(prescribed), 'load_above_prescribed', policy.clause('regular')
    if total <= ceiling:
        return LoadCheck(status='within', units=total, ceiling=ceiling), []
    return LoadCheck(status='above', units=total, ceiling=ceiling), [
        PlanWarning(kind=kind, severity='major', units=total, ceiling=ceiling, clause=clause)]
