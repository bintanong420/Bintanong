"""Owner 30 Oct 2026: a draft cut off at the output limit is retried once with a 1,536-token limit."""
import asyncio
import json

from backend.bintanong_generation.generator import Generator
from backend.bintanong_routing.transport import RuntimeFailure
from test_generation_part_slots import PartModel
from test_request_understanding_pipeline import TEXT, source


class TruncatingDraft(PartModel):
    """Draft requests are cut off unless they carry a larger output limit (or always, when stubborn)."""
    def __init__(self, *, stubborn=False):
        super().__init__()
        self.stubborn = stubborn
        self.limits = []

    async def infer(self, messages, schema, max_output_tokens=None):
        payload = json.loads(messages[1]['content'])
        if 'untrusted_previous_draft' in payload:
            self.limits.append(max_output_tokens)
            if self.stubborn or max_output_tokens is None:
                raise RuntimeFailure('truncated_output')
        return await super().infer(messages, schema)


def run(model):
    return asyncio.run(Generator(model).generate(TEXT, source()))


def test_a_truncated_draft_is_retried_once_with_a_larger_output_limit():
    model = TruncatingDraft()
    answer = run(model)
    assert answer.status == 'answered'
    assert model.limits == [None, 1536]


def test_a_draft_truncated_again_still_refuses():
    model = TruncatingDraft(stubborn=True)
    answer = run(model)
    assert answer.status == 'temporarily_unavailable' and answer.validation == 'tool_error'
    assert model.limits == [None, 1536]
