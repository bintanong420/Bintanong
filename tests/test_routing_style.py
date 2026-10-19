"""Literal style provenance and wire adaptation, not a host language classifier."""
import importlib
from itertools import product

import pytest

from backend.bintanong_routing.contracts import Interpretation
from test_routing_contracts import proposal


def api():
    return importlib.import_module('backend.bintanong_routing.style')


def evidence(name='taglish', english=('request',), filipino=('Paano',)):
    return dict(english_fragments=list(english), filipino_fragments=list(filipino),
                preferred_response_style=name)


def wire(style=None, **updates):
    value = proposal(mentions=[], operations=[], route='RAG')
    value.pop('language')
    value.update(schema_version='bintanong-router-proposal-v2',
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
    schema = api().model_schema(Interpretation.model_json_schema())
    assert jsonschema.Draft202012Validator(schema).is_valid(data) is valid
    if valid:
        canonical, style = api().decode_model_proposal(data)
        assert canonical.language == {'english_only':'en','filipino':'fil',
            'taglish':'taglish','unknown':'unknown'}[name]
        assert style.preferred_response_style == name
    else:
        with pytest.raises(ValueError):
            api().decode_model_proposal(data)


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


def test_wire_decode_is_lossless_for_routing_and_keeps_style_separate_from_facts():
    value = wire()
    canonical, style = api().decode_model_proposal(value)
    style.ground('Paano ako mag-request?')
    assert canonical.route == 'RAG' and canonical.language == 'taglish'
    assert canonical.claims == () and canonical.operations == () and canonical.mentions == ()
    assert style.english_fragments == ('request',)
    assert 'style' in value and 'language' not in value  # caller's proposal untouched
    assert canonical.schema_version == 'bintanong-interpretation-v1'


@pytest.mark.parametrize('value', [proposal(), wire(language='en'), wire(extra='ignored'),
    wire(style=dict(evidence(), extra='ignored'))])
def test_legacy_extra_and_conflicting_wire_fields_cannot_bypass_style(value):
    with pytest.raises(ValueError):
        api().decode_model_proposal(value)


def test_model_schema_preserves_canonical_schema_and_uses_shared_style_definition():
    base = Interpretation.model_json_schema()
    schema = api().model_schema(base)
    assert 'language' in base['properties'] and 'style' not in base['properties']
    assert schema['properties']['style'] == {'$ref':'#/$defs/ResponseStyleEvidence'}
    assert schema['properties']['schema_version']['const'] == 'bintanong-router-proposal-v2'
