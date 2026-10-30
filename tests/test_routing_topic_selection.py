"""Candidate topic narrowing must never authorize evidence or alter semantic routing."""
import asyncio
import json

import pytest
import httpx

from backend.bintanong_routing.contracts import DocumentTopic, NotStatedCue, RequestContext
from backend.bintanong_routing.router import Router
from backend.bintanong_routing.transport import RuntimeFailure
from backend.bintanong_routing.transport import LlamaTransport
from routing_wire_fixtures import wire_fixture
from test_routing_contracts import context, proposal
from test_routing_router import FakeTransport, style_proposal
from test_routing_validation import catalog, registry


MENU = (
    DocumentTopic(subject_id='fictional_office', claims=('filing office',),
        claim_fields={'filing office': ('Office',)},
        source_context=('Synthetic filing procedure, page 1',),
        not_stated=('processing deadline',),
        cues=(NotStatedCue(claim='processing deadline', phrases=('deadline',)),)),
    DocumentTopic(subject_id='fictional_fees', claims=('printed fee amount',)),
    *(DocumentTopic(subject_id=f'other_{i}', claims=(f'printed synthetic clause {i}',))
      for i in range(8)),
)
TEXT = 'Where do I file slip S?'


class Transport(FakeTransport):
    """Only inference is substituted; selection, normalization and host validation are real."""
    def __init__(self, selection, *outputs, text=TEXT):
        super().__init__(*outputs, style_outputs=[json.dumps(
            style_proposal('en', english=[text.split()[0]]))] * 3)
        self.selection = selection

    async def infer(self, messages, schema):
        if schema['properties'].get('schema_version', {}).get('const') != 'bintanong-topic-selection-v1':
            return await super().infer(messages, schema)
        self.calls.append((messages, schema))
        if isinstance(self.selection, Exception):
            raise self.selection
        return self.selection


def selected(ids=('fictional_office',), ambiguous=False):
    return json.dumps(dict(schema_version='bintanong-topic-selection-v1',
        subject_ids=list(ids), ambiguous=ambiguous))


def answer(subject='fictional_office', claims=('filing office',), text=TEXT):
    value = proposal(text=text, language='en', route='RAG', mentions=[], operations=[])
    value['parts'][0].update(subject_id=subject, requested_claims=list(claims))
    return json.dumps(value)


def run(transport, *, text=TEXT, topics=MENU, enabled=True, ctx=None):
    router = Router(transport, catalog=catalog(), registry=registry(),
        documents_available=True, synthetic=True, topics=topics, topic_selection=enabled)
    result = asyncio.run(router.route(text, RequestContext.parse(ctx or context())))
    return result, router


def test_selected_complete_topics_reach_semantic_router_without_mutating_the_release_menu():
    transport = Transport(selected(), answer())
    result, router = run(transport)
    assert result.decision.route == 'RAG' and result.diagnostic == 'validated'
    assert result.proposed.parts[0].requested_claims == ('filing office',)
    assert router.topics == MENU
    assert result.selection_attempts == 1 and result.inference_calls == 3
    assert result.repair_attempts == 0
    selection_messages, selection_schema = transport.calls[0]
    assert selection_schema['properties']['subject_ids']['maxItems'] == 8
    assert set(selection_schema['properties']['subject_ids']['items']['enum']) == {t.subject_id for t in MENU}
    assert json.loads(selection_messages[1]['content'])['original_text'] == TEXT
    messages, schema = transport.calls[1]
    system = messages[0]['content']
    assert 'fictional_office' in system and 'fictional_fees' not in system
    assert all(label in system for label in ('Office', 'Synthetic filing procedure, page 1',
        'processing deadline', 'filing office'))
    branches = schema['$defs']['WirePart']['anyOf']
    assert {b['properties']['subject_id'].get('const') for b in branches} == {'fictional_office', None}
    assert json.loads(messages[1]['content'])['original_text'] == TEXT


@pytest.mark.parametrize('enabled,count', [(False, 10), (True, 8), (True, 0)])
def test_default_and_small_menu_keep_the_existing_inference_path(enabled, count):
    transport = FakeTransport(json.dumps(proposal()),
        style_outputs=[json.dumps(style_proposal('en', english=['A1']))])
    result, _ = run(transport, text='A1', topics=MENU[:count], enabled=enabled)
    assert result.decision.route == 'Symbolic' and result.inference_calls == 2
    assert result.selection_attempts == 0 and len(transport.calls) == 2


