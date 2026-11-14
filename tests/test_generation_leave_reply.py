"""Owner 2 Nov 2026: "how long can a leave of absence be" leads with the printed limit, quoted, then the printed rule.
Live, a draft that buried the limit mid-sentence was rejected on some runs. Fictional wrappers around printed-style text."""
import json
from types import SimpleNamespace

import pytest

from backend.bintanong_generation.leave_reply import leave_reply

RULE = ('Leave of absence shall be applied for in writing before the start of the semester. The application indicating '
        'the reason for the leave and the period which must not exceed one (1) academic year, shall be submitted to '
        'the Department Chair concerned for appropriate action and shall be subject to approval by the Dean.')
BODY = 'LEAVE OF ABSENCE APPLICATION AND NOTIFICATION. ' + RULE + ' A student who is on leave of absence shall not.'
PACK = SimpleNamespace(language='en', cards=(SimpleNamespace(evidence_id='ev-l', kind='document', citations=(),
                       text=json.dumps(dict(fields=[dict(name='body', source_blank=False, value=BODY)]))),))


@pytest.mark.parametrize('language,first,second', [
    ('en', 'The Student Handbook says a leave of absence application indicates "the period which must not exceed one '
           '(1) academic year".', f'The full printed rule: "{RULE}"'),
    ('taglish', 'Ayon sa Student Handbook, ang leave of absence application ay nagsasabi ng "the period which must not '
                'exceed one (1) academic year".', f'Ang buong printed rule: "{RULE}"')])
def test_the_printed_limit_comes_first_then_the_rule(language, first, second):
    part = SimpleNamespace(subject_id='handbook_leave', text='How long can a leave of absence be?')
    claims = leave_reply(SimpleNamespace(language=language, cards=PACK.cards), part)
    assert claims == (dict(text=first, evidence_ids=['ev-l']), dict(text=second, evidence_ids=['ev-l']))


@pytest.mark.parametrize('text', ['How do I apply for a leave of absence?', 'How long is maternity leave?'])
def test_other_leave_questions_are_left_to_the_draft(text):
    assert leave_reply(PACK, SimpleNamespace(subject_id='handbook_leave', text=text)) is None


def test_taglish_length_wording_is_recognised():
    part = SimpleNamespace(subject_id='handbook_leave', text='Gaano katagal pwede ang leave of absence?')
    assert leave_reply(PACK, part) is not None
