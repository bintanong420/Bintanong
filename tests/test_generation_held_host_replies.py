"""A host-written reply never cites a record held for an unresolved malformed condition.

Regression 30 Oct 2026: Charter fee, time and requirement questions (library card, certification of grades,
removal exam, TOR copy) were answered by host-written service replies citing records with an unresolved
malformed_source_condition. The final check (owner 30 Oct: such records are quoted with their limitation) then
raised final_malformed_source_fidelity and the request failed. Such parts now go to the ordinary per-part path,
which quotes the record with its limitation or reports a source gap."""
import copy

from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation import part_answers
from test_generation_fee_reply import EXAMPLE, RATE, fee_integration

HELD = dict(issue='malformed_source_condition', resolution='unresolved', affected_claims=['fictional checklist'])


def test_an_unheld_fee_part_keeps_its_host_reply():
    pack = prepare(fee_integration())
    assert 'r1' in part_answers.host_claims(pack) and 'r1' not in part_answers.document_parts(pack)


def test_a_part_whose_host_reply_cites_a_held_record_is_left_to_the_ordinary_path():
    held = copy.deepcopy(RATE)
    held['source_limits'].append(HELD)
    pack = prepare(fee_integration(cards=(held, EXAMPLE)))
    assert 'r1' not in part_answers.host_claims(pack)
    assert part_answers.document_parts(pack) == ('r1',)
    assert part_answers.host_only(pack) is None
