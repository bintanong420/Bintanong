"""Host wording for a checked term (memory/eligibility plan, Task 4): grouped results with each course's reason,
already-passed courses and possible retakes kept apart, and the source's coverage stated when the term is absent."""
from __future__ import annotations

_ORDINAL = {1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth'}
_TERM = {'first_semester': 'first semester', 'second_semester': 'second semester', 'summer': 'summer', 'any': 'all terms'}
_WORDS = {
    'en': dict(heading='{term} courses in your prospectus, checked against what you told me:',
               met='Prerequisites met', blocked='Blocked by a known prerequisite',
               needs_info='Needs information or source review', already_passed='Already passed',
               retakes='Possible retakes (failed earlier)', needs='needs {courses}', same_term='{course} passed or taken in the same term',
               blank='no prerequisite is printed for it in the prospectus; please confirm with your program adviser',
               unverified='its printed condition is not verified yet; please confirm with your program adviser',
               passed_q='have you passed {course}?', taking_q='are you taking {course} this term?',
               unchecked='it could not be checked right now', retake_met='prerequisites met', blocked_by='blocked: needs {courses}',
               footer='This is the prospectus list for that term. It does not confirm section offerings, slots or '
                      'enrollment approval.',
               partial='Some courses could not be checked right now; they are listed under needs information.',
               uncovered='The reviewed prospectus for this curriculum does not include {term}, so I cannot list its '
                         'courses. It covers: {covered}.',
               question='Which year level and semester is this for? For example: "second year, second semester".',
               join=' and '),
    'taglish': dict(heading='{term} courses sa prospectus mo, chineck base sa sinabi mo:',
                    met='Pasok sa prerequisites', blocked='Blocked ng kilalang prerequisite',
                    needs_info='Kailangan ng info o source review', already_passed='Naipasa mo na',
                    retakes='Posibleng retake (na-fail dati)', needs='kailangan ang {courses}',
                    same_term='{course} na naipasa o kinukuha nang sabay',
                    blank='walang naka-print na prerequisite sa prospectus; paki-confirm sa program adviser',
                    unverified='hindi pa verified ang naka-print na condition; paki-confirm sa program adviser',
                    passed_q='naipasa mo na ba ang {course}?', taking_q='kinukuha mo ba ang {course} ngayong term?',
                    unchecked='hindi ito ma-check ngayon', retake_met='pasok sa prerequisites',
                    blocked_by='blocked: kailangan ang {courses}',
                    footer='Listahan ito ng prospectus para sa term na iyan. Hindi nito kinukumpirma ang section '
                           'offerings, slots o enrollment approval.',
                    partial='May courses na hindi ma-check ngayon; nasa needs information sila.',
                    uncovered='Hindi kasama ang {term} sa na-review na prospectus ng curriculum na ito, kaya hindi ko '
                              'ma-list ang courses nito. Kasama lang ang: {covered}.',
                    question='Para saang year level at semester ito? Halimbawa: "second year, second semester".',
                    join=' at '),
}


def _words(language):
    return _WORDS['en' if language in ('en', 'unknown') else 'taglish']


def term_name(year, term) -> str:
    return f'{_ORDINAL[int(year)]} year, {_TERM[term]}'


def term_question(language) -> str:
    return _words(language)['question']


def _join(items, words):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + words['join'] + items[-1]


def _ids(conditions, prefix):
    return [c.split(':', 1)[1] for c in conditions if c.startswith(prefix + ':')]


def _reason(course, words, shown):
    if course.outcome in ('unsupported', 'error'):
        return words['unchecked']
    if course.group == 'blocked':
        same_term = _ids(course.violated, 'not_enrolled')
        to_pass = [c for c in _ids(course.violated, 'not_completed') if c not in same_term]
        parts = [_join([shown(c) for c in to_pass], words)] if to_pass else []
        parts += [words['same_term'].format(course=shown(c)) for c in same_term]
        key = 'blocked_by' if course.retake else 'needs'
        return words[key].format(courses=_join(parts, words))
    if course.group == 'needs_info':
        if course.unresolved_reason is not None:
            return words['blank' if course.unresolved_reason.startswith('Printed prerequisite cell is blank')
                         else 'unverified']
        asks = [words['passed_q'].format(course=shown(c)) for c in _ids(course.missing, 'completion_unknown')]
        asks += [words['taking_q'].format(course=shown(c)) for c in _ids(course.missing, 'enrollment_unknown')]
        return ' '.join(asks) or words['unchecked']
    return words['retake_met'] if course.retake else None


def _entry(course, words, shown):
    reason = _reason(course, words, shown)
    return course.code if reason is None else f'{course.code} ({reason})'


def term_lines(result, language, shown) -> list[str]:
    words = _words(language)
    inputs = {i.name: i.value for i in result.inputs}
    term = term_name(inputs['year_level'], inputs['semester'])
    if result.status == 'not_covered':
        covered = '; '.join(term_name(*t.split(':')) for t in result.covered_terms)
        return [words['uncovered'].format(term=term, covered=covered)]
    lines = [words['heading'].format(term=term[0].upper() + term[1:])]
    for group in ('met', 'blocked', 'needs_info', 'already_passed'):
        listed = [_entry(c, words, shown) for c in result.courses if c.group == group and not c.retake]
        if listed:
            lines.append(f'{words[group]}: ' + ', '.join(listed))
    retakes = [_entry(c, words, shown) for c in result.courses if c.retake]
    if retakes:
        lines.append(f'{words["retakes"]}: ' + ', '.join(retakes))
    if result.status == 'partial':
        lines.append(words['partial'])
    lines.append(words['footer'])
    return lines
