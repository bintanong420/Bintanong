"""Synthetic builders shared by the runtime contract tests. Fictional digests, ids and text only."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from backend.bintanong_contracts import source

SHA = {"1": "1" * 64, "2": "2" * 64}
REVISION = "0123456789abcdef" * 2 + "01234567"      # a fictional 40-hex pinned revision
EXAMPLES = Path(__file__).resolve().parents[1] / "knowledge" / "manifests" / "examples"
BINDING = {"verification_evidence_ref": "ev-b3", "content_review_evidence_ref": None}


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
        "source_label": "synthetic.pdf", "type_fields": {},
        "register_binding": dict(BINDING) if verification != "pending" else None})


def item(n=1, rank=1, score=0.9, release="release-synth-1", **chunk_kw):
    return {"rank": rank, "score": score, "knowledge_release_id": release,
            "chunk": chunk(n, **chunk_kw).model_dump(mode="json")}


def scope(release="release-synth-1", editions=("edition-synth-handbook-1",)):
    return {"knowledge_release_id": release, "edition_ids": list(editions), "scope_ids": []}


def rule_span(sha=None, version="ver-synth-handbook-1", text="Fictional rule text."):
    s = span(sha or SHA["1"], text=text)
    s["version_id"] = version
    return s


def decided_extras(outcome):
    """The scope and rule spans a decided result carries; an unsupported or error result has neither."""
    if outcome in ("eligible", "ineligible"):
        return {"scope": scope(), "rule_spans": [rule_span()]}
    return {"scope": None, "rule_spans": []}


def version_for(chunk_dict: dict) -> dict:
    """A synthetic register version that a chunk dict cites, with the register's own evidence references."""
    rec = copy.deepcopy(json.loads((EXAMPLES / "synthetic-register.json").read_text(encoding="utf-8"))[1])
    rec.update(document_id=chunk_dict["document_id"], version_id=chunk_dict["version_id"],
               edition_id=chunk_dict["edition_id"], byte_sha256=chunk_dict["byte_sha256"])
    return rec


def versions_for(items) -> list[dict]:
    out: dict[str, dict] = {}
    for it in items:
        c = it["chunk"]
        if c.get("version_id") is not None and c["version_id"] not in out:
            out[c["version_id"]] = version_for(c)
    return list(out.values())


def retrieval(items=None, release="release-synth-1", coverage="sufficient", **over):
    items = [item()] if items is None else items
    d = {"schema_version": "bintanong-retrieval-result-v1", "knowledge_release_id": release, "items": items,
         "versions": versions_for(items), "coverage_status": coverage,
         "config": {"top_k": 5, "score_metric": "cosine", "min_score": None,
                    "embedding_model_id": "synthetic-model", "embedding_model_revision": REVISION}}
    d.update(over)
    return d


# Exact input matrices shared by package, schema and parity checks.
# Model/schema ID matrices retain their original distinct cases and order.

INVALID_SOURCE_FILENAMES = (
    'C:\\Users\\x\\a.pdf',
    'C:/Users/x/a.pdf',
    'dir\\a.pdf',
    '/abs/a.pdf',
    'file:///a.pdf',
    '\\\\host\\share\\a.pdf',
    'a/b.pdf',
    'x:y.pdf',
    '..',
    '.',
    'a\tb.pdf',
    'a\nb.pdf',
    '',
)

PLAIN_SOURCE_FILENAMES = (
    'synthetic-handbook.pdf',
    'Student Handbook (2023) v2.pdf',
    'a.b.c.pptx',
)

PRIVATE_SOURCE_LOCATORS = (
    'C:\\Users\\x\\a.pdf',
    'C:/Users/x/a.pdf',
    'd:\\a',
    '\\\\host\\share',
    '/home/x/a.pdf',
    '/Users/x/a.pdf',
    'file:///a.pdf',
    '../a.pdf',
    'synthetic-locator-x/../y',
    '~/a.pdf',
    'a\\b',
    ' leading',
    '',
    'x\ny',
)

PUBLIC_SOURCE_LOCATORS = (
    'https://example.invalid/handbook.pdf',
    'synthetic-locator-alpha/2',
    'registrar-shelf-3/box-2',
)

MODEL_INVALID_SOURCE_FILENAMES = (
    'file:///a.pdf',
    '~/a.pdf',
    '../a.pdf',
    'D:rel.pdf',
    'dir\\a.pdf',
    'C:\\x\\a.pdf',
    '/abs/a.pdf',
    'https://example.invalid/a.pdf',
    'a/b.pdf',
    '..',
    '.',
    'a\tb.pdf',
    'a\nb.pdf',
    'x:y.pdf',
)

MODEL_PRIVATE_SOURCE_LOCATORS = (
    'file:///a.pdf',
    'file://host/a.pdf',
    'C:\\Users\\x\\a.pdf',
    'C:/Users/x/a.pdf',
    'd:\\a',
    '\\\\host\\share',
    '/home/x/a.pdf',
    '/Users/x/a.pdf',
    '../a.pdf',
    'synthetic-locator-x/../y',
    '~/a.pdf',
    'a\\b',
    ' leading',
    'x\ny',
    '/abs',
)

MODEL_PRIVATE_ID_VARIANTS = (
    'fact-synth-0001 ',
    'FACT-synth-0001',
    'fact-synth-0001\n',
    'ｆact-synth-0001',
    'fact‑synth-0001',
    'fact-synth-0001/x',
    'sess-synth-0001\t',
    ' fact-synth-0001',
    'see fact-synth-0001.',
    '(sess-synth-0001)',
    'x/FACT‐SYNTH-1',
    'fact-0001',
    'sess-7',
)

MODEL_INSTITUTIONAL_ID_VARIANTS = (
    'doc-synth-handbook\n',
    'ver-synth-0001 ',
    'DOC-synth-x',
    ' edition-synth-1',
    'edition-synth-1/x',
    'conflict-synth-0001\t',
    'ｖer-synth-0001',
    'ver‑synth-0001',
    'doc-synth-handbook/x',
    'ver-synth-0001#a',
    'ver-1',
)

SCHEMA_PRIVATE_ID_VARIANTS = (
    'fact-0001',
    'sess-7',
    'fact-synth-0001 ',
    ' fact-synth-0001',
    'FACT-synth-0001',
    'fact-synth-0001\n',
    'ｆact-synth-0001',
    'fact‑synth-0001',
    'fact-synth-0001/x',
    'sess-synth-0001#a',
    'see fact-synth-0001.',
    '(sess-synth-0001)',
    'x/FACT‐SYNTH-1',
)

SCHEMA_INSTITUTIONAL_ID_VARIANTS = (
    'ver-1',
    'doc-synth-handbook\n',
    'ver-synth-0001 ',
    'DOC-synth-x',
    ' edition-synth-1',
    'conflict-synth-0001\t',
    'ｖer-synth-0001',
    'ver‑synth-0001',
    'doc-synth-handbook/x',
    'ver-synth-0001#a',
)

LEGITIMATE_ID_PROSE = (
    'Fact-checking Office of Records',
    'over-the-counter version-controlled copies',
    'edition-specific wording',
    'conflict-resolution procedure',
    'Doc-ument handling',
    'a fact',
    'xfact-synth-0001',
    'verification',
    'sess',
)

FILENAME_PARITY_CASES = INVALID_SOURCE_FILENAMES + ("D:rel.pdf", "https://x.invalid/a.pdf") + PLAIN_SOURCE_FILENAMES
LOCATOR_PARITY_CASES = PRIVATE_SOURCE_LOCATORS + PUBLIC_SOURCE_LOCATORS
