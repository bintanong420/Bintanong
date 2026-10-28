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


def test_a_held_malformed_condition_keeps_the_service_unrendered():
    assert parse_service([('e1', FIRST), ('e2', limited('malformed_source_condition'))]) is None
