"""A positive model verdict cannot complete a documented service-action cutoff."""
import asyncio
import copy
import json

import pytest

from backend.bintanong_generation.contracts import AnswerDraft
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator, _answer
from backend.bintanong_generation.part_answers import (
    PartConfirmationOutput, PartExplanation, assess_slots, bind_confirmation, to_draft)
from backend.bintanong_generation.validation import validate_draft
from test_generation_validation import report
from test_request_understanding_pipeline import TEXT, source


CLIENT = 'Take fictional Form Q to Office V for encoding.'
ACTION = 'Clerk encodes Form Q and asks the client to proceed to Office W for'
UNSAFE = 'Proceed to Office W for final approval, where the clerk encodes Form Q.'
FEE = 'Ang fictional fee ay 40 tokens.'
FIELDS = [('client_step', CLIENT), ('agency_action', ACTION), ('responsible_person', 'Clerk'),
          ('office', 'Office T'), ('fee', ''), ('processing_time', '5 minutes')]


def record():
    return dict(fields=[dict(name=n, value=v, source_blank=not v) for n, v in FIELDS],
        source_limits=[dict(issue='source_cutoff', resolution='unresolved',
                            field_names=['agency_action'])])


def integration(language='en', *, edit=None):
    original = source()
    value = original.model_dump(mode='json')
    value['response_style'] = language
    data = record()
    if edit:
        edit(data)
    first = value['evidence']['documents']['passages'][0]
    first['text'] = json.dumps(data)
    value['evidence']['documents']['passages'].append(dict(first, chunk_id='e'*64, text=FEE))
    value['evidence']['pin']['documents'].append(dict(value['evidence']['pin']['documents'][0], chunk_id='e'*64))
    return type(original).parse(value)


class PositiveModel:
    def __init__(self, *, verdict='answers', duplicate=False):
        self.verdict, self.duplicate = verdict, duplicate
        self.calls = []

    async def infer(self, messages, schema):
        payload = json.loads(messages[1]['content'])
        self.calls.append(payload)
        version = schema['properties'].get('schema_version', {}).get('const')
        if version == PartExplanation.SCHEMA_VERSION:
            cards = payload['evidence']['sources']
            bad = dict(text=UNSAFE, evidence_ids=[cards[0]['evidence_id']])
            return json.dumps(dict(schema_version=version, release_id=payload['evidence']['release_id'],
                language=payload['evidence']['language'], answers=dict(
                    r1=dict(status='answered', claims=[bad]*(2 if self.duplicate else 1)),
                    r2=dict(status='answered', claims=[dict(text=FEE, evidence_ids=[cards[1]['evidence_id']])]))))
        ids = [c['claim']['claim_id'] for p in payload['parts'] for c in p['claims']]
        return json.dumps(dict(parts={p['part_id']: self.verdict for p in payload['parts']},
            support=report(verdicts=[dict(claim_id=i, verdict='supported') for i in ids]).model_dump(mode='json')))


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_cutoff_record_is_quoted_without_completing_or_joining_its_fields(language):
    model = PositiveModel()
    answer = asyncio.run(Generator(model).generate(TEXT, integration(language)))
    assert answer.status == 'answered' and answer.draft_attempts == answer.check_attempts == 1
    claim = answer.claims[0]
    assert 'final approval' not in answer.text and UNSAFE not in answer.text
    assert json.dumps(CLIENT) in claim.text and json.dumps(ACTION) in claim.text
    assert 'Office T' in claim.text and 'Clerk' in claim.text
    assert len(claim.evidence_ids) == 1 and answer.claims[1].text == FEE
    assert 'None' not in claim.text  # blank fee never becomes no fee
    reviewed = model.calls[1]['parts'][0]['claims'][0]['claim']['text']
    assert reviewed == claim.text  # host text is reviewed, not the discarded model draft
    assert answer.part_ledger.semantic_completeness == 'unverified'


def test_duplicate_citations_do_not_duplicate_the_protected_record():
    answer = asyncio.run(Generator(PositiveModel(duplicate=True)).generate(TEXT, integration()))
    assert answer.status == 'answered' and len(answer.claims) == 2


def test_quoted_record_still_requires_the_ordinary_relevance_review():
    model = PositiveModel(verdict='does_not_answer')
    answer = asyncio.run(Generator(model).generate(TEXT, integration()))
    assert answer.status == 'insufficient_evidence' and not answer.claims and answer.check_attempts == 1


