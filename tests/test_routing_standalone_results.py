"""Standalone self-reports use scoped chat memory, never institutional records."""
import asyncio
import json

import pytest

from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_routing.router import Router
from routing_wire_fixtures import wire_fixture
from test_routing_contracts import context, proposal
from test_routing_router import FakeTransport, style_proposal
from test_routing_validation import catalog, registry


def statement(text='I passed A1.', *, kind='structured', language='en', reported=False):
    code = 'A1.' if language == 'en' else 'A1'
    start = text.index(code)
    value = proposal(text=text, language=language, route='RAG', operations=[],
        mentions=[dict(kind='course', text=code, start=start, end=start + len(code))],
        claims=[dict(entity=0, text=text, start=0, end=len(text), state='passed',
                     mode='reported' if reported else 'asserted')],
        parts=[dict(part_id='r1', text=text, start=0, end=len(text), evidence_need=kind, operation_indices=[])])
    wire = wire_fixture(value, text)
    if language == 'fil':  # recorded cx-statement-fil: omitted mention plus zero/unknown placeholder
        wire.update(part_count=0, mentions=[])
    return wire


def route_statement(text='I passed A1.', **options):
    wire = statement(text, **options)
    language = options.get('language', 'en')
    style = style_proposal(language, english=[text] if language == 'en' else [],
                           filipino=[text] if language == 'fil' else [])
    transport = FakeTransport(json.dumps(wire), json.dumps(wire), style_outputs=[json.dumps(style)])
    router = Router(transport, catalog=catalog(), registry=registry(), documents_available=True, synthetic=True)
    return asyncio.run(router.route(text, RequestContext.parse(context())))


@pytest.mark.parametrize('text,options', [
    ('I passed A1.', {}),
    ('Pasado na ako sa A1.', dict(kind='unknown', language='fil')),
])
def test_recorded_statement_shapes_acknowledge_the_grounded_fact(text, options):
    result = route_statement(text, **options)
    assert result.diagnostic == 'facts_noted'
    assert result.decision.missing_facts == ('noted_passed:course-a',)
    assert [(c.course_id, c.state) for c in result.claims] == [('course-a', 'passed')]


@pytest.mark.parametrize('text,reported', [('My friend passed A1.', True), ('My friend passed A1.', False),
                                         ('If I passed A1.', False)])
def test_another_person_or_a_hypothesis_is_never_acknowledged_as_my_result(text, reported):
    result = route_statement(text, reported=reported)
    assert result.diagnostic != 'facts_noted'
    assert not any(c.mode == 'asserted' for c in result.claims)


def test_a_reviewed_alias_ending_in_punctuation_keeps_its_exact_identity():
    from backend.bintanong_routing.wire import WireInterpretation, normalize_interpretation
    result = normalize_interpretation('I passed A1.', WireInterpretation.parse(statement()),
                                      course_names=frozenset({'a1', 'a1.'}))
    assert result.mentions[0].text == 'A1.'


def test_separately_quoted_results_with_a_joining_word_are_both_noted():
    from test_routing_validation import validate
    text = 'I passed A1 and I failed B1.'
    value = proposal(text=text, mentions=[dict(kind='course', text='A1', start=9, end=11),
        dict(kind='course', text='B1', start=25, end=27)], operations=[], route='RAG',
        claims=[dict(entity=0, state='passed', mode='asserted', text='I passed A1', start=0, end=11),
                dict(entity=1, state='failed', mode='asserted', text='I failed B1', start=16, end=27)],
        parts=[dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='structured', operation_indices=[])])
    result = validate(text, value)
    assert result.diagnostic == 'facts_noted'
    assert result.decision.missing_facts == ('noted_passed:course-a', 'noted_failed:course-b')
