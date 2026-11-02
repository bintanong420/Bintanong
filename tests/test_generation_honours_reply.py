"""Owner 2 Nov 2026 (#5): "how long ... to graduate with Latin honors" covers Handbook 5.1.3 and 5.1.4 in full, quoted
exactly from the retrieved cards (the draft dropped rules). Fictional card wrappers around printed-style text."""
import json
from types import SimpleNamespace

import pytest

from backend.bintanong_generation.honours_reply import honours_reply

RESIDENCE = ('5.1.3 RESIDENCE AND UNIT REQUIREMENTS. They must complete the course within the prescribed years. '
             'They must have taken all courses at the university.')
LOAD = ('5.1.4 MINIMUM ACADEMIC LOAD REQUIREMENT. They must have enrolled during each semester not less than the '
        'normal load, unless the lighter load was due to justifiable causes.')
REST = 'It shall be the responsibility of the student to establish the veracity of the cause for under load.'


def card(evidence_id, body):
    return SimpleNamespace(evidence_id=evidence_id, kind='document', citations=(),
                           text=json.dumps(dict(fields=[dict(name='body', source_blank=False, value=body)])))


PACK = SimpleNamespace(language='en', cards=(card('ev-a', '5.1.2 MINIMUM GRADE. Fictional. ' + RESIDENCE + ' ' + LOAD),
                                             card('ev-b', REST + ' 5.1.5 EXEMPLARY BEHAVIOR. Fictional.')))
PART = SimpleNamespace(subject_id='handbook_undergraduate_honors_policy',
                       text='how long do i need to study here to graduate with latin honors?')


def test_the_reply_quotes_both_sections_in_full():
    # Live 2 Nov 2026: a cited lead claim was judged unsupported and sank the answer; the lead is now a host line.
    from backend.bintanong_generation.honours_reply import LEAD
    residence, load = honours_reply(PACK, PART)
    assert LEAD['en'].startswith('To graduate with Latin honors')
    assert residence == dict(text=f'"{RESIDENCE}"', evidence_ids=['ev-a'])
    assert load == dict(text=f'"{LOAD} {REST}"', evidence_ids=['ev-a', 'ev-b'])


@pytest.mark.parametrize('text', ['what grade do I need for cum laude?', 'how long is a leave of absence?'])
def test_other_questions_are_left_to_the_draft(text):
    assert honours_reply(PACK, SimpleNamespace(subject_id=PART.subject_id, text=text)) is None


def test_a_missing_section_keeps_the_draft():
    pack = SimpleNamespace(language='en', cards=(card('ev-a', RESIDENCE),))
    assert honours_reply(pack, PART) is None
