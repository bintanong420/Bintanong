"""Ask mode routing (owner, 4 Nov 2026). Owner GUI test: "Anong subs ang affected if I fail CC4/L tapos paano ko sya
maresolve?" was read as a dependency part (operation index miscounted as 1) plus a document part with no reviewed
topic, and the whole message ended "temporarily unavailable". A recovery cue after a failed course is one recovery
request; and a document part with no topic never sinks an answerable structured part (it is named as unavailable).
Synthetic codes only."""
import asyncio
import json

import pytest

from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
from backend.bintanong_routing.contracts import DocumentTopic, RequestContext
from backend.bintanong_routing.recovery_cue import asks_recovery
from backend.bintanong_routing.router import Router
from test_routing_router import FakeTransport, style_proposal
from test_routing_validation import catalog

TOPIC = DocumentTopic(subject_id='fictional_policy', claims=('printed Form Q policy',))
REGISTRY = CapabilityRegistry({op: Capability('synthetic_' + op, ('curriculum_id', 'course_id')) for op in
                               ('list_affected_courses', 'check_prerequisite_eligibility')})


def quote(text, n=0):
    return dict(text=text, occurrence=n)


def wire(text, parts, *, operations, claims=(), control=None, route='Hybrid', mentions=('A1',)):
    return dict(schema_version='bintanong-interpretation-wire-v4', language='taglish', audience='undergraduate',
                control=control, part_count=len(parts), parts=list(parts), intent='affected courses and next steps',
                mentions=[dict(kind='course', quote=quote(m)) for m in mentions], claims=list(claims),
                operations=list(operations), route=None if control else route, ambiguities=[])


def part(part_id, words, need, indices=()):
    return dict(part_id=part_id, quote=quote(words), evidence_need=need, operation_indices=list(indices),
                subject_id=None, requested_claims=[], detail='whole')


def route(text, value):
    transport = FakeTransport(json.dumps(value), style_outputs=[json.dumps(style_proposal('taglish', english=['A1'],
                                                                                          filipino=[text.split()[0]]))])
    router = Router(transport, catalog=catalog(), registry=REGISTRY, documents_available=True, synthetic=True,
                    topics=(TOPIC,))
    return asyncio.run(router.route(text, RequestContext.parse(dict(
        session_id='sess-a', request_id='req-a', program_id='program-a', curriculum_id='curriculum-a', facts=[]))))


AFFECTED = 'Anong subs ang affected if I fail A1'


def test_the_recorded_gui_shape_becomes_one_recovery_request():
    text = AFFECTED + ' tapos paano ko sya maresolve?'
    value = wire(text, [part('r1', AFFECTED, 'structured', [1]), part('r2', 'tapos paano ko sya maresolve?', 'document')],
                 operations=[dict(name='list_affected_courses', target=quote('A1'))])
    result = route(text, value)
    assert result.diagnostic == 'validated' and result.decision.route == 'Symbolic'
    assert result.decision.predicate_request.predicate == 'list_affected_courses'
    assert {i.name: i.value for i in result.decision.predicate_request.inputs}['course_id'] == 'course-a'
    assert [p.evidence_need for p in result.proposed.parts] == ['structured']
    assert result.unavailable_parts == ()


def test_a_clarify_with_a_stated_failure_and_a_what_can_i_take_question_reaches_the_dependency_check():
    text = 'Hala, bagsak ako sa A1, paano na yung major subs ko? Ano pwede ko itake para maging regular load ako agad?'
    value = wire(text, [part('r1', text, 'unknown')], operations=[], control='clarify',
                 claims=[dict(quote=quote('bagsak ako sa A1'), entity=quote('A1'), state='failed', mode='asserted')])
    result = route(text, value)
    assert result.diagnostic == 'validated' and result.decision.route == 'Symbolic'
    assert result.decision.predicate_request.predicate == 'list_affected_courses'
    assert [c.state for c in result.claims] == ['failed']


def test_a_term_check_beside_the_failed_course_is_folded_into_the_recovery_request():
    text = 'Bagsak ako sa A1. Ano pwede ko itake sa second year second sem? Options ko?'
    value = wire(text, [part('r1', 'Bagsak ako sa A1.', 'structured', [0]),
                        part('r2', 'Ano pwede ko itake sa second year second sem?', 'structured', [1])],
                 operations=[dict(name='list_affected_courses', target=quote('A1')),
                             dict(name='assess_term_prerequisites', target=quote('second year second sem'))],
                 claims=[dict(quote=quote('Bagsak ako sa A1'), entity=quote('A1'), state='failed', mode='asserted')],
                 route='Symbolic', mentions=('A1',))
    value['mentions'].append(dict(kind='term', quote=quote('second year second sem')))
    result = route(text, value)
    assert result.diagnostic == 'validated'
    assert [o.name for o in result.proposed.operations] == ['list_affected_courses']


def test_a_question_about_another_named_course_is_not_rewritten():
    text = 'Bagsak ako sa A1, pwede ko itake ang B1?'
    value = wire(text, [part('r1', text, 'structured', [0])], route='Symbolic', mentions=('A1', 'B1'),
                 operations=[dict(name='check_prerequisite_eligibility', target=quote('B1'))],
                 claims=[dict(quote=quote('Bagsak ako sa A1'), entity=quote('A1'), state='failed', mode='asserted')])
    result = route(text, value)
    assert [o.name for o in result.proposed.operations] == ['check_prerequisite_eligibility']


def test_a_document_part_with_no_topic_is_named_unavailable_and_the_structured_part_still_answers():
    text = AFFECTED + ' tapos saan ang office ng dean?'
    value = wire(text, [part('r1', AFFECTED, 'structured', [0]), part('r2', 'tapos saan ang office ng dean?', 'document')],
                 operations=[dict(name='list_affected_courses', target=quote('A1'))])
    result = route(text, value)
    assert result.diagnostic == 'validated' and result.decision.route == 'Symbolic'
    assert [p.text for p in result.proposed.parts] == [AFFECTED]
    assert result.unavailable_parts == ('tapos saan ang office ng dean?',)


@pytest.mark.parametrize('text', [
    'Ano pwede options ko?', 'paano ko sya maresolve?', 'How do I recover from this?', 'what can I take next?',
    'para maging regular load ako', 'paano na yung major subs ko', 'paano ko mabawi', 'Ano ang gagawin ko?'])
def test_recovery_cues(text):
    assert asks_recovery(text)


@pytest.mark.parametrize('text', [
    'What courses are blocked if I fail A1?', "What can't I take if I fail A1?", 'Paano kung bagsak ako sa A1?',
    'Kung bagsak ako sa A1, ano ang hindi ko ma-take?', 'Anong subs ang affected if I fail A1'])
def test_plain_dependency_questions_have_no_recovery_cue(text):
    assert not asks_recovery(text)
