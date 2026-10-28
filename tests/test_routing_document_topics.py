"""Router topic/fact selection from a release-supplied menu (research real-data mode).

Without a menu the wire schema and prompt are unchanged. With a menu each document
part must name one menu subject (or null) and only that subject's reviewed claims.
"""
import json

import pytest

from backend.bintanong_routing.contracts import DocumentTopic, NotStatedCue, RequestPart
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


NOT_STATED = (DocumentTopic(subject_id='fictional_fees', claims=('printed fee amount',),
                            not_stated=('individual share',)),)


def test_not_stated_facts_are_selectable_and_shown_as_not_stated():
    branch = next(b for b in output_schema(NOT_STATED)['$defs']['WirePart']['anyOf']
                  if b['properties']['subject_id'].get('const') == 'fictional_fees')
    assert branch['properties']['requested_claims']['items']['enum'] == ['printed fee amount', 'individual share']
    from backend.bintanong_routing.contracts import RequestContext
    from test_routing_router import context
    system = build_messages(TEXT, RequestContext.parse(context()), (), _registry(), topics=NOT_STATED)[0]['content']
    assert '"not_stated":["individual share"]' in system


def test_menus_without_not_stated_facts_render_as_before():
    from backend.bintanong_routing.contracts import RequestContext
    from test_routing_router import context
    system = build_messages(TEXT, RequestContext.parse(context()), (), _registry(), topics=MENU)[0]['content']
    assert 'not_stated' not in system


def test_router_accepts_a_not_stated_fact_of_the_chosen_topic():
    from backend.bintanong_routing.router import check_topics
    from backend.bintanong_routing.contracts import Interpretation
    value = json.loads(answer(subject='fictional_fees', claims=('individual share',)))
    proposed = Interpretation.parse(value)
    check_topics(proposed, NOT_STATED)


CUED = (DocumentTopic(subject_id='fictional_fees', claims=('printed fee amount',), not_stated=('individual share',),
                      cues=(NotStatedCue(claim='individual share', phrases=('each student', 'bawat isa')),)),)


def fee_question(text):
    value = proposal(text=text, route='RAG', mentions=[], operations=[], intent='Fee', language='en')
    value['parts'][0].update(subject_id='fictional_fees', requested_claims=['printed fee amount'])
    return json.dumps(value)


@pytest.mark.parametrize('text,expected', [
    ('How much does each student pay?', ('printed fee amount', 'individual share')),
    ('Magkano ang bayad ng bawat isa?', ('printed fee amount', 'individual share')),
    ('What amount does the fee example show?', ('printed fee amount',))])
def test_cue_in_the_part_adds_its_not_stated_fact(text, expected):
    # Owner, 23 Oct 2026 (run 11): a per-person amount question must reach the not-stated fact, so
    # the policy withholds instead of presenting the printed example as one student's share.
    style = json.dumps(style_proposal('en', english=[text.split()[0]]))
    transport = FakeTransport(fee_question(text), style_outputs=[style] * 3)
    result = run(transport, text=text, topics=CUED)
    assert result.decision.route == 'RAG' and result.proposed.parts[0].requested_claims == expected


def test_cue_must_name_one_of_the_topics_not_stated_facts():
    with pytest.raises(ValueError):
        DocumentTopic(subject_id='fictional_fees', claims=('printed fee amount',),
                      cues=(NotStatedCue(claim='printed fee amount', phrases=('each student',)),))


def _undergraduate_clarify_branches(schema):
    return [b for b in schema['oneOf'] if b['properties']['audience'] == {'const': 'undergraduate'}
            and 'clarify' in (b['properties']['control'].get('enum') or [b['properties']['control'].get('const')])]


def _names_something(branch, follow_up):
    props = branch['properties']
    named = [props[f].get('minItems', 0) >= 1 for f in ('operations', 'claims', 'ambiguities')]
    if follow_up:
        named.append(props['previous_course_quote'].get('type') != 'null'
                     and 'null' not in str(props['previous_course_quote'].get('anyOf', '')))
    return any(named)


@pytest.mark.parametrize('follow_up', [False, True])
def test_menu_grammar_has_no_clarification_that_names_nothing(follow_up):
    # Live 559 battery (28 Oct 2026): "Gusto ko mag-shift sa ibang college, ano yung process?" with the
    # shifting topic selected came back control=clarify, no parts/operations/claims/ambiguities, which
    # the host must treat as unavailable information (owner E3) although a reviewed topic answers it.
    branches = _undergraduate_clarify_branches(output_schema(MENU, follow_up=follow_up))
    assert branches and all(_names_something(b, follow_up) for b in branches)


def test_grammar_without_a_menu_keeps_its_clarify_branch():
    schema = output_schema()
    assert any(not _names_something(b, False) for b in _undergraduate_clarify_branches(schema))
