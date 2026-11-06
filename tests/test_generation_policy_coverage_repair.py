"""Coverage repair may quote one complete reviewed policy, without authorizing its relevance."""
from dataclasses import replace
import asyncio
import json

import pytest

from backend.bintanong_generation.part_answers import part_messages
from backend.bintanong_generation.part_answers import PartExplanation
from backend.bintanong_generation.generator import Generator
from test_generation_condition_connectives import pack_with
from test_generation_evidence import integrated
from test_generation_validation import report


POLICY = ('Activities require completion of fictional Module Z. However, the Fictional Coordinator may '
          'approve concurrent attendance for students repeating Module Z. Without approval no credit is earned.')


def policy_pack(*, detail='whole', limits=(), body=POLICY):
    record = json.dumps(dict(fields=[dict(name='body', value=body, source_blank=False)],
                             source_limits=list(limits)))
    pack = pack_with(record, language='taglish')
    part = pack.understanding.parts[0].model_copy(update=dict(
        subject_id='fictional_policy', requested_claims=('reviewed policy fields',), detail=detail))
    return replace(pack, understanding=pack.understanding.model_copy(update=dict(parts=(part,))),
                   record_coverage=(('fictional_policy', 'reviewed policy fields', (pack.cards[0].evidence_id,)),))


def payload(pack, errors=('part_question_not_answered:r1',)):
    return json.loads(part_messages('Can the fictional activities be taken together?', pack, errors=errors)[1]['content'])


def test_coverage_retry_offers_the_whole_clean_policy_including_rule_exception_and_consequence():
    pack = policy_pack()
    offered = payload(pack)['complete_policy_quote_options']['r1']
    assert offered == dict(text=POLICY, evidence_id=pack.cards[0].evidence_id)
    assert 'complete_policy_quote_options' not in payload(pack, errors=())


@pytest.mark.parametrize('updates', [dict(detail='specific'), dict(body='x'*1025),
    dict(limits=[dict(issue='source_cutoff', resolution='unresolved')])])
def test_detail_questions_and_defective_or_oversized_records_get_no_quote_option(updates):
    assert not payload(policy_pack(**updates)).get('complete_policy_quote_options')


def test_unreviewed_additional_card_is_never_offered_as_the_requested_policy():
    pack = policy_pack()
    unrelated = pack_with('Unrelated fictional text.').cards[0]
    pack = replace(pack, cards=(unrelated, *pack.cards))
    assert payload(pack)['complete_policy_quote_options']['r1']['text'] == POLICY


def test_a_multi_record_policy_is_not_replaced_by_an_arbitrary_single_record():
    pack = policy_pack()
    other = pack_with('Fictional continuation.').cards[0]
    pack = replace(pack, cards=(*pack.cards, other), record_coverage=(
        ('fictional_policy', 'reviewed policy fields', (pack.cards[0].evidence_id, other.evidence_id)),))
    assert not payload(pack).get('complete_policy_quote_options')


def test_style_repair_distinguishes_english_quotations_from_english_paraphrases():
    instruction = payload(policy_pack(), errors=('claim_not_in_requested_style',))['repair_instruction']
    assert 'English paraphrase' in instruction and 'pronouns' in instruction


def test_multiple_requested_policy_purposes_keep_their_own_reviewed_record_mapping():
    pack = policy_pack()
    first = pack.cards[0].evidence_id
    other = pack_with('Approval of fictional Form Q is required before attendance.').cards[0]
    part = pack.understanding.parts[0].model_copy(update=dict(
        requested_claims=('reviewed policy fields', 'reviewed approval fields')))
    pack = replace(pack, cards=(*pack.cards, other),
        understanding=pack.understanding.model_copy(update=dict(parts=(part,))), record_coverage=(
            ('fictional_policy', 'reviewed policy fields', (first,)),
            ('fictional_policy', 'reviewed approval fields', (other.evidence_id,))))
    value = payload(pack, errors=())
    assert value['claim_record_coverage']['r1'] == {
        'reviewed policy fields': [first], 'reviewed approval fields': [other.evidence_id]}
    assert 'distinct requested purpose' in value['claim_coverage_instruction']


@pytest.mark.parametrize('accept_quote', [True, False])
def test_complete_quote_repair_still_requires_the_ordinary_question_coverage_review(accept_quote):
    question = 'Can the fictional activities be taken together?'
    original = integrated('RAG', text=question, response_style='taglish')
    value = original.model_dump(mode='json')
    value['evidence']['documents']['passages'] = value['evidence']['documents']['passages'][:1]
    value['evidence']['pin']['documents'] = value['evidence']['pin']['documents'][:1]
    passage = value['evidence']['documents']['passages'][0]
    passage['text'] = json.dumps(dict(fields=[dict(name='body', value=POLICY, source_blank=False)], source_limits=[]))
    value['understanding']['parts'][0].update(subject_id='fictional_policy',
        requested_claims=['reviewed policy fields'], detail='whole')
    value['evidence']['documents']['record_coverage'] = [dict(subject_id='fictional_policy',
        claim='reviewed policy fields', chunk_ids=[passage['chunk_id']])]
    source = type(original).parse(value)

    class RepairModel:
        def __init__(self):
            self.checks = 0

        async def infer(self, messages, schema):
            payload = json.loads(messages[1]['content'])
            if schema['properties'].get('schema_version', {}).get('const') == PartExplanation.SCHEMA_VERSION:
                option = payload.get('complete_policy_quote_options', {}).get('r1')
                text = ('Ayon sa source: "' + option['text'] + '"' if option else
                        'Ang fictional Module Z ay kailangan sa activities.')
                ref = option['evidence_id'] if option else payload['evidence']['sources'][0]['evidence_id']
                return json.dumps(dict(schema_version=PartExplanation.SCHEMA_VERSION,
                    release_id=payload['evidence']['release_id'], language='taglish',
                    answers=dict(r1=dict(status='answered', claims=[dict(text=text, evidence_ids=[ref])]))))
            self.checks += 1
            verdict = 'answers' if self.checks == 2 and accept_quote else 'does_not_answer'
            return json.dumps(dict(parts=dict(r1=verdict), support=report().model_dump(mode='json')))

    model = RepairModel()
    answer = asyncio.run(Generator(model).generate(question, source))
    assert model.checks == 2 and answer.draft_attempts == 2
    assert answer.status == ('answered' if accept_quote else 'insufficient_evidence')
    assert bool(answer.claims) is accept_quote
    if accept_quote:
        assert POLICY in answer.text
