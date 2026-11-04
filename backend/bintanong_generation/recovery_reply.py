"""Host wording for Ask mode (owner, 4 Nov 2026): after the affected-courses lines, the recovery routes (unranked,
quoted from the reviewed Handbook clauses, each needing confirmation), then the greedy drafts already run through the
plan checker. Every draft is headed for adviser review; each term reads with the 2b wording and the D5 heads-up.
Nothing here claims an offering, an approval, a grade or academic standing."""
from __future__ import annotations

_ORDINAL = {1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth'}

_WORDS = {
    'en': dict(
        regular='By "regular load" I take it you mean getting back on your curriculum\'s prescribed sequence of '
                'courses. That is not the Student Handbook\'s "regular student" classification.',
        routes='Ways to take {course} again (not ranked; each needs confirmation):',
        retake='Retake it at its next regular offering{when}. Student Handbook p. {page}: "{text}" The class '
               'schedule for that term is not confirmed here.',
        special='Request a special class. Student Handbook p. {page}: "{text}" It is a request, not an approval; the '
                'source names the University Cashier only for the payment, not who approves the request.',
        off_semester='Ask whether it can open as an off-semester regular class. Student Handbook p. {page}: "{text}" '
                     'Not confirmed: it opens only under those conditions, and the source names no office for it.',
        summer='Take it in summer, within the summer load. Student Handbook p. {page}: "{text}" A summer offering '
               'is not confirmed here.',
        assumed='Assuming {course} was taken in its prescribed term ({failed}) and not passed, and your other courses '
                'before {start} were passed, these drafts start from {start}.',
        stated='Based on the term you mentioned, these drafts start from {start}; your courses before then are '
               'counted as passed unless you told me otherwise.',
        header='Draft, not approved. Show this to your program adviser. Draft {variant}: {title}',
        titles=dict(A='retake at the next regular offering only.', B='with special-class requests.',
                    C='with special-class requests and summer, within the summer load.'),
        term='- {term}{units}: {moved}{kept}. {status}',
        units=' ({units} units)', kept=', plus {n} other prescribed course{s}',
        modes=dict(retake='retake', prescribed='regular offering', special_class_request='special class',
                   summer='summer class', off_semester_request='off-semester class'),
        works='Works.', confirm='Works, needs confirmation.', unknown="I can't fully check this term.",
        request='  {course}: {kind} requested, not yet approved ({conditions}Student Handbook p. {page}). If it does '
                'not open, {course} and the courses that need it move to a later term.',
        d5='  Heads-up: this semester comes to {units} units, but your curriculum lists {ceiling} for it. The Student '
           'Handbook says units above the prescribed load may not be credited (p. {page}). It\'s worth checking with '
           'your Dean or the Registrar before you enroll.',
        summer_load='  Heads-up: this summer comes to {units} units, above the normal summer load of {ceiling} '
                    '(Student Handbook p. {page}). Check with your Dean before you enroll.',
        load_unknown="  I can't check this term's unit load: {reason}.",
        prereq_unknown="  I can't fully check the prerequisites of {course}; please confirm with your program adviser.",
        unchecked='  {course} could not be checked.',
        back='After {term}, the rest follows your prescribed sequence.',
        beyond="This draft goes past your curriculum's last term.",
        dropped=dict(same_as='Draft {variant} is not shown: it comes out the same as Draft {same}.',
                     blocked='Draft {variant} is not shown: {course} would still be blocked in {term} (needs '
                             '{missing}).',
                     not_placed="Draft {variant} is not shown: I couldn't place {course} within the terms I can plan.",
                     no_summer_policy='Draft {variant} is not shown: the summer load rule is not available.',
                     too_long='Draft {variant} is not shown: it needs more terms than I can check.'),
        none="I couldn't make a draft that works.",
        order='Drafts are listed by fewest requests that need approval, then the earliest finish; this is not a '
              'ranking of the best plan.',
        closing='None of this confirms a class offering, an approval, a grade or your academic standing.',
        summer_term='summer after {year} year', join=', '),
    'taglish': dict(
        regular='Sa "regular load," ang ibig sabihin ko ay makabalik ka sa prescribed sequence ng courses sa '
                'curriculum mo. Hindi ito ang "regular student" classification ng Student Handbook.',
        routes='Mga paraan para kunin ulit ang {course} (walang ranking; lahat kailangan pang i-confirm):',
        retake='I-retake ito sa next regular offering{when}. Student Handbook p. {page}: "{text}" Hindi pa '
               'confirmed dito ang class schedule sa term na iyon.',
        special='Mag-request ng special class. Student Handbook p. {page}: "{text}" Request ito, hindi approval; '
                'University Cashier lang ang binanggit ng source para sa bayad, hindi kung sino ang mag-a-approve.',
        off_semester='Itanong kung puwede itong buksan bilang off-semester regular class. Student Handbook p. {page}: '
                     '"{text}" Hindi pa confirmed: bubuksan lang ito kung pasok sa conditions na iyan, at walang '
                     'office na binanggit ang source para dito.',
        summer='Kunin ito sa summer, pasok sa summer load. Student Handbook p. {page}: "{text}" Hindi pa confirmed '
               'dito kung may summer offering.',
        assumed='Assuming na kinuha mo ang {course} sa prescribed term nito ({failed}) at hindi naipasa, at naipasa mo '
                'ang ibang courses bago ang {start}, magsisimula ang mga draft sa {start}.',
        stated='Base sa term na binanggit mo, magsisimula ang mga draft sa {start}; ang courses mo bago iyon ay '
               'binibilang na naipasa maliban kung iba ang sinabi mo.',
        header='Draft lang, hindi pa approved. Ipakita mo ito sa program adviser mo. Draft {variant}: {title}',
        titles=dict(A='retake sa next regular offering lang.', B='may special-class requests.',
                    C='may special-class requests at summer, pasok sa summer load.'),
        term='- {term}{units}: {moved}{kept}. {status}',
        units=' ({units} units)', kept=', kasama ang {n} pang prescribed course{s}',
        modes=dict(retake='retake', prescribed='regular offering', special_class_request='special class',
                   summer='summer class', off_semester_request='off-semester class'),
        works='Works.', confirm='Works, may kailangan pang i-confirm.', unknown='Hindi ko ma-check nang buo ang term na ito.',
        request='  {course}: {kind} na ni-request, hindi pa approved ({conditions}Student Handbook p. {page}). Kung '
                'hindi ito magbukas, maaatras sa mas huling term ang {course} at ang courses na nangangailangan nito.',
        d5="  Heads-up: {units} units ang sem na 'to, pero {ceiling} lang ang nakalista sa curriculum mo. Ayon sa "
           'Student Handbook, puwedeng hindi ma-credit ang sobrang units (p. {page}). Mas okay kung i-check mo muna sa '
           'Dean o sa Registrar bago ka mag-enroll.',
        summer_load='  Heads-up: {units} units ang summer na ito, lampas sa normal summer load na {ceiling} (Student '
                    'Handbook p. {page}). I-check muna sa Dean bago ka mag-enroll.',
        load_unknown='  Hindi ko ma-check ang unit load ng term na ito: {reason}.',
        prereq_unknown='  Hindi ko ma-check nang buo ang prerequisites ng {course}; paki-confirm sa program adviser.',
        unchecked='  Hindi ma-check ang {course}.',
        back='Pagkatapos ng {term}, sunod na ang prescribed sequence mo.',
        beyond='Lalampas ang draft na ito sa huling term ng curriculum mo.',
        dropped=dict(same_as='Hindi ipinapakita ang Draft {variant}: pareho lang ito sa Draft {same}.',
                     blocked='Hindi ipinapakita ang Draft {variant}: blocked pa rin ang {course} sa {term} (kailangan '
                             'ang {missing}).',
                     not_placed='Hindi ipinapakita ang Draft {variant}: hindi ko mailagay ang {course} sa mga term na '
                                'kaya kong i-plan.',
                     no_summer_policy='Hindi ipinapakita ang Draft {variant}: wala ang summer load rule.',
                     too_long='Hindi ipinapakita ang Draft {variant}: masyadong maraming term para ma-check ko.'),
        none='Wala akong nagawang draft na gumagana.',
        order='Nakaayos ang mga draft ayon sa pinakakaunting request na kailangan ng approval, tapos sa pinakamaagang '
              'tapos; hindi ito ranking ng pinakamagandang plan.',
        closing='Wala rito ang nagko-confirm ng class offering, approval, grade o academic standing mo.',
        summer_term='summer pagkatapos ng {year} year', join=', '),
}


def _words(language):
    return _WORDS['en' if language in ('en', 'unknown') else 'taglish']


# Track A (owner 4 Nov 2026): lines that depend on what the student said about themselves. A clause is quoted only
# when the reviewed routes carry it; without it the line is a referral, never an unquoted Handbook rule.
_STATUS = {
    'en': dict(
        removal={'4.0': 'You said you got 4.0 in {course}, so you can remove it instead of retaking it, within the '
                        'succeeding term. Student Handbook p. {page}: "{text}"',
                 'INC': 'You said you got INC in {course}, so you can complete it instead of retaking it, within the '
                        'succeeding term. Student Handbook p. {page}: "{text}"'},
        one_year='Note: the same section also states "within one year" (3.3, 3.7). Student Handbook p. {page}: '
                 '"{text}" Please confirm your deadline with your Dean or the Registrar.',
        before='{needed} next semester need {course}, so the removal must be done before enrollment. Student '
               'Handbook p. {page}: "{text}"',
        before_ask='{needed} next semester need {course}, so ask your Dean about finishing the removal before '
                   'enrollment.',
        forfeit='Heads-up: re-enrolling {course} gives up the removal. Student Handbook p. {page}: "{text}"',
        forfeit_ask='Before you re-enroll {course}, ask your Dean how that affects removing the grade; the drafts '
                    'below are for the case where you retake it.',
        summer_graduating="Since you said you're graduating: the summer load can go up to twelve (12) units with the "
                          "Dean's prior approval (Student Handbook p. {page}). The drafts below still keep to the "
                          'normal summer load.',
        overload="Since you said this is your last semester and you're graduating, an overload may be possible. "
                 'Student Handbook p. {page}: "{text}" It\'s a request, not automatic: ask your Dean and the '
                 'Registrar first.',
        waiver="Since you said you're graduating, you can ask about a prerequisite waiver (an option to ask about, "
               'not part of the drafts below). Student Handbook p. {page}: "{text}"',
        cross='If {course} is not offered, you can ask about cross-enrollment. Student Handbook p. {page}: "{text}"',
        substitution='You can also ask about substitution. Student Handbook p. {page}: "{text}"',
        substitution_limit='Student Handbook p. {page}: "{text}"',
        leave='If you plan to stop for a while, apply for a leave of absence. Student Handbook p. {page}: "{text}"',
        standing="You mentioned {standing}. Student Handbook p. {page}: \"{text}\" I don't work out your academic "
                 'standing or which subjects count as advance courses; please ask your Dean before you enroll. The '
                 "drafts below don't apply this restriction.",
        standings=dict(warning='a warning', probation='being on probation',
                       scholastic_delinquency='a scholastic delinquency'),
        reenroll='  Heads-up: you said you have {grade} in {course}, and this plan re-enrolls it.',
        reenroll_ask='Before you enroll, ask your Dean how re-enrolling {course} affects removing the grade.'),
    'taglish': dict(
        removal={'4.0': 'Sabi mo 4.0 ang grade mo sa {course}, kaya puwede mo itong i-remove imbes na i-retake, sa '
                        'loob ng succeeding term. Student Handbook p. {page}: "{text}"',
                 'INC': 'Sabi mo INC ang grade mo sa {course}, kaya puwede mo itong i-complete imbes na i-retake, sa '
                        'loob ng succeeding term. Student Handbook p. {page}: "{text}"'},
        one_year='Note: sinasabi rin ng parehong section ang "within one year" (3.3, 3.7). Student Handbook p. {page}: '
                 '"{text}" Paki-confirm ang deadline mo sa Dean o sa Registrar.',
        before='Kailangan ng {needed} sa susunod na sem ang {course}, kaya dapat matapos ang removal bago mag-enroll. '
               'Student Handbook p. {page}: "{text}"',
        before_ask='Kailangan ng {needed} sa susunod na sem ang {course}, kaya itanong sa Dean kung paano matatapos '
                   'ang removal bago mag-enroll.',
        forfeit='Heads-up: kapag ni-re-enroll mo ang {course}, mawawala ang removal. Student Handbook p. {page}: '
                '"{text}"',
        forfeit_ask='Bago mo i-re-enroll ang {course}, itanong muna sa Dean kung ano ang epekto nito sa removal ng '
                    'grade; ang mga draft sa baba ay para kung i-retake mo ito.',
        summer_graduating='Dahil sabi mo graduating ka: puwedeng umabot sa twelve (12) units ang summer load kapag '
                          'may prior approval ng Dean (Student Handbook p. {page}). Normal summer load pa rin ang '
                          'sinusunod ng mga draft sa baba.',
        overload='Dahil sabi mo last sem mo na at graduating ka, baka puwede ang overload. Student Handbook p. {page}: '
                 '"{text}" Request ito, hindi automatic: itanong muna sa Dean at sa Registrar.',
        waiver='Dahil sabi mo graduating ka, puwede mong itanong ang prerequisite waiver (option na puwedeng itanong, '
               'hindi kasama sa mga draft sa baba). Student Handbook p. {page}: "{text}"',
        cross='Kung hindi offered ang {course}, puwede mong itanong ang cross-enrollment. Student Handbook p. {page}: '
              '"{text}"',
        substitution='Puwede mo ring itanong ang substitution. Student Handbook p. {page}: "{text}"',
        substitution_limit='Student Handbook p. {page}: "{text}"',
        leave='Kung balak mong huminto muna, mag-apply ng leave of absence. Student Handbook p. {page}: "{text}"',
        standing='Nabanggit mo ang {standing}. Student Handbook p. {page}: "{text}" Hindi ko kinukuwenta ang academic '
                 'standing mo o kung aling subjects ang advance courses; paki-tanong sa Dean bago ka mag-enroll. Hindi '
                 'ina-apply ng mga draft sa baba ang restriction na ito.',
        standings=dict(warning='warning', probation='probation', scholastic_delinquency='scholastic delinquency'),
        reenroll='  Heads-up: sabi mo {grade} ang grade mo sa {course}, at ni-re-enroll ito ng plan na ito.',
        reenroll_ask='Bago ka mag-enroll, itanong sa Dean kung ano ang epekto ng pag-re-enroll ng {course} sa removal '
                     'ng grade.'),
}


def _status_words(language):
    return _STATUS['en' if language in ('en', 'unknown') else 'taglish']


def _quote(words, key, clause, **values):
    return words[key].format(page=clause.page, text=clause.text, **values)


def removal_lines(recovery, language, shown) -> list[str]:
    """A stated 4.0/INC in the failed course: removal within the succeeding term, always with the D6 discrepancy."""
    grade, clause = recovery.failed_grade, {c.kind: c for c in recovery.clauses}
    if grade not in ('4.0', 'INC') or 'removal_period' not in clause:
        return []  # 5.0, no stated grade, or no reviewed removal clause: no removal route
    words, course = _status_words(language), shown(recovery.failed_course_id)
    lines = [words['removal'][grade].format(course=course, page=clause['removal_period'].page,
                                            text=clause['removal_period'].text)]
    if 'removal_one_year' in clause:
        lines.append(_quote(words, 'one_year', clause['removal_one_year']))
    if recovery.removal_needed_by:
        needed = ', '.join(map(shown, recovery.removal_needed_by))
        lines.append(_quote(words, 'before', clause['removal_before_enrollment'], needed=needed, course=course)
                     if 'removal_before_enrollment' in clause
                     else words['before_ask'].format(needed=needed, course=course))
    lines.append(_quote(words, 'forfeit', clause['removal_forfeit'], course=course) if 'removal_forfeit' in clause
                 else words['forfeit_ask'].format(course=course))
    return lines


def status_lines(recovery, language, shown) -> list[str]:
    """Graduating, not-offered, stopping and standing lines; each only when the student said so."""
    status, clause = recovery.status, {c.kind: c for c in recovery.clauses}
    if status is None:
        return []
    words, course, lines = _status_words(language), shown(recovery.failed_course_id), []
    if status.graduating:
        if 'summer' in clause:
            lines.append(words['summer_graduating'].format(page=clause['summer'].page))
        if status.last_semester and status.standing is None and 'overload' in clause:
            lines.append(_quote(words, 'overload', clause['overload']))
        if 'prerequisite_waiver' in clause:
            lines.append(_quote(words, 'waiver', clause['prerequisite_waiver']))
    if status.not_offered:
        if 'cross_enrollment' in clause:
            lines.append(_quote(words, 'cross', clause['cross_enrollment'], course=course))
        if 'substitution' in clause:
            lines.append(_quote(words, 'substitution', clause['substitution']))
            if 'substitution_limit' in clause:
                lines.append(_quote(words, 'substitution_limit', clause['substitution_limit']))
    if status.stopping and 'leave_of_absence' in clause:
        lines.append(_quote(words, 'leave', clause['leave_of_absence']))
    if status.standing is not None and 'advance_courses' in clause:
        lines.append(_quote(words, 'standing', clause['advance_courses'],
                            standing=words['standings'][status.standing]))
    return lines


def _number(value):
    return str(int(value)) if float(value).is_integer() else str(value)


def term_label(term, language) -> str:
    from .term_reply import term_name
    if term.semester == 'summer':
        return _words(language)['summer_term'].format(year=_ORDINAL[term.year])
    return term_name(term.year, term.semester)


def recovery_lines(recovery, language, shown) -> list[str]:
    words = _words(language)
    clause = {c.kind: c for c in recovery.clauses}
    course = shown(recovery.failed_course_id)
    lines = [words['regular']] if recovery.regular_asked else []
    lines.extend(removal_lines(recovery, language, shown))
    when = (f' ({term_label(recovery.next_offering, language)})' if recovery.next_offering is not None else '')
    lines.append(words['routes'].format(course=course))
    for kind, key in (('regular_class', 'retake'), ('special_class', 'special'), ('off_semester', 'off_semester'),
                      ('summer', 'summer')):
        lines.append('- ' + words[key].format(page=clause[kind].page, text=clause[kind].text, when=when))
    lines.extend(status_lines(recovery, language, shown))
    start = term_label(recovery.start_term, language)
    lines.append(words['stated'].format(start=start) if recovery.term_stated else words['assumed'].format(
        course=course, failed=term_label(recovery.failed_term, language), start=start))
    if not recovery.drafts:
        lines.append(words['none'])
    for draft in recovery.drafts:
        lines.append(words['header'].format(variant=draft.variant, title=words['titles'][draft.variant]))
        lines.extend(_term_lines(draft, words, clause, shown, language))
        last = next(t for t in reversed(draft.terms) if t.moved)
        lines.append(words['beyond'] if draft.beyond_curriculum else
                     words['back'].format(term=term_label(last.term, language)))
    for dropped in recovery.dropped:
        lines.append(words['dropped'][dropped.reason].format(
            variant=dropped.variant, same=dropped.same_as, course=shown(dropped.course_id) if dropped.course_id else '',
            term=term_label(dropped.term, language) if dropped.term else '',
            missing=words['join'].join(map(shown, dropped.missing))))
    if len(recovery.drafts) > 1:
        lines.append(words['order'])
    lines.append(words['closing'])
    return lines


def _term_lines(draft, words, clause, shown, language):
    request_clause = {'special_class_request': 'special_class', 'summer': 'summer', 'off_semester_request': 'off_semester'}
    lines = []
    for term in draft.terms:
        verdict = term.verdict
        if not term.moved and verdict.outcome == 'works':
            continue  # an unchanged prescribed term
        status = (words['unknown'] if verdict.outcome == 'unknown'
                  else words['confirm'] if verdict.unconfirmed else words['works'])
        moved = words['join'].join(f'{shown(p.course_id)} ({words["modes"][p.mode]})' for p in term.moved)
        kept = (words['kept'].format(n=len(term.kept), s='' if len(term.kept) == 1 else 's') if term.kept and moved
                else words['join'].join(map(shown, term.kept)))
        lines.append(words['term'].format(term=term_label(term.term, language), moved=moved, kept=kept, status=status,
            units='' if verdict.load.units is None else words['units'].format(units=_number(verdict.load.units))))
        for request in verdict.unconfirmed:
            source = clause[request_clause[request.kind]]
            conditions = ''.join(f'"{c}"; ' for c in source.conditions)
            lines.append(words['request'].format(course=shown(request.course_id), kind=words['modes'][request.kind],
                                                 conditions=conditions, page=source.page))
        for warning in verdict.warnings:
            lines.append(words['d5' if warning.kind == 'load_above_prescribed' else 'summer_load'].format(
                units=_number(warning.units), ceiling=_number(warning.ceiling), page=warning.clause.page))
        for reason in verdict.reasons:
            if reason.kind == 'prerequisite_unknown':
                lines.append(words['prereq_unknown'].format(course=shown(reason.course_id)))
            elif reason.kind in ('not_in_curriculum', 'rule_error'):
                lines.append(words['unchecked'].format(course=shown(reason.course_id)))
        if verdict.load.status == 'unknown':
            lines.append(words['load_unknown'].format(reason=verdict.load.reason))
    return lines
