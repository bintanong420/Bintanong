"""Release Management and Atomic Publication / Rollback.

Implements Master Plan Section 9.2:
- Atomic release publication and activation: incomplete imports remain invisible.
- Strict rollback mechanism to prior validated releases without data destruction.
- Singleton active_release management via PostgreSQL stored procedures.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from .client import SupabaseStorageClient


@dataclass(frozen=True)
class KnowledgeRelease:
    release_id: str
    release_version: str
    description: str
    embedding_set_id: str
    status: str
    published_at: Optional[str] = None
    published_by: Optional[str] = None


class ReleaseManager:
    def __init__(self, client: Optional[SupabaseStorageClient] = None) -> None:
        self.client = client or SupabaseStorageClient()

    def create_release(
        self,
        release_id: str,
        release_version: str,
        description: str,
        embedding_set_id: str,
        chunk_ids: Sequence[str] = (),
        document_version_ids: Sequence[str] = (),
        rule_ids: Sequence[str] = (),
    ) -> KnowledgeRelease:
        """Create a draft knowledge release binding versions, chunks, and embeddings."""
        self.client.rpc(
            "create_knowledge_release",
            params={
                "p_release_id": release_id,
                "p_release_version": release_version,
                "p_description": description,
                "p_embedding_set_id": embedding_set_id,
                "p_chunk_ids": list(chunk_ids),
                "p_document_version_ids": list(document_version_ids),
                "p_rule_ids": list(rule_ids),
            },
            role="admin",
        )

        return KnowledgeRelease(
            release_id=release_id,
            release_version=release_version,
            description=description,
            embedding_set_id=embedding_set_id,
            status="draft",
        )

    def activate_release(self, release_id: str, actor: str = "system") -> None:
        """Atomically promote a release to active and update active_release pointer."""
        self.client.rpc(
            "activate_knowledge_release",
            params={"p_release_id": release_id, "p_actor": actor},
            role="admin",
        )

    def rollback_release(self, target_release_id: str, actor: str = "system") -> None:
        """Atomically point active_release back to a prior validated release."""
        self.client.rpc(
            "rollback_knowledge_release",
            params={"p_target_release_id": target_release_id, "p_actor": actor},
            role="admin",
        )

    def get_active_release(self) -> Optional[Dict[str, Any]]:
        """Retrieve the currently active knowledge release singleton."""
        rows = self.client.select("active_release", columns="*", role="runtime")
        if not rows:
            return None
        active_id = rows[0]["release_id"]
        rel_rows = self.client.select(
            "knowledge_releases",
            columns="*",
            filters={"release_id": f"eq.{active_id}"},
            role="runtime",
        )
        return rel_rows[0] if rel_rows else None

    def list_releases(self, role: str = "admin") -> List[Dict[str, Any]]:
        """List releases (admin sees all; runtime sees only the active release)."""
        return self.client.select("knowledge_releases", columns="*", role=role)
