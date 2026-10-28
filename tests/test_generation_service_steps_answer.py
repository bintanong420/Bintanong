"""Strictly parsed Charter services are answered with host-rendered printed steps, no model wording."""
import asyncio
import json

from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.service_steps import parse_service, render_service
from backend.bintanong_orchestration.contracts import IntegrationResult
from test_generation_part_slots import OFFICE, PartModel
from test_generation_service_steps import FIRST, SECOND, record
from test_request_understanding_pipeline import TEXT, source

SUBJECT = 'fictional_service'


def integration(texts=(FIRST, SECOND), both_parts=True):
    value = source().model_dump(mode='json')
    first = value['evidence']['documents']['passages'][0]
    member = value['evidence']['pin']['documents'][0]
    ids = [f'{n:064x}' for n in range(1, len(texts) + 1)]
    value['evidence']['documents']['passages'] = [dict(first, chunk_id=c, text=t) for c, t in zip(ids, texts)]
    value['evidence']['pin']['documents'] = [dict(member, chunk_id=c) for c in ids]
    whole, other = value['understanding']['parts']
    whole.update(subject_id=SUBJECT, requested_claims=['printed service fields'])
    if both_parts:
        other.update(subject_id=SUBJECT, requested_claims=['printed service totals fields'])
    else:
        other.update(subject_id='other_subject', requested_claims=['printed other fields'])
    value['evidence']['documents']['record_coverage'] = [
        dict(subject_id=SUBJECT, claim='printed service fields', chunk_ids=ids),
        dict(subject_id=SUBJECT, claim='printed service totals fields', chunk_ids=ids)]
    return IntegrationResult.parse(value)


def expected(pack, language='en'):
    cards = [c for c in pack.cards if c.kind == 'document']
    return render_service(parse_service([(c.evidence_id, c.text) for c in cards]), language)


def test_a_parsed_service_is_answered_with_printed_steps_and_no_model_call():
    model = PartModel()
    answer = asyncio.run(Generator(model).generate(TEXT, integration()))
    assert answer.status == 'answered' and model.calls == []
    assert [(c.text, c.evidence_ids) for c in answer.claims] == list(expected(prepare(integration())))
    assert 'Step 1: 1. Pay the fee' in answer.text and 'Printed total: Php 100.00; 16 minutes' in answer.text


def test_other_parts_are_still_explained_by_the_model_beside_the_printed_steps():
    model = PartModel(slots=dict(r2=('answered', [OFFICE])))
    answer = asyncio.run(Generator(model).generate(TEXT, integration(both_parts=False)))
    assert answer.status == 'answered'
    draft_schema = model.calls[0][1]
    assert draft_schema['properties']['answers']['required'] == ['r2']
    assert [c.text for c in answer.claims].count(OFFICE) == 1
    assert len(answer.claims) == len(expected(prepare(integration(both_parts=False)))) + 1


def test_a_service_outside_the_strict_grammar_keeps_the_model_path():
    odd = record(('step1_client_step', '1. Pay'), ('step1_continuation_through_step2_shared_person', 'Clerk'))
    model = PartModel(slots=dict(r1=('answered', [OFFICE]), r2=('answered', [OFFICE])))
    asyncio.run(Generator(model).generate(TEXT, integration(texts=(odd,))))
    assert model.calls  # no host table, so the existing model path runs
