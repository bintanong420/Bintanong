"""An explicit reviewed field quote never relaxes whole-procedure coverage."""
import asyncio
import copy
import json
import hashlib

import pytest

from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.part_answers import part_schema
from backend.bintanong_generation.references import EvidenceReferences
from backend.bintanong_generation.contracts import AnswerDraft
from backend.bintanong_generation.understanding import review_identity
from backend.bintanong_orchestration.adapters import RetrievalAdapter
from backend.bintanong_orchestration.contracts import IntegrationResult
from backend.bintanong_retrieval.candidate_claims import prepare_candidate_claim_reviews
from backend.bintanong_retrieval.candidate_subject import prepare_candidate_subject_catalogue
from backend.bintanong_retrieval.types import RetrievalRequest
from test_candidate_claim_reviews import chunk
from test_generation_evidence import integrated
from test_generation_part_slots import PartModel

VALUE='1. Submit fictional Form Q and wait for confirmation.'
CLAIM='printed first client instruction'
PRIMARY='a'*64
COMPANION='b'*64


def expected(language='en'):
    return ('Ayon sa source: ' if language=='taglish' else 'The source states: ')+f'"{VALUE}"'


def authoring():
    chunks=[chunk(PRIMARY,[COMPANION]),chunk(COMPANION,[PRIMARY])]
    chunks[0]['type_fields']['field_associations'][0].update(name='client_step',value=VALUE)
    assignments=[dict(reading_id=c['chunk_id'],subject_id='fictional_service',basis_ref='synthetic-review') for c in chunks]
    catalogue=prepare_candidate_subject_catalogue(chunks,assignments)
    review=dict(subject_id='fictional_service',claim=CLAIM,finding='visible_fields',
        reviewed_chunk_ids=[PRIMARY,COMPANION],field_refs=[dict(reading_id=PRIMARY,field_name='client_step')],
        basis_ref='synthetic-field-review',basis_sha256='2'*64,answer_mode='quoted_field')
    return chunks,catalogue,review


def fixture(language='en',*,quoted=True,mixed=False):
    question='Ano yung step 1?' if language=='taglish' else 'What is step 1?'
    value=integrated('RAG',text=question,response_style=language).model_dump(mode='json')
    document=value['evidence']['documents']
    primary=document['passages'][0]
    primary['chunk_id']=PRIMARY
    primary['text']=json.dumps(dict(fields=[dict(name='client_step',value=VALUE,source_blank=False),
        dict(name='agency_times',value='3 minutes; 7 minutes',source_blank=False)],source_limits=[]))
    primary['citations'][0]['span_id']=PRIMARY+':0'
    companion=copy.deepcopy(primary)
    companion.update(chunk_id=COMPANION,text=json.dumps(dict(fields=[dict(name='later_step',
        value='2. Visit fictional Office V.',source_blank=False)],source_limits=[])))
    companion['citations'][0]['span_id']=COMPANION+':0'
    document['passages']=[primary,companion]
    value['evidence']['pin']['documents'][0]['chunk_id']=PRIMARY
    member=copy.deepcopy(value['evidence']['pin']['documents'][0])
    member['chunk_id']=COMPANION
    value['evidence']['pin']['documents'].append(member)
    part=value['understanding']['parts'][0]
    part.update(subject_id='fictional_service',requested_claims=[CLAIM]+(['whole procedure'] if mixed else []))
    coverage=dict(subject_id='fictional_service',claim=CLAIM,chunk_ids=[PRIMARY,COMPANION])
    if quoted:
        coverage['quoted_field']=dict(chunk_id=PRIMARY,field_name='client_step',text=VALUE,span_ids=[PRIMARY+':0'])
    document['record_coverage']=[coverage]
    if mixed: document['record_coverage'].append(dict(subject_id='fictional_service',claim='whole procedure',chunk_ids=[PRIMARY,COMPANION]))
    return value,question


def model(text=None,verdicts=None,status='answered'):
    return PartModel(slots=dict(r1=(status,[] if status!='answered' else [text or expected()])),verdicts=verdicts)


