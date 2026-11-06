"""Evaluation-only record of what each search ranked in one turn; a no-op unless a caller opens an observation.

asyncio tasks and `to_thread` copy the context, so a list opened around a turn reaches the retrieval worker.
"""
from contextlib import contextmanager
from contextvars import ContextVar

_searches = ContextVar('bintanong_observed_searches', default=None)


@contextmanager
def observe_retrievals():
    seen = []
    token = _searches.set(seen)
    try:
        yield seen
    finally:
        _searches.reset(token)


def record_search(query, subject_id, requested_claims, candidates):
    seen = _searches.get()
    if seen is not None:
        seen.append(dict(query=query, subject_id=subject_id,
                         requested_claims=None if requested_claims is None else list(requested_claims),
                         candidates=list(candidates), emitted_chunk_ids=[]))


def record_emitted(evidence):
    """Marks the turn's latest search; a turn's searches run one after another."""
    seen = _searches.get()
    if seen:
        seen[-1]['emitted_chunk_ids'] = [item['chunk_id'] for item in evidence]
