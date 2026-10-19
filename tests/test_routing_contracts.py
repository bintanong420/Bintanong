"""Generic synthetic language/request boundaries, not institutional policy."""
import importlib

import pytest


def api():
    return importlib.import_module('backend.bintanong_routing.contracts')


def proposal(**updates):
    value = dict(schema_version='bintanong-interpretation-v1', language='taglish',
                 audience='undergraduate', intent='prerequisite_check',
                 mentions=[dict(kind='course', text='A1', start=0, end=2)],
                 claims=[], operations=[dict(name='check_prerequisite_eligibility', target=0)],
                 route='Symbolic', control=None, ambiguities=[], reason='Check prerequisites.')
    value.update(updates)
    return value


def context(**updates):
    value = dict(session_id='sess-a', request_id='req-a', program_id='program-a',
                 curriculum_id='curriculum-a', facts=[])
    value.update(updates)
    return value


def test_minimal_normalization_preserves_decisive_words_and_numbers():
    original = '  Hindi\tpa passed ang A1 next sem. Grade: 2.00.\n'
    assert api().prepare_query(original) == 'Hindi pa passed ang A1 next sem. Grade: 2.00.'
    assert api().prepare_query('Cafe\u0301 A1') == 'Café A1'


@pytest.mark.parametrize('text', ['', ' \n ', '\ud800', 'a\x00b', 'a\u200bb',
                                  'x' * 8193, '漢' * 6000, b'hello', None],
                         ids=['empty','whitespace','surrogate','nul','format',
                              'characters','utf8-bytes','bytes','none'])
def test_invalid_or_oversized_query_is_rejected(text):
    with pytest.raises(ValueError):
        api().prepare_query(text)


def test_strict_interpretation_preserves_language_and_proposal_without_execution():
    result = api().Interpretation.parse(proposal())
    assert result.language == 'taglish' and result.operations[0].target == 0
    assert result.route == 'Symbolic'
    with pytest.raises(ValueError):
        result.language = 'en'


@pytest.mark.parametrize('update', [dict(route='Direct'), dict(extra='ignored'),
    dict(route='RAG', control='greeting'), dict(route=None, control=None),
    dict(language='English'), dict(operations=[dict(name='op', target=True)]),
    dict(operations=[dict(name='op', target=1)]),
    dict(mentions=[dict(kind='course', text='A1', start=0, end=1)]),
    dict(claims=[dict(entity=2, state='passed', mode='asserted',
                     text='passed', start=0, end=6)])])
def test_invalid_interpretation_cannot_pass_schema(update):
    with pytest.raises(ValueError):
        api().Interpretation.parse(proposal(**update))


def test_session_context_rejects_foreign_and_duplicate_fact_ids():
    fact = dict(fact_id='fact-a', session_id='sess-a', course_id='course-a',
                program_id='program-a', curriculum_id='curriculum-a', state='failed')
    assert api().RequestContext.parse(context(facts=[fact])).facts[0].state == 'failed'
    for facts in [[dict(fact, session_id='sess-b')], [fact, fact],
                  [dict(fact, curriculum_id='curriculum-b')]]:
        with pytest.raises(ValueError):
            api().RequestContext.parse(context(facts=facts))


def test_catalog_requires_review_scope_and_nonempty_aliases():
    value = dict(kind='course', entity_id='course-a', program_id='program-a',
                 curriculum_id='curriculum-a', aliases=['A1'], source_ref='ver-a',
                 review_ref='review-a', reviewed=True)
    assert api().CatalogEntry.parse(value).aliases == ('A1',)
    for update in [dict(reviewed=False), dict(aliases=[]), dict(curriculum_id=None),
                   dict(source_ref='fact-private'), dict(review_ref='')]:
        with pytest.raises(ValueError):
            api().CatalogEntry.parse(dict(value, **update))