def test_explicit_quote_review_is_bound_and_legacy_normalization_stays_identical():
    chunks,catalogue,review=authoring()
    result=prepare_candidate_claim_reviews(catalogue,chunks,[review])
    assert result['reviews'][0]['answer_mode']=='quoted_field'
    legacy=review.copy();legacy.pop('answer_mode')
    assert 'answer_mode' not in prepare_candidate_claim_reviews(catalogue,chunks,[legacy])['reviews'][0]


@pytest.mark.parametrize('change',[dict(answer_mode='anything'),dict(finding='not_stated_in_selected_fields',field_refs=[]),
    dict(field_refs=[]),dict(procedure_order=[PRIMARY,COMPANION])])
def test_quote_review_cannot_relabel_absent_unsupported_or_ordered_fields(change):
    chunks,catalogue,review=authoring()
    with pytest.raises(ValueError): prepare_candidate_claim_reviews(catalogue,chunks,[review|change])


@pytest.mark.parametrize('change',[dict(text='Invented instruction.'),dict(field_name='missing'),dict(span_ids=[COMPANION+':0'])])
def test_field_quote_is_independently_checked_against_emitted_field_and_span(change):
    value,_=fixture()
    value['evidence']['documents']['record_coverage'][0]['quoted_field'].update(change)
    with pytest.raises(ValueError): IntegrationResult.parse(value)


def test_all_context_records_still_required_when_the_answer_is_one_field():
    value,_=fixture()
    value['evidence']['documents']['passages'].pop()
    with pytest.raises(ValueError): IntegrationResult.parse(value)


def test_duplicate_emitted_field_is_not_an_independent_quote_binding():
    value,_=fixture()
    passage=value['evidence']['documents']['passages'][0]
    record=json.loads(passage['text']);record['fields'].append(record['fields'][0].copy())
    passage['text']=json.dumps(record)
    with pytest.raises(ValueError): IntegrationResult.parse(value)


@pytest.mark.parametrize('field_value',[0,'',None])
def test_quoted_mode_requires_one_nonblank_textual_source_value(field_value):
    chunks,catalogue,review=authoring()
    chunks[0]['type_fields']['field_associations'][0]['value']=field_value
    catalogue=prepare_candidate_subject_catalogue(chunks,catalogue['assignments'])
    with pytest.raises(ValueError): prepare_candidate_claim_reviews(catalogue,chunks,[review])


def test_research_adapter_preserves_full_context_and_carries_the_bound_field():
    value,_=fixture(quoted=False)
    document=value['evidence']['documents']
    class Engine:
        def retrieve(self,request,**intent):
            return dict(release_id=request.release_id,status='uncalibrated',
                gaps=['development_calibration_pending'],evidence=document['passages'],
                evidence_policy=dict(assessment=dict(status='reviewed_fields_available',
                    subject_id='fictional_service',claims=[dict(claim=CLAIM,status='reviewed_fields_available',
                        source_review=dict(finding='visible_fields',answer_mode='quoted_field'),
                        source_fields=[dict(chunk_id=PRIMARY,reading_id='fictional-first',
                            field=dict(name='client_step',value=VALUE,source_blank=False,span_indexes=[0]))],
                        required_chunk_ids=[PRIMARY,COMPANION])])) )
    result=asyncio.run(RetrievalAdapter(Engine(),research=True).retrieve(
        RetrievalRequest('What is step 1?','release-synth-1'),
        subject_id='fictional_service',requested_claims=(CLAIM,)))
    assert result.status=='ok' and len(result.passages)==2
    assert set(result.record_coverage[0].chunk_ids)=={PRIMARY,COMPANION}
    assert result.record_coverage[0].quoted_field.text==VALUE
    assert result.record_coverage[0].quoted_field.span_ids==(PRIMARY+':0',)


@pytest.mark.parametrize('language',['en','taglish'])
def test_exact_field_answer_passes_and_still_runs_ordinary_review(language):
    value,question=fixture(language)
    transport=model(expected(language))
    answer=asyncio.run(Generator(transport).generate(question,IntegrationResult.parse(value)))
    assert answer.status=='answered' and answer.check_attempts==1 and len(transport.calls)==2
    assert answer.claims[0].text==expected(language) and answer.citations
    pack=prepare(IntegrationResult.parse(value))
    assert len(pack.cards)==2
    payload=json.loads(transport.calls[0][0][1]['content'])
    assert len(payload['evidence']['sources'])==2
    assert payload['quoted_field_answers']['r1']['text']==expected(language)


