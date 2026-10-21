"""Research-mode answers keep their research reference; fictional rules are not relabelled."""
import asyncio

from backend.bintanong_generation.generator import Generator
from test_orchestration_research_evidence import REF, research_integration


class NoModel:
    async def infer(self, messages, schema):
        raise AssertionError('Symbolic answers are host-rendered')


def test_symbolic_research_answer_carries_the_research_reference():
    integration = research_integration(facts=(('course-1', 'failed'),))
    assert integration.status == 'ready'
    answer = asyncio.run(Generator(NoModel()).generate('A1', integration))
    assert answer.status == 'answered' and answer.research_ref == REF
    assert answer.decision.outcome == 'ineligible' and answer.decision.synthetic is False


def test_synthetic_answers_have_no_research_reference():
    from test_request_understanding_pipeline import source
    answer = asyncio.run(Generator(NoModel()).generate('Where do I file Form Q and what is the fee?',
                                                        source(route='Symbolic')))
    assert answer.research_ref is None
