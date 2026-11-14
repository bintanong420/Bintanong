"""Question/release binding and per-part release guards,not semantic model accuracy."""
import asyncio
import hashlib
import importlib
import json

import pytest

from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator
from backend.bintanong_orchestration.contracts import IntegrationResult
from test_generation_evidence import integrated
from test_generation_validation import report
from test_routing_understanding import part

TEXT = 'Where do I file Form Q and what is the fee?'


def source(*, text=TEXT, route='RAG', request='req-a', need='document'):
    original = integrated(route)
    value = original.model_dump(mode='json')
    operations = []
    predicate = None
    parts = [part('Where do I file Form Q', text=text, need=need),
             part('what is the fee?', text=text, ident='r2')]
    if route != 'RAG':
        result = original.evidence.symbolic
        operations = [dict(name=result.decision.predicate, target=0)]
        predicate = dict(predicate=result.decision.predicate,
                         inputs=[i.model_dump(mode='json') for i in result.inputs])
        parts[0].update(evidence_need='structured', operation_indices=[0])
        if route == 'Symbolic': parts = parts[:1]
    value.update(request_id=request, understanding=dict(
        schema_version='bintanong-request-understanding-v1', request_id=request,
        release_id='release-synth-1', question_sha256=hashlib.sha256(text.encode()).hexdigest(),
        route=route, parts=parts, operations=operations, predicate_request=predicate))
    return IntegrationResult.parse(value)


class Scripted:
    def __init__(self, missing=False):
        self.missing = missing
        self.calls = []

    async def infer(self, messages, schema):
        self.calls.append((messages, schema))
        version = schema['properties']['schema_version']['const']
        payload = json.loads(messages[1]['content'])
        if version == 'bintanong-document-explanation-v1':
            card = payload['evidence']['sources'][0]['evidence_id']
            return json.dumps(dict(schema_version=version,
                release_id=payload['evidence']['release_id'],language=payload['evidence']['language'],
                claims=[dict(claim_id='c1', text='File at fictional Office V.', evidence_ids=[card]),
                        dict(claim_id='c2', text='The fictional fee is 40 tokens.', evidence_ids=[card])]))
        assert version == 'bintanong-part-review-v1'
        identity = payload['review_identity']
        mappings = [dict(part_id='r1', status='mapped', claim_ids=['c1'], reason=None)]
        if payload['requirements'][0]['evidence_need'] == 'structured':
            mappings = []
        if not self.missing:
            mappings.append(dict(part_id='r2', status='mapped',
                claim_ids=['c1','c2'] if not mappings else ['c2'], reason=None))
        support = report(verdicts=[dict(claim_id=c, verdict='supported') for c in ('c1','c2')])
        return json.dumps(dict(schema_version=version,
            requirements_sha256=identity['requirements_sha256'], draft_sha256=identity['draft_sha256'],
            parts=mappings, support=support.model_dump(mode='json')))


def test_ready_integration_requires_explicit_versioned_understanding():
    value = integrated('RAG').model_dump(mode='json')
    value.pop('understanding', None)
    with pytest.raises(ValueError): IntegrationResult.parse(value)
    value['schema_version'] = 'bintanong-candidate-integration-v1'
    with pytest.raises(ValueError): IntegrationResult.parse(value)


@pytest.mark.parametrize('identity,value', [('request_id','req-other'),
                                          ('release_id','release-other')])
def test_integration_rejects_foreign_question_plan(identity, value):
    data = source().model_dump(mode='json')
    data['understanding'][identity] = value
    with pytest.raises(ValueError): IntegrationResult.parse(data)


def test_generator_rejects_another_original_question_before_inference():
    async def scenario():
        model = Scripted()
        with pytest.raises(ValueError, match='question'):
            await Generator(model).generate(TEXT+' Changed.', source())
        assert model.calls == []
    asyncio.run(scenario())


def test_missing_fee_mapping_is_withheld_even_when_every_claim_has_positive_support():
    async def scenario():
        model = Scripted(missing=True)
        answer = await Generator(model, explanation_profile='scoped').generate(TEXT, source())
        assert answer.status != 'answered' and not answer.claims
        assert answer.part_ledger.status == 'unresolved'
        assert answer.part_ledger.entries[1].reason == 'missing_mapping'
        assert len(model.calls) == 2  # existing draft+support,not another classifier
    asyncio.run(scenario())


def test_two_document_parts_are_bound_and_accounted_without_claiming_semantic_truth():
    async def scenario():
        model = Scripted()
        answer = await Generator(model, explanation_profile='scoped').generate(TEXT, source())
        assert answer.status == 'answered'
        assert [e.part_id for e in answer.part_ledger.entries] == ['r1','r2']
        assert answer.part_ledger.semantic_completeness == 'unverified'
        assert len(model.calls) == 2 and answer.check_attempts == 1
        for messages, _ in model.calls:
            assert 'req-a' not in json.dumps(messages) and 'fact-synth' not in json.dumps(messages)
    asyncio.run(scenario())


