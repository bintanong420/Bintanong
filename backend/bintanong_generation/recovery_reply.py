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
        load_unknown="  I can't check the unit load for this term: {reason}.",
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
    when = (f' ({term_label(recovery.next_offering, language)})' if recovery.next_offering is not None else '')
    lines.append(words['routes'].format(course=course))
    for kind, key in (('regular_class', 'retake'), ('special_class', 'special'), ('off_semester', 'off_semester'),
                      ('summer', 'summer')):
        lines.append('- ' + words[key].format(page=clause[kind].page, text=clause[kind].text, when=when))
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
