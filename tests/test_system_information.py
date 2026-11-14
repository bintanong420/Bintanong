"""System descriptions are host-owned metadata, never university-policy evidence."""
import asyncio
import json

import pytest

from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.system_information import system_information
from backend.bintanong_orchestration.contracts import IntegrationResult
from backend.bintanong_orchestration.orchestrator import Orchestrator
from backend.bintanong_routing.contracts import Interpretation
from test_orchestration_pipeline import ctx, ports, resources
from test_routing_contracts import proposal
from test_routing_router import FakeTransport, style_proposal


class NoGeneration:
    async def infer(self, *args):
        raise AssertionError('system information must not be generated')


@pytest.mark.parametrize('text,language', [
    ('What can Bintanong do?', 'en'),
    ('Ano ang saklaw ng Bintanong?', 'fil'),
    ('Ano ang research scope ng Bintanong?', 'taglish'),
])
def test_system_information_runs_through_chat_without_policy_tools(text, language):
    async def scenario():
        value = proposal(text=text, language=language, route=None, control='system_information',
                         mentions=[], operations=[], claims=[])
        style = style_proposal(language, english=[text] if language != 'fil' else [],
                               filipino=[text] if language != 'en' else [])
        model = FakeTransport(json.dumps(value), style_outputs=[json.dumps(style)])
        release = resources()
        result = await Orchestrator(model, releases=ports().SyntheticReleaseProvider(release)).run(text, ctx())
        assert result.status == 'system_information' and result.reason is None
        assert result.evidence is None and result.route is None
        assert not release.retrieval.calls and not release.symbolic.calls
        answer = await Generator(NoGeneration()).generate(text, result)
        assert answer.status == 'system_information' and answer.reason is None
        assert answer.language == ('en' if language == 'en' else 'taglish')
        assert not answer.claims and not answer.citations and answer.decision is None
        assert answer.draft_attempts == 0 and answer.part_ledger is None
        for expected in ('2026', '2027', 'undergraduate', 'Medicine', 'Law', 'graduate',
                         'laboratory school', 'English', 'Taglish', 'COR', 'Bintanong'):
            assert expected in answer.text
        assert 'scope' in answer.text.lower()
        assert ('pending' in answer.text.lower())
        assert ('Prolog' in answer.text and 'RAG' in answer.text)
    asyncio.run(scenario())


@pytest.mark.parametrize('field', ['operations', 'parts', 'claims'])
def test_system_information_cannot_swallow_an_academic_part_or_action(field):
    academic = proposal()
    value = proposal(route=None, control='system_information', mentions=academic['mentions'],
                     operations=[], parts=[], claims=[])
    value[field] = (academic[field] if field != 'claims' else [dict(
        entity=0, state='passed', mode='asserted', text='A1', start=0, end=2)])
    with pytest.raises(ValueError, match='terminal_control'):
        Interpretation.parse(value)


def test_unknown_language_cannot_get_an_english_system_description():
    with pytest.raises(ValueError, match='unsupported_system_information_language'):
        system_information('unknown')


def test_system_information_cannot_be_bound_to_an_academic_route():
    with pytest.raises(ValueError, match='system_information_has_academic_work'):
        IntegrationResult(schema_version=IntegrationResult.SCHEMA_VERSION, request_id='req-a',
                          route='RAG', response_style='en', status='system_information',
                          evidence=None, understanding=None, events=())


def test_model_schema_offers_system_information_without_academic_parts():
    from backend.bintanong_routing.prompt import output_schema
    schema = output_schema()
    branch = next(b for b in schema['oneOf'] if 'system_information' in
                  b['properties']['control'].get('enum', []))
    assert branch['properties']['route'] == {'type': 'null'}
    assert branch['properties']['audience'] == {'const': 'undergraduate'}
    for field in ('parts', 'claims', 'operations'):
        assert branch['properties'][field]['maxItems'] == 0


