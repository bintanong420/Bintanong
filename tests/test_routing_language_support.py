"""Bintanong takes English, Filipino and Taglish only (owner, 25 Oct 2026); a Cebuano question is told so."""
import asyncio
import importlib

import pytest

from backend.bintanong_routing.contracts import Interpretation, RequestContext
from test_routing_contracts import context, proposal
from test_routing_validation import catalog, registry


def validate(text):
    # The model labels Cebuano as Filipino (live 25 Oct), so the proposal itself looks normal.
    value = proposal(text=text, language='fil', route='RAG', operations=[], mentions=[])
    value['parts'] = [dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='document',
                           operation_indices=[])]
    return importlib.import_module('backend.bintanong_routing.validation').validate_interpretation(
        text, RequestContext.parse(context()), Interpretation.parse(value), catalog=catalog(),
        registry=registry(), documents_available=True, synthetic=True)


@pytest.mark.parametrize('text', ['Unsaon nako pag-overload sa akong subjects?',
                                  'Maayong buntag! Pila ka units ang CC 5?',
                                  'Kanus-a ang enrollment karon nga semester?'])
def test_a_cebuano_question_is_told_the_supported_languages(text):
    result = validate(text)
    assert result.decision.control == 'clarify' and result.diagnostic == 'unsupported_language'
    assert result.decision.missing_facts == ('language',)


@pytest.mark.parametrize('text', ['Pwede akong mag-overload?', 'Nako, bumagsak ako sa CC 4. Pwede pa ba?',
                                  'Magkano ang special class fee?', 'Where do I submit my documents?'])
def test_filipino_taglish_and_english_questions_are_not_mistaken_for_cebuano(text):
    assert validate(text).diagnostic != 'unsupported_language'


def test_the_reply_names_the_supported_languages():
    from backend.bintanong_generation.generator import Generator
    from backend.bintanong_orchestration.contracts import IntegrationResult
    from test_generation_loop import Fake
    source = IntegrationResult(understanding=None, schema_version=IntegrationResult.SCHEMA_VERSION, request_id='req-a',
        route=None, response_style='fil', status='clarify', evidence=None, events=(), missing_facts=('language',))
    answer = asyncio.run(Generator(Fake()).generate('Unsaon nako pag-overload sa akong subjects?', source))
    assert answer.status == 'clarification_needed'
    assert 'Bintanong answers in English, Filipino and Taglish only.' in answer.text
    assert 'Sumasagot ang Bintanong sa English, Filipino at Taglish lang.' in answer.text
    assert 'Kulang na impormasyon' not in answer.text
