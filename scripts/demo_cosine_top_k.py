"""Compatibility command for the canonical backend.algorithms demonstration.

Run from the repository root: python -B -m scripts.demo_cosine_top_k
The implementation is in backend/algorithms/nearest_neighbors.py.
"""
import json

from backend.algorithms.nearest_neighbors import demonstration


if __name__ == '__main__':
    print(json.dumps(demonstration(), indent=2))
