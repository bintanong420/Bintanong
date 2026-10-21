"""Router topic/fact selection from a release-supplied menu (research real-data mode).

Without a menu the wire schema and prompt are unchanged. With a menu each document
part must name one menu subject (or null) and only that subject's reviewed claims.
"""
import json

import pytest

from backend.bintanong_routing.contracts import DocumentTopic, RequestPart
from backend.bintanong_routing.prompt import build_messages, output_schema
from test_routing_contracts import proposal
from test_routing_router import FakeTransport, run, style_proposal

MENU = (DocumentTopic(subject_id='fictional_fees', claims=('printed fee amount', 'payment channel')),
        DocumentTopic(subject_id='fictional_office', claims=('filing office',)))
TEXT = 'Where do I file slip S?'


def model(*outputs):
    style = json.dumps(style_proposal('en', english=['Where do I file']))
    return FakeTransport(*outputs, style_outputs=[style] * 3)


def answer(subject='fictional_office', claims=('filing office',)):
    value = proposal(text=TEXT, route='RAG', mentions=[], operations=[], intent='Filing location', language='en')
    value['parts'][0].update(subject_id=subject, requested_claims=list(claims))
    return json.dumps(value)


def test_schema_without_topics_is_unchanged():
    part = output_schema()['$defs']['WirePart']
    assert set(part['properties']) == {'part_id', 'quote', 'evidence_need', 'operation_indices'}


def test_schema_with_topics_pairs_each_topic_with_its_own_claims():
    branches = output_schema(MENU)['$defs']['WirePart']['anyOf']
    by_subject = {b['properties']['subject_id'].get('const'): b['properties']['requested_claims']
                  for b in branches}
    assert set(by_subject) == {'fictional_fees', 'fictional_office', None}
    assert by_subject['fictional_office']['items']['enum'] == ['filing office']
    assert by_subject['fictional_office']['minItems'] == 1
    assert by_subject[None]['maxItems'] == 0
    assert all({'subject_id', 'requested_claims'} <= set(b['required']) for b in branches)


def test_prompt_lists_topics_only_when_a_menu_exists():
    from backend.bintanong_routing.contracts import RequestContext
    from test_routing_router import context
    ctx = RequestContext.parse(context())
    with_menu = build_messages(TEXT, ctx, (), _registry(), topics=MENU)[0]['content']
    without = build_messages(TEXT, ctx, (), _registry())[0]['content']
    assert 'fictional_office' in with_menu and 'filing office' in with_menu
    assert 'fictional_office' not in without and 'Document topics' not in without


def _registry():
    from test_routing_router import registry
    return registry()


def test_router_keeps_a_valid_topic_choice():
    result = run(model(answer()), text=TEXT, topics=MENU)
    assert result.diagnostic == 'validated' and result.decision.route == 'RAG'
    part = result.proposed.parts[0]
    assert part.subject_id == 'fictional_office' and part.requested_claims == ('filing office',)


def test_router_rejects_claims_outside_the_chosen_topic():
    result = run(FakeTransport(answer(claims=('printed fee amount',)), answer(claims=('printed fee amount',))),
                 text=TEXT, topics=MENU)
    assert result.diagnostic == 'invalid_reference'


def test_router_rejects_topic_choices_when_no_menu_exists():
    result = run(FakeTransport(answer(), answer()), text=TEXT)
    assert result.diagnostic == 'invalid_reference'


def test_only_document_parts_carry_topics():
    with pytest.raises(ValueError):
        RequestPart.parse(dict(part_id='r1', text='A1', start=0, end=2, evidence_need='structured',
                               operation_indices=[0], subject_id='fictional_fees', requested_claims=[]))


def test_generation_input_omits_retrieval_topic_labels():
    from backend.bintanong_generation.evidence import prepare
    from backend.bintanong_generation.scope import document_payload
    from test_request_understanding_pipeline import source
    parts = document_payload(prepare(source()))['requested_parts']
    assert parts and all('subject_id' not in p and 'requested_claims' not in p for p in parts)


def test_prompt_shows_plain_topic_fields_while_the_grammar_keeps_paired_branches():
    from backend.bintanong_routing.contracts import RequestContext
    from test_routing_router import context
    ctx = RequestContext.parse(context())
    system = build_messages(TEXT, ctx, (), _registry(), topics=MENU)[0]['content']
    shown = system.split('JSON schema:\n', 1)[1]
    assert 'subject_id' in shown and 'requested_claims' in shown
    assert 'anyOf' not in shown  # per-topic branches stay in the enforced grammar only
    assert 'anyOf' in json.dumps(output_schema(MENU))
