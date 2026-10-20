import asyncio
import json

import pytest

from test_generation_loop import api as generation
from test_generation_loop import part_review
from test_orchestration_pipeline import api as orchestration,ports,resources,transport,ctx


class EchoEvidence:
    """Synthetic protocol helper; no language or support accuracy claim."""
    async def infer(self,messages,schema):
        payload=json.loads(messages[1]['content'])
        if schema['properties']['schema_version']['const']=='bintanong-answer-draft-v1':
            evidence=payload['evidence']
            return json.dumps(dict(schema_version='bintanong-answer-draft-v1',language=evidence['language'],
                release_id=evidence['release_id'],decision_outcome=(evidence['decision'] or {}).get('outcome'),
                claims=[dict(claim_id='c1',text=evidence['sources'][0]['text'],
                    evidence_ids=[evidence['sources'][0]['evidence_id']])]))
        support=dict(schema_version='bintanong-prose-support-v1',language_appropriate=True,
            within_scope=True,verdicts=[dict(claim_id=c['claim_id'],verdict='supported')
                for c in (entry['claim'] for entry in payload['claim_evidence'])])
        return json.dumps(part_review(payload,support))


@pytest.mark.parametrize('route',['RAG','Symbolic','Hybrid'])
def test_composed_request_uses_same_text_context_and_pinned_release(route):
    async def scenario():
        executor=orchestration().Orchestrator(transport(route),releases=ports().SyntheticReleaseProvider(resources()))
        pipeline=generation().AnswerPipeline(executor,generation().Generator(EchoEvidence(),explanation_profile='legacy'))
        result=await pipeline.run('A1 policy',ctx())
        assert result.status=='answered' and result.request_id=='req-a'
        assert result.release_id=='release-synth-1' and result.language=='taglish'
        if route!='RAG': assert result.decision.outcome=='eligible'
    asyncio.run(scenario())


def test_composed_request_deadline_includes_orchestration_time():
    async def scenario():
        class Wait:
            async def run(self,text,context): await asyncio.Event().wait()
        pipeline=generation().AnswerPipeline(Wait(),generation().Generator(EchoEvidence(),explanation_profile='legacy'),timeout_seconds=0.02)
        result=await pipeline.run('A1 policy',ctx())
        assert result.status=='temporarily_unavailable' and result.validation=='timeout'
        assert result.draft_attempts==0
    asyncio.run(scenario())


@pytest.mark.parametrize('language,missing_label,program_label,curriculum_label',[
    ('en','Missing information','degree program','curriculum version'),
    ('fil','Kulang na impormasyon','programa','bersiyon ng kurikulum'),
    ('taglish','Missing information','degree program','curriculum version')])
@pytest.mark.parametrize('missing',['program_id','curriculum_id'])
def test_scope_clarification_names_the_information_the_student_must_supply(
        language,missing_label,program_label,curriculum_label,missing):
    from backend.bintanong_routing.contracts import RequestContext
    from test_routing_contracts import context
    async def scenario():
        executor=orchestration().Orchestrator(transport(language=language),
            releases=ports().SyntheticReleaseProvider(resources()))
        pipeline=generation().AnswerPipeline(executor,generation().Generator(EchoEvidence(),explanation_profile='legacy'))
        request=RequestContext.parse(context(**{missing:None}))
        answer=await pipeline.run('A1 policy',request)
        expected=program_label if missing=='program_id' else curriculum_label
        assert answer.status=='clarification_needed' and answer.draft_attempts==0
        assert f'{missing_label}: {expected}' in answer.text
        assert missing not in answer.text
        assert answer.missing_facts==(missing,)
    asyncio.run(scenario())
