"""Synthetic sanctions: a fallible model must not adjudicate recorded precedence gaps."""
import asyncio
import hashlib
import json

import pytest

from backend.bintanong_generation.generator import Generator
from test_generation_validation import report
from test_request_understanding_pipeline import source


LIMIT = 'precedence between overlapping admission-fraud sanctions'
UNSAFE = 'You will receive only a fictional warning; the other row does not apply.'
SAFE = 'The fictional fee is 40 tokens.'
TEXT = 'Which sanctions are printed for a fictional false entry declaration; what is the fee?'


def row(label, cause, penalty, *, resolution='unresolved', affected=LIMIT):
    return dict(fields=[dict(name='Cause', value=cause, source_blank=False),
        dict(name='1st Offense', value=penalty, source_blank=False),
        dict(name='2nd Offense', value='', source_blank=True)], source_limits=[dict(
            gap_id=f'handbook-disciplinary-{label}-fraud-precedence', issue='claim_not_stated',
            resolution=resolution, affected_claims=[affected], field_names=['Cause'])])


def integration(*, language='en', rows=None, route='RAG', foreign=False):
    original = source(route=route)
    value = original.model_dump(mode='json')
    value['understanding']['question_sha256'] = hashlib.sha256(TEXT.encode()).hexdigest()
    for part, quote in zip(value['understanding']['parts'], TEXT.split('; ')):
        start = TEXT.index(quote)
        part.update(text=quote, start=start, end=start+len(quote))
    value['response_style'] = language
    rows = rows if rows is not None else [
        row('II.6', 'Fictional declaration during entry or continued study.', 'Fictional warning.'),
        row('II.8a', 'Fictional false entry documents.', 'Fictional exclusion.')]
    template = value['evidence']['documents']['passages'][0]
    member = value['evidence']['pin']['documents'][0]
    passages, members = [], []
    for n, content in enumerate([*rows, SAFE], 1):
        chunk = f'{n:064x}'
        passage = dict(template, chunk_id=chunk, text=json.dumps(content) if isinstance(content, dict) else content)
        if foreign and n == 2:
            passage['version_id'] = 'ver-'+'f'*64
            passage['citations'] = [dict(c, version_id='ver-'+'f'*64, byte_sha256='f'*64)
                                    for c in passage['citations']]
        passages.append(passage)
        members.append(dict(member, chunk_id=chunk, version_id=passage['version_id'],
                            byte_sha256=passage['citations'][0]['byte_sha256']))
    if foreign:
        value['evidence']['pin']['sources'].append(dict(version_id='ver-'+'f'*64, byte_sha256='f'*64))
    value['evidence']['documents']['passages'] = passages
    value['evidence']['pin']['documents'] = members
    return type(original).parse(value)


class ChoosingModel:
    def __init__(self, choose=0, *, target='r1', verdict='answers'):
        self.choose, self.target, self.calls = choose, target, []
        self.verdict = verdict

    async def infer(self, messages, schema):
        payload = json.loads(messages[1]['content'])
        self.calls.append(payload)
        version = schema['properties'].get('schema_version', {}).get('const')
        if version == 'bintanong-part-explanation-v1':
            cards = payload['evidence']['sources']
            rows = [c for c in cards if c['text'].startswith('{')]
            safe = next(c for c in cards if c['text'] == SAFE)
            answers = {}
            for part in schema['properties']['answers']['required']:
                card, text = (rows[self.choose], UNSAFE) if part == self.target else (safe, SAFE)
                if payload['evidence']['language'] != 'en':
                    text = 'Ang '+text
                answers[part] = dict(status='answered', claims=[dict(text=text, evidence_ids=[card['evidence_id']])])
            return json.dumps(dict(schema_version=version, release_id=payload['evidence']['release_id'],
                language=payload['evidence']['language'], answers=answers))
        claims = [c['claim']['claim_id'] for p in payload['parts'] for c in p['claims']]
        support = report(verdicts=[dict(claim_id=c, verdict='supported') for c in claims])
        return json.dumps(dict(parts={p['part_id']: self.verdict if p['part_id'] == self.target else 'answers'
                                      for p in payload['parts']},
            support=support.model_dump(mode='json')))


@pytest.mark.parametrize('language,notice', [
    ('en', 'does not establish which sanction applies'),
    ('fil', 'hindi clear kung aling sanction ang applicable'),
    ('taglish', 'hindi clear kung aling sanction ang applicable')])
@pytest.mark.parametrize('choose', [0, 1])
def test_model_choice_is_replaced_by_both_labelled_rows_and_unresolved_precedence(language, notice, choose):
    model = ChoosingModel(choose)
    answer = asyncio.run(Generator(model).generate(TEXT, integration(language=language)))
    assert answer.status == 'answered' and UNSAFE not in answer.text
    assert 'II.6' in answer.text and 'II.8a' in answer.text and notice in answer.text
    assert 'Fictional warning.' in answer.text and 'Fictional exclusion.' in answer.text
    assert 'Fictional declaration during entry or continued study.' in answer.text
    assert 'Fictional false entry documents.' in answer.text
    assert SAFE in answer.text and len(answer.citations) == 3
    assert len(answer.claims) == 3  # two host rows plus the independent part
    assert answer.part_ledger.status == 'all_declared_parts_mapped'
    assert [p['part_id'] for p in model.calls[-1]['parts']] == ['r1', 'r2']


@pytest.mark.parametrize('rows', [
    [row('II.6', 'Fictional entry declaration.', 'Fictional warning.')],
    [row('II.8a', 'Fictional entry document.', 'Fictional exclusion.')],
    [row('II.6', 'Fictional entry declaration.', 'Fictional warning.')]*2])
