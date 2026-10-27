"""Long procedures are drafted in consecutive record segments, then validated and reviewed once."""
import asyncio
import json

from backend.bintanong_generation import part_answers
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator
from backend.bintanong_orchestration.contracts import IntegrationResult
from test_generation_part_slots import PartModel
from test_request_understanding_pipeline import TEXT, source

SUBJECT = 'fictional_service'


def long_integration(records=8):
    value = source().model_dump(mode='json')
    first = value['evidence']['documents']['passages'][0]
    member = value['evidence']['pin']['documents'][0]
    ids = [f'{n:064x}' for n in range(1, records + 1)]
    value['evidence']['documents']['passages'] = [dict(first, chunk_id=c, text=f'Fictional step {n}.')
                                                  for n, c in enumerate(ids, 1)]
    value['evidence']['pin']['documents'] = [dict(member, chunk_id=c) for c in ids]
    whole, totals = value['understanding']['parts']
    whole.update(subject_id=SUBJECT, requested_claims=['whole service'])
    totals.update(subject_id=SUBJECT, requested_claims=['totals'])
    value['evidence']['documents']['record_coverage'] = [
        dict(subject_id=SUBJECT, claim='whole service', chunk_ids=ids),
        dict(subject_id=SUBJECT, claim='totals', chunk_ids=ids[-1:])]
    return IntegrationResult.parse(value)


def test_plan_splits_long_ordered_records_into_balanced_segments():
    pack = prepare(long_integration(8))
    plan = part_answers.segment_plan(pack)
    cards = [c.evidence_id for c in pack.cards]
    assert plan.part_id == 'r1' and plan.nested == ('r2',)
    assert plan.segments == (tuple(cards[:4]), tuple(cards[4:]))
    assert plan.claims_per_segment == 3  # (8 claims - 1 nested part) // 2 segments
    # Each segment's records are pre-grouped, in order, into one group per claim.
    assert plan.groups == (((cards[0], cards[1]), (cards[2],), (cards[3],)),
                           ((cards[4], cards[5]), (cards[6],), (cards[7],)))


def test_segment_schema_binds_each_claim_to_its_record_group():
    pack = prepare(long_integration(8))
    plan = part_answers.segment_plan(pack)
    claims = part_answers.part_schema(pack, None, (plan, 1))['properties']['answers']['properties']['r1'][
        'properties']['claims']
    assert claims['minItems'] == claims['maxItems'] == 3
    assert [item['properties']['evidence_ids']['const'] for item in claims['prefixItems']] == [
        list(group) for group in plan.groups[1]]


def test_short_procedures_keep_the_single_call_path():
    assert part_answers.segment_plan(prepare(long_integration(6))) is None


class SegmentModel(PartModel):
    """Drafts exactly the requested segment; optionally omits one record on the first pass."""
    def __init__(self, omit_first=False):
        super().__init__()
        self.segments, self.omit_first = [], omit_first

    async def infer(self, messages, schema):
        self.calls.append((messages, schema))
        payload = json.loads(messages[1]['content'])
        if 'segment' not in payload:
            self.calls.pop()
            return await super().infer(messages, schema)
        self.segments.append(payload)
        groups = list(payload['segment']['claim_groups'])
        if self.omit_first and len(self.segments) == 1:
            groups = groups[1:]
        answers = dict(r1=dict(status='answered', claims=[dict(text='Fictional step summary.', evidence_ids=g)
                                                           for g in groups]))
        if 'r2' in schema['properties']['answers']['required']:
            answers['r2'] = dict(status='answered', claims=[dict(text='Fictional total.',
                                                                 evidence_ids=payload['record_coverage']['r2'])])
        return json.dumps(dict(schema_version=part_answers.PartExplanation.SCHEMA_VERSION,
                               release_id=payload['evidence']['release_id'], language='en', answers=answers))


def kinds(model):
    return [s['properties'].get('schema_version', {}).get('const', 'review') for _, s in model.calls]


def test_generator_drafts_each_segment_then_reviews_the_merged_answer_once():
    model = SegmentModel()
    answer = asyncio.run(Generator(model).generate(TEXT, long_integration(8)))
    assert answer.status == 'answered' and answer.draft_attempts == answer.check_attempts == 1
    assert kinds(model) == ['bintanong-part-explanation-v1'] * 2 + ['review']
    first, second = model.segments
    assert first['record_coverage']['r1'] == first['segment']['records']  # only this segment's records
    assert first['segment']['index'] == 1 and second['segment']['count'] == 2
    assert 'r2' in model.calls[0][1]['properties']['answers']['required']
    assert 'r2' not in model.calls[1][1]['properties']['answers']['required']
    pack = prepare(long_integration(8))
    cited = [ref for c in answer.claims for ref in c.evidence_ids]
    assert set(c.evidence_id for c in pack.cards) <= set(cited)


def test_incomplete_merged_draft_redrafts_every_segment_with_the_errors():
    model = SegmentModel(omit_first=True)
    answer = asyncio.run(Generator(model).generate(TEXT, long_integration(8)))
    assert answer.status == 'answered' and answer.draft_attempts == 2
    assert len(model.segments) == 4
    assert model.segments[2]['validation_errors'] == ['missing_procedure_record_coverage']