def test_hybrid_uses_actual_canonical_operation_for_structured_part():
    async def scenario():
        # Documentary claim c1 is intentionally not a structured decision witness.
        model = Scripted()
        answer = await Generator(model, explanation_profile='scoped').generate(TEXT, source(route='Hybrid'))
        assert answer.status == 'answered'
        assert answer.part_ledger.canonical_parts == ('r1',)
        assert answer.part_ledger.entries[0].claim_ids == ()
        assert answer.decision == source(route='Hybrid').evidence.symbolic.decision
    asyncio.run(scenario())


def test_symbolic_result_and_parts_are_host_rendered_in_every_profile_without_model_calls():
    async def scenario():
        model=Scripted()
        answer=await Generator(model,explanation_profile='legacy').generate(TEXT,source(route='Symbolic'))
        assert answer.status=='answered' and answer.part_ledger.canonical_parts==('r1',)
        assert not model.calls and not answer.claims
    asyncio.run(scenario())


def test_wrong_symbolic_operation_cannot_be_covered_by_documentary_claims():
    data = source(route='Hybrid').model_dump(mode='json')
    data['understanding']['predicate_request']['predicate'] = 'list_affected_courses'
    wrong = IntegrationResult.parse(data)
    with pytest.raises(ValueError, match='operation'):
        prepare(wrong)


def test_review_identity_cannot_be_replayed_between_requests():
    api = importlib.import_module('backend.bintanong_generation.understanding')
    from backend.bintanong_generation.scope import canonical_draft, DocumentExplanation
    a, b = prepare(source()), prepare(source(request='req-b'))
    def draft(pack):
        return canonical_draft(DocumentExplanation.parse(dict(
            schema_version=DocumentExplanation.SCHEMA_VERSION,release_id=pack.release_id,language=pack.language,
            claims=[dict(claim_id='c1',text='Fictional policy.',evidence_ids=[pack.cards[0].evidence_id])])), pack)
    da, db = draft(a), draft(b)
    assert api.review_identity(a, da) != api.review_identity(b, db)
    from backend.bintanong_generation.requirements import RequirementReview
    identity=api.review_identity(a,da)
    review=RequirementReview.parse(dict(schema_version=RequirementReview.SCHEMA_VERSION,
        requirements_sha256=identity.requirements_sha256,draft_sha256=identity.draft_sha256,
        parts=[dict(part_id='r1',status='mapped',claim_ids=['c1'])],
        support=report().model_dump(mode='json')))
    with pytest.raises(ValueError,match='identity'):
        api.assess(b,db,review)
    schema=api.review_schema(a,da)
    assert schema['properties']['requirements_sha256']['const']==identity.requirements_sha256
    assert schema['properties']['draft_sha256']['const']==identity.draft_sha256


def test_nested_support_version_is_fixed_in_the_model_schema():
    from backend.bintanong_generation import understanding as api
    from backend.bintanong_generation.contracts import AnswerDraft, SupportReport
    pack=prepare(source())
    draft=AnswerDraft.parse(dict(schema_version=AnswerDraft.SCHEMA_VERSION,language='en',
        release_id=pack.release_id,decision_outcome=None,claims=[dict(claim_id='c1',
            text='File at Office V.',evidence_ids=[pack.cards[0].evidence_id])]))
    schema=api.review_schema(pack,draft)
    assert schema['$defs']['SupportReport']['properties']['schema_version']['const']==SupportReport.SCHEMA_VERSION


def test_final_ledger_cannot_point_to_a_claim_that_was_never_generated():
    from backend.bintanong_generation.validation import validate_final
    from backend.bintanong_generation.contracts import CandidateAnswer
    async def scenario():
        integration=source()
        answer=await Generator(Scripted(),explanation_profile='scoped').generate(TEXT,integration)
        changed=answer.model_dump(mode='json')
        changed['part_ledger']['entries'][0]['claim_ids']=['c8']
        with pytest.raises(ValueError,match='part_claim'):
            validate_final(CandidateAnswer.parse(changed),prepare(integration),answer.claims)
    asyncio.run(scenario())


def test_another_course_part_cannot_be_credited_to_the_first_course_operation():
    from backend.bintanong_orchestration.orchestrator import Orchestrator
    from test_orchestration_pipeline import resources, ports, ctx
    from test_routing_contracts import proposal
    from test_routing_router import FakeTransport
    text='Can I take A1 and can I take B1?'
    data=proposal(text=text,language='en',parts=[
        part('Can I take A1',need='structured',operations=(0,),text=text),
        part('can I take B1?',need='structured',operations=(0,),text=text,ident='r2')],
        mentions=[dict(kind='course',text='A1',start=11,end=13),
                  dict(kind='course',text='B1',start=text.index('B1'),end=text.index('B1')+2)])
    async def scenario():
        release=resources()
        integration=await Orchestrator(FakeTransport(json.dumps(data)),
            releases=ports().SyntheticReleaseProvider(release)).run(text,ctx())
        assert integration.status!='ready' and not release.symbolic.calls
    asyncio.run(scenario())
