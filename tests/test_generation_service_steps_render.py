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
    assert render_service(parse_service(many), 'en', max_claims=2) is None
