"""A held deadline can show exact reviewed context without becoming an answer."""
import asyncio
import hashlib

import pytest

from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.render import render_text,selected_cards
from backend.bintanong_generation.validation import validate_final
from test_generation_deadline_conflict import integration as base,rows,VALUES


TEXT='Which fictional period applies?'


class NoInference:
    async def infer(self,*args):
        raise AssertionError('A literal withheld-source context needs no model inference.')


def integration(*,language='en',content=None,foreign=False,requested='applicable period'):
    original=base(language=language,content=content,foreign=foreign)
    value=original.model_dump(mode='json')
    value['understanding']['question_sha256']=hashlib.sha256(TEXT.encode()).hexdigest()
    value['understanding']['parts']=[dict(part_id='r1',text=TEXT,start=0,end=len(TEXT),
        evidence_need='document',operation_indices=[],subject_id='fictional_period',requested_claims=[requested])]
    value['evidence']['documents'].update(status='insufficient_evidence',gaps=['requested_claim_not_established'])
    value['evidence'].update(status='no_evidence',permitted_scope='none')
    value['status']='no_evidence'
    return type(original).parse(value)


@pytest.mark.parametrize('language',['en','fil','taglish'])
def test_withheld_deadline_shows_exact_complete_context_without_asserting_an_answer(language):
    answer=asyncio.run(Generator(NoInference()).generate(TEXT,integration(language=language)))
    assert answer.status=='source_conflict' and answer.validation=='control_fallback'
    assert all(value in answer.text for value in VALUES)
    assert len(answer.citations)==4 and answer.draft_attempts==answer.check_attempts==0
    assert answer.decision is None and not answer.institutional_use_allowed
    assert 'not in Bintanong' not in answer.text and 'Wala pa ito' not in answer.text


@pytest.mark.parametrize('defect',['missing','foreign','bad_limit','unrelated'])
def test_incomplete_or_unrelated_groups_cannot_supply_a_withheld_context(defect):
    content=rows()
    if defect=='missing':content.pop()
    elif defect=='bad_limit':content[0]['source_limits'].insert(0,None)
    reply=asyncio.run(Generator(NoInference()).generate(TEXT,integration(content=content,
        foreign=defect=='foreign',requested='unknown fee' if defect=='unrelated' else 'applicable period')))
    assert reply.status!='answered' and not reply.claims and not reply.citations


def test_final_context_fidelity_rejects_modified_source_words_even_on_a_nonanswer():
    original=integration();pack=prepare(original)
    answer=asyncio.run(Generator(NoInference()).generate(TEXT,original))
    assert answer.claims
    altered=tuple(c.model_copy(update=dict(text=c.text.replace(VALUES[0],'An invented authoritative deadline.')))
                  for c in answer.claims)
    edited=answer.model_copy(update=dict(claims=altered,citations=selected_cards(pack,altered),
        text=render_text(pack,altered,answer.status)))
    with pytest.raises(ValueError,match='source_conflict_context'):
        validate_final(edited,pack,altered)


@pytest.mark.parametrize('reason',['tool_error','timeout','repair_exhausted','validated'])
def test_nonready_claim_fidelity_cannot_be_bypassed_by_changing_validation_reason(reason):
    original=integration();pack=prepare(original)
    answer=asyncio.run(Generator(NoInference()).generate(TEXT,original))
    altered=(answer.claims[0].model_copy(update=dict(text='The authoritative deadline is tomorrow.')),)
    edited=answer.model_copy(update=dict(validation=reason,claims=altered,
        citations=selected_cards(pack,altered),text=render_text(pack,altered,answer.status)))
    with pytest.raises(ValueError,match='source_conflict_context'):
        validate_final(edited,pack,altered)
