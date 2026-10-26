"""Completeness review sees omitted available records; support keeps each claim's own sources."""
import asyncio
import json

from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.part_answers import PartExplanation, confirm_messages, to_draft
from test_generation_evidence import integrated
from test_generation_validation import report


TEXT = 'What are the requirements and steps for fictional Form Q?'
CHECKLIST = 'Bring fictional card Z.'
STEP = json.dumps(dict(fields=[dict(name='client_step', value='Next, fill fictional Form Q.', source_blank=False)],
                       source_limits=[dict(issue='source_cutoff', resolution='unresolved',
                                           affected_claims=['the end of this fictional step'])]))


def integration(route='RAG'):
    original = integrated(route, text=TEXT if route == 'RAG' else 'Check course A1; '+TEXT)
    value = original.model_dump(mode='json')
    value['evidence']['documents']['passages'][0]['text'] = CHECKLIST
    first = value['evidence']['documents']['passages'][0]
    value['evidence']['documents']['passages'].append(dict(first, chunk_id='e'*64, text=STEP))
    value['evidence']['pin']['documents'].append(dict(value['evidence']['pin']['documents'][0],chunk_id='e'*64))
    return type(original).parse(value)


def review_payload(route='RAG'):
    pack = prepare(integration(route))
    doc = next(c for c in pack.cards if c.text == CHECKLIST)
    part = next(p.part_id for p in pack.understanding.parts if p.evidence_need == 'document')
    explanation = PartExplanation.parse(dict(schema_version=PartExplanation.SCHEMA_VERSION,
        release_id=pack.release_id, language='en', answers={part:dict(status='answered',claims=[
            dict(text=CHECKLIST,evidence_ids=[doc.evidence_id])])}))
    draft, slots = to_draft(explanation,pack)
    return pack, json.loads(confirm_messages(TEXT,pack,draft,slots)[1]['content'])


def test_confirmation_can_see_an_available_step_the_draft_omitted():
    pack, payload = review_payload()
    assert {c['text'] for c in payload['available_sources']} == {CHECKLIST, STEP}
    assert len(payload['available_sources']) == 2
    linked = payload['parts'][0]['claims'][0]['source_ids']
    lookup = {c['evidence_id']:c for c in payload['available_sources']}
    attached = [lookup[ref] for ref in linked]
    assert [c['text'] for c in attached] == [CHECKLIST]
    assert 'sources' not in payload['parts'][0]['claims'][0]
    assert json.loads(next(c['text'] for c in payload['available_sources'] if c['text']==STEP))['source_limits']


def test_coverage_context_stays_document_only_in_a_hybrid_review():
    pack, payload = review_payload('Hybrid')
    assert any(c.kind=='rule' for c in pack.cards)
    assert {c['kind'] for c in payload['available_sources']} == {'document'}
    assert 'decision' not in payload and 'structured_context' not in payload
    assert all(c.kind=='document' for c in pack.cards if c.evidence_id in {
        s['evidence_id'] for s in payload['available_sources']})


class MissingStepModel:
    async def infer(self,messages,schema):
        payload=json.loads(messages[1]['content'])
        version=schema['properties'].get('schema_version',{}).get('const')
        if version==PartExplanation.SCHEMA_VERSION:
            card=next(c for c in payload['evidence']['sources'] if c['text']==CHECKLIST)
            return json.dumps(dict(schema_version=version,release_id=payload['evidence']['release_id'],
                language='en',answers=dict(r1=dict(status='answered',claims=[
                    dict(text=CHECKLIST,evidence_ids=[card['evidence_id']])]))))
        # Fallible external reviewer: it can notice the missing step only if the host sends it.
        missing=any(c['text']==STEP for c in payload.get('available_sources',[]))
        support=report(verdicts=[dict(claim_id='c1',verdict='supported')])
        return json.dumps(dict(parts=dict(r1='does_not_answer' if missing else 'answers'),
                               support=support.model_dump(mode='json')))


def test_partial_checklist_is_not_released_when_review_detects_the_omitted_step():
    answer=asyncio.run(Generator(MissingStepModel()).generate(TEXT,integration()))
    assert answer.status=='insufficient_evidence' and not answer.claims
    assert answer.part_ledger.entries[0].status=='uncertain'
    assert answer.draft_attempts==answer.check_attempts==1
