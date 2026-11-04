"""Host replies for explicit plans; offerings, approvals and planned passes remain assumptions."""
from .recovery_reply import _status_words, _words, _number, term_label
from ..bintanong_planning.contracts import TermRef, plan_request_digest


def plan_check_lines(request, result, language, shown, *, routes=None):
    if plan_request_digest(request, result.policy_id, result.policy_sha256) != result.request_sha256:
        raise ValueError('plan_result_mismatch')
    words, english = _words(language), language in ('en', 'unknown')
    lines = []
    for term, verdict in zip(request.terms, result.terms):
        status = ('⛔ Blocked' if verdict.outcome == 'blocked' else '❓ Unknown' if verdict.outcome == 'unknown'
                  else '⚠️ Works with a heads-up' if verdict.warnings or verdict.open_removals
                  else '✅ ' + (words['confirm'] if verdict.unconfirmed else words['works']))
        label = ('Summer' if term.kind == 'summer' else
                 term_label(TermRef(year=term.year_level, semester=term.semester), language))
        lines.append(f"{label}: {', '.join(shown(c.course_id) for c in term.courses)} — {status}")
        for reason in verdict.reasons:
            if reason.kind == 'unmet_prerequisite':
                needs = ', '.join(map(shown, reason.missing))
                lines.append(f"{shown(reason.course_id)} has unmet course requirements: {needs}." if english else
                             f"May hindi met na course requirements ang {shown(reason.course_id)}: {needs}.")
            else:
                lines.append(words['prereq_unknown'].format(course=shown(reason.course_id)))
        clauses = {} if routes is None else {c.kind:c for c in routes.clauses}
        for condition in verdict.unconfirmed:
            source = clauses.get({'special_class_request':'special_class', 'off_semester_request':'off_semester',
                                  'summer':'summer'}[condition.kind])
            if source is not None:
                lines.append(words['request'].format(course=shown(condition.course_id),
                    kind=words['modes'][condition.kind], conditions=''.join(f'"{c}"; ' for c in source.conditions),
                    page=source.page))
                lines.append(f'Student Handbook p. {source.page}: "{source.text}"')
            else:
                lines.append(f"{shown(condition.course_id)}: {words['modes'][condition.kind]} " +
                    ('requested, not yet approved. Its reviewed offering conditions are unavailable; ask your adviser.'
                     if english else 'na ni-request, hindi pa approved. Wala dito ang reviewed offering conditions; itanong sa adviser.'))
        for warning in verdict.warnings:
            lines.append(words['d5' if warning.kind == 'load_above_prescribed' else 'summer_load'].format(
                units=_number(warning.units), ceiling=_number(warning.ceiling), page=warning.clause.page))
        status_words = _status_words(language)
        for course_id in verdict.open_removals:  # Track A 4: re-enrolling an open 4.0/INC
            course = shown(course_id)
            lines.append(status_words['reenroll'].format(grade=request.status.grade(course_id), course=course))
            forfeit = clauses.get('removal_forfeit')
            lines.append('  ' + (status_words['forfeit'].format(course=course, page=forfeit.page, text=forfeit.text)
                                 if forfeit is not None else status_words['reenroll_ask'].format(course=course)))
        if verdict.load.status == 'unknown':
            lines.append(words['load_unknown'].format(reason=verdict.load.reason))
    lines.append('This is a check, not an approval. Later terms assume you pass the courses that work in earlier terms. Show your plan to your program adviser.' if english else
        'Check ito, hindi approval. Assumed na naipasa mo ang courses na gumagana sa earlier terms. Ipakita ang plan sa program adviser mo.')
    return lines


def earliest_term_lines(result, language, shown):
    english = language in ('en', 'unknown')
    if result.status != 'found':
        return ["I can't establish an earliest term from the reviewed rules and stated results. Please ask your program adviser."
                if english else 'Hindi ko matukoy ang pinakamaagang term mula sa reviewed rules at sinabi mong results. Paki-confirm sa program adviser.']
    course, when = shown(result.course_id), term_label(result.term, language)
    assumed = ', '.join(map(shown, result.assumed_passes))
    start = term_label(result.start_term, language)
    return ([f'The earliest you could take {course} is {when}, using its prescribed semester.',
             f'That assumes your other courses before {start} were passed unless you told me otherwise, and you pass these planned courses first: {assumed or "none"}.',
             'This does not confirm a class offering or approval. Ask your program adviser about special-class or summer requests.'] if english else
            [f'Pinakamaagang puwedeng kunin ang {course}: {when}, ayon sa prescribed semester nito.',
             f'Assuming naipasa mo ang ibang courses bago ang {start}, maliban kung iba ang sinabi mo, at maipapasa muna ang mga planned course na ito: {assumed or "wala"}.',
             'Hindi pa confirmed ang class offering o approval. Itanong sa program adviser ang special-class o summer requests.'])
