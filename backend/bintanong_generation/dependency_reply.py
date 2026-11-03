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
               note_one="Note: {courses} has a printed prerequisite condition that isn't verified course by course yet, "
                        'so please confirm it with your program adviser if you plan to take it.',
               note_many="Note: {courses} have printed prerequisite conditions that aren't verified course by course "
                         'yet, so please confirm them with your program adviser if you plan to take them.',
               join=' and '),
    'taglish': dict(none='Walang course sa prospectus mo na may {target} bilang prerequisite, kaya hindi nito mabo-block '
                         'ang ibang course.',
                    some='Kung ma-fail mo ang {target}, apektado ang mga course na ito dahil kasama ito sa prerequisites '
                         'nila (direkta o sa ibang course): {courses}.',
                    note_one='Note: may naka-print na prerequisite condition ang {courses} na hindi pa verified course by '
                             'course, kaya paki-confirm sa program adviser kung balak mo itong i-take.',
                    note_many='Note: may naka-print na prerequisite conditions ang {courses} na hindi pa verified course '
                              'by course, kaya paki-confirm sa program adviser kung balak mo silang i-take.',
                    join=' at '),
}


def _join(items, join):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + join + items[-1]


def dependency_lines(dependencies, target, language, shown) -> list[str]:
    words = _WORDS['en' if language in ('en', 'unknown') else 'taglish']
    courses = [shown(c) for c in dependencies.course_ids]
    lines = [words['some'].format(target=shown(target), courses=', '.join(courses)) if courses
             else words['none'].format(target=shown(target))]
    unverified = [shown(u.split(':', 1)[1]) for u in dependencies.unknown_conditions if ':' in u]
    if unverified:
        key = 'note_one' if len(unverified) == 1 else 'note_many'
        lines.append(words[key].format(courses=_join(unverified, words['join'])))
    return lines
