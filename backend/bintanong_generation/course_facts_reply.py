"""Host-written course-fact lines (owner course facts plan, approved 25 Oct 2026): printed title, units as
printed (CF1) and year/semester, with the prospectus page. Nothing is added up or defaulted; units that are
not printed are said to be not printed. No model call writes these facts."""
from itertools import groupby

_YEARS = {
 'en': ('first year', 'second year', 'third year', 'fourth year', 'fifth year'),
 'fil': ('unang taon', 'ikalawang taon', 'ikatlong taon', 'ikaapat na taon', 'ikalimang taon'),
 'taglish': ('first year', 'second year', 'third year', 'fourth year', 'fifth year')}
_TERMS = {
 'en': dict(first_semester='first semester', second_semester='second semester', summer='summer'),
 'fil': dict(first_semester='unang semestre', second_semester='ikalawang semestre', summer='summer'),
 'taglish': dict(first_semester='first semester', second_semester='second semester', summer='summer')}
_TEXT = {
 'en': dict(heading='{when} courses ({pages}):', capitalize=True, none='units not printed',
            empty='The prospectus lists no courses for {when}.', course='{course}; {when} ({pages}).'),
 'fil': dict(heading='Mga subject sa {when} ({pages}):', capitalize=False, none='walang naka-print na units',
             empty='Walang naka-list na subject sa {when} sa prospectus.', course='{course}; {when} ({pages}).'),
 'taglish': dict(heading='Ito ang subjects sa {when} ({pages}):', capitalize=False, none='walang naka-print na units',
                 empty='Walang naka-list na subjects sa {when} sa prospectus.', course='{course}; {when} ({pages}).')}
_SPLIT = (('units.lecture', 'LEC'), ('units.rle', 'RLE'), ('units.lab', 'LAB'))


def _units(units, text):
    printed = dict(units)
    for field in ('units.printed', 'units.total'):
        if field in printed:
            return f'{printed[field]} units'
    split = [f'{label} {printed[field]}' for field, label in _SPLIT if field in printed]
    return ', '.join(split) if split else text['none']


def _pages(courses):
    pages = sorted({c.page for c in courses})
    return ('p. ' if len(pages) == 1 else 'pp. ') + ', '.join(map(str, pages))


def _when(language, year, term):
    return f"{_YEARS[language][year - 1]}, {_TERMS[language][term]}"


def _course(course, text):
    return f"{course.code}{' ' + course.title if course.title else ''}: {_units(course.units, text)}"


def course_fact_lines(result, language) -> list[str]:
    """Lines for a complete CourseFactsResult; the caller handles every other status."""
    language = language if language in _TEXT else 'en'
    text = _TEXT[language]
    prospectus = lambda courses: 'prospectus ' + _pages(courses)
    if result.predicate == 'course_facts':
        course = result.courses[0]
        return [text['course'].format(course=_course(course, text), when=_when(language, course.year, course.term),
                                      pages=prospectus([course]))]
    inputs = {i.name: i.value for i in result.inputs}
    if not result.courses:
        when = (_YEARS[language][int(inputs['year_level']) - 1] if inputs['semester'] == 'any'
                else _when(language, int(inputs['year_level']), inputs['semester']))
        return [text['empty'].format(when=when)]
    lines = []
    for (year, term), group in groupby(result.courses, key=lambda c: (c.year, c.term)):
        group = list(group)
        when = _when(language, year, term)
        heading = text['heading'].format(when=when, pages=prospectus(group))
        lines.append(heading[0].upper() + heading[1:] if text['capitalize'] else heading)
        lines.extend(_course(c, text) for c in group)
    return lines
