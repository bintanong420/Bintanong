"""Bind legacy prospectus evidence to a pending byte-derived register identity."""
from __future__ import annotations

import re
import json
import tempfile
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ...bintanong_contracts.chunk_adapter import ChunkMappingError, adapt_chunk
from ...bintanong_contracts.governance import SourceDocumentVersion
from ...bintanong_contracts.source import (bind_chunk, check_chunk_binding, check_span_binding,
                                         privileged_key_paths)
from ..prospectus_extractor.identity import InputSnapshot
from .register import load_pending_register


def bind_prospectus_chunks(payload: Mapping[str, Any], version: SourceDocumentVersion, *,
                           page_sizes: Mapping[tuple[str, int], tuple[float, float]]) -> dict[str, Any]:
    """Refuse global identity/shape violations; account for unsupported chunks individually.

    All identity claims are checked before binding, whose shared helper replaces span versions.
    Inputs remain untouched, including on refusal. Output is a candidate, never an approval.
    """
    version = load_pending_register([version])[0]
    if not isinstance(payload, Mapping) or not isinstance(page_sizes, Mapping):
        raise ValueError("payload and page_sizes must be mappings")
    identity = payload.get("run_identity")
    if not isinstance(identity, Mapping) or identity.get("pdf_sha256") != version.byte_sha256:
        raise ValueError("payload digest does not match the pending registered bytes")
    rag = payload.get("rag")
    if not isinstance(rag, Mapping):
        raise ValueError("rag must be a mapping")
    raw_chunks = []
    seen = set()
    for group in ("semantic_chunks", "hierarchical_chunks"):
        chunks = rag.get(group)
        if not isinstance(chunks, list):
            raise ValueError(f"rag.{group} must be a list")
        for raw in chunks:
            if not isinstance(raw, Mapping):
                raise ValueError("chunk must be a mapping")
            chunk_id = raw.get("chunk_id")
            if not isinstance(chunk_id, str) or re.fullmatch(r"[0-9a-f]{64}", chunk_id) is None:
                raise ValueError("chunk needs a SHA-256 identity")
            if chunk_id in seen:
                raise ValueError("duplicate chunk identity")
            seen.add(chunk_id)
            if privileged_key_paths(raw):
                raise ValueError("chunk carries privileged fields")
            if raw.get("pdf_sha256") != version.byte_sha256:
                raise ValueError("chunk digest differs from pending registered bytes")
            for name in ("version_id", "document_id", "edition_id"):
                if raw.get(name) is not None:
                    raise ValueError(f"preexisting chunk {name} is not allowed")
            spans = raw.get("source_spans")
            if not isinstance(spans, list) or any(not isinstance(s, Mapping) for s in spans):
                raise ValueError("source_spans must be a list of mappings")
            for span in spans:
                if span.get("version_id") is not None:
                    raise ValueError("preexisting span version_id is not allowed")
                if span.get("pdf_sha256") != version.byte_sha256:
                    raise ValueError("span digest differs from pending registered bytes")
            raw_chunks.append(raw)

    emitted, rejected = [], []
    for raw in raw_chunks:
        try:
            chunk = adapt_chunk(raw, page_sizes=page_sizes).chunk
        except ChunkMappingError as exc:
            rejected.append({"chunk_id": raw["chunk_id"], "reason": exc.reason})
            continue
        for span in chunk.spans:
            check_span_binding(span, version)
        if any(not s.is_complete or s.bbox is None or s.bbox_origin is None or s.page_size is None
               for s in chunk.spans):
            rejected.append({"chunk_id": raw["chunk_id"], "reason": "incomplete_source_span"})
            continue
        bound = bind_chunk(chunk, version)
        check_chunk_binding(bound, version)
        for span in bound.spans:
            check_span_binding(span, version)
        emitted.append(bound.model_dump(mode="json"))
    return {"version_id": version.version_id, "source_sha256": version.byte_sha256,
            "chunks": emitted, "rejections": rejected}


