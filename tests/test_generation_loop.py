import asyncio
import importlib
import json

import pytest

from backend.bintanong_generation.evidence import prepare
from test_generation_evidence import integrated
from test_generation_validation import draft,report


def api():
    return importlib.import_module('backend.bintanong_generation.generator')


class Fake:
    def __init__(self,*outputs):
        self.outputs=list(outputs)
        self.calls=[]

    async def infer(self,messages,schema):
        self.calls.append((messages,schema))
        value=self.outputs.pop(0)
        if isinstance(value,Exception): raise value
        return value


def good(): return draft().model_dump_json()
def supported(): return report().model_dump_json()


def test_valid_draft_and_separate_support_check_preserve_canonical_result():
    async def scenario():
        model=Fake(good(),supported())
        result=await api().Generator(model).generate('Fictional?',integrated())
        assert result.status=='answered' and result.validation=='validated'
        assert result.decision==integrated().evidence.symbolic.decision
        assert (result.draft_attempts,result.check_attempts,result.answer_repairs)==(1,1,0)
        assert 'fictional-prereq-met' in result.text and result.citations
        assert not result.institutional_use_allowed
    asyncio.run(scenario())


@pytest.mark.parametrize('bad', ['malformed','contradiction','unsupported','wrong_release'])
def test_one_repair_uses_identical_evidence_and_preserves_separate_counters(bad):
    async def scenario():
        if bad=='malformed': outputs=['{bad',good(),supported()]
        elif bad=='wrong_release': outputs=[draft(release_id='release-bad').model_dump_json(),good(),supported()]
        else: outputs=[good(),report(bad).model_dump_json(),good(),supported()]
        model=Fake(*outputs)
        result=await api().Generator(model).generate('Fictional?',integrated())
        assert result.status=='answered' and result.answer_repairs==1 and result.draft_attempts==2
        draft_calls=[m for m,s in model.calls if s['properties']['schema_version']['const']=='bintanong-answer-draft-v1']
        assert len(draft_calls)==2
        assert json.loads(draft_calls[0][1]['content'])['evidence']==json.loads(draft_calls[1][1]['content'])['evidence']
    asyncio.run(scenario())


def test_exhausted_repair_and_incomplete_checker_use_grounded_fallback():
    async def scenario():
        model=Fake(good(),report(verdicts=[]).model_dump_json(),good(),report('unsupported').model_dump_json())
        result=await api().Generator(model).generate('Fictional?',integrated())
        assert result.status=='abstained' and result.validation=='repair_exhausted'
        assert result.decision.outcome=='eligible' and len(model.calls)==4
        assert 'Fictional policy.' not in result.text
    asyncio.run(scenario())


@pytest.mark.parametrize('status', ['unknown','unsupported_scope','conflict','held'])
def test_controls_unknown_and_conflicts_skip_inference(status):
    from backend.bintanong_orchestration.contracts import IntegrationResult
    async def scenario():
        source=integrated(outcome='unknown') if status=='unknown' else IntegrationResult(
            schema_version=IntegrationResult.SCHEMA_VERSION,request_id='req-a',route=None,
            response_style='fil',status=status,evidence=None,events=())
        model=Fake()
        result=await api().Generator(model).generate('Fictional?',source)
        assert result.status!='answered' and not model.calls and result.draft_attempts==0
        if status=='unknown':
            assert result.decision.outcome=='unknown'
            assert 'confirmed result for FICTIONAL-101' in result.text
    asyncio.run(scenario())


def test_overall_generation_deadline_includes_support_check_and_cancellation_propagates():
    async def scenario():
        class Wait(Fake):
            async def infer(self,messages,schema):
                if self.outputs: return await super().infer(messages,schema)
                await asyncio.Event().wait()
        model=Wait(good())
        result=await api().Generator(model,timeout_seconds=0.03).generate('Fictional?',integrated())
        assert result.validation=='timeout' and result.status=='temporarily_unavailable'
        assert result.check_attempts==1 and result.draft_attempts==1
        task=asyncio.create_task(api().Generator(Wait()).generate('Fictional?',integrated()))
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError): await task
    asyncio.run(scenario())


def test_final_text_and_decision_tampering_rejected():
    from backend.bintanong_generation.validation import validate_final
    async def scenario():
        source=integrated()
        result=await api().Generator(Fake(good(),supported())).generate('Fictional?',source)
        with pytest.raises(ValueError,match='render'):
            validate_final(result.model_copy(update={'text':'You are officially enrolled.'}),prepare(source),draft().claims)
    asyncio.run(scenario())


@pytest.mark.parametrize('document_status',['conflicting_sources','release_changed','uncalibrated',
    'needs_scope','needs_subject','needs_claims'])
