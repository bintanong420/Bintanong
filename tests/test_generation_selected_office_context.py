"""Selected office fragments never imply a complete application procedure."""
import pytest

from backend.bintanong_generation.required_context import _quote, _WORDS


@pytest.mark.parametrize('language,notice', [('en', 'not a complete application procedure'),
                                          ('taglish', 'Hindi pa kumpleto'), ('fil', 'Hindi pa kumpleto')])
def test_selected_application_office_fragments_disclose_their_incomplete_coverage(language, notice):
    record = dict(fields=[dict(name='application_form_office_context', value='Obtain fictional form at Office Z.',
                              source_blank=False),
                          dict(name='submission_office_context', value='Submit fictional form and the requirements above.',
                               source_blank=False)], source_limits=[])
    text = _quote(record, _WORDS[language])
    assert notice in text
    assert 'Obtain fictional form at Office Z.' in text
    assert 'Submit fictional form and the requirements above.' in text


def test_unrelated_office_fields_do_not_get_the_selected_application_notice():
    text = _quote(dict(fields=[dict(name='office', value='Office Z', source_blank=False)], source_limits=[]), _WORDS['en'])
    assert 'not a complete application procedure' not in text
