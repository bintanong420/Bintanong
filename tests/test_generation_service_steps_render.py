"""Host-rendered printed steps: verbatim values, English/Taglish frames, claim/evidence limits."""
import json

from backend.bintanong_generation.service_steps import parse_service, render_service
from test_generation_service_steps import FIRST, SECOND, limited, record


def table(*extra):
    return parse_service([('e1', FIRST), ('e2', SECOND), *extra])


def test_english_reply_lists_checklist_steps_actions_and_printed_total_verbatim():
    claims = render_service(table(), 'en')
    overview, *steps = claims
    assert overview == ('2. ISSUANCE OF FICTIONAL CERTIFICATE (Fictional Office). Requirements: '
                        'Student ID (1 copy) — where to secure: Student; Copy of record — where to secure: Client.', ('e1',))
    text = ' '.join(t for t, _ in steps)
    assert ('Step 1: 1. Pay the fee. Fee: Php 100.00. Office actions: 1.1. Receive payment; 1.2. Issue receipt '
            '(Cashier, Cashier Office, 5 minutes).') in text
    assert 'Step 2: 2. Present the receipt. Fee: None. Office actions: 2. Check the record (Counselor, OSAS, 10 minutes).' in text
    assert text.endswith('Printed total: Php 100.00; 16 minutes.')


def test_taglish_frame_keeps_source_words_in_english():
    text = ' '.join(t for t, _ in render_service(table(), 'taglish'))
    assert 'Mga kailangan: Student ID (1 copy) — saan kukunin: Student' in text
    assert 'Step 1: 1. Pay the fee. Bayad: Php 100.00. Gagawin ng office: 1.1. Receive payment' in text
    assert 'Kabuuan ayon sa printed table: Php 100.00; 16 minutes.' in text


def test_claims_stay_within_the_claim_budget_and_cite_their_own_records():
    claims = render_service(table(), 'en', max_claims=2)
    assert len(claims) == 2 and claims[1][1] == ('e1', 'e2')
    assert all(len(ids) <= 8 for _, ids in claims)


def test_source_limits_and_blank_cells_are_stated_not_hidden():
    with_limit = parse_service([('e1', FIRST), ('e2', limited('printed_total_discrepancy'))])
    assert render_service(with_limit, 'en')[-1][0].endswith(
        'Source limitation: Unavailable information: fictional printed_total_discrepancy.')
    blank = parse_service([('e1', record(('step1_client_step', '1. Pay'), ('step1_fee', ''), ('step1_action', '1. Receive')))])
    assert 'Fee: (blank in the printed table).' in render_service(blank, 'en')[-1][0]


def test_too_many_records_for_the_claim_budget_renders_nothing():
    many = [(f'e{n}', record((f'step{n}_client_step', f'{n}. Do'), (f'step{n}_action', f'{n}. Act'))) for n in range(1, 10)]
    assert render_service(parse_service(many), 'en', max_claims=1) is None  # nine records cannot fit one claim


def test_each_step_gets_its_own_claim_when_the_budget_allows():
    claims = render_service(table(), 'en')
    assert len(claims) == 4 and [t.split(':')[0] for t, _ in claims[1:]] == ['Step 1', 'Step 2', 'Step 3']


def test_claims_never_exceed_the_claim_text_limit():
    long_steps = [(f'e{n}', record((f'step{n}_client_step', f'{n}. ' + 'Long instruction. ' * 30),
                                   (f'step{n}_action', f'{n}. Act'))) for n in range(1, 4)]
    claims = render_service(parse_service(long_steps), 'en', max_claims=3)
    assert claims is None or all(len(t) <= 1200 for t, _ in claims)
    huge = [('e1', record(('step1_client_step', '1. ' + 'Very long. ' * 150), ('step1_action', '1. Act')))]
    assert render_service(parse_service(huge), 'en') is None


def test_printed_values_ending_in_a_period_are_not_doubled():
    ended = parse_service([('e1', record(('requirement1', 'Tests.'), ('where_to_secure1', 'Clinics.'),
                                         ('step1_client_step', '1. Go.'), ('step1_action', '1. Act.')))])
    assert '..' not in ' '.join(t for t, _ in render_service(ended, 'en'))
