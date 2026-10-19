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
        if status=='unknown': assert result.decision.outcome=='unknown'
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
