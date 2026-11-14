"""Reviewed source sequence, distinct from citation coverage or semantic truth."""
import asyncio
import json

import pytest

from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator, _answer
from backend.bintanong_generation.part_answers import (
    PartConfirmationOutput, PartExplanation, assess_slots, bind_confirmation, to_draft)
from backend.bintanong_generation.understanding import review_identity
from backend.bintanong_orchestration.contracts import DocumentResult
from backend.bintanong_orchestration.orchestrator import merge_documents
from backend.bintanong_retrieval.candidate_claims import (
    build_candidate_claim_report, prepare_candidate_claim_reviews)
from backend.bintanong_retrieval.candidate_subject import prepare_candidate_subject_catalogue
from test_candidate_claim_reviews import chunk
from test_generation_validation import report
from test_service_record_coverage import CLAIM, SUBJECT, ReviewedEngine, covered_integration, retrieve
from test_generation_completeness_context import TEXT
from test_request_understanding_pipeline import TEXT as TWO_PART_TEXT, source as two_part_source


def source_review():
    chunks = [chunk('z'), chunk('a')]
    for item in chunks:
        item['type_fields']['field_associations'][0].update(name='client_step', value='Fictional step.')
    catalogue = prepare_candidate_subject_catalogue(chunks, [dict(reading_id=item['chunk_id'],
        subject_id=SUBJECT, basis_ref='synthetic-source-review') for item in chunks])
    review = dict(subject_id=SUBJECT, claim=CLAIM, finding='visible_fields',
        reviewed_chunk_ids=['a', 'z'], field_refs=[dict(reading_id=i, field_name='client_step') for i in ('a', 'z')],
        basis_ref='synthetic-source-review#ordered-steps', basis_sha256='2'*64,
        procedure_order=['z', 'a'])
    return catalogue, chunks, review


def test_explicit_review_sequence_survives_lexically_sorted_field_references():
    catalogue, chunks, review = source_review()
    register = prepare_candidate_claim_reviews(catalogue, chunks, [review])
    value = build_candidate_claim_report(catalogue, chunks, subject_id=SUBJECT,
        requested_claims=[CLAIM], emitted_chunk_ids=['a', 'z'], claim_reviews=register)
    assert value['claims'][0]['source_review']['procedure_order'] == ['z', 'a']
    assert [field['reading_id'] for field in value['claims'][0]['source_fields']] == ['a', 'z']
    assert review['procedure_order'] == ['z', 'a']  # no input mutation


@pytest.mark.parametrize('edit', [
    lambda r, c: r.update(procedure_order=['z', 'z']),
    lambda r, c: r.update(procedure_order=['z']),
    lambda r, c: r.update(procedure_order=['z', 'outside']),
    lambda r, c: r.update(procedure_order=[]),
    lambda r, c: r.update(procedure_order='z,a'),
    lambda r, c: r.update(procedure_order=['z', {}]),
    lambda r, c: r.update(finding='not_stated_in_selected_fields', field_refs=[]),
    lambda r, c: c[0].update(version_id='another-version'),
    lambda r, c: c[0]['type_fields']['field_associations'][0].update(name='office'),
    lambda r, c: c[0]['type_fields']['field_associations'][0].update(value=0),
])
def test_procedure_order_requires_exact_reviewed_nonblank_steps_from_one_source(edit):
    catalogue, chunks, review = source_review()
    edit(review, chunks)
    catalogue = prepare_candidate_subject_catalogue(chunks, catalogue['assignments'])
    with pytest.raises(ValueError, match='procedure_order'):
        prepare_candidate_claim_reviews(catalogue, chunks, [review])


def test_adapter_uses_reviewed_order_instead_of_field_or_retrieval_order(monkeypatch):
    original = ReviewedEngine.retrieve
    def ordered(engine, request, **intent):
        raw = original(engine, request, **intent)
        claim = raw['evidence_policy']['assessment']['claims'][0]
        fields = claim['source_fields']
        for index, field in enumerate(fields):
            field['reading_id'] = f'step-{index}'
        claim['source_review']['procedure_order'] = ['step-1', 'step-0']
        return raw
    monkeypatch.setattr(ReviewedEngine, 'retrieve', ordered)
    value = retrieve()
    requirement, = value.record_coverage
    assert requirement.source_ordered is True
    assert requirement.chunk_ids == tuple(p.chunk_id for p in reversed(value.passages))


