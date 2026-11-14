"""Host-rendered printed steps: verbatim values one column per line, Tagalog lead-ins only for
Taglish replies, defects shown as printed with a note, ProseClaim limits respected."""
from backend.bintanong_generation.service_steps import parse_service, render_service
from test_generation_service_steps import FIRST, SECOND, limited, record


def table(*extra):
    return parse_service([('e1', FIRST), ('e2', SECOND), *extra])


# Owner 3 Nov 2026 ("go"): a plain lead, "What to bring", one line per step with its fee, time and office, and the
# office actions in one sentence. Printed values stay verbatim; items the student supplies drop "where to secure".
def test_overview_leads_plainly_and_lists_what_to_bring():
    overview, _ = render_service(table(), 'en')[0]
    assert overview == ("Here's the process for ISSUANCE OF FICTIONAL CERTIFICATE at the Fictional Office, based on "
                        "the Citizen's Charter.\nWhat to bring:\n- Student ID (1 copy)\n- Copy of record")


def test_each_step_is_one_line_with_its_fee_time_and_office_then_the_office_actions():
    claims = render_service(table(), 'en')
    assert claims[1] == ('Steps:\n1. Pay the fee\n   Fee: Php 100.00 · about 5 minutes · Cashier Office (Cashier)\n'
                         '   What the office does: Receive payment; Issue receipt.', ('e1',))
    assert claims[3][0] == ('3. Receive the certificate\n   about 1 minute · OSAS (Counselor)\n'
                            '   What the office does: Seal it.\nTotal: Php 100.00 · about 16 minutes')


def test_a_secured_item_names_where_it_comes_from():
    extra = record(('requirement2', 'Official Receipt'), ('where_to_secure2', 'Cashier Office'))
    overview = render_service(parse_service([('e1', FIRST), ('e2', SECOND), ('e3', extra)]), 'en')[0][0]
    assert '- Official Receipt (from Cashier Office)' in overview
    unspaced = record(('step1_client_step', '1. Pay'), ('step1_subaction1_action', '1.1. Pay'), ('step1_subaction2_action', '1.2.Issue receipt'))
    assert 'What the office does: Pay; Issue receipt.' in render_service(parse_service([('e1', unspaced)]), 'en')[-1][0]


def test_taglish_uses_tagalog_lead_ins_but_keeps_english_source_data():
    claims = render_service(table(), 'taglish')
    assert claims[0][0] == ("Ito ang process para sa ISSUANCE OF FICTIONAL CERTIFICATE sa Fictional Office, ayon sa "
                            "Citizen's Charter.\nDalhin:\n- Student ID (1 copy)\n- Copy of record")
    assert claims[1][0].startswith('Steps:\n1. Pay the fee\n   Fee: Php 100.00 · mga 5 minutes · Cashier Office (Cashier)\n'
                                   '   Gagawin ng office: Receive payment; Issue receipt.')
    assert 'Walang fee' in claims[2][0]
    assert render_service(table(), 'fil') == claims

def test_printed_defects_are_shown_as_printed_with_the_original_document_note():
    held = parse_service([('e1', FIRST), ('e2', limited('malformed_source_condition'))])
    last = render_service(held, 'en')[-1][0]
    assert last.endswith('Source limitation: Unavailable information: fictional malformed_source_condition.\n'
                         "Note: these steps are shown exactly as printed in the Citizen's Charter; any "
                         'inconsistency comes from the original document.')
    tag = render_service(held, 'taglish')[-1][0]
    assert tag.endswith("Note: Ipinapakita ito nang eksakto gaya ng nakaprint sa Citizen's Charter; anumang "
                        'inconsistency ay galing mismo sa original na dokumento.')


def test_blank_cells_are_stated_and_printed_periods_are_not_doubled():
    blank = parse_service([('e1', record(('requirement1', 'Tests.'), ('where_to_secure1', 'Clinics.'),
                                         ('step1_client_step', '1. Pay.'), ('step1_fee', ''), ('step1_action', '1. Receive.')))])
    text = '\n'.join(t for t, _ in render_service(blank, 'en'))
    assert 'Fee: (blank in the printed table)' in text and '..' not in text