def test_missing_or_duplicate_counterpart_withholds_only_affected_part(rows):
    answer = asyncio.run(Generator(ChoosingModel()).generate(TEXT, integration(rows=rows)))
    assert answer.status == 'answered' and UNSAFE not in answer.text
    assert [c.text for c in answer.claims] == [SAFE]
    assert answer.part_ledger.entries[0].reason == 'source_gap'


def test_counterpart_from_another_source_version_cannot_settle_the_overlap():
    answer = asyncio.run(Generator(ChoosingModel()).generate(TEXT, integration(foreign=True)))
    assert UNSAFE not in answer.text and answer.part_ledger.entries[0].reason == 'source_gap'


@pytest.mark.parametrize('resolution,affected', [('resolved', LIMIT), ('unresolved', 'individual share')])
def test_resolved_or_other_not_stated_claim_does_not_trigger_precedence_override(resolution, affected):
    rows = [row('II.6', 'Fictional entry declaration.', 'Fictional warning.',
                resolution=resolution, affected=affected)]
    answer = asyncio.run(Generator(ChoosingModel()).generate(TEXT, integration(rows=rows)))
    assert UNSAFE in answer.text and len(answer.claims) == 2


def test_uncited_overlap_rows_do_not_replace_an_independent_answer():
    answer = asyncio.run(Generator(ChoosingModel(target='none')).generate(TEXT, integration()))
    assert all(c.text == SAFE for c in answer.claims)
    assert 'II.6' not in answer.text and 'II.8a' not in answer.text


def test_canonical_hybrid_result_survives_the_comparative_document_reply():
    answer = asyncio.run(Generator(ChoosingModel(target='r2')).generate(TEXT, integration(route='Hybrid')))
    assert answer.status == 'answered' and answer.decision.outcome == 'eligible'
    assert answer.part_ledger.canonical_parts == ('r1',)
    assert UNSAFE not in answer.text and 'II.6' in answer.text and 'II.8a' in answer.text


def test_blank_penalty_is_unspecified_rather_than_no_penalty():
    answer = asyncio.run(Generator(ChoosingModel()).generate(TEXT, integration()))
    assert '2nd Offense: unspecified' in answer.text
    assert 'no penalty' not in answer.text.lower()


def test_newly_added_counterpart_cannot_bypass_its_malformed_source_hold():
    rows = [row('II.6', 'Fictional entry declaration.', 'Fictional warning.'),
            row('II.8a', 'Fictional entry document.', 'Fictional exclusion.')]
    rows[1]['source_limits'].append(dict(issue='malformed_source_condition', resolution='unresolved',
                                       affected_claims=['exception'], field_names=['Cause']))
    answer = asyncio.run(Generator(ChoosingModel()).generate(TEXT, integration(rows=rows)))
    assert UNSAFE not in answer.text and 'Fictional exclusion.' not in answer.text
    assert [c.text for c in answer.claims] == [SAFE]
    assert answer.part_ledger.entries[0].reason == 'source_gap'


def test_comparison_does_not_overflow_eight_claims_and_erase_independent_parts():
    text = '; '.join(f'Fictional question {n}?' for n in range(1, 9))
    value = integration().model_dump(mode='json')
    value['understanding']['question_sha256'] = hashlib.sha256(text.encode()).hexdigest()
    parts = []
    for n, quote in enumerate(text.split('; '), 1):
        start = text.index(quote)
        parts.append(dict(part_id=f'r{n}', text=quote, start=start, end=start+len(quote),
                          evidence_need='document', operation_indices=[]))
    value['understanding']['parts'] = parts
    answer = asyncio.run(Generator(ChoosingModel()).generate(text, type(integration()).parse(value)))
    assert answer.status == 'answered' and UNSAFE not in answer.text
    assert all(e.status == 'mapped' for e in answer.part_ledger.entries[1:])
    assert len([c for c in answer.claims if c.text == SAFE]) == 7
    assert len(answer.claims) <= 8


def test_corrected_comparison_still_needs_to_answer_its_own_question_part():
    model = ChoosingModel(verdict='does_not_answer')
    answer = asyncio.run(Generator(model).generate(TEXT, integration()))
    assert answer.status == 'insufficient_evidence' and not answer.claims
    assert answer.part_ledger.entries[0].status == 'uncertain'
    assert UNSAFE not in answer.text and 'Fictional warning.' not in answer.text


def test_comparison_preserves_an_independently_cited_claim_in_the_same_slot():
    from backend.bintanong_generation.evidence import prepare
    from backend.bintanong_generation.part_answers import PartExplanation,to_draft
    pack = prepare(integration())
    overlap = next(c for c in pack.cards if 'Fictional warning.' in c.text)
    independent = next(c for c in pack.cards if c.text == SAFE)
    explanation = PartExplanation.parse(dict(schema_version=PartExplanation.SCHEMA_VERSION,
        release_id=pack.release_id,language='en',answers=dict(
            r1=dict(status='answered',claims=[dict(text=UNSAFE,evidence_ids=[overlap.evidence_id]),
                                            dict(text=SAFE,evidence_ids=[independent.evidence_id])]),
            r2=dict(status='not_in_evidence',claims=[]))))
    draft,slots = to_draft(explanation,pack)
    assert any(c.text == SAFE for c in draft.claims)
    assert len(draft.claims) == 3 and len(slots['r1'][1]) == 3
    assert UNSAFE not in ' '.join(c.text for c in draft.claims)
    assert 'II.6' in draft.claims[0].text and 'II.8a' in draft.claims[1].text