@pytest.mark.parametrize('language',['en','fil','taglish'])
def test_nonready_hybrid_never_renders_a_positive_or_negative_canonical_conclusion(document_status,language):
    from backend.bintanong_orchestration.contracts import IntegrationResult
    from backend.bintanong_orchestration.integration import assemble
    from test_orchestration_integration import pin,documents,symbolic
    async def scenario():
        for outcome in ('eligible','ineligible'):
            evidence=assemble(pin(),'Hybrid',documents=documents(document_status),symbolic=symbolic(outcome))
            source=IntegrationResult(schema_version=IntegrationResult.SCHEMA_VERSION,request_id='req-a',
                route='Hybrid',response_style=language,status=evidence.status,evidence=evidence,events=())
            answer=await api().Generator(Fake()).generate('Fictional?',source)
            assert answer.decision.outcome==outcome
            assert 'conditions satisfied' not in answer.text and 'condition is unmet' not in answer.text
            assert 'Sa sinuring prerequisite:' not in answer.text and 'Sa supported prerequisite check,' not in answer.text
            assert 'fictional-prereq' not in answer.text and not answer.citations
    asyncio.run(scenario())


def test_document_clarification_withholds_complete_dependency_listing():
    from backend.bintanong_orchestration.contracts import IntegrationResult
    from backend.bintanong_orchestration.integration import assemble
    from backend.bintanong_symbolic.runtime import DependencyResult
    from test_orchestration_integration import pin,documents,symbolic
    async def scenario():
        sym=symbolic()
        dependencies=DependencyResult(schema_version=DependencyResult.SCHEMA_VERSION,
            synthetic=True,activation_allowed=False,eligibility_executable=False,
            relation='potential_prior_completion_dependency',coverage_scope='supplied_bundle',
            status='complete',inputs=sym.inputs,course_ids=('fictional-dependent',),
            unknown_conditions=(),rule_bundle_version=sym.rule_bundle_version,scope=sym.scope,
            rule_ids=sym.rule_ids,rule_spans=sym.rule_spans,error_code=None)
        evidence=assemble(pin(),'Hybrid',documents=documents('needs_scope'),dependencies=dependencies)
        source=IntegrationResult(schema_version=IntegrationResult.SCHEMA_VERSION,request_id='req-a',
            route='Hybrid',response_style='en',status=evidence.status,evidence=evidence,events=())
        answer=await api().Generator(Fake()).generate('Fictional?',source)
        assert answer.status=='clarification_needed' and answer.dependencies==dependencies
        assert 'fictional-dependent' not in answer.text and not answer.citations
    asyncio.run(scenario())


@pytest.mark.parametrize('where',['draft','checker'])
def test_deeply_nested_json_uses_bounded_repair_then_fallback(where):
    async def scenario():
        nested='['*20000+'0'+']'*20000
        model=Fake(nested,nested) if where=='draft' else Fake(good(),nested,good(),nested)
        answer=await api().Generator(model).generate('Fictional?',integrated())
        assert answer.validation=='repair_exhausted' and answer.answer_repairs==1
    asyncio.run(scenario())


def test_unexpected_transport_error_is_a_fixed_fallback_without_exception_body():
    async def scenario():
        answer=await api().Generator(Fake(RuntimeError('PRIVATE upstream response'))).generate('Fictional?',integrated())
        assert answer.validation=='tool_error' and 'PRIVATE' not in answer.text
    asyncio.run(scenario())


def test_candidate_answer_preserves_typed_claim_mapping_and_safe_scope():
    async def scenario():
        answer=await api().Generator(Fake(good(),supported())).generate('Fictional?',integrated())
        assert answer.claims==draft().claims
        assert answer.structured_context.inputs[0].value=='FICTIONAL-101'
        assert all(i.fact_ref is None for i in answer.structured_context.inputs)
    asyncio.run(scenario())


@pytest.mark.parametrize('route,outcome',[('RAG',None),('Symbolic','eligible'),('Hybrid','ineligible')])
def test_request_grammar_only_allows_the_host_decision_and_matches_prompt(route,outcome):
    from backend.bintanong_generation.contracts import AnswerDraft
    from backend.bintanong_generation.prompt import output_schema
    async def scenario():
        base=output_schema(AnswerDraft)
        source=integrated(route,outcome=outcome or 'eligible')
        pack=prepare(source)
        model=Fake(draft(pack).model_dump_json(),supported())
        answer=await api().Generator(model).generate('Fictional?',source)
        assert answer.status=='answered'
        messages,schema=model.calls[0]
        field=schema['properties']['decision_outcome']
        assert field.get('type')==('null' if outcome is None else 'string')
        if outcome is not None: assert field['const']==outcome
        prompted_schema=json.loads(messages[0]['content'].split('\nOutput schema:\n',1)[1])
        assert prompted_schema==schema
        assert output_schema(AnswerDraft)==base
    asyncio.run(scenario())


@pytest.mark.parametrize('invented',['eligible','unknown'])
def test_rag_still_rejects_a_decision_invented_by_a_nonconforming_transport(invented):
    async def scenario():
        pack=prepare(integrated('RAG'))
        invalid=draft(pack,decision_outcome=invented).model_dump_json()
        model=Fake(invalid,invalid)
        answer=await api().Generator(model).generate('Fictional?',integrated('RAG'))
        assert answer.validation=='repair_exhausted' and answer.decision is None
        assert answer.check_attempts==0 and not answer.claims
    asyncio.run(scenario())