def test_claims_respect_budget_text_and_record_limits():
    claims = render_service(table(), 'en', max_claims=2)
    assert len(claims) == 2 and claims[1][1] == ('e1', 'e2')
    many = [(f'e{n}', record((f'step{n}_client_step', f'{n}. Do'), (f'step{n}_action', f'{n}. Act'))) for n in range(1, 10)]
    assert render_service(parse_service(many), 'en', max_claims=1) is None  # nine records cannot fit one claim
    huge = [('e1', record(('step1_client_step', '1. ' + 'Very long. ' * 150), ('step1_action', '1. Act')))]
    assert render_service(parse_service(huge), 'en') is None
    assert all(len(t) <= 1200 and len(ids) <= 8 for t, ids in render_service(table(), 'en'))


def test_a_step_longer_than_one_claim_continues_in_the_next_claim_without_changing_words():
    actions = [(f'step1_subaction{k}_action', f'1.{k}. ' + 'Verify the submitted document carefully. ' * 6)
               for k in range(1, 7)]
    long_step = parse_service([('e1', record(('step1_client_step', '1. Submit'), *actions,
                                             ('step1_shared_time', '1 day')))])
    claims = render_service(long_step, 'en')
    assert len(claims) >= 2 and all(len(t) <= 1200 for t, _ in claims)
    assert claims[1][0].startswith('Step 1 (continued):\n')
    joined = '\n'.join(t for t, _ in claims)
    line = '   - ' + ('Verify the submitted document carefully. ' * 6).rstrip().rstrip('.')
    assert joined.count(line) == 6 and joined.index('about 1 day') < joined.index(line)


def test_long_checklist_splits_with_exact_item_citations_without_raising_claim_limits():
    records = [('meta', record(('service_title', 'A request')))]
    for n in range(1, 11):
        records.append((f'req{n}', record((f'requirement{n}', f'Item {n}: ' + 'Required document details. ' * 5),
                                        (f'where_to_secure{n}', f'Office {n}'))))
    records.append(('steps', record(('step1_client_step', 'Submit'), ('step1_action', 'Receive'))))
    claims = render_service(parse_service(records), 'taglish')
    assert claims is not None and len(claims) <= 8
    assert all(len(t) <= 1200 and len(ids) <= 8 for t, ids in claims)
    for n in range(1, 11):
        matching = [(t, ids) for t, ids in claims if f'Item {n}:' in t]
        assert len(matching) == 1 and f'req{n}' in matching[0][1]
    assert 'Dalhin:' in claims[0][0] and ' (kunin sa Office 1)' in claims[0][0]


# Owner 28 Oct 2026: answer only the printed detail that was asked (the whole service when asked for everything).
def test_fee_detail_lists_only_printed_fees_and_the_printed_total():
    # Owner 2 Nov 2026 (#7-8 polish): a plain lead, only the steps that charge, then "the other steps have no fee";
    # a single charge needs no separate total. Printed values stay verbatim.
    claims = render_service(table(), 'en', detail='fees')
    assert claims == (("2. ISSUANCE OF FICTIONAL CERTIFICATE\nHere's the fee for this service:\n"
                       'Step 1: 1. Pay the fee — Fee: Php 100.00\nThe other steps have no fee.', ('e1', 'e2')),)


def test_a_not_stated_note_is_left_out_of_a_fee_answer_and_other_notes_read_as_a_heads_up():
    # Live #7: "Source limitation: Unavailable information: PD907 eligibility ... (claim_not_stated)." reached
    # students for a price question; a note about another fact is left out, a source defect stays as a heads-up.
    other = parse_service([('e1', FIRST), ('e2', limited('claim_not_stated'))])
    text = '\n'.join(t for t, _ in render_service(other, 'en', detail='fees'))
    assert 'claim_not_stated' not in text and 'Source limitation' not in text and 'Note:' not in text
    held = parse_service([('e1', FIRST), ('e2', limited('malformed_source_condition'))])
    text = '\n'.join(t for t, _ in render_service(held, 'en', detail='fees'))
    assert 'Heads-up: fictional malformed_source_condition.' in text and 'Source limitation' not in text


def test_requirements_detail_is_the_checklist_without_steps():
    claims = render_service(table(), 'en', detail='requirements')
    assert claims == (('2. ISSUANCE OF FICTIONAL CERTIFICATE\nOffice: Fictional Office\nRequirements:\n'
                       '- Student ID (1 copy) — where to secure: Student\n- Copy of record — where to secure: Client', ('e1',)),)


