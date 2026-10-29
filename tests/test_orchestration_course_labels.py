"""Answers carry printed-code labels only for the courses they mention (fictional data).

A multi-curriculum release holds hundreds of course labels; the result keeps the referenced ones.
"""
from backend.bintanong_orchestration.orchestrator import referenced_labels


def test_only_labels_of_referenced_courses_are_kept_from_a_large_release():
    labels = tuple((f'course-{i:03d}', f'ZZ {i}') for i in range(600))
    evidence = {'decision': {'violated_conditions': ['not_completed:course-007']}, 'inputs': [{'value': 'course-123'}]}
    kept = referenced_labels(labels, evidence, ('completion_unknown:course-450',))
    assert kept == {'course-007': 'ZZ 7', 'course-123': 'ZZ 123', 'course-450': 'ZZ 450'}


def test_an_id_that_only_prefixes_another_is_not_matched():
    labels = (('course-1', 'ZZ 1'), ('course-12', 'ZZ 12'))
    assert referenced_labels(labels, {'x': 'course-12'}) == {'course-12': 'ZZ 12'}


def test_a_course_choice_is_labelled_with_its_printed_details():
    # Owner, 29 Oct 2026: "Did you mean A or B?" shows each choice's printed title, year/semester and units.
    from backend.bintanong_orchestration.orchestrator import choice_labels
    details = (('course-a', 'ZZ 1 — Fictional Ethics (Third Year, First Semester; 3 units)'), ('course-b', 'ZZ 2 — x'))
    missing = ('course_choice:course-a', 'completion_unknown:course-b')
    assert choice_labels(details, missing) == {'course-a': 'ZZ 1 — Fictional Ethics (Third Year, First Semester; 3 units)'}
