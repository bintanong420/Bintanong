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
                    C='with special-class requests and summer, within the summer load.',
                    D='preferred: just in time, with special-class requests and summer as needed.'),
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
        order='Draft D comes first: courses wait until needed, using summer only when needed by the next term. '
              'Other drafts follow by fewest requests, then earliest finish. Offerings and approvals need confirmation.',
        other_order='Drafts follow by fewest requests, then earliest finish; offerings and approvals need confirmation.',
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
                    C='may special-class requests at summer, pasok sa summer load.',
                    D='preferred: just in time, may special-class requests at summer kung kailangan.'),
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
        order='Nauuna ang Draft D: hinihintay ang term na kailangan ang courses, at summer lang kung kailangan sa '
              'next term. Ang ibang draft ay ayon sa pinakakaunting request, tapos sa pinakamaagang tapos. '
              'Kailangan pa ring i-confirm ang offerings at approvals.',
        other_order='Ayon sa pinakakaunting request ang mga draft, tapos sa pinakamaagang tapos. Kailangan pa ring '
                    'i-confirm ang offerings at approvals.',
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


# Each line names its clause through {ref}: inline in the plan-check reply, by short name in the Markdown recovery
# reply, whose "Sources / rules" section quotes every clause once (owner 4 Nov 2026 layout).
_INLINE = 'Student Handbook p. {page}: "{text}"'
for _lang in _STATUS.values():
    for _key, _value in list(_lang.items()):
        if isinstance(_value, str):
            _lang[_key] = _value.replace(_INLINE, '{ref}')
    _lang['removal'] = {g: v.replace(_INLINE, '{ref}') for g, v in _lang['removal'].items()}


def _status_words(language):
    return _STATUS['en' if language in ('en', 'unknown') else 'taglish']


def inline_ref(clause):
    return _INLINE.format(page=clause.page, text=clause.text)


def _quote(words, key, clause, cite=inline_ref, **values):
    return words[key].format(ref=cite(clause), page=clause.page, **values)


def removal_lines(recovery, language, shown, cite=inline_ref) -> list[str]:
    """A stated 4.0/INC in the failed course: removal within the succeeding term, always with the D6 discrepancy."""
    grade, clause = recovery.failed_grade, {c.kind: c for c in recovery.clauses}
    if grade not in ('4.0', 'INC') or 'removal_period' not in clause:
        return []  # 5.0, no stated grade, or no reviewed removal clause: no removal route
    words, course = _status_words(language), shown(recovery.failed_course_id)
    lines = [words['removal'][grade].format(course=course, ref=cite(clause['removal_period']))]
    if 'removal_one_year' in clause:
        lines.append(_quote(words, 'one_year', clause['removal_one_year'], cite))
    if recovery.removal_needed_by:
        needed = ', '.join(map(shown, recovery.removal_needed_by))
        lines.append(_quote(words, 'before', clause['removal_before_enrollment'], cite, needed=needed, course=course)
                     if 'removal_before_enrollment' in clause
                     else words['before_ask'].format(needed=needed, course=course))
    lines.append(_quote(words, 'forfeit', clause['removal_forfeit'], cite, course=course)
                 if 'removal_forfeit' in clause else words['forfeit_ask'].format(course=course))
    return lines


