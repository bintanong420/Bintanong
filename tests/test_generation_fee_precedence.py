"""Owner 2 Nov 2026 (#10): the Citizen's Charter fee comes first; the older Handbook figure is shown for transparency.
Fictional card wrappers around the two printed amounts; the host reply quotes only what the cards print."""
import json
from types import SimpleNamespace

import pytest

from backend.bintanong_generation.fee_precedence import HELD, fee_precedence_reply

CHARTER = dict(fields=[dict(name='step2_client_step', value='Pay the overdue fines to the librarian', source_blank=False),
                       dict(name='step2_fee', value='Php 10.00/day for overdue', source_blank=False)],
               source_limits=[dict(issue='claim_not_stated', resolution='unresolved', affected_claims=[HELD])])
HANDBOOK = dict(fields=[dict(name='body', source_blank=False, value=(
    'FINES ● Materials returned late are subject to overdue fines: General Circulation Books – Php 2.00/day '
    'Reserved Books ● The fine is charged when the University Library is open for service.'))], source_limits=[])


def card(evidence_id, content, filename):
    return SimpleNamespace(evidence_id=evidence_id, kind='document', text=json.dumps(content),
                           citations=(SimpleNamespace(filename=filename),))


def pack(language='en', cards=None):
    return SimpleNamespace(language=language, cards=cards if cards is not None else (
        card('ev-c', CHARTER, 'PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition.pdf'),
        card('ev-h', HANDBOOK, 'PSU Student Handbook.pdf')))


ASKED = SimpleNamespace(requested_claims=(HELD,))
EXPECTED = {
    'en': ("The overdue fine is Php 10.00/day, per the Citizen's Charter 2025 (University Library, Returning of Books).",
           'Heads-up: the older Student Handbook (2021) lists "General Circulation Books – Php 2.00/day" and doesn\'t '
           'print the Reserved Books amount. Please confirm with the University Library.'),
    'taglish': ("Ang overdue fine ay Php 10.00/day, ayon sa Citizen's Charter 2025 (University Library, Returning of Books).",
                'Heads-up: sa mas lumang Student Handbook (2021), "General Circulation Books – Php 2.00/day" ang nakalista, '
                'at walang naka-print na amount para sa Reserved Books. Paki-confirm sa University Library.')}


@pytest.mark.parametrize('language', ['en', 'taglish', 'fil'])
def test_the_charter_fine_leads_and_the_handbook_fine_is_disclosed(language):
    first, second = fee_precedence_reply(pack(language), ASKED)
    assert (first['text'], second['text']) == EXPECTED['taglish' if language == 'fil' else language]
    assert first['evidence_ids'] == ['ev-c'] and second['evidence_ids'] == ['ev-h']


def test_the_reply_still_works_after_the_owner_resolved_note_is_removed_from_the_card():
    cards = (card('ev-c', dict(CHARTER, source_limits=[]), 'PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition.pdf'),
             card('ev-h', HANDBOOK, 'PSU Student Handbook.pdf'))
    first, _ = fee_precedence_reply(pack(cards=cards), ASKED)
    assert first['evidence_ids'] == ['ev-c']


def test_without_the_held_claim_nothing_changes():
    assert fee_precedence_reply(pack(), SimpleNamespace(requested_claims=('printed returns fields',))) is None


@pytest.mark.parametrize('missing', ['handbook', 'charter', 'edition'])
def test_a_missing_printed_amount_or_edition_keeps_the_old_behaviour(missing):
    cards = list(pack().cards)
    if missing == 'handbook':
        cards.pop()
    elif missing == 'charter':
        cards[0] = card('ev-c', dict(CHARTER, fields=CHARTER['fields'][:1]), cards[0].citations[0].filename)
    else:
        cards[0] = card('ev-c', CHARTER, 'Citizens-Charter-2023.pdf')
    assert fee_precedence_reply(pack(cards=tuple(cards)), ASKED) is None


def test_the_orchestrator_fetches_both_printed_records_for_the_held_claim():
    from backend.bintanong_orchestration.orchestrator import FEE_PRECEDENCE, _topic_intents
    assert HELD in FEE_PRECEDENCE
    part = SimpleNamespace(evidence_need='document', subject_id='charter_returns', requested_claims=(HELD,),
                           text='Magkano ang multa?')
    intents = _topic_intents(SimpleNamespace(parts=(part,)))
    assert [i['subject_id'] for _, i in intents] == ['charter_returns', 'handbook_library']
    assert [i['requested_claims'] for _, i in intents] == [('printed returns fields',), ('printed library fields',)]
    assert all(words == 'Magkano ang multa?' for words, _ in intents)


def test_other_topics_keep_their_intents():
    from backend.bintanong_orchestration.orchestrator import _topic_intents
    part = SimpleNamespace(evidence_need='document', subject_id='fees', requested_claims=('printed amount',), text='q')
    assert _topic_intents(SimpleNamespace(parts=(part,))) == [(None, dict(subject_id='fees',
                                                                         requested_claims=('printed amount',)))]
