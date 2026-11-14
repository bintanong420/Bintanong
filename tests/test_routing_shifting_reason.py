"""A reason for shifting is not a course prerequisite check (synthetic programs)."""
import asyncio
import json

from backend.bintanong_routing.contracts import DocumentTopic, RequestContext
from backend.bintanong_routing.router import Router
from test_routing_contracts import context
from test_routing_router import FakeTransport, style_proposal
from test_routing_validation import catalog, registry
from test_routing_wire import quote

TEXT = 'Pwede ba akong mag-shift sa Program B kasi bagsak ako?'
TOPICS = (DocumentTopic(subject_id='handbook_shifting', claims=('printed shifting fields',)),
          DocumentTopic(subject_id='handbook_drop_shift_faq', claims=('printed FAQ 8 shifting steps',)))


def packet():
    return dict(schema_version='bintanong-interpretation-wire-v4', language='fil', audience='undergraduate',
        control=None, part_count=1, intent='eligibility and shifting procedure', route='Hybrid', ambiguities=[],
        mentions=[dict(kind='program', quote=quote('Program B'))],
        claims=[dict(quote=quote('bagsak ako'), entity=quote('Program B'), state='failed', mode='asserted')],
        operations=[dict(name='check_prerequisite_eligibility', target=quote('Program B'))],
        parts=[dict(part_id='r1', quote=quote(TEXT), evidence_need='structured', operation_indices=[0],
                    subject_id='handbook_shifting', requested_claims=['printed shifting fields'], detail='whole')])


def test_recorded_program_target_and_unbound_failure_reach_the_shifting_documents():
    from backend.bintanong_routing.contracts import CatalogEntry
    destination = CatalogEntry.parse(dict(kind='program', entity_id='program-b', program_id='program-b',
        curriculum_id=None, aliases=['Program B'], source_ref='ver-a', review_ref='review-a', reviewed=True))
    value = json.dumps(packet())
    style = json.dumps(style_proposal('fil', english=[], filipino=[TEXT]))
    router = Router(FakeTransport(value, value, style_outputs=[style]), catalog=(*catalog(), destination),
                    registry=registry(), documents_available=True, synthetic=True, topics=TOPICS)
    result = asyncio.run(router.route(TEXT, RequestContext.parse(context())))
    assert result.diagnostic == 'validated' and result.decision.route == 'RAG'
    assert result.decision.predicate_request is None and result.claims == ()
    assert result.proposed.parts[0].subject_id == 'handbook_shifting'
    assert result.proposed.parts[0].requested_claims == ('printed shifting fields',)
    assert (result.program_id, result.curriculum_id) == ('program-a', 'curriculum-a')
    assert result.attempts == 1
