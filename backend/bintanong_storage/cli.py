"""Command Line Interface for Bintanong Storage Management.

Allows administrative inspection, artifact loading, and release activation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .client import SupabaseStorageClient
from .loader import BatchKnowledgeLoader
from .release import ReleaseManager
from .retrieval import KnowledgeRetriever


def cmd_status(client: SupabaseStorageClient) -> int:
    release_mgr = ReleaseManager(client)
    active = release_mgr.get_active_release()
    releases = release_mgr.list_releases(role="admin")
    tables_summary = {}
    for tbl in ("documents", "chunks", "chunk_embeddings", "knowledge_releases"):
        rows = client.select(tbl, columns="count", role="admin")
        tables_summary[tbl] = len(rows)

    print(json.dumps({
        "status": "healthy",
        "active_release": active,
        "total_releases": len(releases),
        "table_sample_counts": tables_summary,
    }, indent=2))
    return 0


def cmd_load(
    client: SupabaseStorageClient,
    manifest: Path,
    embeddings: Path,
    chunks_path: Optional[Path] = None,
) -> int:
    loader = BatchKnowledgeLoader(client)
    chunks_data = None
    if chunks_path and chunks_path.is_file():
        with chunks_path.open("r", encoding="utf-8") as f:
            chunks_data = json.load(f)

    summary = loader.load_artifacts(
        manifest_path=manifest,
        embeddings_path=embeddings,
        chunks=chunks_data,
    )
    print(json.dumps({
        "embedding_set_id": summary.embedding_set_id,
        "total_chunks_loaded": summary.total_chunks_loaded,
        "total_embeddings_loaded": summary.total_embeddings_loaded,
    }, indent=2))
    return 0


def cmd_activate(client: SupabaseStorageClient, release_id: str, actor: str) -> int:
    release_mgr = ReleaseManager(client)
    release_mgr.activate_release(release_id, actor=actor)
    print(f"Successfully activated knowledge release: {release_id}")
    return 0


def cmd_rollback(client: SupabaseStorageClient, release_id: str, actor: str) -> int:
    release_mgr = ReleaseManager(client)
    release_mgr.rollback_release(release_id, actor=actor)
    print(f"Successfully rolled back to knowledge release: {release_id}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status")

    load_p = sub.add_parser("load")
    load_p.add_argument("--manifest", type=Path, required=True)
    load_p.add_argument("--embeddings", type=Path, required=True)
    load_p.add_argument("--chunks", type=Path, default=None)

    act_p = sub.add_parser("activate")
    act_p.add_argument("--release-id", type=str, required=True)
    act_p.add_argument("--actor", type=str, default="cli-operator")

    rb_p = sub.add_parser("rollback")
    rb_p.add_argument("--release-id", type=str, required=True)
    rb_p.add_argument("--actor", type=str, default="cli-operator")

    args = parser.parse_args(argv)
    client = SupabaseStorageClient()

    try:
        if args.command == "status":
            return cmd_status(client)
        if args.command == "load":
            return cmd_load(client, args.manifest, args.embeddings, args.chunks)
        if args.command == "activate":
            return cmd_activate(client, args.release_id, args.actor)
        if args.command == "rollback":
            return cmd_rollback(client, args.release_id, args.actor)
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
