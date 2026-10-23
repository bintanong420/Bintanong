"""Owner-approved style floor (22 October 2026): a question with Filipino grammar words is never
answered as English-only, and a failed-routing clarification still gets the model's style."""
import asyncio
import json

import pytest

from routing_wire_fixtures import wire_fixture
from test_routing_contracts import proposal
from test_routing_router import FakeTransport, run, style_proposal


def answered(text, style):
    return run(FakeTransport(json.dumps(proposal(text=text, language='en')),
                             style_outputs=[json.dumps(style)]), text=text)


def test_english_only_label_with_filipino_grammar_words_becomes_taglish():
    text = 'A1 sa exam, ano ang rule?'
    result = answered(text, style_proposal('en', english=['exam'], filipino=[]))
    assert result.diagnostic == 'validated' and result.response_style == 'taglish'
    assert result.style_floor_applied is True
    evidence = result.style_evidence
    assert evidence.preferred_response_style == 'taglish'
    assert evidence.english_fragments == ('exam',)
    assert set(evidence.filipino_fragments) == {'sa', 'ang'}  # 'ano' is not on the list
    evidence.ground(text)  # host fragments are literal substrings of the question


@pytest.mark.parametrize('text', ['A1 rules for BA students?', 'A1 MA and SI units', 'A1 may 2026 fee'])
def test_english_questions_and_acronyms_keep_the_english_label(text):
    result = answered(text, style_proposal('en', english=['A1'], filipino=[]))
    assert result.response_style == 'en' and result.style_floor_applied is False


@pytest.mark.parametrize('language', ['fil', 'taglish'])
def test_floor_never_changes_filipino_or_taglish_labels(language):
    text = 'A1 sa exam'
    style = style_proposal(language, english=['exam'] if language == 'taglish' else [], filipino=['sa'])
    result = answered(text, style)
    assert result.response_style == language and result.style_floor_applied is False


def wrong_reference(text, target):
    value = wire_fixture(proposal(text=text), text)
    value['operations'][0]['target'] = dict(text=target, occurrence=0)
    return json.dumps(value)


TEXT = 'A1 ang patakaran'


def test_failed_reference_clarification_still_runs_the_style_call():
    bad = wrong_reference(TEXT, 'patakaran')
    transport = FakeTransport(bad, bad, style_outputs=[
        json.dumps(style_proposal('fil', english=[], filipino=['ang patakaran']))])
    result = run(transport, text=TEXT)
    assert result.diagnostic == 'invalid_reference' and not result.decision.dispatchable
    assert result.response_style == 'fil' and result.style_attempts == 1
    assert len(transport.calls) == 3


@pytest.mark.parametrize('style_output', ['bad json',
    json.dumps(style_proposal('fil', english=[], filipino=['invented']))])
def test_failed_style_on_the_clarification_path_keeps_unknown_without_a_repair(style_output):
    bad = wrong_reference(TEXT, 'patakaran')
    transport = FakeTransport(bad, bad, style_outputs=[style_output])
    result = run(transport, text=TEXT)
    assert result.diagnostic == 'invalid_reference' and result.response_style == 'unknown'
    assert len(transport.calls) == 3


def test_style_timeout_on_the_clarification_path_keeps_the_clarification():
    from backend.bintanong_routing.transport import RuntimeFailure
    bad = wrong_reference(TEXT, 'patakaran')
    result = run(FakeTransport(bad, bad, style_outputs=[RuntimeFailure('model_timeout')]), text=TEXT)
    assert result.diagnostic == 'invalid_reference' and result.response_style == 'unknown'


def test_format_failures_do_not_spend_a_style_call():
    transport = FakeTransport('bad', 'still bad')
    assert run(transport).diagnostic == 'invalid_model_output' and len(transport.calls) == 2


def test_orchestrator_clarification_carries_the_students_style():
    from backend.bintanong_orchestration.orchestrator import Orchestrator
    from test_orchestration_pipeline import ports, resources, ctx
    bad = wrong_reference(TEXT, 'patakaran')
    transport = FakeTransport(bad, bad, style_outputs=[
        json.dumps(style_proposal('fil', english=[], filipino=['ang patakaran']))])
    result = asyncio.run(Orchestrator(transport,
        releases=ports().SyntheticReleaseProvider(resources())).run(TEXT, ctx()))
    assert result.status == 'clarify' and result.response_style == 'fil'


def test_generation_and_routing_share_one_function_word_list():
    from backend.bintanong_generation import part_answers
    from backend.bintanong_routing import style
    assert part_answers.has_filipino_function_word is style.has_filipino_function_word


