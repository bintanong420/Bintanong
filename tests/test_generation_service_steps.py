"""Strict printed service tables: every field consumed by an explicit grammar, or no table."""
import json

import pytest

from backend.bintanong_generation.service_steps import parse_service


def record(*fields):
    return json.dumps(dict(fields=[dict(name=n, value=v, source_blank=v == '') for n, v in fields],
                           service_group=dict(logical_step_id='S', part_count=2, part_order=0), source_limits=[]))


FIRST = record(('service_title', '2. ISSUANCE OF FICTIONAL CERTIFICATE'), ('office_label', 'Office/Division:'),
               ('office', 'Fictional Office'), ('requirement1', 'Student ID (1 copy)'), ('where_to_secure1', 'Student'),
               ('alumni_requirement', 'Copy of record'), ('alumni_where_to_secure', 'Client'),
               ('step1_client_step', '1. Pay the fee'), ('step1_shared_fee', 'Php 100.00'),
               ('step1_subaction1_action', '1.1. Receive payment'), ('step1_subaction2_action', '1.2. Issue receipt'),
               ('step1_shared_time', '5 minutes'), ('step1_shared_person', 'Cashier'), ('step1_shared_office', 'Cashier Office'))
SECOND = record(('step2_client_step', '2. Present the receipt'), ('step2_fee', 'None'),
                ('step2_action', '2. Check the record'), ('step2_time', '10 minutes'), ('step2_person', 'Counselor'),
                ('step2_office', 'OSAS'), ('step3_client_step', '3. Receive the certificate'),
                ('step3_subaction1_action', '3.1. Seal it'), ('step3_subaction1_time', '1 minute'),
                ('step3_subaction1_person', 'Counselor'), ('step3_subaction1_office', 'OSAS'),
                ('total_label', 'TOTAL'), ('total_fee', 'Php 100.00'), ('total_time', '16 minutes'))


def test_complete_service_becomes_an_ordered_step_table_with_verbatim_values():
    table = parse_service([('e1', FIRST), ('e2', SECOND)])
    assert table.title == '2. ISSUANCE OF FICTIONAL CERTIFICATE' and table.office == 'Fictional Office'
    assert table.checklist == (('Student ID (1 copy)', 'Student'), ('Copy of record', 'Client'))
    first, second, third = table.steps
    assert (first.client_step, first.fee) == ('1. Pay the fee', 'Php 100.00')
    assert [(a.action, a.time, a.person, a.office) for a in first.actions] == [
        ('1.1. Receive payment', '5 minutes', 'Cashier', 'Cashier Office'),
        ('1.2. Issue receipt', '5 minutes', 'Cashier', 'Cashier Office')]
    assert first.shared == ('time', 'person', 'office') and first.evidence_ids == ('e1',)
    assert [(a.action, a.office) for a in second.actions] == [('2. Check the record', 'OSAS')]
    assert third.fee is None and third.actions[0].time == '1 minute'
    assert (table.total_fee, table.total_time) == ('Php 100.00', '16 minutes')
    assert table.evidence_ids == ('e1', 'e2')


def test_a_step_split_across_records_cites_both():
    split = record(('step1_client_step', '1. Pay'), ('step1_subaction1_action', '1.1. Receive'))
    rest = record(('step1_shared_time', '5 minutes'), ('step1_shared_person', 'Cashier'), ('step1_shared_office', 'Office'))
    assert parse_service([('e1', split), ('e2', rest)]).steps[0].evidence_ids == ('e1', 'e2')


@pytest.mark.parametrize('extra', [
    ('step1_continuation_through_step2_shared_person', 'Clerk'),   # unknown shape
    ('step3_subaction1_action', 'Gap before step 2'),               # no step 2/3 client steps
    ('step1_time', '9 minutes'),                                    # conflicts with shared time
    ('application_step1_client_step', 'Another phase'),             # phases need reviewed ordering
])
def test_anything_outside_the_strict_grammar_yields_no_table(extra):
    broken = record(('step1_client_step', '1. Pay'), ('step1_subaction1_action', '1.1. Receive'),
                    ('step1_shared_time', '5 minutes'), extra)
    assert parse_service([('e1', broken)]) is None


def test_a_step_without_any_agency_action_yields_no_table():
    assert parse_service([('e1', record(('step1_client_step', '1. Pay'), ('step1_fee', 'None')))]) is None


def test_blank_source_cells_stay_blank_not_none_or_zero():
    blank = record(('step1_client_step', '1. Pay'), ('step1_fee', ''), ('step1_action', '1. Receive'))
    assert parse_service([('e1', blank)]).steps[0].fee == ''


