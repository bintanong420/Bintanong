"""Selected office fragments never imply a complete application procedure."""
import pytest
import json

from backend.bintanong_generation.required_context import _quote, _WORDS
from backend.bintanong_generation.render import render_text
from test_generation_condition_connectives import pack_with, draft


@pytest.mark.parametrize('language,notice', [('en', 'not a complete application procedure'),
                                          ('taglish', 'Hindi pa kumpleto'), ('fil', 'Hindi pa kumpleto')])
def test_selected_application_office_fragments_disclose_their_incomplete_coverage(language, notice):
    record = dict(fields=[dict(name='application_form_office_context', value='Obtain fictional form at Office Z.',
                              source_blank=False),
                          dict(name='submission_office_context', value='Submit fictional form and the requirements above.',
                               source_blank=False)], source_limits=[])
    pack = pack_with(json.dumps(record), language=language)
    claim = draft(pack, _quote(record, _WORDS[language]))
    text = render_text(pack, claim.claims, 'answered')
    assert notice in text
    assert notice not in claim.claims[0].text
    assert 'Obtain fictional form at Office Z.' in text
    assert 'Submit fictional form and the requirements above.' in text


def test_unrelated_office_fields_do_not_get_the_selected_application_notice():
    text = _quote(dict(fields=[dict(name='office', value='Office Z', source_blank=False)], source_limits=[]), _WORDS['en'])
    assert 'not a complete application procedure' not in text


def test_uncited_office_fragments_do_not_add_a_notice_to_an_unrelated_answer():
    record = dict(fields=[dict(name=name, value='Fictional office context.', source_blank=False)
        for name in ('application_form_office_context', 'submission_office_context')], source_limits=[])
    pack = pack_with('Unrelated fictional rule.', json.dumps(record))
    claim = draft(pack, 'Unrelated fictional rule.')
    assert 'not a complete application procedure' not in render_text(pack, claim.claims, 'answered')


def test_fragment_notice_does_not_introduce_a_source_condition_disjunction():
    import json
    from backend.bintanong_generation.part_answers import disjunction_errors
    from test_generation_condition_connectives import pack_with, draft
    record = dict(fields=[dict(name='application_form_office_context', value='Obtain fictional form at Office Z.',
        source_blank=False), dict(name='submission_office_context', value='Submit fictional form.', source_blank=False)],
        source_limits=[])
    pack = pack_with(json.dumps(record))
    assert disjunction_errors(draft(pack, _quote(record, _WORDS['en'])), pack) == ()