def status_lines(recovery, language, shown, cite=inline_ref) -> list[str]:
    """Graduating, not-offered, stopping and standing lines; each only when the student said so."""
    status, clause = recovery.status, {c.kind: c for c in recovery.clauses}
    if status is None:
        return []
    words, course, lines = _status_words(language), shown(recovery.failed_course_id), []
    if status.graduating:
        if 'summer' in clause:
            lines.append(_quote(words, 'summer_graduating', clause['summer'], cite))
        if status.last_semester and status.standing is None and 'overload' in clause:
            lines.append(_quote(words, 'overload', clause['overload'], cite))
        if 'prerequisite_waiver' in clause:
            lines.append(_quote(words, 'waiver', clause['prerequisite_waiver'], cite))
    if status.not_offered:
        if 'cross_enrollment' in clause:
            lines.append(_quote(words, 'cross', clause['cross_enrollment'], cite, course=course))
        if 'substitution' in clause:
            lines.append(_quote(words, 'substitution', clause['substitution'], cite))
            if 'substitution_limit' in clause:
                lines.append(_quote(words, 'substitution_limit', clause['substitution_limit'], cite))
    if status.stopping and 'leave_of_absence' in clause:
        lines.append(_quote(words, 'leave', clause['leave_of_absence'], cite))
    if status.standing is not None and 'advance_courses' in clause:
        lines.append(_quote(words, 'standing', clause['advance_courses'], cite,
                            standing=words['standings'][status.standing]))
    return lines


def _number(value):
    return str(int(value)) if float(value).is_integer() else str(value)


def _short_term(year, semester):
    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(year, 'th')
    ordinal = f"{year}{suffix}"
    return (f'Summer after {ordinal} year' if semester == 'summer' else
            f"{ordinal} year, {'1st' if semester == 'first_semester' else '2nd'} sem")


def term_label(term, language, *, compact=False) -> str:
    if compact:
        return _short_term(term.year, term.semester)
    from .term_reply import term_name
    if term.semester == 'summer':
        return _words(language)['summer_term'].format(year=_ORDINAL[term.year])
    return term_name(term.year, term.semester)


# Markdown layout (owner 4 Nov 2026, "adapt how ChatGPT handles text layouting"): a direct answer first, one heading
# per section, one table per draft, every Handbook clause quoted once under "Sources / rules" and named by its short
# name elsewhere, and the approval line once at the end. It stays readable as plain text.
NAMES = dict(regular_class='Regular class', special_class='Special class', off_semester='Off-semester class',
             summer='Summer load', removal_period='Removal period', removal_one_year='Removal within one year',
             removal_before_enrollment='Removal before enrollment', removal_forfeit='Forfeiture of removal',
             overload='Overload', prerequisite_waiver='Prerequisite waiver', cross_enrollment='Cross-enrollment',
             substitution='Substitution', substitution_limit='Limits on substitution',
             leave_of_absence='Leave of absence', advance_courses='Advance courses', maximum_load='Maximum load')

