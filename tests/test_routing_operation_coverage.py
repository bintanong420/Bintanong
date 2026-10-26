"""An orphan model operation gets the existing repair budget, never silent rerouting."""
import asyncio
from copy import deepcopy
import json

import pytest

from backend.bintanong_routing.contracts import DocumentTopic, RequestContext
from backend.bintanong_routing.router import Router
from backend.bintanong_routing.wire import WireInterpretation, normalize_interpretation
from test_routing_router import FakeTransport, style_proposal
from test_routing_wire import packet, TEXT as HYBRID_TEXT


TEXT = 'What is the printed policy for Form Q?'
TOPIC = DocumentTopic(subject_id='fictional_policy', claims=('printed Form Q policy',))


def orphan():
    return dict(schema_version=WireInterpretation.SCHEMA_VERSION, language='en',
        audience='undergraduate', intent='fictional policy question', control=None,
        part_count=1, parts=[dict(part_id='r1', quote=dict(text=TEXT, occurrence=0),
            evidence_need='document', operation_indices=[], subject_id=TOPIC.subject_id,
            requested_claims=['printed Form Q policy'])], mentions=[], claims=[],
        operations=[dict(name='check_prerequisite_eligibility', target=dict(text='Form Q', occurrence=0))],
        route='Hybrid', ambiguities=[])


def run(*outputs):
    transport = FakeTransport(*(json.dumps(o) if isinstance(o, dict) else o for o in outputs),
        style_outputs=[json.dumps(style_proposal('en', english=[TEXT], filipino=[]))])
    result = asyncio.run(Router(transport, documents_available=True, topics=(TOPIC,)).route(
        TEXT, RequestContext(session_id='sess-operation', request_id='req-operation')))
    return result, transport


def test_unreferenced_operation_is_rejected_before_late_dispatch_validation():
    with pytest.raises(ValueError, match='unreferenced_operation'):
        normalize_interpretation(TEXT, WireInterpretation.parse(orphan()))


def test_model_can_repair_its_own_operation_part_mismatch_into_document_retrieval():
    corrected = dict(orphan(), operations=[], route='RAG')
    result, transport = run(orphan(), corrected)
    assert result.diagnostic == 'validated' and result.decision.route == 'RAG'
    assert result.decision.predicate_request is None and not result.proposed.operations
    assert result.attempts == 2 and result.style_attempts == 1 and result.inference_calls == 3
    assert result.proposed.parts[0].subject_id == 'fictional_policy'
    assert result.proposed.parts[0].requested_claims == ('printed Form Q policy',)
    repair = transport.calls[1][0]
    assert repair[2]['content'] == json.dumps(orphan())
    assert TEXT in repair[-1]['content'] and 'unreferenced_operation' in repair[-1]['content']


def test_repeated_orphan_operation_stays_unavailable_without_silent_rag_fallback():
    result, transport = run(orphan(), orphan())
    assert result.decision.route is None and result.decision.control == 'evidence_unavailable'
    assert result.decision.predicate_request is None and result.diagnostic == 'invalid_reference'
    assert result.attempts == 2 and result.inference_calls == len(transport.calls) == 3
    assert result.response_style == 'en'


def test_operation_mismatch_repair_uses_the_shared_budget_after_bad_json():
    result, transport = run('bad json', orphan())
    assert result.diagnostic == 'invalid_reference' and not result.decision.dispatchable
    assert result.attempts == 2 and len(transport.calls) == 3


def test_repaired_interpretation_is_still_checked_against_the_topic_menu():
    corrected = dict(orphan(), operations=[], route='RAG')
    corrected['parts'][0]['requested_claims'] = ['invented policy claim']
    result, transport = run(orphan(), corrected)
    assert result.diagnostic == 'invalid_reference' and not result.decision.dispatchable
    assert len(transport.calls) == 3


@pytest.mark.parametrize('audience,control', [('excluded', 'unsupported_scope'),
    ('unrelated', 'unsupported_scope'), ('unknown', 'clarify')])
def test_audience_hold_precedes_orphan_operation_repair(audience, control):
    value = dict(orphan(), audience=audience)
    result, transport = run(value)
    assert result.decision.control == control and not result.decision.dispatchable
    assert result.attempts == 1 and len(transport.calls) == 2


def test_explicit_clarification_keeps_its_unlinked_intent_without_retry():
    value = dict(orphan(), route=None, control='clarify')
    result, transport = run(value)
    assert result.decision.control == 'clarify' and result.diagnostic == 'model_control'
    assert result.attempts == 1 and len(transport.calls) == 2


def test_semantic_ambiguity_is_not_changed_into_a_repair_attempt():
    result, transport = run(dict(orphan(), ambiguities=['Which fictional procedure is intended?']))
    assert result.diagnostic == 'model_ambiguity' and result.decision.control == 'clarify'
    assert result.attempts == 1 and len(transport.calls) == 2


@pytest.mark.parametrize('index', [0, 1])
def test_linked_hybrid_operation_and_existing_index_correction_remain_valid(index):
    value = packet()
    value['parts'][0]['operation_indices'] = [index]
    result = normalize_interpretation(HYBRID_TEXT, WireInterpretation.parse(value))
    assert result.route == 'Hybrid' and len(result.operations) == 1
    assert result.parts[0].operation_indices == (0,)
    assert result.claims[0].state == 'failed'


def test_unused_second_operation_cannot_hide_beside_a_valid_linked_operation():
    value = deepcopy(packet())
    value['operations'].append(dict(name='list_missing_prerequisites',
                                    target=dict(text='B2', occurrence=0)))
    with pytest.raises(ValueError, match='unreferenced_operation'):
        normalize_interpretation(HYBRID_TEXT, WireInterpretation.parse(value))
