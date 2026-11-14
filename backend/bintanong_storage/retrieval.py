"""Knowledge Retriever and Exact Cosine Vector Search.

Implements Master Plan Section 9.2:
- Exact cosine search via pgvector operator `<=>` (1 - distance = cosine similarity).
- Executes search via `match_chunks` RPC under runtime role (anon key).
- Verifies that RLS automatically excludes draft or superseded chunks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from .client import SupabaseStorageClient


@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    similarity: float
    text: str
    source_text: str
    section_path: List[str]
    scope: List[str]
    chunk_type: str


class KnowledgeRetriever:
    def __init__(self, client: Optional[SupabaseStorageClient] = None) -> None:
        self.client = client or SupabaseStorageClient()

    def search(
        self,
        query_vector: Sequence[float],
        match_threshold: float = 0.0,
        match_count: int = 10,
        role: str = "runtime",
    ) -> List[SearchResult]:
        """Perform exact cosine similarity search over active release chunks."""
        if len(query_vector) != 1024:
            raise ValueError(f"Query vector must have 1024 dimensions, got {len(query_vector)}")

        params = {
            "query_embedding": list(query_vector),
            "match_threshold": float(match_threshold),
            "match_count": int(match_count),
        }

        raw_results = self.client.rpc("match_chunks", params=params, role=role)
        results: List[SearchResult] = []
        for r in raw_results or []:
            results.append(
                SearchResult(
                    chunk_id=r["chunk_id"],
                    similarity=float(r["similarity"]),
                    text=r["text"],
                    source_text=r.get("source_text", r["text"]),
                    section_path=r.get("section_path") or [],
                    scope=r.get("scope") or [],
                    chunk_type=r["chunk_type"],
                )
            )
        return results
