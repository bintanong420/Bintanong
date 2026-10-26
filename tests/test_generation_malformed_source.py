"""A known malformed condition cannot become a supported model interpretation.

All policy wording is fictional. The break caught is releasing a model-authored
claim from an explicitly held record, even when a reviewer would approve it.
"""
import asyncio
import json

import pytest

from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.part_answers import PartExplanation, to_draft
from test_generation_validation import report
from test_request_understanding_pipeline import TEXT, source


HELD = 'The unclear exception allows fictional Form Q to bypass approval.'
SAFE = 'The fictional fee is 40 tokens.'


def integration(*, issue='malformed_source_condition', resolution='unresolved', language='en', route='RAG'):
    original = source(route=route)
    value = original.model_dump(mode='json')
    value['response_style'] = language
    passages = value['evidence']['documents']['passages']
    passages[0]['text'] = json.dumps(dict(fields=[dict(name='condition', source_blank=False,
        value='Fictional Form Q exception has malformed wording.')], source_limits=[dict(
        issue=issue, resolution=resolution, field_names=['condition'],
        affected_claims=['meaning of the fictional exception'])]))
    second = dict(passages[0], chunk_id='0'*63+'2', text=SAFE)
    passages.append(second)
    value['evidence']['pin']['documents'].append(dict(value['evidence']['pin']['documents'][0],
        chunk_id=second['chunk_id']))
    return type(original).parse(value)


class ApprovingModel:
    """A fallible external model; actual host assembly/validation/rendering run."""
    def __init__(self, *, held_parts=('r1',), include_foreign=False, verdict='answers'):
        self.held_parts = held_parts
        self.include_foreign = include_foreign
        self.verdict = verdict
        self.calls = []

    async def infer(self, messages, schema):
        payload = json.loads(messages[1]['content'])
        self.calls.append(payload)
        version = schema['properties'].get('schema_version', {}).get('const')
        if version == 'bintanong-part-explanation-v1':
            cards = payload['evidence']['sources']
            held = next(c['evidence_id'] for c in cards if c['text'].startswith('{'))
            safe = next(c['evidence_id'] for c in cards if c['text'] == SAFE)
            answers = {}
            for part in schema['properties']['answers']['required']:
                text, evidence = (HELD, held) if part in self.held_parts else (SAFE, safe)
                if payload['evidence']['language'] != 'en':
                    text = 'Ang '+text  # exercise host guard without an unrelated style failure
                refs = [evidence] + (['ev-'+'f'*64] if self.include_foreign else [])
                answers[part] = dict(status='answered', claims=[dict(text=text, evidence_ids=refs)])
            return json.dumps(dict(schema_version=version, release_id=payload['evidence']['release_id'],
                language=payload['evidence']['language'], answers=answers))
        claims = [c['claim']['claim_id'] for p in payload['parts'] for c in p['claims']]
        support = report(verdicts=[dict(claim_id=c, verdict='supported') for c in claims])
        return json.dumps(dict(parts={p['part_id']: self.verdict for p in payload['parts']},
            support=support.model_dump(mode='json')))


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_held_record_cannot_answer_even_when_the_model_asserts_an_exception(language):
    model = ApprovingModel(held_parts=('r1', 'r2'))
    answer = asyncio.run(Generator(model).generate(TEXT, integration(language=language)))
    assert answer.status == 'insufficient_evidence'
    assert not answer.claims and not answer.citations and HELD not in answer.text
    assert [(e.status, e.reason) for e in answer.part_ledger.entries] == [
        ('unavailable', 'source_gap'), ('unavailable', 'source_gap')]
    assert answer.check_attempts == 0
    assert ('hindi malinaw' if language == 'fil' else 'unclear') in answer.text
    assert "not in Bintanong's reviewed sources yet" not in answer.text


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_other_part_keeps_its_answer_citation_and_review_binding(language):
    model = ApprovingModel()
    answer = asyncio.run(Generator(model).generate(TEXT, integration(language=language)))
    assert answer.status == 'answered' and HELD not in answer.text
    assert len(answer.claims) == len(answer.citations) == 1
    assert SAFE in answer.claims[0].text and answer.claims[0].claim_id == 'c1'
    assert [(e.part_id, e.status, e.claim_ids, e.reason) for e in answer.part_ledger.entries] == [
        ('r1', 'unavailable', (), 'source_gap'), ('r2', 'mapped', ('c1',), None)]
    assert answer.part_ledger.status == 'some_parts_unavailable'
    assert [p['part_id'] for p in model.calls[-1]['parts']] == ['r2']
    assert all(c.text == SAFE for c in answer.citations)
    assert ('hindi malinaw' if language == 'fil' else 'unclear') in answer.text


def test_canonical_hybrid_result_survives_an_unavailable_document_part():
    model = ApprovingModel(held_parts=('r2',))
    answer = asyncio.run(Generator(model).generate(TEXT, integration(route='Hybrid')))
    assert answer.status == 'answered' and answer.decision.outcome == 'eligible'
    assert not answer.claims and HELD not in answer.text
    assert answer.part_ledger.canonical_parts == ('r1',)
    assert answer.part_ledger.entries[1].reason == 'source_gap'
    assert answer.check_attempts == 0


@pytest.mark.parametrize('issue,resolution', [('malformed_source_condition', 'resolved'),
    ('source_cutoff', 'unresolved'), ('claim_not_stated', 'unresolved')])
def test_other_or_resolved_limits_do_not_invoke_the_malformed_record_hold(issue, resolution):
    # This test checks the metadata boundary, not the truth of fictional prose.
    model = ApprovingModel()
    answer = asyncio.run(Generator(model).generate(TEXT, integration(issue=issue, resolution=resolution)))
    assert answer.status == 'answered' and len(answer.claims) == 2
    assert answer.part_ledger.status == 'all_declared_parts_mapped'


def test_uncited_malformed_record_does_not_block_safe_claims():
    answer = asyncio.run(Generator(ApprovingModel(held_parts=())).generate(TEXT, integration()))
    assert answer.status == 'answered' and len(answer.claims) == 2
    assert all(c.text == SAFE for c in answer.claims)


def test_hold_does_not_hide_a_foreign_evidence_reference():
    pack = prepare(integration())
    held = next(c.evidence_id for c in pack.cards if c.text.startswith('{'))
    explanation = PartExplanation.parse(dict(schema_version=PartExplanation.SCHEMA_VERSION,
        release_id=pack.release_id, language='en', answers={p: dict(status='answered', claims=[dict(
            text=HELD, evidence_ids=[held, 'ev-'+'f'*64])]) for p in ('r1', 'r2')}))
    with pytest.raises(ValueError, match='non_document_evidence'):
        to_draft(explanation, pack)


def test_source_gap_notice_does_not_hide_another_parts_failed_verification():
    model = ApprovingModel(verdict='does_not_answer')
    answer = asyncio.run(Generator(model).generate(TEXT, integration()))
    assert answer.status == 'insufficient_evidence' and not answer.claims
    assert [(e.status, e.reason) for e in answer.part_ledger.entries] == [
        ('unavailable', 'source_gap'), ('uncertain', 'uncertain')]
    assert 'A supported explanation could not be verified from the supplied evidence.' in answer.text
    assert 'incomplete or unclear' in answer.text and SAFE not in answer.text
