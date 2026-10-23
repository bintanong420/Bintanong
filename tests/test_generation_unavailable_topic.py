"""Owner, 24 Oct 2026 (E1): missing in-scope information gets an honest unavailable reply with a university-office
referral, in the student's language (everyday Filipino, Taglish for Taglish). Synthetic evidence only."""
import asyncio

import pytest

from backend.bintanong_orchestration.contracts import IntegrationResult
from backend.bintanong_orchestration.integration import assemble
from test_generation_loop import Fake, api
from test_orchestration_integration import documents, pin

REFERRAL = {'en': 'university office', 'fil': 'opisina ng unibersidad', 'taglish': 'university office'}


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_topic_outside_the_reviewed_sources_is_unavailable_with_an_office_referral(language):
    evidence = assemble(pin(), 'RAG', documents=documents('needs_subject', passages=[]))
    source = IntegrationResult(understanding=None, schema_version=IntegrationResult.SCHEMA_VERSION, request_id='req-a',
                               route='RAG', response_style=language, status=evidence.status, evidence=evidence,
                               events=())
    answer = asyncio.run(api().Generator(Fake(), explanation_profile='legacy').generate('Fictional procedure?', source))
    assert answer.status == 'insufficient_evidence' and not answer.claims
    assert REFERRAL[language] in answer.text