def test_rejected_interpretation_never_becomes_the_request_understanding():
    from backend.bintanong_orchestration.orchestrator import Orchestrator
    from test_orchestration_pipeline import ports, resources, ctx
    bad = wrong_reference(TEXT, 'patakaran')
    transport = FakeTransport(bad, bad, style_outputs=[
        json.dumps(style_proposal('fil', english=[], filipino=['ang patakaran']))])
    result = asyncio.run(Orchestrator(transport,
        releases=ports().SyntheticReleaseProvider(resources())).run(TEXT, ctx()))
    assert result.understanding is None


def test_topic_rejection_keeps_style_but_orchestrator_drops_the_rejected_parts(monkeypatch):
    from test_routing_document_topics import MENU, TEXT as TOPIC_TEXT, answer, model
    rejected = answer(claims=('printed fee amount',))
    routed = run(model(rejected, rejected), text=TOPIC_TEXT, topics=MENU)
    assert routed.diagnostic == 'invalid_reference' and routed.response_style == 'en'
    assert routed.proposed is not None and routed.style_evidence is not None

    from backend.bintanong_orchestration import orchestrator
    from test_orchestration_pipeline import ports, resources, ctx

    class Stub:
        def __init__(self, *a, **k): pass
        async def route(self, text, context): return routed
    monkeypatch.setattr(orchestrator, 'Router', Stub)
    result = asyncio.run(orchestrator.Orchestrator(FakeTransport(),
        releases=ports().SyntheticReleaseProvider(resources())).run(TOPIC_TEXT, ctx()))
    assert result.status == 'clarify' and result.response_style == 'en'
    assert result.understanding is None


# Owner O5 (23 Oct 2026): the symmetric floor. A Filipino label on a question with literal English grammar or
# number words becomes Taglish. Quoted text and catalog names (course titles can hold "and") never count.
def test_filipino_label_with_english_grammar_words_becomes_taglish():
    text = 'A1: pwede ba after ng exam?'
    result = answered(text, style_proposal('fil', english=[], filipino=['pwede ba']))
    assert result.response_style == 'taglish' and result.style_floor_applied is True
    evidence = result.style_evidence
    assert evidence.english_fragments == ('after',) and evidence.filipino_fragments == ('pwede ba',)
    evidence.ground(text)


def test_english_number_and_ordinal_words_count_as_english():
    text = 'A1: kailan ang deadline sa second semester?'
    result = answered(text, style_proposal('fil', english=[], filipino=['kailan ang']))
    assert result.response_style == 'taglish' and result.style_evidence.english_fragments == ('second',)


def test_quoted_text_is_not_the_students_own_english():
    text = 'A1: ano ang kasunod ng "Office for"?'
    result = answered(text, style_proposal('fil', english=[], filipino=['ano ang kasunod']))
    assert result.response_style == 'fil' and result.style_floor_applied is False


def test_words_inside_a_catalog_course_title_do_not_count():
    from test_routing_validation import catalog, entry
    text = 'A1 at Life and Works, pwede ko bang kunin?'
    titled = (*catalog(), entry(entity='course-c', alias='Life and Works'))
    result = run(FakeTransport(json.dumps(proposal(text=text, language='en')),
                               style_outputs=[json.dumps(style_proposal('fil', english=[], filipino=['pwede ko']))]),
                 text=text, catalog=titled)
    assert result.response_style == 'fil' and result.style_floor_applied is False


@pytest.mark.parametrize('text', ['A1: pwede ba FOR IT?', 'A1: may bayad ba at kailan?'])
def test_acronyms_and_filipino_lookalikes_keep_the_filipino_label(text):
    result = answered(text, style_proposal('fil', english=[], filipino=['pwede ba'] if 'pwede' in text else ['may bayad']))
    assert result.response_style == 'fil' and result.style_floor_applied is False


@pytest.mark.parametrize('text', ['A1 at Microbiology and Parasitology, pwede ba?',
                                  'A1 o Life and Works of Rizal, pwede ba?',
                                  'A1 at Mathematics in the Modern World, pwede ba?'])
def test_title_case_names_outside_the_catalog_do_not_count(text):
    # The research catalog holds printed codes only, so course titles are masked as Title Case names.
    result = answered(text, style_proposal('fil', english=[], filipino=['pwede ba']))
    assert result.response_style == 'fil' and result.style_floor_applied is False


def test_lowercase_english_next_to_a_title_still_counts():
    text = 'A1 at Life and Works, pwede ba after ng midterm?'
    result = answered(text, style_proposal('fil', english=[], filipino=['pwede ba']))
    assert result.response_style == 'taglish' and result.style_evidence.english_fragments == ('after',)
