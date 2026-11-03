"""The course result a student's own words state (memory/eligibility plan, Task 1).

The model proposes claims; the host keeps only a state the claim's own clause supports, so a proposed `passed`
needs pass words and a negated course is never a pass. English, Filipino and Taglish. Anything else (a bare
number, INC, another person's result, an unclear statement) supplies no result, and the check asks instead.
"""
from __future__ import annotations

import re

from ..bintanong_contracts.runtime import folded

# Clause boundaries. "and"/"at" also join courses governed by one verb ("failed A and B"); a clause without its
# own result word inherits the previous clause's word, so both readings work.
_BOUNDARY = re.compile(r",|;|\.|\b(?:but|pero|tapos|kaso|however|though|although|while|and|at|saka)\b")


def _words(*items):
    return re.compile(r'(?<![\w-])(?:' + '|'.join(items) + r')(?![\w-])')


_UNSURE = _words(r"(?:do not|don't|dont) know", r'not sure', r'(?:hindi|di) ko (?:pa )?(?:alam|sure)', 'ewan')
_FAIL = _words('failed', 'fail', 'failing', 'flunked', 'flunk', 'bagsak', 'bumagsak', 'binagsak', 'ibinagsak', 'nabagsak',
               r'(?:did not|didn\'t|didnt) pass', r'(?:hindi|di) (?:ako )?(?:pumasa|nakapasa)')
_PASS = _words(r'pass(?:ed)?', 'pasado', 'pumasa', 'nakapasa', 'napasa', 'naipasa', 'napapasa', 'naipapasa',
               'nakakapasa', r'complet(?:ed|e)', r'finish(?:ed)?', 'natapos', r'tapos na')
_ENROLL = _words(r'enroll(?:ed|ing)?', r'naka-?enroll', r'currently taking', 'taking', 'kinukuha',
                 r'nag-?ta-?take', 'tinitake')
_TAKE = _words(r'take[n]?', 'took', 'natake', 'natatake', 'nakuha', 'nakukuha', 'kinuha', 'kumuha',
               r'nag-?take', r'i-?take')
_NEGATION = _words('not', r"\w+n't", 'never', 'no', 'hindi', 'di', 'wala', 'hnd', 'nope')
_YET = _words('yet', 'pa')
_OTHER_PERSON = _words('friend', 'friends', 'classmate', 'blockmate', 'he', 'she', 'they', 'kaibigan', 'kaklase',
                       'siya', 'sila', 'kuya', 'ate', 'tropa')


def clause_reading(clause: str) -> str | None:
    """One clause's stated result, or 'other_person'/'unsure', or None."""
    text = folded(clause).replace('’', "'")
    if _OTHER_PERSON.search(text):
        return 'other_person'
    negated = bool(_NEGATION.search(text))
    if _UNSURE.search(text):
        return 'taken_unknown' if (_TAKE.search(text) or _PASS.search(text)) else 'unsure'
    if _PASS.search(text) and negated and _YET.search(text):
        return 'not_passed'
    if _FAIL.search(text):
        return 'failed'
    if _PASS.search(text):
        return 'not_passed' if negated else 'passed'
    if _ENROLL.search(text):
        return 'not_enrolled' if negated else 'enrolled'
    if _TAKE.search(text):
        return 'not_taken' if negated else 'taken_unknown'
    return None


_KNOWN = ('passed', 'failed', 'not_passed', 'not_taken', 'enrolled', 'not_enrolled')


def stated_result(text: str, claim: tuple[int, int], course: tuple[int, int],
                  other_courses: tuple[tuple[int, int], ...] = ()) -> str | None:
    """The state the student states about the course at `course` within the claim span, or None."""
    start, end = claim
    cuts = [start, *(m.start() + start for m in _BOUNDARY.finditer(text[start:end])), end]
    clauses = [(a, b) for a, b in zip(cuts, cuts[1:]) if b > a]
    index = next(i for i, (a, b) in enumerate(clauses) if a <= course[0] < b or b == end)

    def names_course(a, b):
        return any(a <= s < b for s, _ in other_courses) or a <= course[0] < b

    readings = [clause_reading(text[a:b]) for a, b in clauses]
    own = readings[index]
    # A later clause naming no other course states this course's result ("I took A and passed").
    later = []
    for (a, b), reading in zip(clauses[index + 1:], readings[index + 1:]):
        if names_course(a, b):
            break
        later.append(reading)
    found = [r for r in (own, *later) if r is not None]
    if any(r in ('other_person', 'unsure') for r in found):
        return 'taken_unknown' if 'taken_unknown' in found else None
    decisive = [r for r in found if r in _KNOWN]
    if decisive:
        return decisive[-1] if own in (None, 'taken_unknown') else own if own in _KNOWN else decisive[0]
    if found:
        return found[0]
    # A clause that only names the course takes the verb of the clause that governs it ("failed A and B").
    for reading in reversed(readings[:index]):
        if reading is not None:
            return None if reading in ('other_person', 'unsure') else reading
    return None


_NEXT_TERM = re.compile(r'(?<![\w-])(?:next|susunod na|upcoming) (?:sem|semester|term|trimester)(?![\w-])')


def enrollment_period(text: str) -> str:
    """The term an enrollment statement covers: 'next' only when it says so, otherwise the current term."""
    return 'next' if _NEXT_TERM.search(folded(text)) else 'current'


_IF = re.compile(r'(?<![\w-])(?:if|what if|kung|kapag|pag|assuming|suppose|supposing|halimbawa)(?![\w-])')


def inside_if_clause(text: str, course_start: int) -> bool:
    """True when the course is stated inside an "if/kung/kapag" clause of its own sentence: a premise for this check,
    never a report to remember (memory/eligibility plan, Example A)."""
    sentence = max(text.rfind(mark, 0, course_start) for mark in '.?!') + 1
    return bool(_IF.search(folded(text[sentence:course_start])))
