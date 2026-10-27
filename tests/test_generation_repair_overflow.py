"""A repair prompt that overflows retries once without the model's own previous draft."""
import asyncio
import json

from backend.bintanong_generation.generator import Generator
from backend.bintanong_routing.transport import RuntimeFailure
from test_generation_part_slots import PartModel
from test_request_understanding_pipeline import TEXT, source


class OverflowingRepair(PartModel):
    """First draft is invalid; a repair carrying that draft overflows the context preflight."""
    def __init__(self, *, overflow_without_previous=False):
        super().__init__()
        self.overflow_without_previous = overflow_without_previous
        self.sent = []

    async def infer(self, messages, schema):
        payload = json.loads(messages[1]['content'])
        if 'untrusted_previous_draft' in payload:  # draft request, not a part review
            self.sent.append(payload)
            if len(self.sent) == 1:
                return 'not json'
            if payload['untrusted_previous_draft'] or self.overflow_without_previous:
                raise RuntimeFailure('context_overflow')  # preflight: no inference happened
        return await super().infer(messages, schema)


def run(model):
    return asyncio.run(Generator(model).generate(TEXT, source()))


def test_overflowing_repair_retries_with_errors_and_complete_sources_but_no_previous_draft():
    model = OverflowingRepair()
    answer = run(model)
    assert answer.status == 'answered' and answer.draft_attempts == 2
    first, overflowed, retried = model.sent
    assert overflowed['untrusted_previous_draft'] == 'not json'
    assert retried['untrusted_previous_draft'] == ''
    assert retried['validation_errors'] == overflowed['validation_errors'] == ['invalid_draft']
    assert retried['evidence'] == overflowed['evidence'] == first['evidence']


def test_repair_still_refuses_when_it_overflows_without_the_previous_draft():
    model = OverflowingRepair(overflow_without_previous=True)
    answer = run(model)
    assert answer.status == 'temporarily_unavailable' and answer.validation == 'tool_error'
    assert len(model.sent) == 3


def test_initial_overflow_is_not_retried():
    class InitialOverflow(PartModel):
        async def infer(self, messages, schema):
            self.calls.append((messages, schema))
            raise RuntimeFailure('context_overflow')
    model = InitialOverflow()
    assert run(model).status == 'temporarily_unavailable' and len(model.calls) == 1
