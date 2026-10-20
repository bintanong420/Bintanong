"""Catalog visibility and real host binding; no model-accuracy claims."""
import asyncio
import json

import pytest

from backend.bintanong_routing import combined, prompt
from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_routing.router import Router
from test_routing_contracts import context
from test_routing_validation import entry, registry
from test_routing_wire_boundary import Model, STYLE


@pytest.mark.parametrize('module', [prompt, combined], ids=['separate', 'combined'])
def test_actual_messages_are_catalog_invariant_and_preserve_remaining_input(module):
    ctx = RequestContext.parse(context(facts=[dict(fact_id='fact-private-record',
        session_id='sess-a', program_id='program-a', curriculum_id='curriculum-a',
        course_id='course-a', state='passed')]))
    messages = module.build_messages('Can I take A1?', ctx, (entry(),), registry())
    other = module.build_messages('Can I take A1?', ctx,
        (entry(entity='course-other', alias='UNRELATED9', curriculum='curriculum-old'),), registry())
    assert messages == other
    data = json.loads(messages[1]['content'])
    assert data == dict(original_text='Can I take A1?', normalized_text='Can I take A1?',
        context=dict(program_id='program-a', curriculum_id='curriculum-a',
            facts=[dict(course_id='course-a', state='passed')]),
        available_operations=['check_prerequisite_eligibility'])
    sent = json.dumps(messages)
    assert all(private not in sent for private in ['sess-a', 'req-a', 'fact-private-record'])


@pytest.mark.parametrize('router_class', [Router, combined.CombinedRouter], ids=['separate', 'combined'])
def test_catalog_still_controls_curriculum_binding_after_literal_extraction(router_class):
    text = 'Can I take A1?'
    quote = dict(text='A1', occurrence=0)
    packet = dict(schema_version='bintanong-interpretation-wire-v1', language='en',
        audience='undergraduate', route='Symbolic', control=None, intent='eligibility',
        mentions=[dict(kind='course', quote=quote)], claims=[],
        operations=[dict(name='check_prerequisite_eligibility', target=quote)],
        parts=[dict(part_id='r1', quote=dict(text=text, occurrence=0),
                    evidence_need='structured', operation_indices=[0])], ambiguities=[], reason='Check eligibility.')
    catalog = (entry(), entry(entity='course-old', curriculum='curriculum-old'))
    for curriculum, expected in [('curriculum-a', 'course-a'), ('curriculum-old', 'course-old'), (None, None)]:
        model = (Model(dict(schema_version='bintanong-routing-style-v2', interpretation=packet,
                            style=STYLE['style'])) if router_class is combined.CombinedRouter
                 else Model(packet, STYLE))
        router = router_class(model, catalog=catalog, registry=registry(), synthetic=True)
        ctx = RequestContext.parse(context(curriculum_id=curriculum))
        result = asyncio.run(router.route(text, ctx))
        if expected:
            assert result.diagnostic == 'validated' and result.decision.route == 'Symbolic'
            assert {i.name: i.value for i in result.decision.predicate_request.inputs} == {
                'curriculum_id': curriculum, 'course_id': expected}
        else:
            assert result.diagnostic == 'missing_scope' and not result.decision.dispatchable
        assert len(model.calls) == (1 if router_class is combined.CombinedRouter else 2)
        assert result.repair_attempts == 0
        assert 'reviewed_aliases' not in json.loads(model.calls[0][0][1]['content'])
