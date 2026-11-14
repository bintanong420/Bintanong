"""A thank-you (router control greeting) gets "you're welcome", not "Hello" (owner f-list, 24-25 Oct 2026)."""
import asyncio

import pytest

from backend.bintanong_generation.generator import Generator
from backend.bintanong_orchestration.contracts import IntegrationResult
from test_generation_loop import Fake


def greeting(language):
    return IntegrationResult(understanding=None, schema_version=IntegrationResult.SCHEMA_VERSION, request_id='req-a',
                             route=None, response_style=language, status='greeting', evidence=None, events=())


def reply(text, language):
    return asyncio.run(Generator(Fake()).generate(text, greeting(language)))


@pytest.mark.parametrize('text,language,expected', [
    ('Thank you po!', 'taglish', 'Walang anuman! Ask ka lang anytime tungkol sa undergraduate academic affairs.'),
    ('thanks', 'en', "You're welcome! Ask me anytime about undergraduate academic affairs."),
    ('Maraming salamat po', 'fil', 'Walang anuman! Ask ka lang anytime tungkol sa undergraduate academic affairs.')])
def test_a_thank_you_gets_a_welcome(text, language, expected):
    answer = reply(text, language)
    assert answer.status == 'greeting' and answer.validation == 'thanks'
    assert expected in answer.text and 'Hello' not in answer.text


def test_a_hello_still_gets_the_greeting():
    answer = reply('Hi', 'en')
    assert 'Hello. I can help' in answer.text and answer.validation == 'control_fallback'
