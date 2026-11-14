"""Unplaced candidate courses must not invent term labels or break JSON export."""
import copy
import json

import pytest

from backend.bintanong_tools.prospectus_extractor.views import build_curriculum_by_term


@pytest.mark.parametrize('unplaced', [
    {'course_code': 'SYN-201', 'year_level': None, 'semester': 'Second Semester', 'term_index': 99},
    {'course_code': 'SYN-202', 'year_level': 'First Year', 'semester': None, 'term_index': 99},
])
def test_unplaced_course_keeps_unknown_fields_without_corrupting_term_tree(unplaced):
    placed = {'course_code': 'SYN-101', 'year_level': 'First Year',
              'semester': 'First Semester', 'term_index': 1}
    courses = [unplaced, placed]
    before = copy.deepcopy(courses)

    tree = build_curriculum_by_term(courses)
    exported = json.loads(json.dumps({'courses': courses, 'curriculum_by_term': tree}, sort_keys=True))

    assert exported['curriculum_by_term'] == {'First Year': {'First Semester': [placed]}}
    assert exported['courses'] == before
    assert courses == before
