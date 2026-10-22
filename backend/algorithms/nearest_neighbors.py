"""Synthetic exact cosine top-k reference; live retrieval uses pgvector SQL.

Run from the repository root: python -B -m backend.algorithms.nearest_neighbors
The hand-selected vectors demonstrate arithmetic,not semantic retrieval quality.
"""
import json

from .similarity import cosine_similarity


def demonstration():
    query = (1.0, 0.0)
    candidates = {
        'vector-a': (1.0, 0.0),
        'vector-b': (0.8, 0.6),
        'vector-c': (0.0, 1.0),
        'vector-d': (-1.0, 0.0),
    }
    scored = []
    for candidate_id, vector in candidates.items():
        similarity = cosine_similarity(query, vector)
        scored.append(dict(candidate_id=candidate_id, vector=vector,
                           similarity=similarity, distance=1.0 - similarity))
    ranked = sorted(scored, key=lambda row: (-row['similarity'], row['candidate_id']))
    k, min_similarity = 3, 0.5
    selected = [row for row in ranked if row['similarity'] >= min_similarity][:k]
    return dict(synthetic=True, implementation='educational Python exhaustive scan',
                runtime_implementation='pgvector retrieve_context RPC',
                query=query, k=k, min_similarity=min_similarity,
                ranked=ranked, selected=selected)


if __name__ == '__main__':
    print(json.dumps(demonstration(), indent=2))
