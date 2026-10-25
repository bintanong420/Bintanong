"""Owner, 24 Oct 2026 (step 2e follow-up, "Rate + example"): a special class fee question gets one
host-written reply in every language: the printed rate, the printed example, "your own charge is not
stated" and the office referral. No model wording, no arithmetic. Values here are fictional; the host
must copy them from the reviewed evidence fields, never from constants.
"""
import asyncio
import hashlib
import json

import pytest

from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator
from backend.bintanong_orchestration.contracts import IntegrationResult
from test_generation_evidence import integrated

RATE = dict(fields=[dict(name='printed_rate_php_per_hour', source_blank=False, value='11.11')], source_limits=[])
EXAMPLE = dict(fields=[dict(name='lecture_units', source_blank=False, value='2'),
                       dict(name='lecture_hours', source_blank=False, value='36'),
                       dict(name='amount_php_as_printed', source_blank=False, value='999.00')],
               source_limits=[dict(issue='claim_not_stated', resolution='unresolved',
                                   affected_claims=['official individual student assessment'])])
EXPECTED = {
    'en': ['The printed special class rate is PHP 11.11 per hour.',
           'The printed example is a 2-lecture-unit class of 36 hours: PHP 999.00.',
           'Your own charge is not stated in the source. Please ask the right university office.'],
    'fil': ['Ang naka-print na rate ng special class ay PHP 11.11 kada oras.',
            'Ang naka-print na halimbawa ay klase na may 2 lecture units at 36 oras: PHP 999.00.',
            'Hindi nakasulat sa source kung magkano ang babayaran mo mismo. '
            'Pakitanong sa tamang opisina ng unibersidad.'],
    'taglish': ['Ang printed rate ng special class ay PHP 11.11 per hour.',
                'Ang printed example ay class na 2 lecture units at 36 hours: PHP 999.00.',
                'Hindi naka-state sa source kung magkano ang babayaran mo mismo. '
                'Paki-ask sa tamang university office.']}


class NoModel:
    def __init__(self):
        self.calls = []

    async def infer(self, messages, schema):
        self.calls.append(schema)
        raise AssertionError('the fee reply must not call the model')


def fee_integration(text='How much is the special class fee?', *, language='en', cards=(RATE, EXAMPLE),
                    subject='special_class_fees'):
    value = integrated('RAG', text=text).model_dump(mode='json')
    template = value['evidence']['documents']['passages'][0]
    passages, members = [], []
    for n, card in enumerate(cards, 1):
        chunk = f'{n:064x}'
        passages.append(dict(template, chunk_id=chunk, text=json.dumps(card)))
        members.append(dict(value['evidence']['pin']['documents'][0], chunk_id=chunk))
    value['evidence']['documents']['passages'] = passages
    value['evidence']['pin']['documents'] = members
    value['response_style'] = language
    part = value['understanding']['parts'][0]
    part.update(subject_id=subject, requested_claims=['printed special class rate'])
    assert value['understanding']['question_sha256'] == hashlib.sha256(text.encode()).hexdigest()
    return IntegrationResult.parse(value)


def generate(integration, model, text='How much is the special class fee?'):
    return asyncio.run(Generator(model).generate(text, integration))


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_fee_question_gets_the_host_written_rate_example_and_referral(language):
    model = NoModel()
    answer = generate(fee_integration(language=language), model)
    assert model.calls == []
    assert answer.status == 'answered' and answer.validation == 'validated'
    assert [c.text for c in answer.claims] == EXPECTED[language]
    cards = {c.evidence_id: json.loads(c.text) for c in prepare(fee_integration(language=language)).cards}
    rate, example = (next(i for i, t in cards.items() if t == card) for card in (RATE, EXAMPLE))
    assert [c.evidence_ids for c in answer.claims] == [(rate,), (example,), (example,)]
    assert [(e.part_id, e.claim_ids) for e in answer.part_ledger.entries] == [('r1', ('c1', 'c2', 'c3'))]


def test_fee_reply_never_states_a_computed_total():
    answer = generate(fee_integration(), NoModel())
    assert '399.96' not in answer.text  # 11.11 x 36 would be arithmetic, not a printed value


class DraftModel:
    """Any model call proves the host template was not used."""
    def __init__(self):
        self.calls = []

    async def infer(self, messages, schema):
        self.calls.append(schema)
        payload = json.loads(messages[1]['content'])
        return json.dumps(dict(schema_version='bintanong-part-explanation-v1',
            release_id=payload['evidence']['release_id'], language='en',
            answers=dict(r1=dict(status='not_in_evidence', claims=[]))))


@pytest.mark.parametrize('kwargs', [dict(cards=(EXAMPLE,)), dict(cards=(RATE,)), dict(subject='overload')])
def test_without_both_printed_cards_or_the_fee_topic_the_model_explains(kwargs):
    model = DraftModel()
    answer = generate(fee_integration(**kwargs), model)
    assert model.calls and answer.status == 'insufficient_evidence'


