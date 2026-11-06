"""A named deficiency gets its reviewed method and shared approvals, not another mark's procedure."""
import json

import pytest

from backend.bintanong_routing.contracts import DocumentTopic
from test_routing_contracts import proposal
from test_routing_router import FakeTransport, run, style_proposal


TOPIC = DocumentTopic(subject_id='grade_completion',
    claims=('printed timing', 'fictional INC method', 'fictional shared approval', 'fictional four method context'),
    claim_headings={
        'fictional INC method': ('9.2 REMOVAL OF “INC”',),
        'fictional shared approval': ('9.3 EXAMINATION FOR REMOVAL OR COMPLETION',
                                    '9.4 FORFEITURE OF RIGHT TO REMOVE OR COMPLETE'),
        'fictional four method context': ('9.5 REMOVAL OF ‘4’', '9.6 NO IMPROVEMENT OF GRADE')},
    not_stated=('deadline precedence',))


@pytest.mark.parametrize('question, expected', [
    ('How do I complete an INC grade?', ('fictional INC method', 'fictional shared approval')),
    ('How do I remove a grade of 4?', ('fictional shared approval', 'fictional four method context')),
])
def test_requested_mark_uses_its_own_printed_method_and_shared_approval(question, expected):
    value = proposal(text=question, route='RAG', mentions=[], operations=[], language='en')
    value['parts'][0].update(subject_id=TOPIC.subject_id, requested_claims=['printed timing'], detail='whole')
    style = json.dumps(style_proposal('en', english=[question]))
    result = run(FakeTransport(json.dumps(value), style_outputs=[style] * 3), text=question, topics=(TOPIC,))
    assert result.proposed.parts[0].requested_claims == expected


def test_a_timing_detail_keeps_the_selected_reviewed_timing_claim():
    question = 'When is the deadline for the INC grade?'
    value = proposal(text=question, route='RAG', mentions=[], operations=[], language='en')
    value['parts'][0].update(subject_id=TOPIC.subject_id, requested_claims=['printed timing'], detail='processing_time')
    style = json.dumps(style_proposal('en', english=[question]))
    result = run(FakeTransport(json.dumps(value), style_outputs=[style] * 3), text=question, topics=(TOPIC,))
    assert result.proposed.parts[0].requested_claims == ('printed timing',)


@pytest.mark.parametrize('question', ['How do I complete INC and remove grade 4?',
                                    'How do I remove 4 units?'])
def test_mixed_marks_or_unrelated_units_do_not_choose_a_single_mark_method(question):
    value = proposal(text=question, route='RAG', mentions=[], operations=[], language='en')
    value['parts'][0].update(subject_id=TOPIC.subject_id, requested_claims=list(TOPIC.claims), detail='whole')
    style = json.dumps(style_proposal('en', english=[question]))
    result = run(FakeTransport(json.dumps(value), style_outputs=[style] * 3), text=question, topics=(TOPIC,))
    assert result.proposed.parts[0].requested_claims == TOPIC.claims


def test_without_reviewed_headings_the_existing_whole_procedure_fallback_stays_available():
    question = 'How do I complete an INC grade?'
    topic = TOPIC.model_copy(update=dict(claim_headings={}))
    value = proposal(text=question, route='RAG', mentions=[], operations=[], language='en')
    value['parts'][0].update(subject_id=topic.subject_id, requested_claims=['printed timing'], detail='whole')
    style = json.dumps(style_proposal('en', english=[question]))
    result = run(FakeTransport(json.dumps(value), style_outputs=[style] * 3), text=question, topics=(topic,))
    assert result.proposed.parts[0].requested_claims == topic.claims
