"""Synthetic builders shared by the runtime contract tests. Fictional digests, ids and text only."""

from __future__ import annotations

from backend.bintanong_contracts import source

SHA = {"1": "1" * 64, "2": "2" * 64}


def span(sha, page=1, cell="t0-c1", text="Fictional printed rule."):
    return {"schema_version": "bintanong-source-span-v1", "byte_sha256": sha, "version_id": None, "page": page,
            "printed_page_label": None,
            "locator": {"kind": "table_cells", "table_index": 0, "cell_ids": [cell], "item_ids": [], "ref": None},
            "text": text, "bbox": None, "bbox_origin": None, "page_size": None,
            "extraction": {"source_kind": "synthetic", "resolution_method": "deterministic",
                           "repair_id": None, "ocr_confidence": None}}


def chunk(n=1, edition="1", doc="doc-synth-handbook", chunker="palsu-chunker-v1", verification="observed"):
    sha = SHA[edition]
    source_text, text = f"Fictional printed rule {n}.", f"Explanation {n}."
    ver = f"ver-synth-handbook-{edition}"
    s = span(sha, cell=f"t0-c{n}", text=source_text)
    s["version_id"] = ver
    return source.Chunk.parse({
        "schema_version": "bintanong-chunk-v1", "chunk_id": f"{n:064x}", "chunk_type": "course",
        "chunker_version": chunker, "edition_id": f"edition-synth-handbook-{edition}", "document_id": doc,
        "version_id": ver, "byte_sha256": sha, "anchored": True, "source_verification": verification,
        "content_review": "pending", "text": text, "source_text": source_text, "spans": [s],
        "section_path": [], "scope": [], "content_hash": source.compute_content_hash(source_text, text),
        "token_count": {"count": 4, "method": "estimate-v1", "exact": False,
                        "includes_prefix_and_special_tokens": False},
        "source_label": "synthetic", "type_fields": {}})


def item(n=1, rank=1, score=0.9, release="release-synth-1", **chunk_kw):
    return {"rank": rank, "score": score, "knowledge_release_id": release,
            "chunk": chunk(n, **chunk_kw).model_dump(mode="json")}


def retrieval(items=None, release="release-synth-1", coverage="sufficient", **over):
    items = [item()] if items is None else items
    d = {"schema_version": "bintanong-retrieval-result-v1", "knowledge_release_id": release, "items": items,
         "coverage_status": coverage,
         "config": {"top_k": 5, "score_metric": "cosine", "min_score": None,
                    "embedding_model_id": "synthetic-model", "embedding_model_revision": "r1" + "0" * 38}}
    d.update(over)
    return d
