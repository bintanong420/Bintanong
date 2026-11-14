"""Owner 3 Nov 2026 ("Go", fix 1): a whole-procedure question about a printed Charter service whose record is held
for a malformed condition gets the host-printed steps when that record's limitation is printed in the reply.
Live: the 11-record transfer-credentials procedure could not fit the 8-claim draft and always abstained.
A one-detail part keeps the 30 Oct ordinary path. Fictional fixture."""
import asyncio

from backend.bintanong_generation import part_answers
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator
from test_generation_part_slots import PartModel
from test_generation_service_steps import FIRST, limited
from test_generation_service_steps_answer import expected, integration
from test_request_understanding_pipeline import TEXT

HELD = (FIRST, limited('malformed_source_condition'))


def test_a_whole_service_with_a_held_record_gets_the_printed_steps_and_its_limitation():
    model = PartModel()
    answer = asyncio.run(Generator(model).generate(TEXT, integration(texts=HELD)))
    assert answer.status == 'answered' and model.calls == []
    assert [(c.text, c.evidence_ids) for c in answer.claims] == list(expected(prepare(integration(texts=HELD))))
    assert 'Source limitation: Unavailable information: fictional malformed_source_condition.' in answer.text


def test_a_one_detail_part_with_a_held_record_keeps_the_ordinary_path():
    pack = prepare(integration(texts=HELD, details=('fees', 'fees')))
    assert not part_answers.host_claims(pack)
