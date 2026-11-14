"""Year/semester mentions read deterministically from the student's own words."""
import importlib

import pytest


def parse(text):
    return importlib.import_module('backend.bintanong_routing.terms').parse_term(text)


@pytest.mark.parametrize('text,expected', [
    ('first year', (1, 'any')),
    ('1st yr 2nd sem', (1, 'second_semester')),
    ('second year, first semester', (2, 'first_semester')),
    ('Second Year First Sem', (2, 'first_semester')),
    ('unang taon', (1, 'any')),
    ('ikalawang taon, unang sem', (2, 'first_semester')),
    ('2nd sem ng 3rd year', (3, 'second_semester')),
    ('3rd year summer', (3, 'summer')),
    ('4th year midyear', (4, 'summer')),
    ('fifth year', (5, 'any')),
    ('first year 1st semester', (1, 'first_semester')),
    ('unang taon, ikalawang semestre', (1, 'second_semester')),
    ('ikatlong taon unang sem.', (3, 'first_semester')),
])
def test_year_and_semester_come_from_the_words_attached_to_them(text, expected):
    assert parse(text) == expected


@pytest.mark.parametrize('text', ['first sem', 'summer', 'CC 5', 'sixth year', 'year', '', 'first year third sem'])
def test_no_stated_year_is_not_guessed(text):
    assert parse(text) is None
