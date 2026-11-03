"""Task 1 (memory/eligibility plan): the host keeps only the course result the student's own words state.

Fictional course codes only; the shapes cover a number, a hyphenated lab suffix and an A/B pair."""
import pytest

from backend.bintanong_routing.claim_evidence import stated_result


def read(text, course, *others):
    """The state stated for `course` in `text` (the whole text is the claim); `others` are other course mentions."""
    start = text.index(course)
    spans = tuple((text.index(o), text.index(o) + len(o)) for o in others)
    return stated_result(text, (0, len(text)), (start, start + len(course)), spans)


@pytest.mark.parametrize('text,course,expected', [
    ('I passed ZZ 10', 'ZZ 10', 'passed'),
    ('Pasado na ako sa ZZ-2/L', 'ZZ-2/L', 'passed'),
    ('Naipasa ko na yung ZZ15-101A', 'ZZ15-101A', 'passed'),
    ('I already completed ZZ 10', 'ZZ 10', 'passed'),
    ('I failed ZZ 10', 'ZZ 10', 'failed'),
    ('Bumagsak ako sa ZZ-2/L', 'ZZ-2/L', 'failed'),
    ("I didn't pass ZZ 10", 'ZZ 10', 'failed'),
    ('Can I take ZZ 11 after failing ZZ 10?', 'ZZ 10', 'failed'),
    ("I haven't passed ZZ 10 yet", 'ZZ 10', 'not_passed'),
    ('Hindi ko pa napapasa ang ZZ-2/L', 'ZZ-2/L', 'not_passed'),
    ('di pa pasado sa ZZ 10', 'ZZ 10', 'not_passed'),
    ("I haven't taken ZZ 10 yet", 'ZZ 10', 'not_taken'),
    ('Hindi ko pa nakukuha ang ZZ15-101B', 'ZZ15-101B', 'not_taken'),
    ('I have never taken ZZ 10', 'ZZ 10', 'not_taken'),
    ('Natake ko na yung ZZ-2/L', 'ZZ-2/L', 'taken_unknown'),
    ('I took ZZ 10 last year', 'ZZ 10', 'taken_unknown'),
    ("I took ZZ 10 but I don't know if I passed", 'ZZ 10', 'taken_unknown'),
    ("I'm taking ZZ 10 this term", 'ZZ 10', 'enrolled'),
    ('Naka-enroll ako sa ZZ-2/L ngayon', 'ZZ-2/L', 'enrolled'),
    ("I'm not enrolled in ZZ 10", 'ZZ 10', 'not_enrolled'),
])
def test_each_stated_result_is_kept_as_said(text, course, expected):
    assert read(text, course) == expected


@pytest.mark.parametrize('text,course', [
    ('ZZ 10', 'ZZ 10'),                          # no statement at all
    ('I got 2.5 in ZZ 10', 'ZZ 10'),             # a bare number is not a pass or a failure
    ('INC ako sa ZZ-2/L', 'ZZ-2/L'),
    ('My friend passed ZZ 10', 'ZZ 10'),         # another person's result is not the speaker's
    ('Sabi ng kaibigan ko pasado siya sa ZZ 10', 'ZZ 10'),
])
def test_no_result_is_supplied_without_the_students_own_statement(text, course):
    assert read(text, course) is None


def test_one_verb_covers_every_course_it_governs():
    text = 'I failed ZZ 3 and ZZ 4'
    assert read(text, 'ZZ 3', 'ZZ 4') == read(text, 'ZZ 4', 'ZZ 3') == 'failed'


def test_negation_and_verb_bind_to_their_own_course():
    text = "I passed ZZ 3 but haven't taken ZZ 4"
    assert read(text, 'ZZ 3', 'ZZ 4') == 'passed'
    assert read(text, 'ZZ 4', 'ZZ 3') == 'not_taken'
    filipino = 'Pasado ako sa ZZ 3 pero hindi ko pa natatake ang ZZ 4'
    assert read(filipino, 'ZZ 3', 'ZZ 4') == 'passed'
    assert read(filipino, 'ZZ 4', 'ZZ 3') == 'not_taken'


def test_a_result_stated_after_the_course_in_its_own_clause_applies_to_it():
    assert read('Natake ko na ang ZZ 10 pero bagsak ako', 'ZZ 10') == 'failed'
    assert read('I took ZZ 10 and passed', 'ZZ 10') == 'passed'


def test_a_completion_and_an_enrollment_of_the_same_course_are_read_separately():
    text = 'Hindi ko pa napapasa ang ZZ 12, pero naka-enroll ako sa ZZ 12 this term'
    first = text.index('ZZ 12')
    second = text.index('ZZ 12', first + 1)
    assert stated_result(text, (0, len(text)), (first, first + 5), ((second, second + 5),)) == 'not_passed'
    assert stated_result(text, (0, len(text)), (second, second + 5), ((first, first + 5),)) == 'enrolled'