def test_index_text_cannot_be_replaced_by_a_generated_answer():
    from backend.bintanong_generation.evidence import prepare
    from backend.bintanong_generation.validation import validate_final
    result = IntegrationResult(schema_version=IntegrationResult.SCHEMA_VERSION, request_id='req-a',
        route=None, response_style='en', status='system_information', evidence=None,
        understanding=None, events=())
    answer = asyncio.run(Generator(NoGeneration()).generate('What can you do?', result))
    tampered = answer.model_copy(update={'text': 'I can officially change your grades.'})
    with pytest.raises(ValueError, match='final_render_mismatch'):
        validate_final(tampered, prepare(result), ())


@pytest.mark.parametrize('name', ['Medicine', 'program B'])
def test_system_coverage_question_does_not_resolve_a_student_curriculum(name):
    from backend.bintanong_routing.validation import validate_interpretation
    from test_routing_validation import catalog, registry
    text = f'Does Bintanong support {name}?'
    start = text.index(name)
    value = Interpretation.parse(proposal(text=text, route=None, control='system_information',
        mentions=[dict(kind='program', text=name, start=start, end=start+len(name))],
        operations=[], claims=[]))
    result = validate_interpretation(text, ctx(), value, catalog=catalog(), registry=registry())
    assert result.decision.control == 'system_information'
    assert result.decision.predicate_request is None and result.query.entities == ()


def test_mixed_self_information_and_academic_question_asks_for_separate_questions():
    async def scenario():
        text = 'What can you do? How do I remove an INC?'
        value = proposal(text=text, language='en', route=None, control='clarify',
                         intent='system_information_mixed', mentions=[], operations=[], claims=[])
        style = style_proposal('en', english=[text], filipino=[])
        release = resources()
        result = await Orchestrator(FakeTransport(json.dumps(value), style_outputs=[json.dumps(style)]),
            releases=ports().SyntheticReleaseProvider(release)).run(text, ctx())
        answer = await Generator(NoGeneration()).generate(text, result)
        assert answer.status == 'clarification_needed'
        assert 'separate questions' in answer.text
        assert not release.retrieval.calls and not release.symbolic.calls
    asyncio.run(scenario())


def test_compiler_preserves_mixed_question_clarification_without_relying_on_intent_wording():
    from backend.bintanong_routing.compile import compile_reply
    from test_routing_wire import quote
    text = 'What can you do? How do I remove an INC?'
    wire = dict(schema_version='bintanong-interpretation-wire-v4', language='en', audience='undergraduate',
        control='clarify', route=None, intent='system information and procedure query', part_count=2,
        mentions=[], claims=[], operations=[], ambiguities=[], parts=[
            dict(part_id='r1', quote=quote('What can you do?'), evidence_need='unknown', operation_indices=[]),
            dict(part_id='r2', quote=quote('How do I remove an INC?'), evidence_need='document', operation_indices=[])])
    result = compile_reply(wire, text, ctx())
    assert result.control == 'clarify' and result.intent == 'system_information_mixed'
    assert not result.operations and not result.parts


def test_selected_policy_topic_cannot_override_mixed_question_clarification(monkeypatch):
    from test_routing_topic_selection import Transport, selected, run
    monkeypatch.setenv('BINTANONG_ROUTER_COMPILE', '1')
    text = 'What can you do? Where do I file slip S?'
    value = proposal(text=text, language='en', route=None, control='clarify',
        intent='system information and procedure query', mentions=[], operations=[], claims=[], parts=[])
    for key, words, need in [('r1', 'What can you do?', 'unknown'),
                             ('r2', 'Where do I file slip S?', 'document')]:
        value['parts'].append(dict(part_id=key, text=words, start=text.index(words),
            end=text.index(words)+len(words), evidence_need=need, operation_indices=[],
            subject_id='fictional_office' if need=='document' else None,
            requested_claims=['filing office'] if need=='document' else []))
    result, _ = run(Transport(selected(), json.dumps(value), text=text), text=text)
    assert result.decision.control == 'clarify' and result.decision.route is None
    assert result.decision.missing_facts == ('separate_system_question',)
