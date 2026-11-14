"""A claim that states a printed rule keeps the printed exception attached to it.

Observed 30 Oct 2026 (summer-load, English and Taglish): "What is the normal unit load for summer?" was answered
with the nine-unit rule while the next printed sentence, a twelve-unit exception subject to the Dean's approval,
was dropped. Prompt wording alone did not change the draft; a deterministic check sends it back for repair."""
import asyncio
import json

from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation import part_answers
from test_generation_condition_connectives import draft, pack_with
from test_generation_part_slots import PartModel
from test_request_understanding_pipeline import TEXT, source

RULE = ('FICTIONAL LOAD. The normal load for the fictional term shall be six (6) units. '
        'Graduating students may, however, be allowed a higher load not to exceed eight (8) units, '
        'subject to prior approval of the Dean.')


def test_a_rule_without_its_attached_exception_is_rejected():
    pack = pack_with(RULE)
    claim = 'The normal load for the fictional term is six (6) units.'
    assert part_answers.omitted_exception_errors(draft(pack, claim), pack) == ('omitted_printed_exception',)


def test_a_rule_with_its_exception_passes():
    pack = pack_with(RULE)
    claim = ('The normal load is six (6) units; graduating students may be allowed up to eight (8) units '
             'with the prior approval of the Dean.')
    assert part_answers.omitted_exception_errors(draft(pack, claim), pack) == ()


def test_an_exception_to_a_rule_the_claim_does_not_state_is_not_required():
    pack = pack_with('Late payment costs ten (10) tokens. ' + RULE)
    claim = 'Late payment costs ten (10) tokens.'
    assert part_answers.omitted_exception_errors(draft(pack, claim), pack) == ()


def test_an_unnumbered_exception_is_left_to_the_reviewer():
    pack = pack_with('Classes start at seven (7). Laboratory classes may, however, start later.')
    assert part_answers.omitted_exception_errors(draft(pack, 'Classes start at seven (7).'), pack) == ()


def test_printed_fields_are_read_from_a_record_card():
    record = json.dumps(dict(evidence_sha256='1' * 64, fields=[dict(name='body', source_blank=False, value=RULE)]))
    pack = pack_with(record)
    claim = 'The normal load for the fictional term is six (6) units.'
    assert part_answers.omitted_exception_errors(draft(pack, claim), pack) == ('omitted_printed_exception',)


def test_only_answered_slots_are_checked():
    pack = pack_with(RULE)
    proposal = draft(pack, 'The normal load for the fictional term is six (6) units.')
    assert part_answers.omitted_exception_errors(proposal, pack, {'r1': ('host', ('c1',))}) == ()
    assert part_answers.omitted_exception_errors(proposal, pack, {'r1': ('answered', ('c1',))}) == (
        'omitted_printed_exception',)


def test_the_repair_request_quotes_the_omitted_printed_exception():
    pack = pack_with(RULE)
    messages = part_answers.part_messages(TEXT, pack, errors=('omitted_printed_exception',))
    instruction = json.loads(messages[1]['content'])['exception_instruction']
    assert 'as printed' in instruction['instruction']
    assert any('eight (8) units' in sentence for sentence in instruction['printed_exceptions'])
    clean = json.loads(part_answers.part_messages(TEXT, pack)[1]['content'])
    assert 'exception_instruction' not in clean


class Recording(PartModel):
    def __init__(self):
        super().__init__()
        self.drafts = []

    async def infer(self, messages, schema):
        payload = json.loads(messages[1]['content'])
        if 'untrusted_previous_draft' in payload:
            self.drafts.append(payload)
        return await super().infer(messages, schema)


def test_generator_sends_an_omitted_exception_back_for_repair(monkeypatch):
    from backend.bintanong_generation import generator
    found = iter([('omitted_printed_exception',)])
    monkeypatch.setattr(generator, 'omitted_exception_errors', lambda draft, pack, slots: next(found, ()))
    model = Recording()
    answer = asyncio.run(Generator(model).generate(TEXT, source()))
    assert answer.draft_attempts == 2
    assert 'omitted_printed_exception' in model.drafts[1]['validation_errors']
