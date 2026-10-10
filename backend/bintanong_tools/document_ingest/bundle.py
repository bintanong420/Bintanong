"""Consume only complete, hash-checked pending institutional candidate bundles."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ...bintanong_contracts.source import Chunk, check_chunk_binding, check_span_binding
from ..prospectus_extractor.identity import bytes_sha256, conversion_identity
from .policy_chunks import build_policy_chunks
from .procedure_text import CLASSIFICATIONS, _json, read_procedure_items
from .prospectus import _captured_page_sizes, _prospectus_report, bind_prospectus_chunks
from .register import load_pending_register
from .report import build_ingestion_report


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse(data):
    try:
        return json.loads(data, object_pairs_hook=_object, parse_constant=_nonfinite)
    except (UnicodeError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid candidate JSON") from exc


def _nonfinite(value):
    raise ValueError("non-finite JSON number")


def _read(root, name):
    path = root / name
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file() or root not in path.resolve().parents:
        raise ValueError("artifact must be a contained regular file without symlinks")
    return path.read_bytes()


def load_candidate_bundle(path: Path) -> dict[str, Any]:
    """Integrity/completeness are checked here; candidate review eligibility remains false."""
    root = Path(path).absolute()
    try:
        return _load(root)
    except (OSError, KeyError, TypeError, AttributeError, IndexError) as exc:
        raise ValueError("incomplete or malformed candidate bundle") from exc


def _load(root):
    manifest = _parse(_read(root, "manifest.json"))
    if (not isinstance(manifest, dict) or manifest.get("complete") is not True
            or manifest.get("candidate_only") is not True or manifest.get("source_unchanged") is not True):
        raise ValueError("root candidate completion is absent or false")
    declared_kind = manifest.get("document_kind")
    if declared_kind is not None and declared_kind not in CLASSIFICATIONS | {"prospectus_candidate"}:
        raise ValueError("unknown candidate document kind")
    prospectus = declared_kind == "prospectus_candidate"
    candidate_name = "prospectus_candidates.json" if prospectus else "procedure_candidates.json"
    nested_names = {"raw_docling.json", "raw_docling.meta.json", candidate_name}
    names = {f"conversion/{n}" for n in nested_names | {"manifest.json"}} | {
        "source_register.json", "chunks.json", "ingestion_report.json"}
    if not isinstance(manifest.get("files"), dict) or set(manifest["files"]) != names:
        raise ValueError("candidate manifest has unknown, unsafe or missing artifacts")
    disk_names = set()
    for item in root.rglob("*"):
        if item.is_symlink():
            raise ValueError("symlink artifact refused")
        if item.is_dir():
            if item != root / "conversion":
                raise ValueError("unknown artifact directory")
        elif item.is_file():
            disk_names.add(item.relative_to(root).as_posix())
        else:
            raise ValueError("artifact is not a regular file")
    if disk_names != names | {"manifest.json"}:
        raise ValueError("unknown or missing files in candidate bundle")
    artifacts = {n: _read(root, n) for n in names}
    if any(bytes_sha256(data) != manifest["files"][name] for name, data in artifacts.items()):
        raise ValueError("candidate artifact digest mismatch")
    parsed = {n: _parse(data) for n, data in artifacts.items()}
    nested = parsed["conversion/manifest.json"]
    if (nested.get("complete") is not True or nested.get("source_unchanged") is not True
            or nested.get("source_sha256") != manifest["source_sha256"]
            or nested.get("version_id") != manifest["version_id"] or set(nested.get("files", {})) != nested_names):
        raise ValueError("nested conversion completion identity mismatch")
    if any(nested["files"][n] != bytes_sha256(artifacts[f"conversion/{n}"]) for n in nested_names):
        raise ValueError("nested artifact digest mismatch")
    records = list(load_pending_register(parsed["source_register.json"]))
    if not records or any(v.namespace != "institutional" for v in records):
        raise ValueError("institutional pending source register required")
    versions = {v.version_id: v for v in records}
    version = versions.get(manifest["version_id"])
    if version is None or version.byte_sha256 != manifest["source_sha256"]:
        raise ValueError("root source/version not in register")
    report, chunks_data = parsed["ingestion_report.json"], parsed["chunks.json"]
    kind = report.get("classification")
    if (kind not in CLASSIFICATIONS | {"prospectus_candidate"} or (declared_kind is not None and declared_kind != kind)
            or (kind == "prospectus_candidate") != prospectus):
        raise ValueError("document kind does not match report/artifact schema")
    metadata, raw = parsed["conversion/raw_docling.meta.json"], parsed["conversion/raw_docling.json"]
    settings = metadata.get("conversion_settings")
    source_format = report.get("source_format")
    source_key = "pdf_sha256" if source_format == "pdf" else "source_sha256"
    if (source_format not in {"pdf", "pptx"} or not isinstance(raw, dict) or not isinstance(settings, dict)
            or not settings or metadata.get(source_key) != version.byte_sha256
            or metadata.get("raw_json_sha256") != bytes_sha256(artifacts["conversion/raw_docling.json"])):
        raise ValueError("conversion metadata lacks captured raw/source/settings identity")
    identity = (conversion_identity(version.byte_sha256, settings) if source_format == "pdf" else
                bytes_sha256(_json({"source_sha256": version.byte_sha256, "settings": settings}).encode("utf-8")))
    if metadata.get("conversion_identity") != identity:
        raise ValueError("conversion settings identity mismatch")
    chunks = [Chunk.parse(c) for c in chunks_data["chunks"]]
    if len({c.chunk_id for c in chunks}) != len(chunks):
        raise ValueError("duplicate chunk identity")
    for chunk in chunks:
        check_chunk_binding(chunk, version)
        if chunk.scope:
            raise ValueError("pending candidate cannot assert scope")
        for span in chunk.spans:
            check_span_binding(span, version)
            if span.version_id != version.version_id or not span.is_complete:
                raise ValueError("candidate span lacks exact registered version/evidence")
    if prospectus:
        if (source_format != "pdf" or nested.get("conversion_identity") != identity
                or metadata.get("conversion_status") not in (None, "success")):
            raise ValueError("prospectus conversion incomplete")
        payload = parsed[f"conversion/{candidate_name}"]
        run = payload["run_identity"]
        if ("prolog" in payload or run.get("pdf_sha256") != version.byte_sha256
                or run.get("input_sha256") != version.byte_sha256 or run.get("conversion_identity") != identity
                or run.get("conversion_settings") != settings or run.get("review_input_only") is not False
                or payload["quality_report"].get("production_artifacts_emitted") is not False):
            raise ValueError("prospectus domain payload is not an inactive captured candidate")
        from ..prospectus import ProvisionalSource
        from ..prospectus_extractor.authority import build_authority
        authority = build_authority(audit_status=payload["audit"]["status"], metadata=payload["metadata"],
            courses=payload["courses"], source=ProvisionalSource(version.byte_sha256, version.acquisition_locators[0]),
            pdf_hash_check="matched")
        if any(payload.get(k) != v for k, v in authority.items()):
            raise ValueError("prospectus domain payload inflates authority")
        sizes = _captured_page_sizes(metadata, raw)
        expected = bind_prospectus_chunks(payload, version, page_sizes=sizes)
        if expected != chunks_data or _prospectus_report(payload, expected, version, metadata) != report:
            raise ValueError("prospectus chunks/report do not match domain candidates")
    else:
        labels = {p["physical_page"]: p["printed_page_label"] for p in report["page_map"]
                  if p["printed_page_label"] is not None}
        candidates = read_procedure_items(raw, version, source_format=source_format, classification=kind,
                                         printed_page_labels=labels)
        result = build_policy_chunks(candidates, token_cap=chunks_data["token_cap"])
        if (candidates.as_dict() != parsed[f"conversion/{candidate_name}"] or result.as_dict() != chunks_data
                or build_ingestion_report(candidates, result, conversion_metadata=metadata) != report):
            raise ValueError("policy/procedure candidates/chunks/report do not match captured conversion")
    checked = {"document_kind": kind, "candidate_only": True, "review_eligible": False,
               "source_register": records, "chunks": chunks, "report": report}
    if prospectus:
        checked.update(domain_payload=payload, conversion={"raw_docling": raw, "metadata": metadata})
    return checked
