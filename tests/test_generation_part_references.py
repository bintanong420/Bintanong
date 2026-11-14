"""Short draft references preserve canonical per-part policy and review boundaries."""
import asyncio
import json

import pytest

from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_runtime.application import RuntimeSettings
from test_generation_part_slots import FEE, OFFICE, PartModel
from test_request_understanding_pipeline import TEXT, source
from test_generation_service_cutoff import integration as cutoff_integration
from test_service_record_coverage import covered_integration
from test_generation_completeness_context import TEXT as COVERAGE_TEXT


class ShortParts(PartModel):
    def __init__(self, bad=None):
        super().__init__()
        self.bad = bad

    async def infer(self, messages, schema):
        version = schema['properties'].get('schema_version', {}).get('const')
        if version != 'bintanong-part-explanation-short-v1':
            return await super().infer(messages, schema)
        self.calls.append((messages, schema))
        payload = json.loads(messages[1]['content'])
        cards = payload['evidence']['sources']
        ref = cards[0]['evidence_id']
        refs = [ref]
        if self.bad == 'unknown': refs = ['e32']
        if self.bad == 'canonical': refs = ['ev-'+'a'*64]
        if self.bad == 'duplicate': refs = [ref, ref]
        if self.bad == 'rule': refs = ['e2']
        if self.bad == 'private': refs = ['sess-other-1']
        if self.bad == 'repair' and not payload['validation_errors']: refs = ['e32']
        answers = {p: dict(status='answered', claims=[dict(text=OFFICE if p=='r1' else FEE,
            evidence_ids=[cards[1]['evidence_id']] if p=='r2' and len(cards)>1 and self.bad is None else refs)])
                   for p in schema['properties']['answers']['required']}
        if self.bad == 'missing_part': answers.pop('r2')
        if self.bad == 'extra': answers['r1']['claims'][0]['office'] = 'invented'
        if self.bad == 'unavailable_placeholder':
            answers['r1'].update(status='source_gap', claims=[dict(text='Unusable placeholder.',evidence_ids=['e32'])])
        return json.dumps(dict(schema_version=version, release_id=payload['evidence']['release_id'],
                               language='en', answers=answers))


def run(model, integration=None):
    return asyncio.run(Generator(model, reference_profile='short').generate(TEXT, integration or source()))


def test_short_parts_restore_full_ids_before_the_unchanged_reviewer_and_final_output():
    model = ShortParts()
    answer = run(model)
    assert answer.status == 'answered' and answer.draft_attempts == answer.check_attempts == 1
    assert [c.text for c in answer.claims] == [OFFICE, FEE]
    draft_payload = json.loads(model.calls[0][0][1]['content'])
    review_payload = json.loads(model.calls[1][0][1]['content'])
    assert draft_payload['evidence']['sources'][0]['evidence_id'] == 'e1'
    assert all(ref.startswith('ev-') for c in answer.claims for ref in c.evidence_ids)
    assert all(s['evidence_id'].startswith('ev-') for s in review_payload['available_sources'])
    assert answer.part_ledger.semantic_completeness == 'unverified'


@pytest.mark.parametrize('bad', ['unknown', 'canonical', 'duplicate', 'missing_part', 'extra', 'private'])
def test_invalid_short_wire_uses_one_repair_then_withholds_before_review(bad):
    model = ShortParts(bad)
    answer = run(model)
    assert answer.status == 'abstained' and answer.validation == 'repair_exhausted'
    assert answer.draft_attempts == 2 and answer.check_attempts == 0


def test_short_parts_preserve_source_content_and_all_required_record_references():
    original = covered_integration()
    model = ShortParts()
    asyncio.run(Generator(model,reference_profile='short').generate(COVERAGE_TEXT, original))
    payload = json.loads(model.calls[0][0][1]['content'])
    pack = prepare(original)
    assert [s['text'] for s in payload['evidence']['sources']] == [c.text for c in pack.cards]
    assert payload['record_coverage'] == {'r1': ['e1', 'e2']}
    assert payload['untrusted_question'] == COVERAGE_TEXT
    assert payload['evidence']['requested_parts'] == [p.model_dump(mode='json', exclude={'subject_id', 'requested_claims', 'detail'})
                                                    for p in pack.understanding.parts]


def test_short_ids_are_decoded_before_the_source_cutoff_fidelity_guard():
    model = ShortParts()
    answer = run(model, cutoff_integration())
    assert answer.status == 'answered'
    assert 'continuation is unavailable' in answer.claims[0].text
    assert OFFICE not in answer.claims[0].text
    assert answer.claims[1].text == FEE
    assert all(ref.startswith('ev-') for c in answer.claims for ref in c.evidence_ids)


def test_short_parts_are_opt_in_and_other_profile_combinations_stay_restricted():
    assert Generator(PartModel()).reference_profile == 'canonical'
    assert RuntimeSettings(generation_reference_profile='short', explanation_profile='parts').explanation_profile == 'parts'
    for profile in ('scoped', 'covered', 'guarded'):
        with pytest.raises(ValueError): Generator(PartModel(), reference_profile='short', explanation_profile=profile)


def test_rule_alias_cannot_be_used_as_documentary_support_in_a_hybrid_part():
    answer = run(ShortParts('rule'),source(route='Hybrid'))
    assert answer.status == 'abstained' and answer.check_attempts == 0


def test_unavailable_slot_placeholder_cannot_erase_an_independent_answer():
    answer = run(ShortParts('unavailable_placeholder'))
    assert answer.status == 'answered' and [c.text for c in answer.claims] == [FEE]
    assert answer.part_ledger.status == 'some_parts_unavailable'


def test_short_repair_uses_the_same_aliases_then_runs_canonical_review():
    model = ShortParts('repair')
    answer = run(model)
    assert answer.status == 'answered' and answer.draft_attempts == 2 and answer.check_attempts == 1
    first,second = [json.loads(call[0][1]['content']) for call in model.calls[:2]]
    assert first['evidence'] == second['evidence']
    assert second['validation_errors'] == ['invalid_draft']


def test_codec_is_request_local_preserves_prose_and_rejects_a_foreign_pack():
    from backend.bintanong_generation.references import EvidenceReferences
    from backend.bintanong_generation.part_answers import ShortPartExplanation,decode_part_explanation,part_messages
    first = prepare(source())
    changed = source().model_dump(mode='json')
    changed['evidence']['documents']['passages'][0]['text'] = 'Other fictional service.'
    second = prepare(type(source()).parse(changed))
    text = 'Literal e1 and ev-'+'a'*64+' stay unchanged in prose.'
    wire = ShortPartExplanation.parse(dict(schema_version=ShortPartExplanation.SCHEMA_VERSION,
        release_id=first.release_id,language='en',answers=dict(r1=dict(status='answered',
            claims=[dict(text=text,evidence_ids=['e1'])]))))
    one = decode_part_explanation(wire,EvidenceReferences(first))
    two = decode_part_explanation(wire,EvidenceReferences(second))
    assert one.answers['r1'].claims[0].text == two.answers['r1'].claims[0].text == text
    assert one.answers['r1'].claims[0].evidence_ids != two.answers['r1'].claims[0].evidence_ids
    with pytest.raises(ValueError,match='reference_pack_mismatch'):
        part_messages(TEXT,first,references=EvidenceReferences(second))
