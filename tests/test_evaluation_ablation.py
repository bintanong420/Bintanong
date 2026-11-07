"""Controlled evidence comparison; synthetic outputs only."""
import asyncio
import json
import pytest

from backend.bintanong_api.ablation import compare_evidence
from test_api_presentation import answer_for


class Model:
    def __init__(self):
        self.calls = []
        self.metadata = dict(model_file='synthetic.gguf', temperature=0, seed=0)

    async def infer(self, messages, schema):
        self.calls.append(messages)
        return json.dumps(dict(answer='Synthetic experimental output.'))


def test_conditions_share_prompt_and_sources_but_never_leak_the_symbolic_report_into_b():
    model = Model()
    answer = answer_for('Hybrid')
    result = asyncio.run(compare_evidence('A1 policy', answer, lambda: model))
    assert result['outcome'] == 'completed'
    assert [c['condition'] for c in result['conditions']] == ['A', 'B', 'C']
    inputs = [json.loads(call[1]['content']) for call in model.calls]
    assert inputs[0]['sources'] == [] and inputs[0]['symbolic'] is None
    assert inputs[1]['sources'] == inputs[2]['sources'] and inputs[1]['sources']
    assert inputs[1]['symbolic'] is None
    assert inputs[2]['symbolic']['decision'] == answer.decision.model_dump(mode='json')
    assert model.calls[0][0] == model.calls[1][0] == model.calls[2][0]
    assert 'gold' not in str(inputs).lower()
    assert all(c['student_answer_validated'] is False for c in result['conditions'])


def test_document_only_question_is_not_called_a_symbolic_ablation():
    model = Model()
    result = asyncio.run(compare_evidence('A1 policy', answer_for('RAG'), lambda: model))
    assert result['outcome'] == 'not_applicable'
    assert not model.calls


def test_failed_conditions_remain_in_the_comparison_and_other_conditions_run():
    from backend.bintanong_routing.transport import RuntimeFailure
    model = Model()
    original = model.infer
    async def infer(messages, schema):
        if len(model.calls) == 1:
            model.calls.append(messages)
            raise RuntimeFailure('context_overflow')
        return await original(messages, schema)
    model.infer = infer
    result = asyncio.run(compare_evidence('A1 policy', answer_for('Hybrid'), lambda: model))
    assert result['outcome'] == 'partial_failure'
    assert [c['outcome'] for c in result['conditions']] == ['completed', 'failed', 'completed']
    assert result['conditions'][1]['error'] == 'context_overflow'


@pytest.mark.parametrize('raw', ['[]', '{"answer":" "}', '{"answer":"ok","certified":true}'])
def test_malformed_outputs_are_retained_as_failures_without_certification(raw):
    model = Model()
    async def infer(messages, schema):
        return raw
    model.infer = infer
    result = asyncio.run(compare_evidence('A1 policy', answer_for('Hybrid'), lambda: model))
    assert all(c['error'] == 'invalid_output' and c['answer'] is None for c in result['conditions'])
