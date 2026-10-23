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