def ordered_integration(*, ordered=True, other_subject=False):
    original = covered_integration(other_subject=other_subject)
    value = original.model_dump(mode='json')
    documents = value['evidence']['documents']
    for item, label in zip(documents['passages'], ('First fictional step.', 'Second fictional step.')):
        item['text'] = label
    documents['passages'].reverse()  # retrieval order is deliberately wrong
    if ordered:
        documents['record_coverage'][0]['source_ordered'] = True
    return type(original).parse(value)


def test_absent_order_retains_the_original_document_serialization():
    value = covered_integration().evidence.documents.model_dump(mode='json')
    assert DocumentResult.parse(value).model_dump(mode='json') == value
    assert 'source_ordered' not in value['record_coverage'][0]


def test_merging_identical_ordered_requirements_preserves_the_sequence_flag():
    documents = ordered_integration().evidence.documents
    merged = merge_documents([documents, documents])
    assert merged.record_coverage == documents.record_coverage


@pytest.mark.parametrize('change', ['reverse', 'unordered'])
def test_merging_cannot_discard_or_reconcile_incompatible_order_contracts(change):
    first = ordered_integration().evidence.documents
    other = first.model_dump(mode='json')
    if change == 'reverse':
        other['record_coverage'][0]['chunk_ids'].reverse()
    else:
        other['record_coverage'][0].pop('source_ordered')
    with pytest.raises(ValueError, match='order'):
        merge_documents([first, DocumentResult.parse(other)])


class StepModel:
    def __init__(self, mode='reverse', *, repair=False, unavailable=False):
        self.mode, self.repair, self.unavailable = mode, repair, unavailable
        self.calls = []

    async def infer(self, messages, schema):
        payload = json.loads(messages[1]['content'])
        self.calls.append(payload)
        version = schema['properties'].get('schema_version', {}).get('const')
        if version in ('bintanong-part-explanation-v1', 'bintanong-part-explanation-short-v1'):
            cards = sorted((card for card in payload['evidence']['sources']
                if card['text'].endswith('fictional step.')), key=lambda card: card['text'])
            if self.mode == 'reverse' and not (self.repair and payload['validation_errors']):
                cards.reverse()
            if self.mode == 'repeat':
                cards = [cards[0], cards[1], cards[0]]
            claims = [dict(text=card['text'], evidence_ids=[card['evidence_id']]) for card in cards]
            if self.mode == 'combined':
                claims = [dict(text='Two fictional steps.', evidence_ids=[card['evidence_id'] for card in cards])]
            return json.dumps(dict(schema_version=version, release_id=payload['evidence']['release_id'],
                language='en', answers=dict(r1=dict(status='source_gap' if self.unavailable else 'answered',
                    claims=[] if self.unavailable else claims))))
        ids = [entry['claim']['claim_id'] for part in payload['parts'] for entry in part['claims']]
        return json.dumps(dict(parts={part['part_id']: 'answers' for part in payload['parts']}, support=report(verdicts=[
            dict(claim_id=identity, verdict='supported') for identity in ids]).model_dump(mode='json')))


@pytest.mark.parametrize('profile', ['canonical', 'short'])
@pytest.mark.parametrize('mode', ['reverse', 'repeat', 'combined'])
def test_approving_reviewer_cannot_release_wrong_or_ambiguous_step_order(profile, mode):
    model = StepModel(mode)
    answer = asyncio.run(Generator(model, reference_profile=profile).generate(TEXT, ordered_integration()))
    assert answer.status == 'abstained' and answer.draft_attempts == 2 and answer.check_attempts == 0
    assert 'procedure_record_order' in model.calls[1]['validation_errors']


@pytest.mark.parametrize('profile', ['canonical', 'short'])
def test_one_existing_repair_restores_reviewed_order_before_ordinary_review(profile):
    model = StepModel(repair=True)
    original = ordered_integration()
    answer = asyncio.run(Generator(model, reference_profile=profile).generate(TEXT, original))
    assert answer.status == 'answered' and answer.draft_attempts == 2 and answer.check_attempts == 1
    assert [claim.text for claim in answer.claims] == ['First fictional step.', 'Second fictional step.']
    source_ids = {source['text']: source['evidence_id'] for source in model.calls[0]['evidence']['sources']}
    assert model.calls[0]['record_order']['r1'] == [[source_ids['First fictional step.'], source_ids['Second fictional step.']]]
    assert all(ref.startswith('ev-') for sequence in model.calls[-1]['record_order']['r1'] for ref in sequence)


