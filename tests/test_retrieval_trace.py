"""Owner GUI 3 Nov 2026 ("trace between the RAG (KNN ranking) + LLM response"): an opt-in retrieval trace records, per
retrieval, the topic, requested claims, every candidate's rank and similarity, and which chunks reached the model.
It never records question or chunk text. Synthetic fixture."""
import json

from backend.bintanong_retrieval.types import RetrievalRequest
from tests.test_retrieval_claim_filter import fixture


def test_the_trace_records_ranking_and_emitted_chunks_without_text(tmp_path, monkeypatch):
    trace = tmp_path / 'retrieval-trace.jsonl'
    monkeypatch.setenv('BINTANONG_RETRIEVAL_TRACE', str(trace))
    engine, _ = fixture()
    engine.retrieve(RetrievalRequest('synthetic printed amount', 'release-test'),
                    subject_id='fees', requested_claims=('printed amount',))
    record, = [json.loads(line) for line in trace.read_text(encoding='utf-8').splitlines()]
    assert (record['subject_id'], record['requested_claims']) == ('fees', ['printed amount'])
    assert [c['rank'] for c in record['candidates']] == list(range(1, len(record['candidates']) + 1))
    assert all(isinstance(c['similarity'], float) for c in record['candidates'])
    assert [e['chunk_id'] for e in record['emitted']] == ['a', 'b']
    assert 'synthetic printed amount' not in trace.read_text(encoding='utf-8')
    assert 'Synthetic amount' not in trace.read_text(encoding='utf-8')


def test_no_trace_is_written_unless_asked(tmp_path, monkeypatch):
    monkeypatch.delenv('BINTANONG_RETRIEVAL_TRACE', raising=False)
    engine, _ = fixture()
    engine.retrieve(RetrievalRequest('synthetic printed amount', 'release-test'),
                    subject_id='fees', requested_claims=('printed amount',))
    assert not list(tmp_path.iterdir())