def _prospectus_report(payload, bound, version, metadata):
    """Account for all extractor candidates and all binding outcomes without implying review."""
    rag = payload["rag"]
    candidates = rag["semantic_chunks"] + rag["hierarchical_chunks"]
    emitted = {c["chunk_id"] for c in bound["chunks"]}
    rejected = {r["chunk_id"]: r["reason"] for r in bound["rejections"]}
    if (len(emitted) != len(bound["chunks"]) or len(rejected) != len(bound["rejections"])
            or emitted & rejected.keys() or emitted | rejected.keys() != {c["chunk_id"] for c in candidates}):
        raise ValueError("prospectus candidate accounting is incomplete")
    blocked = payload["audit"]["status"] == "error"
    if blocked and candidates:
        raise ValueError("failed curriculum audit cannot supply ready chunks")
    needs = ["source_verification_pending", "content_review_pending", "scope_issuer_effectivity_pending",
             "estimated_tokens_only", "conflicts_not_assessed"]
    if blocked:
        needs.append("curriculum_audit_failed")
    if bound["rejections"] or rag["rejected_chunks"]:
        needs.append("extraction_findings_require_review")
    return {"accounting_complete": True, "classification": "prospectus_candidate", "source_format": "pdf",
            "source_version": version.model_dump(mode="json"), "source_sha256": version.byte_sha256,
            "source_verification": "pending", "content_review": "pending", "approval_id": None,
            "review_eligible": False, "extraction_blocked": blocked, "audit_status": payload["audit"]["status"],
            "audit": payload["audit"], "conversion": metadata,
            "conversion_settings": metadata["conversion_settings"],
            "tool_versions": metadata["conversion_settings"]["versions"],
            "token_count_method": "estimate-v1", "counts": {
                "raw_items": payload["evidence"]["raw_item_count"],
                "raw_tables": payload["evidence"]["table_count"], "courses": len(payload["courses"]),
                "candidate_chunks": len(candidates), "chunks": len(bound["chunks"]),
                "binding_rejections": len(bound["rejections"]), "extractor_rejections": len(rag["rejected_chunks"])},
            "candidate_coverage": [{"chunk_id": c["chunk_id"], "outcome": "emitted" if c["chunk_id"] in emitted
                                    else "rejected", "reason": rejected.get(c["chunk_id"])} for c in candidates],
            "rejections": bound["rejections"], "extractor_rejections": rag["rejected_chunks"], "review_needs": needs}


class _StrictConverter:
    """Guard the loader seam before it can export raw data or trigger a backend retry."""

    def __init__(self, active, settings, snapshot, *, attested):
        self.active, self.settings, self.snapshot = active, settings, snapshot
        self.attested, self.status = attested, None

    def convert(self, stream):
        result = self.active.convert(stream)
        errors = getattr(result, "errors", None)
        status = getattr(result, "status", None)
        status = getattr(status, "value", status)
        if errors or (status is not None and status != "success"):
            raise RuntimeError("conversion errors or non-success status; partial prospectus refused")
        if _converter_settings(self.active, None if self.attested else self.settings) != self.settings:
            raise ValueError("conversion settings changed during conversion")
        self.snapshot.verify_unchanged()
        self.status = status
        return result


def _converter_settings(converter, settings=None):
    """Check factory settings against actual options, or an injected converter's attestation."""
    from_factory = settings is not None
    settings = settings if from_factory else getattr(converter, "conversion_settings", None)
    if not isinstance(settings, Mapping):
        raise ValueError("injected converter must attest its actual conversion_settings")
    settings = json.loads(json.dumps(dict(settings), allow_nan=False))
    if (not isinstance(settings.get("backend"), str) or not settings["backend"].strip()
            or not isinstance(settings.get("profile"), str) or not settings["profile"].strip()
            or not isinstance(settings.get("versions"), dict) or not settings["versions"]
            or any(not isinstance(v, str) or not v.strip() for v in settings["versions"].values())):
        raise ValueError("conversion settings need an actual backend, profile and versions")
    # A real Docling converter exposes the backend class and pipeline options we can verify.
    options = getattr(converter, "format_to_options", None)
    if from_factory and options is None:
        raise ValueError("default converter actual settings cannot be verified")
    if options is not None:
        from docling.datamodel.base_models import InputFormat
        option = options.get(InputFormat.PDF)
        backend = getattr(option, "backend", None)
        backend_name = getattr(backend, "__name__", "")
        expected = {"DoclingParseV4DocumentBackend": "docling_parse", "PyPdfiumDocumentBackend": "pypdfium2"}
        if expected.get(backend_name) != settings["backend"]:
            raise ValueError("conversion backend does not match declared settings")
        pipeline = getattr(option, "pipeline_options", None)
        table = getattr(pipeline, "table_structure_options", None)
        actual = {"do_ocr": getattr(pipeline, "do_ocr", None),
                  "force_backend_text": getattr(pipeline, "force_backend_text", None),
                  "do_table_structure": getattr(pipeline, "do_table_structure", None),
                  "cell_matching": getattr(table, "do_cell_matching", None),
                  "table_mode": getattr(getattr(table, "mode", None), "value", None)}
        if any(v is None or k not in settings or settings[k] != v for k, v in actual.items()):
            raise ValueError("conversion pipeline options do not match declared settings")
        if actual["do_ocr"]:
            languages = getattr(getattr(pipeline, "ocr_options", None), "lang", None)
            declared = settings.get("ocr_languages")
            if (not isinstance(languages, (list, tuple)) or not isinstance(declared, list)
                    or any(not isinstance(v, str) or not v.strip() for v in [*languages, *declared])
                    or sorted(languages) != sorted(declared)):
                raise ValueError("conversion OCR languages do not match declared settings")
        from ..prospectus_extractor.identity import installed_versions
        installed = installed_versions()
        if any(settings["versions"].get(name) != version for name, version in installed.items()):
            raise ValueError("conversion versions do not match installed Docling packages")
    return settings


