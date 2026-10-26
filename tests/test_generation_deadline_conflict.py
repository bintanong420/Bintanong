"""Conflicting printed statements stay quotations, never an adjudicated deadline."""
import asyncio
import hashlib
import json

import pytest

from backend.bintanong_generation.generator import Generator
from test_generation_precedence import integration as base, ChoosingModel, SAFE, UNSAFE


TEXT='What do the fictional timing statements say; what is the fee?'
VALUES=('Fictional mark X may be reviewed during the next cycle.',
        'Fictional mark X may instead be repeated; only one review is offered.',
        'A later fictional mark retains the remaining original period.',
        'Another printed paragraph states a different cycle.')


def rows():
    return [dict(fields=[dict(name=f'5.{n+1}',value=value,source_blank=False)],
        service_group=dict(logical_step_id='fictional-period',part_count=4,part_order=n,
                           part_reading_id=f'fictional-period::{n}'),
        source_limits=[dict(issue='conflicting_deadlines',resolution='unresolved',gap_id='period-gap',
                            field_names=[f'5.{n+1}'],affected_claims=['applicable period'])])
        for n,value in enumerate(VALUES)]


def integration(*,language='en',content=None,foreign=False):
    original=base(language=language,rows=content if content is not None else rows(),foreign=foreign)
    value=original.model_dump(mode='json')
    value['understanding']['question_sha256']=hashlib.sha256(TEXT.encode()).hexdigest()
    for part,quote in zip(value['understanding']['parts'],TEXT.split('; ')):
        start=TEXT.index(quote)
        part.update(text=quote,start=start,end=start+len(quote))
    return type(original).parse(value)


@pytest.mark.parametrize('language,notice',[
    ('en','does not establish which deadline applies'),
    ('fil','hindi malinaw kung aling deadline ang susundin'),
    ('taglish','hindi clear kung aling deadline ang applicable')])
def test_every_printed_statement_is_quoted_and_the_conflict_reaches_ordinary_review(language,notice):
    model=ChoosingModel()
    answer=asyncio.run(Generator(model).generate(TEXT,integration(language=language)))
    assert answer.status=='answered' and UNSAFE not in answer.text
    assert notice in answer.text and SAFE in answer.text
    assert all(f'"{value}"' in answer.text for value in VALUES)
    assert len(answer.citations)==5
    reviewed=' '.join(c['claim']['text'] for p in model.calls[-1]['parts'] for c in p['claims'])
    assert all(value in reviewed for value in VALUES) and notice in reviewed


@pytest.mark.parametrize('defect',['missing','duplicate_order','wrong_count','mixed_group','mixed_gap','oversized','malformed'])
def test_incomplete_or_unsafe_group_withholds_its_slot_and_keeps_independent_part(defect):
    content=rows()
    if defect=='missing':content.pop()
    elif defect=='duplicate_order':content[-1]['service_group']['part_order']=0
    elif defect=='wrong_count':content[-1]['service_group']['part_count']=5
    elif defect=='mixed_group':content[-1]['service_group']['logical_step_id']='another-group'
    elif defect=='mixed_gap':content[-1]['source_limits'][0]['gap_id']='another-gap'
    elif defect=='oversized':content[-1]['fields'][0]['value']='Fictional value '*100
    else:content[-1]['fields'][0]['source_blank']=True
    answer=asyncio.run(Generator(ChoosingModel()).generate(TEXT,integration(content=content)))
    assert answer.status=='answered' and [c.text for c in answer.claims]==[SAFE]
    assert answer.part_ledger.entries[0].reason=='source_gap'


def test_a_foreign_version_cannot_supply_a_conflicting_companion():
    answer=asyncio.run(Generator(ChoosingModel()).generate(TEXT,integration(foreign=True)))
    assert answer.status=='answered' and [c.text for c in answer.claims]==[SAFE]
    assert answer.part_ledger.entries[0].reason=='source_gap'


def test_positive_source_transform_still_requires_the_ordinary_part_review():
    answer=asyncio.run(Generator(ChoosingModel(verdict='does_not_answer')).generate(TEXT,integration()))
    assert answer.status=='insufficient_evidence' and not answer.claims


def test_resolved_deadline_metadata_does_not_rewrite_an_unrelated_proposal():
    content=rows()
    for record in content:record['source_limits'][0]['resolution']='resolved'
    answer=asyncio.run(Generator(ChoosingModel()).generate(TEXT,integration(content=content)))
    assert answer.status=='answered' and UNSAFE in answer.text


def test_two_slots_can_share_identical_verified_quotations_without_duplicate_support_ids():
    from backend.bintanong_generation.evidence import prepare
    from backend.bintanong_generation.part_answers import PartExplanation,to_draft,confirm_schema
    pack=prepare(integration())
    ref=next(c.evidence_id for c in pack.cards if VALUES[0] in c.text)
    explanation=PartExplanation.parse(dict(schema_version=PartExplanation.SCHEMA_VERSION,
        release_id=pack.release_id,language=pack.language,answers={p:dict(status='answered',
        claims=[dict(text=UNSAFE,evidence_ids=[ref])]) for p in ('r1','r2')}))
    draft,slots=to_draft(explanation,pack)
    assert slots['r1'][1]==slots['r2'][1] and len(draft.claims)==1
    assert all(value in draft.claims[0].text for value in VALUES)
    assert confirm_schema(pack,draft,slots)['$defs']['ClaimVerdict']['properties']['claim_id']['enum']==['c1']


@pytest.mark.parametrize('position',[0,1])
def test_a_malformed_extra_limit_withholds_only_the_affected_part(position):
    content=rows()
    content[0]['source_limits'].insert(position,None)
    answer=asyncio.run(Generator(ChoosingModel()).generate(TEXT,integration(content=content)))
    assert answer.status=='answered' and [c.text for c in answer.claims]==[SAFE]


def test_taglish_framing_applies_to_every_block_of_a_long_exact_quotation():
    content=rows()
    for record in content:record['fields'][0]['value']='Fictional timing statement. '*20
    answer=asyncio.run(Generator(ChoosingModel()).generate(TEXT,integration(language='taglish',content=content)))
    assert answer.status=='answered'
    assert all('Ang printed statement' in c.text for c in answer.claims if 'Fictional timing statement.' in c.text)


def test_shared_five_claim_group_is_budgeted_by_new_claims_not_repeated_slot_references():
    from backend.bintanong_generation.evidence import prepare
    from backend.bintanong_generation.part_answers import PartExplanation,to_draft
    content=rows()
    content.append(json.loads(json.dumps(content[-1])))
    for n,record in enumerate(content):
        record['service_group'].update(part_count=5,part_order=n,part_reading_id=f'fictional-period::{n}')
        record['fields'][0]['value']='Fictional timing statement. '*35
    pack=prepare(integration(content=content))
    ref=next(c.evidence_id for c in pack.cards if 'Fictional timing statement.' in c.text)
    explanation=PartExplanation.parse(dict(schema_version=PartExplanation.SCHEMA_VERSION,
        release_id=pack.release_id,language=pack.language,answers={p:dict(status='answered',
        claims=[dict(text=UNSAFE,evidence_ids=[ref])]) for p in ('r1','r2')}))
    draft,slots=to_draft(explanation,pack)
    assert slots['r1'][0]==slots['r2'][0]=='answered'
    assert slots['r1'][1]==slots['r2'][1]==('c1','c2','c3','c4','c5')
    assert len(draft.claims)==5