def limited(issue):
    value = json.loads(SECOND)
    value['source_limits'] = [dict(issue=issue, resolution='unresolved', gap_id='limit-1',
                                   message=f'Unavailable information: fictional {issue}.')]
    return json.dumps(value)


def test_unresolved_source_limits_are_carried_verbatim_with_the_table():
    table = parse_service([('e1', FIRST), ('e2', limited('printed_total_discrepancy'))])
    assert table.limits == ('Unavailable information: fictional printed_total_discrepancy.',)


def test_a_malformed_printed_condition_is_kept_as_printed_with_its_limit():
    # Owner29Oct: show defective printed tables as is, with a note; model interpretation stays held.
    table = parse_service([('e1', FIRST), ('e2', limited('malformed_source_condition'))])
    assert table.limits == ('Unavailable information: fictional malformed_source_condition.',)

@pytest.mark.parametrize('row_start', [1, 2])
def test_explicit_rows_preserve_same_row_columns_and_original_row_numbers(row_start):
    fields = [('service_title_and_description', '1. FICTIONAL BORROWING Description.'),
              ('office_division', 'Office/Division: Library'),
              ('transaction_type', 'G2C'), ('who_may_avail', 'Students'),
              ('requirement1_checklist', 'Library card'), ('requirement1_where_to_secure', 'Client')]
    for row in range(row_start, row_start + 2):
        fields.extend([(f'row{row}_client_step', f'Client row {row}'),
                       (f'row{row}_agency_actions', f'Action row {row}'),
                       (f'row{row}_fees', ''), (f'row{row}_processing_time', f'{row} minutes'),
                       (f'row{row}_person', f'Librarian {row}'), (f'row{row}_office', 'Library')])
    fields.extend([('total_fees', 'None'), ('total_processing_time', '3 minutes')])
    table = parse_service([('e1', record(*fields))])
    assert table is not None
    assert table.checklist == (('Library card', 'Client'),)
    assert [(s.number, s.actions[0].action, s.actions[0].time, s.actions[0].person) for s in table.steps] == [
        (row_start, f'Action row {row_start}', f'{row_start} minutes', f'Librarian {row_start}'),
        (row_start + 1, f'Action row {row_start + 1}', f'{row_start + 1} minutes', f'Librarian {row_start + 1}')]
    assert table.total_fee == 'None' and table.total_time == '3 minutes'


def test_row_grammar_refuses_missing_interior_row_and_mixed_step_names():
    for fields in [
        [('row1_client_step', 'First'), ('row1_agency_actions', 'First action'),
         ('row3_client_step', 'Third'), ('row3_agency_actions', 'Third action')],
        [('row1_client_step', 'First'), ('step1_action', 'Mixed action')],
    ]:
        assert parse_service([('e1', record(*fields))]) is None


def test_scoped_checklists_and_service_notes_keep_their_printed_scope():
    fields = [('service_title_and_note', '1. A SERVICE *Note: a condition'),
              ('registration_description', 'Registration description'),
              ('in_campus_requirements_heading', 'CHECKLIST (In-Campus)'),
              ('in_campus_where_heading', 'WHERE TO SECURE'),
              ('out_of_campus_requirements_heading', 'CHECKLIST (Out of Campus)'),
              ('out_of_campus_where_heading', 'WHERE TO SECURE'),
              ('in_campus_requirement1', 'Program proposal'), ('in_campus_where_to_secure1', 'Organization'),
              ('out_of_campus_requirement1', 'Travel order'), ('out_of_campus_where_to_secure1', 'College'),
              ('second_copy_note', '*Second copy needs a letter'),
              ('step1_client_step', 'Request'), ('step1_action', 'Receive'), ('end_transaction_label', 'End')]
    table = parse_service([('e1', record(*fields))])
    assert table is not None
    from backend.bintanong_generation.service_steps import render_service
    text = '\n'.join(t for t, _ in render_service(table, 'en'))
    assert 'Registration description' in text and '*Second copy needs a letter' in text
    assert text.index('CHECKLIST (In-Campus)') < text.index('Program proposal') < text.index('CHECKLIST (Out of Campus)') < text.index('Travel order')
    assert '1. A SERVICE *Note: a condition' in text


