"""Exact reviewed procedure records survive retrieval and gate per-part answer citations."""
import asyncio
import json

import pytest

from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.validation import validate_final
from backend.bintanong_orchestration.adapters import RetrievalAdapter
from backend.bintanong_orchestration.contracts import DocumentResult
from backend.bintanong_orchestration.orchestrator import merge_documents
from backend.bintanong_retrieval.types import RetrievalRequest
from test_generation_completeness_context import TEXT, CHECKLIST, STEP, integration
from test_generation_validation import report


SUBJECT, CLAIM = 'fictional_service', 'visible service instructions'


def coverage(ids):
    return dict(subject_id=SUBJECT, claim=CLAIM, chunk_ids=list(ids))


def result_payload():
    return integration().evidence.documents.model_dump(mode='json')


class ReviewedEngine:
    def __init__(self, *, finding='visible_fields', field_name='client_step'):
        self.finding,self.field_name=finding,field_name

    def retrieve(self,request,**intent):
        value=result_payload()
        fields=[dict(chunk_id=p['chunk_id'],field=dict(name=self.field_name,value='Fictional step.',source_blank=False))
                for p in value['passages']]
        return dict(release_id=request.release_id,status='uncalibrated',gaps=['development_calibration_pending'],
            evidence=value['passages'],evidence_policy=dict(assessment=dict(
                status='reviewed_fields_available',subject_id=SUBJECT,claims=[dict(claim=CLAIM,
                    status='reviewed_fields_available',source_review=dict(finding=self.finding),source_fields=fields)])))


def retrieve(**kwargs):
    return asyncio.run(RetrievalAdapter(ReviewedEngine(**kwargs),research=True).retrieve(
        RetrievalRequest('Fictional service?', 'release-synth-1'),subject_id=SUBJECT,requested_claims=(CLAIM,)))


def test_research_adapter_carries_exact_visible_client_step_record_requirements():
    value=retrieve().model_dump(mode='json')
    assert value.get('record_coverage')==[coverage([p['chunk_id'] for p in value['passages']])]


@pytest.mark.parametrize('kwargs',[dict(finding='not_stated_in_selected_fields'),dict(field_name='requirement_1')])
def test_unstated_or_checklist_only_fields_do_not_require_every_service_record(kwargs):
    assert 'record_coverage' not in retrieve(**kwargs).model_dump(mode='json')


def test_legacy_document_result_serialization_stays_byte_identical_without_coverage():
    value=result_payload()
    assert DocumentResult.parse(value).model_dump(mode='json')==value


def test_coverage_references_must_exist_in_the_emitted_document_result():
    value=result_payload()
    value['record_coverage']=[coverage(['f'*64])]
    with pytest.raises(ValueError):DocumentResult.parse(value)


def test_merging_topics_keeps_each_claims_own_record_requirement():
    first=retrieve()
    value=result_payload()
    value['passages']=[dict(value['passages'][0],chunk_id='d'*64)]
    value['record_coverage']=[dict(subject_id='other_service',claim='other instruction',chunk_ids=['d'*64])]
    merged=merge_documents([first,DocumentResult.parse(value)])
    assert [(r['subject_id'],r['chunk_ids']) for r in merged.model_dump(mode='json')['record_coverage']]==[
        (SUBJECT,[p.chunk_id for p in first.passages]),('other_service',['d'*64])]


def covered_integration(*,other_subject=False):
    original=integration()
    value=original.model_dump(mode='json')
    part=value['understanding']['parts'][0]
    part.update(subject_id='other_service' if other_subject else SUBJECT,requested_claims=[CLAIM])
    value['evidence']['documents']['record_coverage']=[coverage([
        p['chunk_id'] for p in value['evidence']['documents']['passages']])]
    return type(original).parse(value)


class ProcedureModel:
    def __init__(self, *,repair=False,unavailable=False):
        self.repair,self.unavailable=repair,unavailable
        self.calls=[]

    async def infer(self,messages,schema):
        payload=json.loads(messages[1]['content']);self.calls.append(payload)
        version=schema['properties'].get('schema_version',{}).get('const')
        if version=='bintanong-part-explanation-v1':
            cards=payload['evidence']['sources']
            chosen=[c for c in cards if c['text']==CHECKLIST]
            if payload['validation_errors'] and self.repair:chosen=cards
            claims=[dict(text='Fictional reviewed step.' if c['text']==STEP else CHECKLIST,
                         evidence_ids=[c['evidence_id']]) for c in chosen]
            return json.dumps(dict(schema_version=version,release_id=payload['evidence']['release_id'],language='en',
                answers=dict(r1=dict(status='source_gap' if self.unavailable else 'answered',
                                     claims=[] if self.unavailable else claims))))
        claims=[c['claim']['claim_id'] for p in payload['parts'] for c in p['claims']]
        return json.dumps(dict(parts=dict(r1='answers'),support=report(verdicts=[
            dict(claim_id=c,verdict='supported') for c in claims]).model_dump(mode='json')))


def test_approving_reviewer_cannot_release_an_answer_that_omits_a_required_record():
    model=ProcedureModel()
    answer=asyncio.run(Generator(model).generate(TEXT,covered_integration()))
    assert answer.status=='abstained' and not answer.claims
    assert answer.draft_attempts==2 and answer.check_attempts==0
    assert 'missing_procedure_record_coverage' in model.calls[1]['validation_errors']


def test_existing_single_repair_can_add_missing_records_before_normal_support_review():
    model=ProcedureModel(repair=True)
    answer=asyncio.run(Generator(model).generate(TEXT,covered_integration()))
    assert answer.status=='answered' and len(answer.citations)==2
    assert answer.draft_attempts==2 and answer.check_attempts==1
    assert 'record_coverage' in model.calls[0] and len(model.calls[0]['record_coverage']['r1'])==2


def test_other_subject_or_unavailable_slot_is_not_forced_to_fabricate_steps():
    answer=asyncio.run(Generator(ProcedureModel()).generate(TEXT,covered_integration(other_subject=True)))
    assert answer.status=='answered' and answer.draft_attempts==1
    answer=asyncio.run(Generator(ProcedureModel(unavailable=True)).generate(TEXT,covered_integration()))
    assert answer.status=='insufficient_evidence' and answer.check_attempts==0


def test_final_validation_cannot_bypass_the_record_requirement():
    covered=covered_integration()
    value=covered.model_dump(mode='json')
    value['evidence']['documents'].pop('record_coverage')
    old_answer=asyncio.run(Generator(ProcedureModel()).generate(TEXT,type(covered).parse(value)))
    assert old_answer.status=='answered'
    with pytest.raises(ValueError,match='record_coverage'):
        validate_final(old_answer,prepare(covered),old_answer.claims)
