"""Canonical vector mathematics shared by existing adapters and paper demos."""
import math
from typing import Sequence


def normalize_l2(vector: Sequence[float]) -> tuple[float, ...]:
    """Normalize vector to unit Euclidean norm."""
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0.0:
        raise ValueError("Cannot L2-normalize zero vector")
    return tuple(v / norm for v in vector)


def cosine_similarity(v1: Sequence[float], v2: Sequence[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)
