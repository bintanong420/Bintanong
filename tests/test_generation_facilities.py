"""General facility guidance and a specific library workflow keep separate scopes."""
import asyncio
import json

import pytest

from backend.bintanong_generation.generator import Generator
from test_generation_evidence import integrated
from test_generation_research import NoModel
from test_generation_service_steps import FIRST, SECOND, record

TEXT = 'How do we reserve a room for our fictional club?'
GENERAL = record(('body', '6. How to avail the use of university rooms and facilities? '
    'A. Submit fictional Form R to the Fictional Coordinator. B. Follow the agreed fictional terms.'))


def integration(picked='charter_library_facilities', language='en'):
    original = integrated('RAG', text=TEXT, response_style=language)
    value = original.model_dump(mode='json')
    passages = value['evidence']['documents']['passages']
    member = value['evidence']['pin']['documents'][0]
    ids = [f'{n:064x}' for n in range(1, 4)]
    value['evidence']['documents']['passages'] = [dict(passages[0], chunk_id=c, text=t)
        for c, t in zip(ids, (FIRST, SECOND, GENERAL))]
    value['evidence']['pin']['documents'] = [dict(member, chunk_id=c) for c in ids]
    claims = {'charter_library_facilities': 'printed library facilities fields',
              'handbook_student_faq': 'printed student faq fields'}
    value['understanding']['parts'][0].update(subject_id=picked, requested_claims=[claims[picked]], detail='whole')
    value['evidence']['documents']['record_coverage'] = [
        dict(subject_id=s, claim=c, chunk_ids=ids[:2] if s == 'charter_library_facilities' else ids[2:])
        for s, c in claims.items()]
    return type(original).parse(value)


@pytest.mark.parametrize('picked', ['handbook_student_faq', 'charter_library_facilities'])
@pytest.mark.parametrize('language', ['en', 'taglish'])
def test_both_sources_are_quoted_with_library_scope_explicit(picked, language):
    answer = asyncio.run(Generator(NoModel()).generate(TEXT, integration(picked, language)))
    assert answer.status == 'answered'
    assert 'Fictional Coordinator' in answer.text and 'agreed fictional terms' in answer.text
    assert ('Library-specific' if language == 'en' else 'Para lang sa library') in answer.text
    assert 'Pay the fee' in answer.text and 'Present the receipt' in answer.text
    assert len(answer.citations) == 3
