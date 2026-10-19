import asyncio
import json

import pytest

from test_generation_loop import api as generation
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
        return json.dumps(dict(schema_version='bintanong-prose-support-v1',language_appropriate=True,
            within_scope=True,verdicts=[dict(claim_id=c['claim_id'],verdict='supported')
                for c in payload['untrusted_draft']['claims']]))


@pytest.mark.parametrize('route',['RAG','Symbolic','Hybrid'])
def test_composed_request_uses_same_text_context_and_pinned_release(route):
    async def scenario():
        executor=orchestration().Orchestrator(transport(route),releases=ports().SyntheticReleaseProvider(resources()))
        pipeline=generation().AnswerPipeline(executor,generation().Generator(EchoEvidence()))
        result=await pipeline.run('A1',ctx())
        assert result.status=='answered' and result.request_id=='req-a'
        assert result.release_id=='release-synth-1' and result.language=='taglish'
        if route!='RAG': assert result.decision.outcome=='eligible'
    asyncio.run(scenario())


def test_composed_request_deadline_includes_orchestration_time():
    async def scenario():
        class Wait:
            async def run(self,text,context): await asyncio.Event().wait()
        pipeline=generation().AnswerPipeline(Wait(),generation().Generator(EchoEvidence()),timeout_seconds=0.02)
        result=await pipeline.run('A1',ctx())
        assert result.status=='temporarily_unavailable' and result.validation=='timeout'
        assert result.draft_attempts==0
    asyncio.run(scenario())