@pytest.mark.parametrize('extra',[' The fee is zero.',' Processing time is 3 minutes.'])
def test_nonconforming_transport_cannot_add_policy_or_collapse_times(extra):
    value,question=fixture()
    transport=model(expected()+extra)
    answer=asyncio.run(Generator(transport).generate(question,IntegrationResult.parse(value)))
    assert answer.status=='abstained' and not answer.claims and answer.check_attempts==0


def test_quote_does_not_override_a_negative_ordinary_reviewer():
    value,question=fixture()
    answer=asyncio.run(Generator(model(verdicts={'r1':'does_not_answer'})).generate(question,IntegrationResult.parse(value)))
    assert answer.status!='answered' and answer.check_attempts>0


def test_mixed_claim_or_other_explanation_profile_withholds_before_inference():
    for mixed,profile in ((True,'parts'),(False,'scoped')):
        value,question=fixture(mixed=mixed)
        transport=model()
        answer=asyncio.run(Generator(transport,explanation_profile=profile).generate(question,IntegrationResult.parse(value)))
        assert answer.status=='abstained' and answer.validation=='unsupported_answer_scope'
        assert not transport.calls


def test_legacy_whole_procedure_still_rejects_an_answer_citing_only_one_record():
    value,question=fixture(quoted=False)
    answer=asyncio.run(Generator(model()).generate(question,IntegrationResult.parse(value)))
    assert answer.status=='abstained' and answer.check_attempts==0


def test_unavailable_quote_slot_never_fabricates_a_field_answer():
    value,question=fixture()
    answer=asyncio.run(Generator(model(status='not_in_evidence')).generate(question,IntegrationResult.parse(value)))
    assert answer.status!='answered' and not answer.claims


@pytest.mark.parametrize('short',[False,True])
def test_quote_schema_is_per_part_and_does_not_constrain_ordinary_parts(short):
    value,question=fixture()
    added='What are the later steps?'
    combined=question+' '+added
    plan=value['understanding']
    plan['question_sha256']=hashlib.sha256(combined.encode()).hexdigest()
    plan['parts'].append(dict(part_id='r2',text=added,start=len(question)+1,end=len(combined),
        evidence_need='document',operation_indices=[],subject_id='fictional_service',requested_claims=['whole procedure']))
    value['evidence']['documents']['record_coverage'].append(dict(subject_id='fictional_service',
        claim='whole procedure',chunk_ids=[PRIMARY,COMPANION]))
    pack=prepare(IntegrationResult.parse(value))
    refs=EvidenceReferences(pack) if short else None
    schema=part_schema(pack,refs)
    quote=schema['properties']['answers']['properties']['r1']['properties']['claims']
    assert quote['maxItems']==1 and quote['items']['properties']['text']['const']==expected()
    target='e1' if short else pack.cards[0].evidence_id
    assert quote['items']['properties']['evidence_ids']['items']['const']==target
    slot,claim=('ShortPartSlot','ShortPartClaim') if short else ('PartSlot','PartClaim')
    assert schema['properties']['answers']['properties']['r2']=={'$ref':'#/$defs/'+slot}
    assert 'const' not in schema['$defs'][claim]['properties']['text']


def test_review_identity_binds_explicit_quote_scope_without_changing_legacy_payloads():
    quoted,_=fixture()
    legacy,_=fixture(quoted=False)
    first,second=(prepare(IntegrationResult.parse(v)) for v in (quoted,legacy))
    draft=AnswerDraft.parse(dict(schema_version=AnswerDraft.SCHEMA_VERSION,
        release_id=first.release_id,language='en',decision_outcome=None,
        claims=[dict(claim_id='c1',text=expected(),evidence_ids=[first.cards[0].evidence_id])]))
    assert review_identity(first,draft).requirements_sha256!=review_identity(second,draft).requirements_sha256
    assert 'field_quotes' not in second.model_payload()