_MD = {
    'en': dict(
        fastest='**Earliest projected return among these drafts: Draft {variant}**, by {term}. '
                'This is not a confirmed feasible schedule; each step still needs approval.',
        fewest='**Draft {variant}** needs the fewest requests; Draft {fast} gets you back on your prescribed sequence '
               'soonest ({term}). Each step still needs approval.',
        only='**Draft {variant}** gets you back on your prescribed sequence by {term}. Each step still needs approval.',
        late='**Draft {variant}** is shown first; every draft goes past your curriculum\'s last term. '
             'Each step still needs approval.',
        delayed='What gets delayed', delayed_intro='If you fail {course}, these courses need it (directly or through '
                                                     'another course):',
        options='Your options for {course}', drafts='Drafts', sources='Sources / rules',
        retake='Retake it at its next regular offering{when} ({ref}). The class schedule for that term is not '
               'confirmed here.',
        special='Request a special class ({ref}). It is a request, not an approval; the source names the University '
                'Cashier only for the payment, not who approves the request.',
        off_semester='Ask whether it can open as an off-semester regular class ({ref}). It opens only under those '
                     'conditions, and the source names no office for it.',
        summer='Take it in summer, within the summer load ({ref}). A summer offering is not confirmed here.',
        ref='see {name}, p. {page}', table='| Term | Courses | Notes |', rule='| --- | --- | --- |',
        draft='#### Draft {variant}: {title}', back='Back on your prescribed sequence from {term}.',
        request='{course}: {kind} requested, not yet approved (see {name})',
        d5='Heads-up: {units} units, your curriculum lists {ceiling}; extra units may not be credited (see Maximum '
           'load). Check with your Dean or the Registrar.',
        summer_load='Heads-up: {units} units, above the normal summer load of {ceiling} (see Summer load). Check with '
                    'your Dean.',
        load_unknown="Can't check this term's unit load: {reason}.",
        prereq_unknown="Can't fully check {course}'s prerequisites; confirm with your program adviser.",
        unchecked="{course} couldn't be checked.", kept='{n} other prescribed course{s}', plus='plus',
        closing='These are drafts, not approved: show them to your program adviser. None of this confirms a class '
                'offering, an approval, a grade or your academic standing.'),
    'taglish': dict(
        fastest='**Pinakamaagang projected return sa mga draft na ito: Draft {variant}**, sa {term}. '
                'Hindi pa confirmed na feasible ang schedule; kailangan pa ng approval ang bawat step.',
        fewest='**Draft {variant}** ang may pinakakaunting request; ang Draft {fast} ang pinakamabilis makabalik sa '
               'prescribed sequence mo ({term}). Kailangan pa rin ng approval ang bawat step.',
        only='**Draft {variant}**: balik ka sa prescribed sequence mo pagdating ng {term}. Kailangan pa rin ng '
             'approval ang bawat step.',
        late='**Draft {variant}** ang unang ipinapakita; lalampas ang lahat ng draft sa huling term ng '
             'curriculum mo. Kailangan pa rin ng approval ang bawat step.',
        delayed='Ano ang maaatras', delayed_intro='Kung ma-fail mo ang {course}, kailangan ito ng mga course na ito '
                                                   '(direkta o sa ibang course):',
        options='Mga option mo para sa {course}', drafts='Mga draft', sources='Sources / rules',
        retake='I-retake ito sa next regular offering{when} ({ref}). Hindi pa confirmed dito ang class schedule sa '
               'term na iyon.',
        special='Mag-request ng special class ({ref}). Request ito, hindi approval; University Cashier lang ang '
                'binanggit ng source para sa bayad, hindi kung sino ang mag-a-approve.',
        off_semester='Itanong kung puwede itong buksan bilang off-semester regular class ({ref}). Bubuksan lang ito '
                     'kung pasok sa conditions, at walang office na binanggit ang source para dito.',
        summer='Kunin ito sa summer, pasok sa summer load ({ref}). Hindi pa confirmed dito kung may summer offering.',
        ref='tingnan ang {name}, p. {page}', table='| Term | Courses | Notes |', rule='| --- | --- | --- |',
        draft='#### Draft {variant}: {title}', back='Balik sa prescribed sequence mo simula {term}.',
        request='{course}: {kind} na ni-request, hindi pa approved (tingnan ang {name})',
        d5="Heads-up: {units} units, {ceiling} lang ang nakalista sa curriculum mo; puwedeng hindi ma-credit ang sobra "
           '(tingnan ang Maximum load). I-check muna sa Dean o sa Registrar.',
        summer_load='Heads-up: {units} units, lampas sa normal summer load na {ceiling} (tingnan ang Summer load). '
                    'I-check muna sa Dean.',
        load_unknown='Hindi ma-check ang unit load ng term na ito: {reason}.',
        prereq_unknown='Hindi ma-check nang buo ang prerequisites ng {course}; paki-confirm sa program adviser.',
        unchecked='Hindi ma-check ang {course}.', kept='{n} pang prescribed course{s}', plus='kasama ang',
        closing='Mga draft lang ito, hindi pa approved: ipakita mo sa program adviser mo. Wala rito ang nagko-confirm '
                'ng class offering, approval, grade o academic standing mo.'),
}


def _key(term):
    return term.year, ('first_semester', 'second_semester', 'summer').index(term.semester)


def _cell(text):
    return text.replace('|', '/')