def _captured_page_sizes(metadata, raw):
    """Captured PDF geometry is authoritative, including when an audit emitted no chunks."""
    sizes = metadata.get("pdf_page_sizes")
    if not isinstance(sizes, dict) or not sizes:
        raise ValueError("captured PDF page sizes are missing")
    result = {}
    for page, size in sizes.items():
        if (not isinstance(page, str) or not page.isdecimal() or str(int(page)) != page or int(page) < 1
                or not isinstance(size, list) or len(size) != 2
                or any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in size)):
            raise ValueError("invalid captured PDF page size")
        result[(metadata["pdf_sha256"], int(page))] = tuple(size)
    if sorted(p for _, p in result) != list(range(1, len(result) + 1)):
        raise ValueError("captured PDF page sizes are not contiguous")
    pages = raw.get("pages", {})
    if not isinstance(pages, dict):
        raise ValueError("invalid raw page geometry")
    for page, details in pages.items():
        key = (metadata["pdf_sha256"], int(page))
        if key not in result or not isinstance(details, dict):
            raise ValueError("raw page geometry is outside captured PDF")
        size = details.get("size")
        if size is None:
            continue
        values = [size.get("width"), size.get("height")] if isinstance(size, dict) else []
        if (len(values) != 2 or any(type(v) not in (int, float) or not math.isfinite(v) for v in values)
                or any(abs(a - b) > .01 for a, b in zip(values, result[key]))):
            raise ValueError("raw page geometry disagrees with captured PDF size")
    return result


