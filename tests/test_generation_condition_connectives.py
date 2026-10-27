"""Claims may not join printed conditions with a disjunction the cited source does not state."""
import asyncio
from dataclasses import replace
import json

from backend.bintanong_generation.contracts import AnswerDraft
from backend.bintanong_generation.evidence import _card, prepare
from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation import part_answers
from test_generation_part_slots import FEE, PartModel
from test_request_understanding_pipeline import TEXT, source

LISTED = ('Cross-enrollment is allowed provided: a) the subject is not offered; '
          'b) the schedule is in conflict. c) the subject is not a major subject. '
          'd) the units do not exceed nine (9).')


def pack_with(*texts, language='en'):
    pack = prepare(source())
    cards = tuple(_card('document', text, list(pack.cards[0].citations)) for text in texts)
    return replace(pack, cards=cards, language=language)


def draft(pack, *texts, cited=None):
    ids = cited or [pack.cards[0].evidence_id]
    return AnswerDraft.parse(dict(schema_version=AnswerDraft.SCHEMA_VERSION, release_id=pack.release_id,
        language=pack.language, decision_outcome=None,
        claims=[dict(claim_id=f'c{n}', text=t, evidence_ids=ids) for n, t in enumerate(texts, 1)]))


def test_or_between_listed_conditions_is_rejected():
    pack = pack_with(LISTED)
    claim = 'Allowed if the subject is not offered, or the schedule conflicts, or it is not a major subject.'
    assert part_answers.disjunction_errors(draft(pack, claim), pack) == ('introduced_disjunction',)


def test_conditions_listed_as_printed_pass():
    pack = pack_with(LISTED)
    claim = ('Allowed provided: a) the subject is not offered; b) the schedule is in conflict; '
             'c) it is not a major subject; d) at most nine units.')
    assert part_answers.disjunction_errors(draft(pack, claim), pack) == ()


def test_a_disjunction_printed_in_the_cited_source_may_be_restated():
    pack = pack_with('No student may cross-enroll in two (2) or more schools.')
    assert part_answers.disjunction_errors(draft(pack, 'You cannot cross-enroll in two or more schools.'), pack) == ()


def test_tagalog_o_counts_as_a_disjunction():
    pack = pack_with(LISTED, language='taglish')
    claim = 'Pwede kung hindi offered yung subject o kaya may conflict sa schedule.'
    assert part_answers.disjunction_errors(draft(pack, claim), pack) == ('introduced_disjunction',)
    printed = pack_with('Two (2) or more schools are not allowed.', language='taglish')
    assert part_answers.disjunction_errors(draft(printed, 'Bawal sa dalawa o higit pang schools.'), printed) == ()


def test_counts_use_only_the_sources_each_claim_cites():
    pack = pack_with(LISTED, 'Pay at the cashier or online.')
    first = pack.cards[0].evidence_id
    claim = 'Allowed if the subject is not offered or the schedule conflicts.'
    assert part_answers.disjunction_errors(draft(pack, claim, cited=[first]), pack) == ('introduced_disjunction',)


class DisjunctionThenListed(PartModel):
    """First draft joins conditions with 'or'; the repair lists them as printed."""
    def __init__(self):
        super().__init__(slots=dict(r1=('answered', ['File Form Q at Office V or at Office W.']),
                                    r2=('answered', [FEE])))
        self.drafts = []

    async def infer(self, messages, schema):
        payload = json.loads(messages[1]['content'])
        if 'untrusted_previous_draft' in payload:
            self.drafts.append(payload)
            if len(self.drafts) == 2:
                self.slots = dict(r1=('answered', ['File Form Q at fictional Office V.']), r2=('answered', [FEE]))
        return await super().infer(messages, schema)


def test_generator_repairs_an_introduced_disjunction_with_plain_instruction():
    model = DisjunctionThenListed()
    answer = asyncio.run(Generator(model).generate(TEXT, source()))
    assert answer.status == 'answered' and answer.draft_attempts == 2
    repair = model.drafts[1]
    assert 'introduced_disjunction' in repair['validation_errors']
    assert 'as printed' in repair['condition_instruction']


def test_host_written_claims_are_not_checked():
    pack = pack_with('The fee is 40 tokens.')
    proposal = draft(pack, 'The fee is 40 tokens.', 'Bintanong cannot confirm whether it applies now or later.')
    slots = {'r1': ('answered', ('c1',)), 'r2': ('host', ('c2',))}
    assert part_answers.disjunction_errors(proposal, pack, slots) == ()
    assert part_answers.disjunction_errors(proposal, pack, {'r1': ('answered', ('c1', 'c2'))}) == ('introduced_disjunction',)