def recovery_sections(recovery, language, shown, dependencies=None, *, compact=False):
    """Host sections shared by full copy text and the progressive student view."""
    words, md = _words(language), _MD['en' if language in ('en', 'unknown') else 'taglish']
    if compact:
        md = dict(md, draft='### Plan {variant}: {title}')
    titles = ({'A': 'Retake at the next regular offering', 'B': 'Request special classes',
               'C': 'Special classes and summer', 'D': 'Special classes and summer as needed'}
              if language in ('en', 'unknown') else
              {'A': 'Retake sa next regular offering', 'B': 'Mag-request ng special classes',
               'C': 'Special classes at summer', 'D': 'Special classes at summer kung kailangan'})
    clause = {c.kind: c for c in recovery.clauses}
    course = shown(recovery.failed_course_id)
    used = {}  # short name -> (page, text): each clause quoted once under Sources / rules

    def cite(source, name=None):
        name = name or NAMES[source.kind]
        used.setdefault(name, (source.page, source.text))
        return md['ref'].format(name=name, page=source.page)

    lines = _answer(recovery, md, language, compact=compact)
    if recovery.regular_asked:
        lines.append(words['regular'])
    if dependencies is not None:
        lines.extend(['', '### ' + md['delayed'], *_delayed(dependencies, recovery, md, shown, language, compact=compact)])
    sections = [('overview', lines)]
    lines = ['', '### ' + md['options'].format(course=course)]
    lines.extend('- ' + line for line in removal_lines(recovery, language, shown, cite))
    when = f' ({term_label(recovery.next_offering, language, compact=compact)})' if recovery.next_offering is not None else ''
    for kind, key in (('regular_class', 'retake'), ('special_class', 'special'), ('off_semester', 'off_semester'),
                      ('summer', 'summer')):
        lines.append('- ' + md[key].format(ref=cite(clause[kind]), when=when))
    sections.append(('options', lines))
    sections.append(('conditions', ['- ' + line for line in status_lines(recovery, language, shown, cite)]))
    lines = ['', '### ' + md['drafts']]
    start = term_label(recovery.start_term, language, compact=compact)
    lines.append(words['stated'].format(start=start) if recovery.term_stated else words['assumed'].format(
        course=course, failed=term_label(recovery.failed_term, language, compact=compact), start=start))
    if not recovery.drafts:
        lines.append(words['none'])
    sections.append(('assumptions', lines))
    for draft in recovery.drafts:
        lines = ['', md['draft'].format(variant=draft.variant, title=titles[draft.variant] if compact else words['titles'][draft.variant]),
                 md['table'], md['rule']]
        lines.extend(_rows(draft, md, words, clause, shown, language, cite, compact=compact))
        unknown = dict.fromkeys(reason.course_id for term in draft.terms for reason in term.verdict.reasons
                                if reason.kind == 'prerequisite_unknown')
        if unknown:
            lines.append(md['prereq_unknown'].format(course=', '.join(map(shown, unknown))))
        lines.append(words['beyond'] if draft.beyond_curriculum or draft.rejoin_term is None
                     else md['back'].format(term=term_label(draft.rejoin_term, language, compact=compact)))
        sections.append(('draft', lines))
    lines = []
    for dropped in recovery.dropped:
        lines.append(words['dropped'][dropped.reason].format(
            variant=dropped.variant, same=dropped.same_as, course=shown(dropped.course_id) if dropped.course_id else '',
            term=term_label(dropped.term, language, compact=compact) if dropped.term else '',
            missing=words['join'].join(map(shown, dropped.missing))))
    if len(recovery.drafts) > 1 and not recovery.fastest_asked:
        lines.append(words['order' if recovery.drafts[0].variant == 'D' else 'other_order'])
    sections.append(('order', lines))
    sections.append(('sources', ['', '### ' + md['sources'], *[
        f'- **{name}** (Student Handbook p. {page}): "{text}"' for name, (page, text) in used.items()]]))
    sections.append(('closing', ['', md['closing']]))
    return sections


def recovery_lines(recovery, language, shown, dependencies=None) -> list[str]:
    return [line for _, lines in recovery_sections(recovery, language, shown, dependencies) for line in lines]


