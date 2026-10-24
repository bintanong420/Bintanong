"""Read a year level and semester from the words a student used ("2nd yr first sem", "unang taon").

The year is the ordinal attached to year/yr/taon and the semester the ordinal attached to sem/semester;
nothing is assumed when the year is not stated.
"""
import re

_ORDINALS = {
    1: r'first|1st|unang|una',
    2: r'second|2nd|ikalawang|ikalawa|pangalawang|pangalawa',
    3: r'third|3rd|ikatlong|ikatlo|pangatlong|pangatlo',
    4: r'fourth|4th|ikaapat|ika-apat|pang-apat',
    5: r'fifth|5th|ikalimang|ikalima|panlimang|panlima',
}
_ORDINAL = '|'.join(f'(?P<o{n}>{words})' for n, words in _ORDINALS.items())
_YEAR = re.compile(rf'\b(?:{_ORDINAL})(?:\s+na)?\s+(?:year|yr|taon)\b', re.I)
_SEMESTER = re.compile(rf'\b(?:{_ORDINAL})\s+sem(?:ester|estre)?\b', re.I)
_SUMMER = re.compile(r'\b(?:summer|mid-?year)\b', re.I)


def _ordinal(match) -> int:
    return next(n for n in _ORDINALS if match.group(f'o{n}'))


def parse_term(text: str) -> tuple[int, str] | None:
    year = _YEAR.search(text)
    if year is None:
        return None
    semester = _SEMESTER.search(text)
    if semester is None:
        return _ordinal(year), 'summer' if _SUMMER.search(text) else 'any'
    terms = {1: 'first_semester', 2: 'second_semester'}
    return (_ordinal(year), terms[_ordinal(semester)]) if _ordinal(semester) in terms else None
