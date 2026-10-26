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


@pytest.mark.parametrize('kwargs',[dict(finding='not_stated_in_selected_fields')])
def test_unstated_fields_do_not_require_source_records(kwargs):
    assert 'record_coverage' not in retrieve(**kwargs).model_dump(mode='json')


@pytest.mark.parametrize('field_name',['requirement_1','Cause','3.3'])
def test_nonblank_requested_fields_also_require_their_own_records(field_name):
    result = retrieve(field_name=field_name)
    assert result.record_coverage[0].chunk_ids == tuple(p.chunk_id for p in result.passages)


def test_required_companion_records_are_mandatory_even_without_direct_claim_fields():
    class WithCompanion(ReviewedEngine):
        def retrieve(self,request,**intent):
            value=super().retrieve(request,**intent)
            claim=value['evidence_policy']['assessment']['claims'][0]
            claim['source_fields']=claim['source_fields'][:1]
            claim['required_chunk_ids']=[p['chunk_id'] for p in value['evidence']]
            return value
    result=asyncio.run(RetrievalAdapter(WithCompanion(),research=True).retrieve(
        RetrievalRequest('Fictional service?','release-synth-1')))
    assert result.record_coverage[0].chunk_ids==tuple(p.chunk_id for p in result.passages)


def test_reviewed_sequence_can_be_a_subset_of_all_required_context_records():
    class OrderedWithContext(ReviewedEngine):
        def retrieve(self,request,**intent):
            value=super().retrieve(request,**intent)
            value['evidence'].append(dict(value['evidence'][0],chunk_id='c'*64,text='Fictional total context.'))
            claim=value['evidence_policy']['assessment']['claims'][0]
            for n,field in enumerate(claim['source_fields']):field['reading_id']=f'step-{n}'
            claim['source_review']['procedure_order']=['step-0','step-1']
            claim['required_chunk_ids']=[p['chunk_id'] for p in value['evidence']]
            return value
    result=asyncio.run(RetrievalAdapter(OrderedWithContext(),research=True).retrieve(
        RetrievalRequest('Fictional service?','release-synth-1')))
    requirement=result.record_coverage[0]
    assert set(requirement.chunk_ids)=={p.chunk_id for p in result.passages}
    assert requirement.sequence_chunk_ids==tuple(p.chunk_id for p in result.passages[:2])


@pytest.mark.parametrize('sequence,ordered',[(('a'*64,),True),(('a'*64,'a'*64),True),
    (('a'*64,'c'*64),True),(('a'*64,'b'*64),False)])
def test_invalid_explicit_sequence_subset_rejects(sequence,ordered):
    from backend.bintanong_orchestration.contracts import DocumentRecordCoverage
    with pytest.raises(ValueError):
        DocumentRecordCoverage(subject_id=SUBJECT,claim=CLAIM,chunk_ids=('a'*64,'b'*64),
            source_ordered=ordered,sequence_chunk_ids=sequence)


def test_prepared_order_excludes_required_context_that_is_not_a_client_step():
    from backend.bintanong_generation.part_answers import required_record_sources,required_record_order
    value=covered_integration().model_dump(mode='json')
    docs=value['evidence']['documents'];third=dict(docs['passages'][0],chunk_id='c'*64,text='Fictional total context.')
    docs['passages'].append(third)
    value['evidence']['pin']['documents'].append(dict(value['evidence']['pin']['documents'][0],chunk_id='c'*64))
    identities=[p['chunk_id'] for p in docs['passages']]
    docs['record_coverage']=[dict(subject_id=SUBJECT,claim=CLAIM,chunk_ids=identities,
        source_ordered=True,sequence_chunk_ids=identities[:2])]
    pack=prepare(type(integration()).parse(value))
    texts={c.evidence_id:c.text for c in pack.cards}
    assert {texts[ref] for ref in required_record_sources(pack)['r1']}=={CHECKLIST,STEP,'Fictional total context.'}
    assert [texts[ref] for ref in required_record_order(pack)['r1'][0]]==[CHECKLIST,STEP]


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


def test_part_confirmation_receives_exact_requested_claims_and_record_requirements():
    from backend.bintanong_generation.part_answers import PartExplanation,to_draft,confirm_messages
    pack=prepare(covered_integration())
    explanation=PartExplanation.parse(dict(schema_version=PartExplanation.SCHEMA_VERSION,
        release_id=pack.release_id,language='en',answers=dict(r1=dict(status='answered',claims=[
            dict(text=card.text,evidence_ids=[card.evidence_id]) for card in pack.cards]))))
    draft,slots=to_draft(explanation,pack)
    payload=json.loads(confirm_messages(TEXT,pack,draft,slots)[1]['content'])
    assert payload['parts'][0]['requested_claims']==[CLAIM]
    assert set(payload['required_records']['r1'])=={c.evidence_id for c in pack.cards}


def test_review_identity_binds_the_requested_record_floor():
    from dataclasses import replace
    from backend.bintanong_generation.part_answers import PartExplanation,to_draft
    from backend.bintanong_generation.understanding import review_identity
    pack=prepare(covered_integration())
    draft,_=to_draft(PartExplanation.parse(dict(schema_version=PartExplanation.SCHEMA_VERSION,
        release_id=pack.release_id,language='en',answers=dict(r1=dict(status='answered',claims=[
            dict(text=card.text,evidence_ids=[card.evidence_id]) for card in pack.cards])))),pack)
    weaker=replace(pack,record_coverage=())
    assert review_identity(pack,draft).requirements_sha256!=review_identity(weaker,draft).requirements_sha256


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
    with pytest.raises(ValueError,match='final_part_identity_mismatch'):
        validate_final(old_answer,prepare(covered),old_answer.claims)
    from backend.bintanong_generation.contracts import AnswerDraft
    from backend.bintanong_generation.generator import _answer
    from backend.bintanong_generation.understanding import review_identity
    pack=prepare(covered)
    draft=AnswerDraft.parse(dict(schema_version=AnswerDraft.SCHEMA_VERSION,
        release_id=pack.release_id,language=pack.language,decision_outcome=None,
        claims=[c.model_dump(mode='json') for c in old_answer.claims]))
    rebound=old_answer.part_ledger.model_copy(update=dict(identity=review_identity(pack,draft)))
    with pytest.raises(ValueError,match='record_coverage'):
        _answer(pack,'answered',claims=old_answer.claims,reason='validated',ledger=rebound)
