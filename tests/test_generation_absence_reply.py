"""Owner 2 Nov 2026 (#3, p or q): an absence answer gives the excuse-slip rule and then the "if you were sick" branch,
quoted from the retrieved sickness record. Fictional card wrappers around printed-style text."""
import json
from types import SimpleNamespace

import pytest

from backend.bintanong_generation.absence_reply import sickness_branch

SICK = ('Certificate of sickness will be issued only to those who went to PSU clinic for consultation and treatment of '
        'the illness to be certified. Otherwise, they have to obtain certificate of sickness from their attending '
        'physicians.')


def card(evidence_id, body):
    return SimpleNamespace(evidence_id=evidence_id, kind='document', citations=(),
                           text=json.dumps(dict(fields=[dict(name='body', source_blank=False, value=body)])))


CARDS = (card('ev-a', 'ABSENCE. Any student who is absent must obtain an excuse slip.'),
         card('ev-s', 'A.8. ' + SICK + ' A.9. Fictional next rule.'))
PART = SimpleNamespace(subject_id='handbook_attendance', text='umabsent ako kahapon, ano kailangan ko gawin?')
SLIP = SimpleNamespace(text='Kumuha ka ng excuse slip.', evidence_ids=('ev-a',))


@pytest.mark.parametrize('language,expected', [('taglish', f'Kung may sakit ka: "{SICK}"'),
                                               ('en', f'If you were sick: "{SICK}"')])
def test_the_sickness_branch_follows_the_excuse_slip_answer(language, expected):
    extra = sickness_branch(SimpleNamespace(language=language, cards=CARDS), PART, (SLIP,))
    assert extra == dict(text=expected, evidence_ids=['ev-s'])


def test_no_branch_when_the_answer_already_cites_the_sickness_record_or_is_not_about_absence():
    pack = SimpleNamespace(language='en', cards=CARDS)
    assert sickness_branch(pack, PART, (SLIP, SimpleNamespace(text='x', evidence_ids=('ev-s',)))) is None
    other = SimpleNamespace(subject_id='handbook_attendance', text='how is attendance counted?')
    assert sickness_branch(pack, other, (SLIP,)) is None
    assert sickness_branch(SimpleNamespace(language='en', cards=CARDS[:1]), PART, (SLIP,)) is None