@pytest.mark.parametrize('raw', [
    'not json', '[]', 'null', '{}',
    selected(('absent_topic',)), selected(('fictional_office', 'fictional_office')),
    selected(tuple(t.subject_id for t in MENU[:9])), selected(ambiguous=True),
    '{"schema_version":"bintanong-topic-selection-v1","subject_ids":[],"ambiguous":"false"}',
    '{"schema_version":"bintanong-topic-selection-v1","subject_ids":[1],"ambiguous":false}',
    '{"schema_version":"bintanong-topic-selection-v1","subject_ids":[],"ambiguous":false,"answer":"yes"}',
    '{"schema_version":"bintanong-topic-selection-v1","subject_ids":[],"ambiguous":true,"ambiguous":false}',
    pytest.param(' ' * 65537, id='oversized'),
])
def test_invalid_or_ambiguous_selection_withholds_without_detail_or_fallback(raw):
    transport = Transport(raw, answer())
    result, _ = run(transport)
    assert result.decision.control == 'evidence_unavailable' and not result.decision.dispatchable
    assert result.diagnostic == 'topic_selection_unavailable'
    assert result.selection_attempts == 1 and result.attempts == 0
    assert result.inference_calls == 1 and len(transport.calls) == 1


@pytest.mark.parametrize('code', ['context_overflow', 'model_timeout', 'model_connection_error'])
def test_selector_transport_failure_cannot_fall_back_to_full_menu(code):
    result, _ = run(Transport(RuntimeFailure(code), answer()))
    assert result.diagnostic == code and not result.decision.dispatchable
    assert result.inference_calls == 1


def test_empty_selection_keeps_structured_semantics_and_excluded_audience_controls():
    for value, expected_route, expected_control in (
        (proposal(), 'Symbolic', None),
        (proposal(route=None, control='unsupported_scope', audience='excluded',
            mentions=[], operations=[]), None, 'unsupported_scope'),
    ):
        result, _ = run(Transport(selected(()), json.dumps(value), text='A1'), text='A1')
        assert result.decision.route == expected_route and result.decision.control == expected_control
        assert result.inference_calls == 3


def test_empty_selection_does_not_authorize_a_document_answer():
    result, _ = run(Transport(selected(()), answer(None, ())))
    assert result.decision.control == 'evidence_unavailable'
    assert result.diagnostic == 'topic_selection_unavailable'


def test_detailed_router_cannot_escape_to_an_unselected_existing_topic():
    bad = answer('fictional_fees', ('printed fee amount',))
    result, _ = run(Transport(selected(), bad, bad))
    assert result.diagnostic == 'invalid_reference' and not result.decision.dispatchable
    assert result.selection_attempts == 1 and result.repair_attempts == 1


def test_selection_retains_multiple_document_parts():
    text = 'Where do I file slip S and what fee is printed?'
    value = proposal(text=text, route='RAG', language='en', mentions=[], operations=[], parts=[])
    for ident, quote, subject, claim in (
        ('r1', 'Where do I file slip S', 'fictional_office', 'filing office'),
        ('r2', 'what fee is printed?', 'fictional_fees', 'printed fee amount'),
    ):
        start = text.index(quote)
        value['parts'].append(dict(part_id=ident, text=quote, start=start, end=start+len(quote),
            evidence_need='document', operation_indices=[], subject_id=subject, requested_claims=[claim]))
    result, _ = run(Transport(selected(('fictional_office', 'fictional_fees')),
        json.dumps(value), text=text), text=text)
    assert result.decision.route == 'RAG'
    assert [p.subject_id for p in result.proposed.parts] == ['fictional_office', 'fictional_fees']


