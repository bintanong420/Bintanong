"""Compiled routing preserves the existing distinction between policy and a term check."""
import json

import pytest

from routing_wire_fixtures import wire_fixture
from test_routing_contracts import proposal
from test_routing_topic_selection import Transport, run, selected


@pytest.mark.parametrize('compiled', [False, True])
def test_topic_backed_generic_check_does_not_invent_a_term(monkeypatch, compiled):
    monkeypatch.setenv('BINTANONG_ROUTER_COMPILE', '1' if compiled else '0')
    text = 'Does the university allow concurrent requirements?'
    wrong = wire_fixture(proposal(text=text, mentions=[dict(kind='term', text=text, start=0, end=len(text))],
        operations=[dict(name='assess_term_prerequisites', target=0)]), text)
    wrong['mentions'] = []
    wrong['parts'][0].update(subject_id='fictional_office', requested_claims=['filing office'])
    result, _ = run(Transport(selected(), json.dumps(wrong), text=text), text=text)
    assert result.diagnostic == 'validated' and result.decision.route == 'RAG'
    assert result.attempts == 1
    assert not result.proposed.operations and not result.proposed.mentions


@pytest.mark.parametrize('compiled', [False, True])
def test_an_explicit_term_target_still_requires_the_missing_year(monkeypatch, compiled):
    monkeypatch.setenv('BINTANONG_ROUTER_COMPILE', '1' if compiled else '0')
    text = 'Which subjects can I take next semester?'
    value = wire_fixture(proposal(text=text,
        mentions=[dict(kind='term', text='next semester', start=text.index('next semester'), end=len(text)-1)],
        operations=[dict(name='assess_term_prerequisites', target=0)]), text)
    value['parts'][0].update(subject_id='fictional_office', requested_claims=['filing office'])
    result, _ = run(Transport(selected(), json.dumps(value), text=text), text=text)
    assert result.decision.control == 'clarify' and result.diagnostic == 'missing_term'
