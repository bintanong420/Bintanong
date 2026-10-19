"""Literal style provenance and wire adaptation, not a host language classifier."""
import importlib
from itertools import product

import pytest

from test_routing_contracts import proposal


def api():
    return importlib.import_module('backend.bintanong_routing.style')


def evidence(name='taglish', english=('request',), filipino=('Paano',)):
    return dict(english_fragments=list(english), filipino_fragments=list(filipino),
                preferred_response_style=name)


def wire(style=None, **updates):
    value = dict(schema_version='bintanong-response-style-v1',
                 style=evidence() if style is None else style)
    value.update(updates)
    return value


@pytest.mark.parametrize('name,english,filipino', list(product(
    ['english_only', 'filipino', 'taglish', 'unknown'], [(), ('Hi',)], [(), ('kumusta',)])))
def test_style_schema_and_python_agree_on_evidence_combinations(name, english, filipino):
    jsonschema = pytest.importorskip('jsonschema')
    wanted = {'english_only':(True,False), 'filipino':(False,True),
              'taglish':(True,True), 'unknown':(False,False)}[name]
    valid = (bool(english), bool(filipino)) == wanted
    data = wire(evidence(name, english, filipino))
    schema = api().style_output_schema()
    assert jsonschema.Draft202012Validator(schema).is_valid(data) is valid
    if valid:
        style = api().StyleProposal.parse(data).style
        assert style.language == {'english_only':'en','filipino':'fil',
            'taglish':'taglish','unknown':'unknown'}[name]
        assert style.preferred_response_style == name
    else:
        with pytest.raises(ValueError):
            api().StyleProposal.parse(data)


@pytest.mark.parametrize('text,fragment,valid', [
    ('Paano ako mag-request?', 'request', True),
    ('Hi, Hi, kumusta?', 'Hi', True),
    ('Hi', 'hi', False),
    ('Hi', ' Hi ', False),
    ('Cafe\u0301', 'Café', False),
    ('Hello', 'invented', False),
])
def test_style_grounding_uses_original_literal_text(text, fragment, valid):
    style = api().StyleEvidence.parse(evidence('english_only', (fragment,), ()))
    if valid:
        style.ground(text)
    else:
        with pytest.raises(ValueError, match='ungrounded_response_style'):
            style.ground(text)


@pytest.mark.parametrize('english', [[' '], ['x'*161], ['Hi']*5, [True]])
def test_style_fragments_are_bounded_nonblank_strings(english):
    with pytest.raises(ValueError):
        api().StyleEvidence.parse(evidence('english_only', english, ()))


def test_style_proposal_is_independent_of_routes_and_student_facts():
    value = wire()
    parsed = api().StyleProposal.parse(value)
    parsed.style.ground('Paano ako mag-request?')
    assert parsed.style.language == 'taglish'
    assert parsed.style.english_fragments == ('request',)
    for extra in [dict(route='Symbolic'), dict(claims=[]), dict(operations=[])]:
        with pytest.raises(ValueError):
            api().StyleProposal.parse(dict(value, **extra))


@pytest.mark.parametrize('value', [proposal(), wire(language='en'), wire(extra='ignored'),
    wire(style=dict(evidence(), extra='ignored'))])
def test_legacy_extra_and_conflicting_wire_fields_cannot_bypass_style(value):
    with pytest.raises(ValueError):
        api().StyleProposal.parse(value)


def test_style_schema_is_versioned_and_cannot_accept_a_routing_proposal():
    jsonschema = pytest.importorskip('jsonschema')
    schema = api().style_output_schema()
    assert schema['properties']['schema_version']['const'] == 'bintanong-response-style-v1'
    assert not jsonschema.Draft202012Validator(schema).is_valid(proposal())
    assert set(schema['properties']) == {'schema_version', 'style'}