@pytest.mark.parametrize('edit', [
    lambda r: r['fields'].append(dict(name='unknown_field', value='Extra', source_blank=False)),
    lambda r: r['fields'].append(copy.deepcopy(r['fields'][0])),
    lambda r: r['fields'][1].update(source_blank='false'),
    lambda r: r['fields'][1].update(value='', source_blank=True),
    lambda r: r['source_limits'][0]['field_names'].append('missing_field'),
    lambda r: r['source_limits'][0]['field_names'].append({}),
    lambda r: r['fields'][1].update(value='A'*1300),
])
def test_ambiguous_or_oversized_record_withholds_only_the_affected_part(edit):
    model = PositiveModel()
    answer = asyncio.run(Generator(model).generate(TEXT, integration(edit=edit)))
    assert answer.status == 'answered' and [c.text for c in answer.claims] == [FEE]
    assert [(e.part_id, e.status, e.reason) for e in answer.part_ledger.entries] == [
        ('r1', 'unavailable', 'source_gap'), ('r2', 'mapped', None)]
    assert [p['part_id'] for p in model.calls[1]['parts']] == ['r2']


@pytest.mark.parametrize('edit', [
    lambda r: r['source_limits'][0].update(resolution='resolved'),
    lambda r: r.update(source_limits=[]),
])
def test_other_records_keep_the_ordinary_model_review_path(edit):
    answer = asyncio.run(Generator(PositiveModel()).generate(TEXT, integration(edit=edit)))
    assert answer.status == 'answered' and answer.claims[0].text == UNSAFE


def unsafe_draft(pack):
    ids = [c.evidence_id for c in pack.cards]
    return AnswerDraft.parse(dict(schema_version=AnswerDraft.SCHEMA_VERSION,
        release_id=pack.release_id, language='en', decision_outcome=None,
        claims=[dict(claim_id='c1', text=UNSAFE, evidence_ids=[ids[0]]),
                dict(claim_id='c2', text=FEE, evidence_ids=[ids[1]])]))


def test_draft_validation_rejects_untransformed_cutoff_prose():
    pack = prepare(integration())
    assert 'service_cutoff_fidelity' in validate_draft(unsafe_draft(pack), pack)


def test_final_validation_cannot_release_an_unsafe_draft_with_a_positive_bound_ledger():
    pack = prepare(integration())
    draft = unsafe_draft(pack)
    slots = dict(r1=('answered', ('c1',)), r2=('answered', ('c2',)))
    output = PartConfirmationOutput.parse(dict(parts=dict(r1='answers', r2='answers'),
        support=report(verdicts=[dict(claim_id=i, verdict='supported') for i in ('c1', 'c2')]).model_dump(mode='json')))
    ledger = assess_slots(pack, draft, slots, bind_confirmation(pack, draft, output))
    with pytest.raises(ValueError, match='cutoff'):
        _answer(pack, 'answered', claims=draft.claims, reason='validated', ledger=ledger)


def test_expanding_two_records_cannot_erase_an_independent_parts_claim_budget():
    original = integration()
    value = original.model_dump(mode='json')
    third = copy.deepcopy(value['evidence']['documents']['passages'][0])
    third.update(chunk_id='d'*64, text=third['text'].replace('Form Q', 'Form R'))
    value['evidence']['documents']['passages'].append(third)
    value['evidence']['pin']['documents'].append(dict(value['evidence']['pin']['documents'][0], chunk_id='d'*64))
    pack = prepare(type(original).parse(value))
    refs = [c.evidence_id for c in pack.cards]
    proposal = PartExplanation.parse(dict(schema_version=PartExplanation.SCHEMA_VERSION,
        release_id=pack.release_id, language='en', answers=dict(
            r1=dict(status='answered', claims=[dict(text=UNSAFE, evidence_ids=[refs[0], refs[2]])]),
            r2=dict(status='answered', claims=[dict(text=FEE, evidence_ids=[refs[1]]) for _ in range(7)]))))
    draft, slots = to_draft(proposal, pack)
    assert slots['r1'] == ('source_gap', ())
    assert slots['r2'][0] == 'answered' and len(draft.claims) == 7
    assert all(c.text == FEE for c in draft.claims)
