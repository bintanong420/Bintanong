"""Owner, 29 Oct 2026: reviewed Filipino shorthand is expanded before understanding; codes and PWD stay as typed."""
import asyncio

import pytest

from backend.bintanong_routing.shorthand import expand_shorthand


@pytest.mark.parametrize('typed,expanded', [
    ('pwd ko b i-take ung CS 6 kht d ko npasa ung CC 4/L?', 'pwede ko ba i-take yung CS 6 kahit hindi ko npasa yung CC 4/L?'),
    ('Pno mg drop ng subj?', 'Paano mag drop ng subject?'),
    ('anu residence requirement pra mka-graduate?', 'ano residence requirement para maka-graduate?'),
    ('kelan aq considered 2nd year?', 'kailan ako considered second year?'),
    ('ano prereqs s CC5? anu parusa s pgyoyosi', 'ano prerequisites sa CC5? ano parusa sa paninigarilyo'),
])
def test_reviewed_shortcuts_are_expanded_as_whole_words(typed, expanded):
    assert expand_shorthand(typed) == expanded


@pytest.mark.parametrize('typed', ['PWD discount sa tuition?', 'NCM 15-116 B at AD-3/L', "the student's ID", 'D. Dean'])
def test_codes_uppercase_letters_pwd_and_apostrophes_stay_as_typed(typed):
    assert expand_shorthand(typed) == typed


def test_the_answer_pipeline_understands_the_expanded_text():
    from backend.bintanong_generation.generator import AnswerPipeline
    from test_orchestration_pipeline import ctx
    seen = []

    class Stop(Exception):
        pass

    class Recording:
        async def run(self, text, context):
            seen.append(text); raise Stop
    with pytest.raises(Stop):
        asyncio.run(AnswerPipeline(Recording(), object()).run('pwd b mg drop?', ctx()))
    assert seen == ['pwede ba mag drop?']