def test_complete_unnumbered_record_rows_keep_their_local_columns_and_printed_total():
    overview = record(('service_title', 'FICTIONAL REQUEST'), ('description', 'Service description'),
                      ('office', 'Central office'), ('conditional_representation_heading', 'If represented:'),
                      ('conditional_authorization', 'Authorization letter'),
                      ('authorization_where_to_secure_shared', 'Client'))
    first = record(('client_step', 'Submit request'), ('agency_action', 'Receive and check'),
                   ('fees_shared', ''), ('processing_time', '4 minutes'),
                   ('person_shared', 'First clerk'), ('office_shared', 'First office'))
    second = record(('client_step', 'Receive response'), ('agency_action', 'Release response'),
                    ('fees', 'None'), ('processing_time', '1 minute'), ('person', 'Second clerk'),
                    ('office', 'Second office'), ('printed_total', 'TOTAL None 5 Minutes'))
    records = []
    for order, (evidence, text) in enumerate([('meta', overview), ('first', first), ('second', second)]):
        body = json.loads(text)
        body['service_group'].update(part_count=3, part_order=order)
        records.append((evidence, json.dumps(body)))
    table = parse_service(records)
    assert table is not None and table.office == 'Central office'
    assert [(s.client_step, s.fee, s.actions[0].person, s.actions[0].office, s.evidence_ids) for s in table.steps] == [
        ('Submit request', '', 'First clerk', 'First office', ('first',)),
        ('Receive response', 'None', 'Second clerk', 'Second office', ('second',))]
    from backend.bintanong_generation.service_steps import render_service
    claims = render_service(table, 'en')
    assert 'If represented: Authorization letter' in claims[0][0]
    assert claims[-1][0].endswith('TOTAL None 5 Minutes')
    assert claims[-1][1] == ('second',)


@pytest.mark.parametrize('fields', [
    [('client_step', 'Submit'), ('processing_time', '1 minute')],
    [('agency_action', 'Receive'), ('person', 'Clerk')],
    [('client_step', 'Submit'), ('agency_action', 'Receive'), ('unknown_pairing', 'Clerk')],
    [('conditional_authorization', 'Letter')],
])
def test_incomplete_record_rows_and_unscoped_conditions_refuse(fields):
    assert parse_service([('e1', record(*fields))]) is None


def test_explicit_shared_ranges_keep_coverage_and_cite_the_range_record():
    a = record(('step1_client_step', 'Request'), ('step1_action', 'Receive'),
               ('step2_client_step', 'Return'), ('step2_subaction1_action', 'Check'),
               ('step2_subaction2_action', 'Sign'), ('step2_subaction3_action', 'Release'))
    ranges = record(('steps1_2_shared_office', 'Office'), ('steps1_2_shared_person', 'Clerk'),
                    ('step2_subactions2_3_time', '5 minutes'))
    table = parse_service([('a', a), ('range', ranges)])
    assert table is not None
    assert [s.evidence_ids for s in table.steps] == [('a', 'range'), ('a', 'range')]
    assert [a.office for s in table.steps for a in s.actions] == ['Office'] * 4
    assert [a.time for a in table.steps[1].actions] == [None, '5 minutes', '5 minutes']


@pytest.mark.parametrize('name', ['steps1_3_shared_person', 'step1_subactions1_2_person'])
def test_shared_ranges_must_not_create_missing_steps_or_actions(name):
    assert parse_service([('e', record(('step1_client_step', 'Ask'), ('step1_action', 'Receive'), (name, 'Clerk')))]) is None


def test_clinical_assistant_conditional_time_and_split_fee_remain_separate():
    fields = [('step1_client_step', 'Request treatment'), ('step1_subaction1_action', 'Examine'),
              ('step1_conditional_time', '10 minutes simple; 25 minutes treatment'),
              ('step1_shared_person', 'Physician'), ('step1_assisting_person', 'Nurse (to assist treatment)'),
              ('step1_fee_start', 'Beneficiaries None; Others –'),
              ('step1_fee_continuation', 'pay upon validation'), ('step1_agency_heading', 'Process documents:')]
    table = parse_service([('e', record(*fields))])
    assert table is not None
    assert table.steps[0].fee == 'Beneficiaries None; Others – pay upon validation'
    assert table.steps[0].actions[0].person == 'Physician'
    from backend.bintanong_generation.service_steps import render_service
    text = '\n'.join(t for t, _ in render_service(table, 'en'))
    assert 'Nurse (to assist treatment)' in text and 'Process documents:' in text
    assert '10 minutes simple; 25 minutes treatment' in text


@pytest.mark.parametrize('fields', [
    [('step1_fee_continuation', 'Missing start')], [('step1_fee_start', 'Missing continuation')],
    [('step1_fee_start', 'Start'), ('step1_fee_continuation', 'End'), ('step1_fee', 'Conflict')],
])
def test_split_fee_requires_both_fragments_and_no_competing_fee(fields):
    assert parse_service([('e', record(('step1_client_step', 'Ask'), ('step1_action', 'Act'), *fields))]) is None