def test_order_is_not_imposed_on_an_unordered_other_subject_or_unavailable_part():
    for original in (ordered_integration(ordered=False), ordered_integration(other_subject=True)):
        answer = asyncio.run(Generator(StepModel()).generate(TEXT, original))
        assert answer.status == 'answered' and answer.draft_attempts == 1
    answer = asyncio.run(Generator(StepModel(unavailable=True)).generate(TEXT, ordered_integration()))
    assert answer.status == 'insufficient_evidence' and answer.check_attempts == 0


def test_unavailable_ordered_part_keeps_an_independent_answer_and_its_normal_review():
    value = two_part_source().model_dump(mode='json')
    documents = value['evidence']['documents']
    first = documents['passages'][0]
    first['text'] = 'First fictional step.'
    second = dict(first, chunk_id='e'*64, text='Second fictional step.')
    fee = dict(first, chunk_id='d'*64, text='Independent fictional fee.')
    documents['passages'].extend([second, fee])
    member = value['evidence']['pin']['documents'][0]
    value['evidence']['pin']['documents'].extend([dict(member, chunk_id=step['chunk_id']) for step in (second, fee)])
    documents['record_coverage'] = [dict(subject_id=SUBJECT, claim=CLAIM,
        chunk_ids=[first['chunk_id'], second['chunk_id']], source_ordered=True)]
    value['understanding']['parts'][0].update(subject_id=SUBJECT, requested_claims=[CLAIM])
    original = type(two_part_source()).parse(value)

    class IndependentFee(StepModel):
        async def infer(self, messages, schema):
            raw = await super().infer(messages, schema)
            payload = json.loads(messages[1]['content'])
            output = json.loads(raw)
            if 'answers' in output:
                card = next(card for card in payload['evidence']['sources'] if card['text'] == fee['text'])
                output['answers']['r2'] = dict(status='answered', claims=[dict(
                    text=fee['text'], evidence_ids=[card['evidence_id']])])
            return json.dumps(output)

    model = IndependentFee(unavailable=True)
    answer = asyncio.run(Generator(model).generate(TWO_PART_TEXT, original))
    assert answer.status == 'answered' and [claim.text for claim in answer.claims] == [fee['text']]
    assert answer.part_ledger.status == 'some_parts_unavailable' and answer.check_attempts == 1
    assert [part['part_id'] for part in model.calls[-1]['parts']] == ['r2']
    assert 'record_order' not in model.calls[-1]


def test_review_identity_binds_the_explicit_sequence_without_changing_legacy_evidence():
    original = ordered_integration()
    pack = prepare(original)
    model = StepModel(mode='correct')
    answer = asyncio.run(Generator(model).generate(TEXT, original))
    from backend.bintanong_generation.contracts import AnswerDraft
    draft = AnswerDraft.parse(dict(schema_version=AnswerDraft.SCHEMA_VERSION,
        release_id=pack.release_id, language='en', decision_outcome=None,
        claims=[claim.model_dump(mode='json') for claim in answer.claims]))
    unordered = prepare(ordered_integration(ordered=False))
    assert 'record_order' not in unordered.model_payload()
    assert review_identity(pack, draft).requirements_sha256 != review_identity(unordered, draft).requirements_sha256


@pytest.mark.parametrize('reorder_mapping', [False, True])
def test_positive_bound_ledger_cannot_bypass_order_at_final_validation(reorder_mapping):
    pack = prepare(ordered_integration())
    cards = sorted(pack.cards, key=lambda card: card.text, reverse=True)
    explanation = PartExplanation.parse(dict(schema_version=PartExplanation.SCHEMA_VERSION,
        release_id=pack.release_id, language='en', answers=dict(r1=dict(status='answered', claims=[
            dict(text=card.text, evidence_ids=[card.evidence_id]) for card in cards]))))
    draft, slots = to_draft(explanation, pack)
    if reorder_mapping:
        slots['r1'] = ('answered', tuple(reversed(slots['r1'][1])))
    output = PartConfirmationOutput.parse(dict(parts=dict(r1='answers'), support=report(verdicts=[
        dict(claim_id=claim.claim_id, verdict='supported') for claim in draft.claims]).model_dump(mode='json')))
    ledger = assess_slots(pack, draft, slots, bind_confirmation(pack, draft, output))
    with pytest.raises(ValueError, match='record_coverage'):
        _answer(pack, 'answered', claims=draft.claims, reason='validated', ledger=ledger)