@pytest.mark.parametrize('available', [True, False])
def test_hybrid_keeps_the_structured_check_and_withholds_if_its_document_part_is_unselected(available):
    text = 'A1 and policy'
    value = proposal(text=text, route='Hybrid', language='en')
    value['parts'][1].update(subject_id='fictional_office' if available else None,
        requested_claims=['filing office'] if available else [])
    result, _ = run(Transport(selected() if available else selected(()),
        json.dumps(value), text=text), text=text)
    assert result.proposed.operations[0].name == 'check_prerequisite_eligibility'
    if available:
        assert result.decision.route == 'Hybrid'
    else:
        assert result.decision.control == 'evidence_unavailable'


def test_selection_receives_only_the_existing_bounded_follow_up_signal():
    ctx = context()
    ctx['conversation'] = dict(subject_id='fictional_office')
    transport = Transport(selected(), answer())
    result, _ = run(transport, ctx=ctx)
    assert result.decision.route == 'RAG'
    payload = json.loads(transport.calls[0][0][1]['content'])
    assert payload == dict(original_text=TEXT, previous_turn=dict(subject_id='fictional_office'))
    assert json.loads(transport.calls[1][0][1]['content'])['previous_turn'] == payload['previous_turn']


def test_not_stated_cues_survive_narrowing():
    text = 'What is the deadline?'
    result, _ = run(Transport(selected(), answer(text=text), text=text), text=text)
    assert result.decision.route == 'RAG'
    assert result.proposed.parts[0].requested_claims == ('filing office', 'processing deadline')


@pytest.mark.parametrize('overflow_stage,repair,expected_completions', [
    (0, False, 0), (1, False, 1), (2, True, 2), (2, False, 2),
])
def test_exact_transport_guard_withholds_before_each_overflowing_call(
        overflow_stage, repair, expected_completions):
    result, completions = http_run(overflow_stage=overflow_stage, repair=repair)
    assert result.diagnostic == 'context_overflow' and not result.decision.dispatchable
    assert len(completions) == expected_completions
    # Every completed call, including a repair, received the full original question.
    assert all(json.loads(c['messages'][1]['content'])['original_text'] == TEXT for c in completions)


def test_exact_transport_boundary_includes_output_reserve_without_truncating_messages():
    result, completions = http_run()
    assert result.decision.route == 'RAG' and result.inference_calls == 3
    assert len(completions) == 3
    assert completions[0]['max_tokens'] == 768
    assert json.loads(completions[1]['messages'][1]['content'])['original_text'] == TEXT


def http_run(*, overflow_stage=None, repair=False):
    """Real Router + LlamaTransport; only the remote server is synthetic."""
    async def execute():
        preflights, completions = [], []
        outputs = [selected(), 'invalid' if repair else json.dumps(wire_fixture(json.loads(answer()), TEXT))]
        if repair:
            outputs.append(json.dumps(wire_fixture(json.loads(answer()), TEXT)))
        outputs.append(json.dumps(style_proposal('en', english=['Where'])))

        def handler(request):
            body = json.loads(request.content) if request.content else {}
            path = request.url.path
            if path == '/props':
                return httpx.Response(200, json=dict(default_generation_settings=dict(n_ctx=8192),
                    chat_template='synthetic-template', model_path='/synthetic.gguf'))
            if path == '/apply-template':
                preflights.append(body['messages'])
                return httpx.Response(200, json=dict(prompt=f'templated-{len(preflights)-1}'))
            if path == '/tokenize':
                if body['content'].startswith('templated-'):
                    assert body['add_special'] is False and body['parse_special'] is True
                    stage = int(body['content'].rsplit('-', 1)[1])
                    return httpx.Response(200, json=dict(tokens=[1] * (
                        7417 if stage == overflow_stage else 7416)))
                return httpx.Response(200, json=dict(tokens=[2, 3]))
            assert path == '/v1/chat/completions'
            completions.append(body)
            return httpx.Response(200, json=dict(choices=[dict(finish_reason='stop',
                message=dict(content=outputs.pop(0)))]))

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            transport = LlamaTransport('http://synthetic', client=client)
            router = Router(transport, catalog=catalog(), registry=registry(),
                documents_available=True, synthetic=True, topics=MENU, topic_selection=True)
            result = await router.route(TEXT, RequestContext.parse(context()))
        return result, completions
    return asyncio.run(execute())