def test_time_detail_lists_printed_processing_times_and_total():
    claims = render_service(table(), 'en', detail='processing_time')
    assert claims == (("2. ISSUANCE OF FICTIONAL CERTIFICATE\nHere are the processing times for this service:\n"
                       'Step 1: 1. Pay the fee — Processing time: 5 minutes\n'
                       'Step 2: 2. Present the receipt — Processing time: 10 minutes\n'
                       'Step 3: 3. Receive the certificate\n  3.1. Seal it — Processing time: 1 minute\n'
                       'Total: 16 minutes', ('e1', 'e2')),)


def test_detail_keeps_source_limits_and_taglish_lead_ins():
    held = parse_service([('e1', FIRST), ('e2', limited('malformed_source_condition'))])
    text = '\n'.join(t for t, _ in render_service(held, 'taglish', detail='fees'))
    assert 'Ito ang bayad para dito:' in text and 'Walang bayad sa ibang steps.' in text
    assert 'Heads-up: fictional malformed_source_condition.' in text


def test_whole_detail_is_the_existing_rendering():
    assert render_service(table(), 'en', detail='whole') == render_service(table(), 'en')


def test_a_detail_over_many_records_splits_into_claims_citing_only_its_own_records():
    # Live gate run 1 (28 Oct 2026): the TOR-copy time and admission-test fee slices cited every service
    # record (more than eight), so the detail failed the claim limit and fell back to the whole table.
    many = [(f'e{n}', record((f'step{n}_client_step', f'{n}. Do part {n}'), (f'step{n}_fee', 'None'),
                             (f'step{n}_action', f'{n}. Act'), (f'step{n}_time', f'{n} minutes')))
            for n in range(1, 13)]
    table = parse_service(many)
    for detail in ('fees', 'processing_time'):
        claims = render_service(table, 'en', detail=detail)
        assert claims is not None and len(claims) > 1
        assert all(len(text) <= 1200 and len(ids) <= 8 for text, ids in claims)
        assert all('Office actions' not in text for text, _ in claims)
    fee_claims = render_service(table, 'en', detail='fees')
    assert 'Step 12: 12. Do part 12 — Fee: None' in fee_claims[-1][0]
    assert ('e12',) == tuple(i for i in fee_claims[-1][1] if i == 'e12')


def test_a_fee_answer_over_many_free_steps_still_answers_the_fee():
    # Live 2 Nov 2026 (admission test): "The other steps have no fee." cited more than eight records, so the fee
    # answer was refused and the whole service table was shown. Too many free steps are listed as before instead.
    many = [(f'e{n}', record((f'step{n}_client_step', f'{n}. Do part {n}'),
                             (f'step{n}_fee', 'Php 100.00' if n == 3 else 'None'), (f'step{n}_action', f'{n}. Act')))
            for n in range(1, 12)]
    claims = render_service(parse_service(many), 'en', detail='fees')
    text = '\n'.join(t for t, _ in claims)
    assert claims is not None and 'Fee: Php 100.00' in text and 'Office actions' not in text
    assert all(len(ids) <= 8 for _, ids in claims)


def test_detail_keeps_the_printed_phase_heading_where_step_numbers_restart():
    # Real admission test: application steps 1-5 then "FOR RESULT ISSUANCE" steps 1-3; without the heading the
    # fee/time list read "Step 1 ... Step 1".
    fields = [('service_title', 'APPLICATION AND RESULT'),
              ('application_step1_client_step', '1. Submit'), ('application_step1_action', 'Receive'),
              ('application_step1_fee', 'Php 100.00'),
              ('result_phase_heading', 'FOR RESULT ISSUANCE'),
              ('result_step1_client_step', '1. Claim result'), ('result_step1_action', 'Release result'),
              ('result_step1_fee', 'Php 20.00')]  # both phases charge, so both fee lines are listed
    text = render_service(parse_service([('e', record(*fields))]), 'en', detail='fees')[0][0]
    assert text.index('Step 1: 1. Submit') < text.index('FOR RESULT ISSUANCE') < text.index('Step 1: 1. Claim result')
