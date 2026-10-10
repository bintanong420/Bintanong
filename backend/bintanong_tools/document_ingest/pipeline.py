"""Registered snapshot -> installed conversion -> pending chunks -> external report."""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from ...bintanong_contracts.governance import SourceDocumentVersion
from ..prospectus_extractor import loader
from ..prospectus_extractor.identity import InputSnapshot, bytes_sha256, conversion_identity
from .inspection import InspectionRefused, check_out
from .policy_chunks import build_policy_chunks
from .procedure_text import CLASSIFICATIONS, _json, extract_procedure, read_procedure_items
from .register import load_pending_register, version_for_snapshot
from .report import build_ingestion_report


def run_ingestion(snapshot: InputSnapshot,
                  register: Sequence[SourceDocumentVersion | Mapping[str, Any]], *,
                  input_root: Path, out: Path, classification: str,
                  converter: Any = None, printed_page_labels: Mapping[int, str] | None = None) -> dict[str, Any]:
    """Write a candidate bundle. Only its root completion manifest authorizes consumption."""
    root, out = Path(input_root).resolve(), Path(out).resolve()
    if not isinstance(snapshot, InputSnapshot) or root not in snapshot.path.parents:
        raise ValueError("snapshot must belong to the explicit input root")
    if not isinstance(classification, str) or classification not in CLASSIFICATIONS:
        raise ValueError("unsupported candidate classification")
    if snapshot.path.suffix.lower() not in {".pdf", ".pptx"}:
        raise ValueError("document ingestion supports PDF or PPTX")
    if classification == "policy_candidate" and snapshot.path.suffix.lower() != ".pdf":
        raise ValueError("policy candidates require PDF")
    try:
        check_out(root, out)
    except InspectionRefused as exc:
        raise ValueError(str(exc)) from exc
    records = load_pending_register(register)
    version = version_for_snapshot(snapshot, records)
    candidates = extract_procedure(snapshot, records, input_root=root, out=out / "conversion",
        classification=classification, converter=converter, printed_page_labels=printed_page_labels)
    converted = out / "conversion"
    manifest = json.loads((converted / "manifest.json").read_bytes())
    if (manifest.get("complete") is not True or manifest.get("source_unchanged") is not True
            or manifest.get("source_sha256") != snapshot.sha256 or manifest.get("version_id") != version.version_id):
        raise ValueError("conversion completion identity mismatch")
    required = {"raw_docling.json", "raw_docling.meta.json", "procedure_candidates.json"}
    if set(manifest.get("files", {})) != required:
        raise ValueError("conversion manifest has incomplete files")
    artifacts = {name: (converted / name).read_bytes() for name in sorted(required)}
    if any(bytes_sha256(data) != manifest["files"][name] for name, data in artifacts.items()):
        raise ValueError("conversion artifact digest mismatch")
    metadata = json.loads(artifacts["raw_docling.meta.json"])
    settings = metadata.get("conversion_settings")
    source_key = "pdf_sha256" if snapshot.path.suffix.lower() == ".pdf" else "source_sha256"
    if (metadata.get(source_key) != snapshot.sha256 or not isinstance(settings, dict)
            or metadata.get("raw_json_sha256") != bytes_sha256(artifacts["raw_docling.json"])):
        raise ValueError("conversion metadata does not bind source and raw bytes")
    identity = (conversion_identity(snapshot.sha256, settings) if source_key == "pdf_sha256" else
                bytes_sha256(_json({"source_sha256": snapshot.sha256, "settings": settings}).encode("utf-8")))
    if metadata.get("conversion_identity") != identity:
        raise ValueError("conversion identity mismatches actual settings")
    raw_candidates = read_procedure_items(json.loads(artifacts["raw_docling.json"]), version,
        source_format=snapshot.path.suffix.lower().lstrip("."), classification=classification,
        printed_page_labels=printed_page_labels)
    if (raw_candidates.as_dict() != candidates.as_dict()
            or json.loads(artifacts["procedure_candidates.json"]) != candidates.as_dict()):
        raise ValueError("candidates do not match captured conversion bytes")
    chunks = build_policy_chunks(candidates)
    report = build_ingestion_report(candidates, chunks, conversion_metadata=metadata)
    snapshot.verify_unchanged()
    outputs = {"source_register.json": [v.model_dump(mode="json") for v in records],
               "chunks.json": chunks.as_dict(), "ingestion_report.json": report}
    hashes = {f"conversion/{name}": bytes_sha256(data) for name, data in artifacts.items()}
    hashes["conversion/manifest.json"] = bytes_sha256((converted / "manifest.json").read_bytes())
    for name, payload in outputs.items():
        data = (_json(payload) + "\n").encode("utf-8")
        loader._write_bytes_atomic(out / name, data)
        hashes[name] = bytes_sha256(data)
    snapshot.verify_unchanged()
    completion = {"complete": True, "candidate_only": True, "source_unchanged": True,
                  "source_sha256": snapshot.sha256, "version_id": version.version_id, "files": hashes}
    loader._write_bytes_atomic(out / "manifest.json", (_json(completion) + "\n").encode("utf-8"))
    return report