# Mixed messages (owner "Answer what's covered"): a fee part keeps the host reply; the model explains the rest.
from test_generation_part_slots import OFFICE, PartModel
from test_request_understanding_pipeline import TEXT, source


def mixed(route='RAG'):
    value = source(route=route).model_dump(mode='json')
    first = value['evidence']['documents']['passages'][0]
    member = value['evidence']['pin']['documents'][0]
    extra = [(f'{n:064x}', json.dumps(card)) for n, card in enumerate((RATE, EXAMPLE), 2)]
    value['evidence']['documents']['passages'] = [first] + [dict(first, chunk_id=c, text=t) for c, t in extra]
    value['evidence']['pin']['documents'] = [member] + [dict(member, chunk_id=c) for c, _ in extra]
    fee = next(p for p in value['understanding']['parts'] if p['part_id'] == 'r2')
    fee.update(subject_id='special_class_fees', requested_claims=['printed special class rate'])
    return IntegrationResult.parse(value)


def test_fee_part_of_a_mixed_message_gets_the_host_claims_and_the_model_explains_the_rest():
    model = PartModel(slots=dict(r1=('answered', [OFFICE])))
    answer = asyncio.run(Generator(model).generate(TEXT, mixed()))
    assert answer.status == 'answered' and [c.text for c in answer.claims] == [OFFICE, *EXPECTED['en']]
    draft_schema, review_schema = (call[1] for call in model.calls)
    assert draft_schema['properties']['answers']['required'] == ['r1']
    assert draft_schema['$defs']['PartSlot']['properties']['claims']['maxItems'] == 5  # 8 minus 3 host claims
    assert review_schema['properties']['parts']['required'] == ['r1']
    assert review_schema['$defs']['ClaimVerdict']['properties']['claim_id']['enum'] == ['c1']  # host claims unreviewed
    assert [(e.part_id, e.claim_ids) for e in answer.part_ledger.entries] == [
        ('r1', ('c1',)), ('r2', ('c2', 'c3', 'c4'))]


def test_fee_part_is_answered_when_the_other_part_is_unavailable():
    model = PartModel(slots=dict(r1=('not_in_evidence', [])))
    answer = asyncio.run(Generator(model).generate(TEXT, mixed()))
    assert answer.status == 'answered' and [c.text for c in answer.claims] == EXPECTED['en']
    assert answer.part_ledger.status == 'some_parts_unavailable' and len(model.calls) == 1
    assert 'The part about "Where do I file Form Q" is not' in answer.text


def test_hybrid_check_with_a_fee_part_needs_no_model_call():
    model = NoModel()
    answer = asyncio.run(Generator(model).generate(TEXT, mixed('Hybrid')))
    assert model.calls == [] and answer.status == 'answered' and answer.decision is not None
    assert [c.text for c in answer.claims] == EXPECTED['en']
    assert answer.part_ledger.canonical_parts == ('r1',)


# Owner, 25 Oct 2026 (roster 18, accepted T2): a question whether the fee still applies (now or for a school year)
# gets the memo's printed date, "cannot confirm it still applies" and the office referral; no rate.
CURRENCY = {
    'en': ('Are the special-class fees still in effect for 2026–2027?',
           ["The special class fee in Bintanong's reviewed sources comes from a memo dated 1 January 2001.",
            'Bintanong cannot confirm whether it still applies now or for the school year you asked about. '
            'Please ask the right university office.']),
    'fil': ('May bisa pa ba ang mga bayarin sa special class para sa 2026–2027?',
            ['Ang special class fee sa mga na-review na source ng Bintanong ay galing sa memo na may petsang '
             '1 January 2001.',
             'Hindi makumpirma ng Bintanong kung may bisa pa ito ngayon o sa school year na tinanong mo. '
             'Pakitanong sa tamang opisina ng unibersidad.']),
    'taglish': ('Applicable pa ba ang special-class fees ngayong 2026–2027?',
                ['Yung special class fee sa reviewed sources ng Bintanong ay galing sa memo na dated 1 January 2001.',
                 'Hindi ma-confirm ng Bintanong kung valid pa ito ngayon o sa school year na tinanong mo. '
                 'Paki-ask sa tamang university office.'])}


@pytest.fixture
def memo_date(monkeypatch):
    from backend.bintanong_generation import fee_reply
    version = fee_integration().evidence.documents.passages[0].citations[0].version_id
    monkeypatch.setattr(fee_reply, 'MEMO_DATES', {version: '1 January 2001'})


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_a_question_whether_the_fee_still_applies_gets_the_memo_date_and_referral_without_the_rate(language, memo_date):
    text, expected = CURRENCY[language]
    model = NoModel()
    answer = generate(fee_integration(text, language=language), model, text)
    assert model.calls == [] and answer.status == 'answered'
    assert [c.text for c in answer.claims] == expected
    assert '11.11' not in answer.text and '999.00' not in answer.text


def test_without_a_reviewed_memo_date_the_currency_reply_states_no_date():
    text, expected = CURRENCY['en']
    answer = generate(fee_integration(text), NoModel(), text)
    assert [c.text for c in answer.claims] == expected[1:]
