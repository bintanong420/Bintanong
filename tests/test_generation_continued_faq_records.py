"""Owner 3 Nov 2026 (H4): a printed FAQ page split across consecutive records reads as one text. Live, "4. How do I
claim accident insurance? A." ended one record and its answer began the next, and the draft called it a source
cutoff. Only the Handbook FAQ topics get this note. Fictional fixture."""
import json

from backend.bintanong_generation import part_answers
from backend.bintanong_generation.evidence import prepare
from test_generation_fee_reply import EXAMPLE, RATE, fee_integration


def draft_payload(subject):
    pack = prepare(fee_integration(cards=(RATE, EXAMPLE), subject=subject))
    return pack, json.loads(part_answers.part_messages('How do I claim fictional insurance?', pack)[-1]['content'])


def test_faq_records_are_marked_as_one_continuous_page():
    pack, payload = draft_payload('handbook_student_faq')
    ids = [c.evidence_id for c in pack.cards if c.kind == 'document']
    assert len(payload['continued_records']) == 1 and len(payload['continued_records'][0]) == len(ids) == 2
    assert 'not a source cutoff' in payload['continued_records_instruction']
    assert part_answers.continued_records(pack) == [ids]


def test_other_topics_get_no_continuation_note():
    pack, payload = draft_payload('fictional_policy')
    assert 'continued_records' not in payload and part_answers.continued_records(pack) == []