def _answer(recovery, md, language, *, compact=False):
    if not recovery.drafts:
        return [_words(language)['none']]
    first = recovery.drafts[0]
    timely = [d for d in recovery.drafts if d.rejoin_term is not None and not d.beyond_curriculum]
    if not timely:
        return [md['late'].format(variant=first.variant)]
    if not recovery.fastest_asked and first.variant == 'D' and first in timely:
        return [md['only'].format(variant=first.variant, term=term_label(first.rejoin_term, language, compact=compact))]
    fastest = min(timely, key=lambda d: (_key(d.rejoin_term), d.requests))
    when = term_label(fastest.rejoin_term, language, compact=compact)
    if recovery.fastest_asked or fastest is first:
        return [md['fastest' if recovery.fastest_asked else 'only'].format(variant=fastest.variant, term=when)]
    return [md['fewest'].format(variant=first.variant, fast=fastest.variant, term=when)]


def _delayed(dependencies, recovery, md, shown, language, *, compact=False):
    from .term_reply import term_name
    from ..bintanong_symbolic.course_facts import TERM_ORDER
    placed = {c: (y, s) for c, y, s in dependencies.placements}
    groups = {}
    for course in dependencies.course_ids:
        groups.setdefault(placed.get(course), []).append(course)

    def order(term):
        return (9, 9) if term is None else (term[0], TERM_ORDER.index(term[1]) if term[1] in TERM_ORDER else 9)
    lines = [md['delayed_intro'].format(course=shown(recovery.failed_course_id))]
    for term in sorted(groups, key=order):
        label = (_short_term(*term) if compact else term_name(*term)) if term is not None else '?'
        lines.append(f'- {label[:1].upper() + label[1:]}: ' + ', '.join(sorted(map(shown, groups[term]))))
    from .dependency_reply import dependency_lines
    lines.extend(dependency_lines(dependencies, recovery.failed_course_id, language, shown)[1:])  # condition notes
    return lines


def _rows(draft, md, words, clause, shown, language, cite, *, compact=False):
    request_clause = {'special_class_request': 'special_class', 'summer': 'summer', 'off_semester_request': 'off_semester'}
    rows = []
    for term in draft.terms:
        verdict = term.verdict
        if not term.moved and verdict.outcome == 'works':
            continue  # an unchanged prescribed term
        units = '' if verdict.load.units is None else f' ({_number(verdict.load.units)} units)'
        courses = [f'{shown(p.course_id)} ({words["modes"][p.mode]})' for p in term.moved]
        if term.kept:
            kept = md['kept'].format(n=len(term.kept), s='' if len(term.kept) == 1 else 's')
            courses.append(f'{md["plus"]} {kept}' if courses else ', '.join(map(shown, term.kept)))
        notes = [words['unknown'] if verdict.outcome == 'unknown'
                 else words['confirm'] if verdict.unconfirmed else words['works']]
        for request in verdict.unconfirmed:
            source = clause[request_clause[request.kind]]
            cite(source)
            notes.append(md['request'].format(course=shown(request.course_id), kind=words['modes'][request.kind],
                                              name=NAMES[source.kind]))
        for warning in verdict.warnings:
            cite(warning.clause, 'Maximum load' if warning.kind == 'load_above_prescribed' else 'Summer load')
            notes.append(md['d5' if warning.kind == 'load_above_prescribed' else 'summer_load'].format(
                units=_number(warning.units), ceiling=_number(warning.ceiling)))
        for reason in verdict.reasons:
            if reason.kind in ('not_in_curriculum', 'rule_error', 'units_missing'):
                notes.append(md['unchecked'].format(course=shown(reason.course_id)))
        if verdict.load.status == 'unknown':
            notes.append(md['load_unknown'].format(reason=verdict.load.reason))
        rows.append(f'| {_cell(term_label(term.term, language, compact=compact))}{units} | {_cell(", ".join(courses))} | '
                    f'{_cell(". ".join(note.rstrip(".") for note in notes))}. |')
    return rows
