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
