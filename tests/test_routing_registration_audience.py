"""Generic enrollment requirements do not establish a freshman-only audience."""
import json

import pytest

from backend.bintanong_routing.contracts import DocumentTopic
from backend.bintanong_routing.topic_selection import add_companions
from test_routing_contracts import proposal
from test_routing_router import FakeTransport, run, style_proposal


FRESHMAN = DocumentTopic(subject_id='handbook_registration', claims=('freshman requirements',),
                         source_items=('1. UNDERGRADUATE FRESHMAN',))
GENERAL = DocumentTopic(subject_id='charter_registration', claims=('registration service fields',),
                        source_labels=('REGISTRATION for old and new students',))
MENU = (FRESHMAN, GENERAL)


def reply(text, subject):
    value = proposal(text=text, route='RAG', mentions=[], operations=[], language='en')
    value['parts'][0].update(subject_id=subject.subject_id, requested_claims=list(subject.claims))
    return json.dumps(value)


@pytest.mark.parametrize('compiled', ['0', '1'])
def test_generic_enrollment_repairs_an_unstated_freshman_assumption(monkeypatch, compiled):
    monkeypatch.setenv('BINTANONG_ROUTER_COMPILE', compiled)
    text = 'What documents do I need to enroll next term?'
    model = FakeTransport(reply(text, FRESHMAN), reply(text, GENERAL), style_outputs=[json.dumps(
        style_proposal('en', english=[text]))] * 3)
    result = run(model, text=text, topics=MENU)
    assert result.attempts == 2 and result.diagnostic == 'validated'
    assert result.proposed.parts[0].subject_id == GENERAL.subject_id


def test_explicit_freshman_enrollment_keeps_its_scoped_source():
    text = 'I am an undergraduate freshman. What must I submit to enroll?'
    result = run(FakeTransport(reply(text, FRESHMAN), style_outputs=[json.dumps(
        style_proposal('en', english=[text]))] * 3), text=text, topics=MENU)
    assert result.attempts == 1 and result.proposed.parts[0].subject_id == FRESHMAN.subject_id


def test_generic_enrollment_offers_general_registration_beside_a_scoped_choice():
    assert add_companions((FRESHMAN,), MENU, 'Ano ang kailangan para mag-enroll?') == MENU
    assert add_companions((FRESHMAN,), MENU, 'What are the freshman requirements?') == (FRESHMAN,)


def test_a_repeated_unstated_freshman_choice_never_dispatches():
    text = 'What documents do I need for registration?'
    bad = reply(text, FRESHMAN)
    result = run(FakeTransport(bad, bad, style_outputs=[json.dumps(
        style_proposal('en', english=[text]))] * 3), text=text, topics=MENU)
    assert result.attempts == 2 and not result.decision.dispatchable


def test_negated_freshman_status_does_not_authorize_freshman_requirements():
    from backend.bintanong_routing.topic_selection import freshman_context
    assert not freshman_context('Hindi po ako freshman. Ano ang kailangan sa enrollment?')
    assert not freshman_context('I am not a freshman. What do I need?')
    assert freshman_context('Incoming first-year student: what must I submit?')


def test_a_foreign_registration_request_does_not_gain_a_general_registration_companion():
    foreign = DocumentTopic(subject_id='handbook_foreign_registration', claims=('foreign requirements',))
    assert add_companions((foreign,), (*MENU, foreign), 'What do foreign students need to enroll?') == (foreign,)
