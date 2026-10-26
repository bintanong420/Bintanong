"""Required companions carry exact source wording and unresolved applicability limits."""
import asyncio
import json

import pytest

from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.part_answers import record_coverage_errors
from test_generation_precedence import integration as base,ChoosingModel,SAFE,UNSAFE,TEXT


PRIMARY='Fictional consequence A or B upon discretion in the activity.'
MEASURES='Fictional measure Q; Fictional measure R.'
LIMIT='Which fictional measure applies automatically is not established.'


def inputs(*,language='en',defect=None,footer=False):
    primary=dict(fields=[dict(name='Cause',value='Fictional declaration.',source_blank=False),
        dict(name='1st Offense',value=PRIMARY,source_blank=False)],source_limits=[])
    context=dict(fields=[dict(name='Scope',value='Additional fictional measures.',source_blank=False),
        dict(name='Measures',value=MEASURES,source_blank=False)],source_limits=[dict(
            issue='claim_not_stated',resolution='unresolved',affected_claims=['automatic applicability'],message=LIMIT)])
    if footer:
        primary['fields']=[dict(name='client_step',value='Submit fictional Form Q.',source_blank=False)]
        context['fields']=[dict(name='printed_total_time',value='17 fictional minutes',source_blank=False)]
        context['source_limits']=[dict(issue='printed_total_discrepancy',resolution='unresolved',
            affected_claims=['reconciled time'],message='The printed total differs from the visible step times.')]
    if defect=='bad_field':context['fields'][0]['source_blank']=True
    elif defect=='bad_limit':context['source_limits'].insert(0,None)
    elif defect=='held':context['source_limits'].append(dict(issue='malformed_source_condition',resolution='unresolved'))
    elif defect=='oversized':context['fields'][0]['value']='Fictional context '*100
    elif defect=='bad_name':context['fields'][0]['name']=[]
    original=base(language=language,rows=[primary,context],foreign=defect=='foreign')
    value=original.model_dump(mode='json')
    value['understanding']['parts'][0].update(subject_id='fictional_rules',requested_claims=['printed consequences'])
    value['evidence']['documents']['record_coverage']=[dict(subject_id='fictional_rules',claim='printed consequences',
        chunk_ids=[p['chunk_id'] for p in value['evidence']['documents']['passages'][:2]])]
    return type(original).parse(value)


@pytest.mark.parametrize('language',['en','fil','taglish'])
def test_linked_applicability_context_keeps_exact_primary_conditions_and_shared_measures(language):
    model=ChoosingModel()
    answer=asyncio.run(Generator(model).generate(TEXT,inputs(language=language)))
    assert answer.status=='answered' and UNSAFE not in answer.text
    assert PRIMARY in answer.text and MEASURES in answer.text and LIMIT in answer.text
    assert SAFE in answer.text and len(answer.citations)==3
    assert answer.check_attempts>=1
    assert all(c['claim']['text'] in answer.text for p in model.calls[-1]['parts'] for c in p['claims'])


def test_required_total_context_is_quoted_with_the_specific_discrepancy():
    answer=asyncio.run(Generator(ChoosingModel()).generate(TEXT,inputs(footer=True)))
    assert answer.status=='answered'
    assert '17 fictional minutes' in answer.text
    assert 'The printed total differs from the visible step times.' in answer.text
    assert SAFE in answer.text


@pytest.mark.parametrize('defect',['bad_field','bad_limit','held','oversized','foreign','bad_name'])
def test_unsafe_companion_cannot_be_added_by_a_positive_review(defect):
    answer=asyncio.run(Generator(ChoosingModel()).generate(TEXT,inputs(defect=defect)))
    assert answer.status=='answered' and [c.text for c in answer.claims]==[SAFE]
    assert answer.part_ledger.entries[0].reason=='source_gap'


def test_context_quotation_still_requires_ordinary_relevance_review():
    answer=asyncio.run(Generator(ChoosingModel(verdict='does_not_answer')).generate(TEXT,inputs()))
    assert answer.status=='insufficient_evidence' and not answer.claims


def test_positive_claim_coverage_cannot_hide_altered_quoted_condition():
    integration=inputs();pack=prepare(integration)
    answer=asyncio.run(Generator(ChoosingModel()).generate(TEXT,integration))
    assert answer.status=='answered'
    claims=tuple(c.model_copy(update=dict(text=c.text.replace(PRIMARY,'The consequence applies automatically.')))
                 for c in answer.claims)
    slots={e.part_id:(e.status,e.claim_ids) for e in answer.part_ledger.entries}
    assert record_coverage_errors(pack,claims,slots)==('source_context_not_preserved',)