def test_style_repair_is_counted_separately_from_selection():
    transport = Transport(selected(), answer())
    transport.style_outputs = ['bad', json.dumps(style_proposal('en', english=['Where']))]
    result, _ = run(transport)
    assert result.decision.route == 'RAG'
    assert (result.selection_attempts, result.attempts, result.style_attempts) == (1, 1, 2)
    assert result.inference_calls == 4 and result.repair_attempts == 1


def test_concurrent_requests_on_one_router_keep_their_own_topic_selection():
    async def execute():
        gate = asyncio.Event()
        selections = []

        class ConcurrentTransport:
            async def infer(self, messages, schema):
                text = json.loads(messages[1]['content'])['original_text']
                is_fees = text == 'What fee is printed?'
                subject = 'fictional_fees' if is_fees else 'fictional_office'
                claim = 'printed fee amount' if is_fees else 'filing office'
                version = schema['properties']['schema_version']['const']
                if version == 'bintanong-topic-selection-v1':
                    selections.append(text)
                    if len(selections) == 2:
                        gate.set()
                    await gate.wait()
                    return selected((subject,))
                if version == 'bintanong-response-style-v2':
                    return json.dumps(style_proposal('en', english=[text.split()[0]]))
                return json.dumps(wire_fixture(json.loads(answer(subject, (claim,), text)), text))

        router = Router(ConcurrentTransport(), registry=registry(), documents_available=True,
            synthetic=True, topics=MENU, topic_selection=True)
        ctx = RequestContext.parse(context())
        results = await asyncio.gather(router.route(TEXT, ctx), router.route('What fee is printed?', ctx))
        # Also exercise a later request after both previous selections completed.
        results.append(await router.route(TEXT, ctx))
        return results, router

    results, router = asyncio.run(execute())
    assert [r.decision.route for r in results] == ['RAG', 'RAG', 'RAG']
    assert [r.proposed.parts[0].subject_id for r in results] == [
        'fictional_office', 'fictional_fees', 'fictional_office']
    assert router.topics == MENU


def test_evaluation_explains_selector_calls_separately_from_routing_and_style():
    from backend.bintanong_routing.evaluation import evaluate_cases
    from test_routing_evaluation import case, metadata
    transport = Transport(selected(()), json.dumps(proposal(language='en')), text='A1')
    router = Router(transport, catalog=catalog(), registry=registry(),
        documents_available=True, synthetic=True, topics=MENU, topic_selection=True)
    report = asyncio.run(evaluate_cases(router, [case()], metadata()))
    assert report['selection_calls'] == 1
    assert report['records'][0]['selection_attempts'] == 1
    assert report['inference_calls'] == report['selection_calls'] + report['routing_calls'] + report['style_calls']


def detail_answer(claims, detail, text=TEXT):
    value = json.loads(answer(claims=claims, text=text))
    value['parts'][0]['detail'] = detail
    return json.dumps(value)


def test_whole_procedure_request_naming_only_a_not_stated_fact_answers_the_printed_procedure():
    result, _ = run(Transport(selected(), detail_answer(['processing deadline'], 'whole')))
    assert result.decision.route == 'RAG'
    assert result.proposed.parts[0].requested_claims == ('filing office',)


def test_a_specific_request_for_a_not_stated_fact_still_withholds():
    result, _ = run(Transport(selected(), detail_answer(['processing deadline'], 'specific')))
    assert result.proposed.parts[0].requested_claims == ('processing deadline',)


def test_a_whole_request_whose_words_name_the_not_stated_fact_keeps_it():
    text = 'Where do I file slip S and what is the deadline?'
    result, _ = run(Transport(selected(), detail_answer(['processing deadline'], 'whole', text=text), text=text),
                    text=text)
    assert 'processing deadline' in result.proposed.parts[0].requested_claims


# Owner 30 Oct 2026 benchmark: "What is the penalty for plagiarism?" named only a not-stated fact of a 39-fact
# sanctions topic; replacing it with every printed fact exceeded the eight-claim bound and the host clarified.
SANCTIONS = DocumentTopic(subject_id='fictional_sanctions',
    claims=(*(f'printed rule {i} fields: {i}. Synthetic offense number {i}' for i in range(9)),
            'printed rule 9 fields: 9. Littering on the synthetic campus', 'missing item 10'),
    not_stated=('missing item 10',))


