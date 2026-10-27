"""Nested same-subject parts share required record coverage; nothing required goes uncited."""
from dataclasses import replace
import json

from backend.bintanong_generation.contracts import ProseClaim
from backend.bintanong_generation.evidence import _card, prepare
from backend.bintanong_generation.part_answers import part_messages, record_coverage_errors
from test_request_understanding_pipeline import TEXT, source

SUBJECT = 'fictional_service'


def pack_for(r1=('whole service', ('e1', 'e2', 'e3')), r2=('totals', ('e1', 'e2', 'e3')), r2_subject=SUBJECT):
    pack = prepare(source())
    cards = tuple(_card('document', f'Fictional record {n}.', list(pack.cards[0].citations)) for n in range(1, 4))
    ids = {f'e{n}': c.evidence_id for n, c in enumerate(cards, 1)}
    parts = [p.model_copy(update=dict(subject_id=subject, requested_claims=(claim,)))
             for p, (subject, claim) in zip(pack.understanding.parts, ((SUBJECT, r1[0]), (r2_subject, r2[0])))]
    coverage = ((SUBJECT, r1[0], tuple(ids[i] for i in r1[1])), (r2_subject, r2[0], tuple(ids[i] for i in r2[1])))
    pack = replace(pack, cards=cards, record_coverage=coverage,
                   understanding=pack.understanding.model_copy(update=dict(parts=tuple(parts))))
    return pack, ids


def claims(ids, *cited):
    return tuple(ProseClaim(claim_id=f'c{n}', text='Fictional explanation.', evidence_ids=tuple(ids[i] for i in refs))
                 for n, refs in enumerate(cited, 1))


SLOTS = {'r1': ('answered', ('c1', 'c2')), 'r2': ('answered', ('c3',))}


def test_nested_part_relies_on_the_covering_parts_citations():
    pack, ids = pack_for()
    assert record_coverage_errors(pack, claims(ids, ('e1', 'e2'), ('e3',), ('e3',)), SLOTS) == ()


def test_shared_family_still_needs_every_required_record_cited_once():
    pack, ids = pack_for()
    assert record_coverage_errors(pack, claims(ids, ('e1',), ('e2',), ('e2',)), SLOTS) == (
        'missing_procedure_record_coverage',)


def test_a_part_with_records_outside_the_covering_set_must_cite_them_itself():
    pack, ids = pack_for(r1=('whole service', ('e1', 'e2')), r2=('totals', ('e2', 'e3')))
    assert record_coverage_errors(pack, claims(ids, ('e1', 'e2'), ('e2',), ('e2',)), SLOTS) == (
        'missing_procedure_record_coverage',)


def test_another_subject_never_covers_a_part():
    pack, ids = pack_for(r2_subject='other_service')
    assert record_coverage_errors(pack, claims(ids, ('e1', 'e2'), ('e3',), ('e1',)), SLOTS) == (
        'missing_procedure_record_coverage',)


def test_prompt_names_the_part_that_carries_the_shared_procedure():
    pack, _ = pack_for(r1=('whole service', ('e1', 'e2', 'e3')), r2=('totals', ('e3',)))
    payload = json.loads(part_messages(TEXT, pack)[1]['content'])
    assert payload['shared_record_coverage'] == {'r2': 'r1'}


def test_review_prompt_also_names_the_covering_part():
    from backend.bintanong_generation.contracts import AnswerDraft
    from backend.bintanong_generation.part_answers import confirm_messages
    pack, ids = pack_for(r1=('whole service', ('e1', 'e2', 'e3')), r2=('totals', ('e3',)))
    draft = AnswerDraft.parse(dict(schema_version=AnswerDraft.SCHEMA_VERSION, release_id=pack.release_id,
        language=pack.language, decision_outcome=None,
        claims=[c.model_dump(mode='json') for c in claims(ids, ('e1', 'e2', 'e3'), ('e3',))]))
    payload = json.loads(confirm_messages(TEXT, pack, draft, {'r1': ('answered', ('c1',)), 'r2': ('answered', ('c2',))})[1]['content'])
    assert payload['shared_record_coverage'] == {'r2': 'r1'}
