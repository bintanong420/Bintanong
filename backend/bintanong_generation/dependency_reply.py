"""Host wording for "what does failing X block?" (owner report, 4 Nov 2026).

The answer names the courses whose reviewed rules need the course (directly or through another course), or says none
do. Courses whose printed condition is not verified course by course are named in one short note, because such a
condition could still include it; blank cells (no prerequisite) and year standing name no course and are not listed.
"""
from __future__ import annotations

_WORDS = {
    'en': dict(none='No course in your prospectus lists {target} as a prerequisite, so failing it does not block another '
                    'course.',
               some='If you fail {target}, these courses are affected because their prerequisites include it (directly '
                    'or through another course): {courses}.',
               term_some='In {term}, failing {target} blocks: {courses}.',
               term_none='In {term}, no course needs {target}.',
               later='Courses in other terms that need it: {courses}.',
               also='It also affects courses in other terms: {courses}.',
               note='Note: {course} requires "{printed}" (as printed). I can\'t check that from individual course results, '
                    'so please confirm it with your program adviser.',
               note_unprinted="Note: {course} has a prerequisite condition I can't check from individual course results, "
                              'so please confirm it with your program adviser.'),
    'taglish': dict(none='Walang course sa prospectus mo na may {target} bilang prerequisite, kaya hindi nito mabo-block '
                         'ang ibang course.',
                    some='Kung ma-fail mo ang {target}, apektado ang mga course na ito dahil kasama ito sa prerequisites '
                         'nila (direkta o sa ibang course): {courses}.',
                    term_some='Sa {term}, mabo-block ng pag-fail sa {target} ang: {courses}.',
                    term_none='Sa {term}, walang course na nangangailangan ng {target}.',
                    later='Mga course sa ibang term na nangangailangan nito: {courses}.',
                    also='Apektado rin ang mga course sa ibang term: {courses}.',
                    note='Note: "{printed}" ang naka-print na requirement ng {course}, at hindi ko ito ma-check gamit ang '
                         'bawat course result. Paki-confirm sa program adviser.',
                    note_unprinted='Note: may prerequisite condition ang {course} na hindi ko ma-check gamit ang bawat '
                                   'course result. Paki-confirm sa program adviser.'),
}


def dependency_lines(dependencies, target, language, shown, term=None, with_terms=False) -> list[str]:
    """term: (year, semester) the question asked about, or None; 'any' semester means the whole year.
    with_terms: name each listed course's prescribed term (Ask mode, owner 4 Nov 2026)."""
    from .term_reply import term_name
    words = _WORDS['en' if language in ('en', 'unknown') else 'taglish']
    placed = {course: (year, semester) for course, year, semester in dependencies.placements}

    def in_term(course):
        year, semester = placed.get(course, (None, None))
        return year == term[0] and (term[1] == 'any' or semester == term[1])

    def with_term(course):
        return f'{shown(course)} ({term_name(*placed[course])})' if course in placed else shown(course)
    from ..bintanong_symbolic.course_facts import TERM_ORDER
    # Printed order of the curriculum (year, then term), not internal ids (live 4 Nov 2026).
    ordered = sorted(dependencies.course_ids, key=lambda c: (placed.get(c, (9, ''))[0],
        TERM_ORDER.index(placed[c][1]) if c in placed and placed[c][1] in TERM_ORDER else 9, shown(c)))
    if term is not None:
        name = term_name(*term) if term[1] != 'any' else f'{term_name(term[0], "first_semester").split(",")[0]}'
        inside = [c for c in ordered if in_term(c)]
        later = [c for c in ordered if not in_term(c)]
        lines = [words['term_some'].format(term=name, target=shown(target), courses=', '.join(map(shown, inside)))
                 if inside else words['term_none'].format(term=name, target=shown(target))]
        if later:
            lines.append(words['also' if inside else 'later'].format(courses=', '.join(map(with_term, later))))
    else:
        courses = [with_term(c) if with_terms else shown(c) for c in ordered]
        lines = [words['some'].format(target=shown(target), courses=', '.join(courses)) if courses
                 else words['none'].format(target=shown(target))]
    printed = dict(dependencies.printed_conditions)
    for condition in dependencies.unknown_conditions:
        course = condition.split(':', 1)[1] if ':' in condition else None
        if course is None:
            continue
        lines.append(words['note'].format(course=shown(course), printed=printed[course]) if course in printed
                     else words['note_unprinted'].format(course=shown(course)))
    return lines