def run_prospectus_ingestion(snapshot: InputSnapshot, register, *, input_root: Path, out: Path,
                             converter: Any = None) -> dict[str, Any]:
    """Publish a complete pending candidate; the root manifest is written last."""
    from ..prospectus import ProvisionalSource
    from ..prospectus_extractor import loader, pipeline
    from ..prospectus_extractor.identity import (bytes_sha256, conversion_identity,
                                                conversion_settings, run_identity)
    from .inspection import InspectionRefused, check_out
    from .procedure_text import _json
    from .register import version_for_snapshot

    root, out = Path(input_root).resolve(), Path(out).resolve()
    if not isinstance(snapshot, InputSnapshot) or root not in snapshot.path.parents or snapshot.path.suffix.lower() != ".pdf":
        raise ValueError("prospectus requires a captured PDF within the explicit input root")
    try:
        check_out(root, out)
    except InspectionRefused as exc:
        raise ValueError(str(exc)) from exc
    records = load_pending_register(register)
    version = version_for_snapshot(snapshot, records)
    if any(v.namespace != "institutional" for v in records):
        raise ValueError("private sources cannot enter institutional candidate bundles")
    settings = conversion_settings() if converter is None else _converter_settings(converter)
    # Import first so the protected loader cannot reach its legacy interpreter relaunch.
    loader.load_docling()
    active = converter if converter is not None else loader.get_shared_converter(
        device="auto", backend=settings["backend"], settings=settings)
    if converter is None:
        _converter_settings(active, settings)
    strict = _StrictConverter(active, settings, snapshot, attested=converter is not None)
    import pypdfium2 as pdfium
    page_sizes = {}
    with pdfium.PdfDocument(snapshot.data) as pdf:
        for index in range(len(pdf)):
            page = pdf[index]
            try:
                page_sizes[(snapshot.sha256, index + 1)] = tuple(page.get_size())
            finally:
                page.close()
    snapshot.verify_unchanged()
    out.mkdir(parents=True, exist_ok=True)
    converted = out / "conversion"
    with tempfile.TemporaryDirectory(prefix="prospectus-stage-") as staging:
        loaded = loader.load_document_result(snapshot.path, converter=strict, snapshot=snapshot,
            force_reconvert=True, raw_json_path=converted / "raw_docling.json", stage_dir=Path(staging))
        raw_bytes = loaded.raw_json_bytes
        if (loaded.cache_status != "converted" or not isinstance(raw_bytes, bytes)
                or bytes_sha256(raw_bytes) != loaded.raw_json_sha256 or not isinstance(loaded.meta_bytes, bytes)
                or bytes_sha256(loaded.meta_bytes) != loaded.meta_sha256):
            raise ValueError("conversion lacks captured raw bytes and identity metadata")
        metadata = json.loads(loaded.meta_bytes)
        if (metadata.get("pdf_sha256") != snapshot.sha256
                or metadata.get("raw_json_sha256") != bytes_sha256(raw_bytes)
                or metadata.get("conversion_identity") != conversion_identity(snapshot.sha256, metadata["conversion_settings"])):
            raise ValueError("conversion metadata does not match captured source/raw/settings")
        metadata.update(conversion_settings=settings, conversion_identity=conversion_identity(snapshot.sha256, settings),
                        conversion_status=strict.status, settings_basis="injected_converter_attestation" if converter is not None
                        else "existing_converter_factory", pdf_page_sizes={str(p): list(size) for (_, p), size in page_sizes.items()})
        _captured_page_sizes(metadata, json.loads(raw_bytes))
        payload = pipeline.build_payload(loaded.document, snapshot.path, semantic_doc_path=None, semantic_map={},
            raw_json_path=converted / "raw_docling.json", source=ProvisionalSource(snapshot.sha256, version.acquisition_locators[0]),
            pdf_sha256=snapshot.sha256, pdf_hash_check="matched")
        payload.pop("prolog")
        payload["quality_report"]["production_artifacts_emitted"] = False
        payload["evidence"]["raw_item_count"] = len(json.loads(raw_bytes).get("texts", []))
        payload["run_identity"] = run_identity(snapshot.path, None, snapshot=snapshot, settings=settings)
        bound = bind_prospectus_chunks(payload, version, page_sizes=page_sizes)
        report = _prospectus_report(payload, bound, version, metadata)
        outputs = {"conversion/raw_docling.json": raw_bytes,
                   "conversion/raw_docling.meta.json": (_json(metadata) + "\n").encode("utf-8"),
                   "conversion/prospectus_candidates.json": (_json(payload) + "\n").encode("utf-8")}
        nested = {"complete": True, "source_unchanged": True, "source_sha256": snapshot.sha256,
                  "version_id": version.version_id, "conversion_identity": metadata["conversion_identity"],
                  "files": {Path(n).name: bytes_sha256(b) for n, b in outputs.items()}}
        outputs["conversion/manifest.json"] = (_json(nested) + "\n").encode("utf-8")
        for name, value in {"source_register.json": [v.model_dump(mode="json") for v in records],
                            "chunks.json": bound, "ingestion_report.json": report}.items():
            outputs[name] = (_json(value) + "\n").encode("utf-8")
        for name, data in outputs.items():
            snapshot.verify_unchanged()
            loader._write_bytes_atomic(out / name, data)
        snapshot.verify_unchanged()
        completion = {"complete": True, "candidate_only": True, "document_kind": "prospectus_candidate",
                      "source_unchanged": True, "source_sha256": snapshot.sha256, "version_id": version.version_id,
                      "files": {n: bytes_sha256(b) for n, b in outputs.items()}}
        loader._write_bytes_atomic(out / "manifest.json", (_json(completion) + "\n").encode("utf-8"))
    return report