@pytest.mark.parametrize('reverse', [False, True])
def test_mixed_numbered_and_row_grammar_refuses_in_both_record_orders(reverse):
    records = [('row', record(('row1_client_step', 'Ask'), ('row1_agency_actions', 'Receive'))),
               ('step', record(('step2_client_step', 'Return'), ('step2_action', 'Release')))]
    assert parse_service(records[::-1] if reverse else records) is None


def test_unnumbered_rows_follow_explicit_reviewed_group_order_even_when_input_is_shuffled():
    records = []
    for order in range(2):
        body = json.loads(record(('client_step', ['First request', 'Then receive'][order]),
                                 ('agency_action', ['Receive request', 'Release reply'][order])))
        body['service_group'] = dict(logical_step_id='reviewed-sequence', part_count=2, part_order=order)
        records.append((f'e{order}', json.dumps(body)))
    table = parse_service(records[::-1])
    assert table is not None
    assert [s.client_step for s in table.steps] == ['First request', 'Then receive']
    body = json.loads(records[1][1]); body['service_group']['part_order'] = 0
    assert parse_service([records[0], ('duplicate', json.dumps(body))]) is None


def test_explicit_local_and_continuation_scope_keeps_window_only_on_local_actions():
    first = record(('step1_client_step', 'Submit'), ('step1_subaction1_action', 'Receive'),
                   ('step1_subaction2_action', 'Release form'), ('step1_local_person', 'Local clerk'),
                   ('step1_local_office', 'Local office'), ('step1_local_window', 'Window 1'))
    rest = record(('step1_subaction3_action', 'Refer client'),
                  ('step1_continuation_through_step2_shared_person', 'Continuation clerk'),
                  ('step1_continuation_through_step2_shared_office', 'Continuation office'),
                  ('step2_client_step', 'Pay'), ('step2_action', 'Receive payment'))
    table = parse_service([('local', first), ('continuation', rest)])
    assert table is not None
    assert [(a.person, a.office, a.window) for a in table.steps[0].actions] == [
        ('Local clerk', 'Local office', 'Window 1'), ('Local clerk', 'Local office', 'Window 1'),
        ('Continuation clerk', 'Continuation office', None)]
    assert table.steps[1].actions[0].person == 'Continuation clerk'
    assert table.steps[1].evidence_ids == ('continuation',)


def test_same_number_staff_pairs_stay_separate_without_splitting_joint_labels():
    fields = [('step1_client_step', 'Request'), ('step1_subaction1_action', 'Issue form and receipt'),
              ('step1_subaction1_person1', 'Assistant / Clerk'), ('step1_subaction1_office1', 'Registrar'),
              ('step1_subaction1_person2', 'Cashier staff'), ('step1_subaction1_office2', 'Cashier office')]
    table = parse_service([('e', record(*fields))])
    assert table is not None
    from backend.bintanong_generation.service_steps import render_service
    text = '\n'.join(t for t, _ in render_service(table, 'en'))
    assert 'Person responsible: Assistant / Clerk\n    Office: Registrar' in text
    assert 'Person responsible: Cashier staff\n    Office: Cashier office' in text
    assert parse_service([('e', record(*fields[:-1]))]) is None


def test_phase_scoped_steps_preserve_reset_numbering_result_heading_and_requirement_scope():
    fields = [('service_title', 'APPLICATION AND RESULT'),
              ('application_requirement1', 'Application form'), ('application_where_to_secure1', 'Office'),
              ('result_requirements_scope', 'Additional Requirement for Issuance of Result'),
              ('result_requirement1', 'Claim stub'), ('result_requirement2', 'ID'),
              ('result_where_to_secure_shared', 'Client'),
              ('application_step1_client_step', '1. Submit'), ('application_step1_action', 'Receive'),
              ('application_step2_client_step', '2. Receive permit'), ('application_step2_action', 'Issue permit'),
              ('result_phase_heading', 'FOR RESULT ISSUANCE'),
              ('result_step1_client_step', '1. Claim result'), ('result_step1_action', 'Release result')]
    table = parse_service([('e', record(*fields))])
    assert table is not None
    from backend.bintanong_generation.service_steps import render_service
    text = '\n'.join(t for t, _ in render_service(table, 'en'))
    assert text.index('Step 2: 2. Receive permit') < text.index('FOR RESULT ISSUANCE') < text.index('Step 1: 1. Claim result')
    assert 'Additional Requirement for Issuance of Result\n- Claim stub — where to secure: Client\n- ID — where to secure: Client' in text
    assert parse_service([('e', record(*[f for f in fields if f[0] != 'result_phase_heading']))]) is None