def sanction_question(text):
    value = json.loads(answer('fictional_sanctions', ('missing item 10',), text))
    value['parts'][0]['detail'] = 'whole'
    return run(Transport(selected(('fictional_sanctions',)), *[json.dumps(value)] * 2, text=text), text=text,
               topics=(*MENU, SANCTIONS))[0]


def test_a_large_topic_answers_the_printed_fact_the_part_names():
    result = sanction_question('What is the penalty for littering?')
    assert result.decision.route == 'RAG'
    assert result.proposed.parts[0].requested_claims == (
        'printed rule 9 fields: 9. Littering on the synthetic campus',)


def test_a_large_topic_naming_no_printed_fact_keeps_the_model_choice():
    result = sanction_question('What is the penalty for this?')
    assert result.decision.route == 'RAG'
    assert result.proposed.parts[0].requested_claims == ('missing item 10',)


# Owner 30 Oct 2026 benchmark: "Kailan ako considered second year?" selected one topic, then the router
# returned an empty clarification (no parts, ambiguity or course) and the student got no answer.
def empty_clarify(text):
    return json.dumps(proposal(text=text, language='taglish', route=None, control='clarify',
                               mentions=[], operations=[], parts=[]))


def test_an_empty_clarification_after_one_settled_topic_answers_that_topic():
    text = 'Kailan ako mag-file ng slip S?'
    result, _ = run(Transport(selected(), empty_clarify(text), text=text), text=text)
    assert result.decision.route == 'RAG'
    part = result.proposed.parts[0]
    assert (part.subject_id, part.requested_claims, part.text) == ('fictional_office', ('filing office',), text)


def test_an_empty_clarification_with_two_selected_topics_still_clarifies():
    text = 'Kailan ako mag-file ng slip S?'
    result, _ = run(Transport(selected(('fictional_office', 'fictional_fees')), empty_clarify(text), text=text),
                    text=text)
    assert result.decision.route is None and not result.proposed.parts


def test_an_empty_clarification_without_topic_selection_still_clarifies():
    text = 'Kailan ako mag-file ng slip S?'
    result, _ = run(FakeTransport(empty_clarify(text), style_outputs=[json.dumps(
        style_proposal('taglish', english=['slip']))] * 3), text=text, topics=MENU[:1], enabled=False)
    assert result.decision.route is None and not result.proposed.parts


def test_a_short_asked_word_also_names_longer_printed_words():
    # Robustness 30 Oct 2026: "exam" must reach "cheating in examinations", not only a row printing "exam";
    # a three-letter Filipino word ("ano") must not name "another".
    topic = SANCTIONS.model_copy(update=dict(claims=(
        *SANCTIONS.claims[:7], 'printed rule 7 fields: 7. Allowing another student to sit',
        'printed rule 8 fields: 8. Cheating in examinations',
        'printed rule 9 fields: 9. Selling exam answers', 'missing item 10')))
    result = run(Transport(selected(('fictional_sanctions',)), empty_clarify('Ano parusa sa exam?'),
                           text='Ano parusa sa exam?'), text='Ano parusa sa exam?', topics=(*MENU, topic))[0]
    assert result.proposed.parts[0].requested_claims == (
        'printed rule 8 fields: 8. Cheating in examinations', 'printed rule 9 fields: 9. Selling exam answers')


def test_an_eligibility_check_on_an_unlisted_reviewed_course_stays_symbolic():
    # Owner 30 Oct 2026 benchmark: the target course was quoted but not listed as a mention.
    text = 'Can I take B1?'
    wire = dict(schema_version='bintanong-interpretation-wire-v4', language='en', part_count=1,
        audience='undergraduate', intent='eligibility check', mentions=[], claims=[],
        operations=[dict(name='check_prerequisite_eligibility', target=dict(text='B1', occurrence=0))],
        parts=[dict(part_id='r1', quote=dict(text=text, occurrence=0), evidence_need='structured',
                    operation_indices=[0], subject_id='fictional_office', requested_claims=['filing office'],
                    detail='whole')],
        route='Symbolic', control=None, ambiguities=[])
    result, _ = run(Transport(selected(), json.dumps(wire), text=text), text=text)
    assert result.decision.route == 'Symbolic'
    assert result.proposed.parts[0].evidence_need == 'structured'
