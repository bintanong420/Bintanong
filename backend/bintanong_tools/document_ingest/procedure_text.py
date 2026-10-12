"""Procedure/form candidates; PPTX and unresolved tables remain review-only."""
from __future__ import annotations

import importlib
import json
import re
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

from ...bintanong_contracts.base import reject_foreign_ids
from ...bintanong_contracts.governance import SourceDocumentVersion
from ..prospectus_extractor import loader
from ..prospectus_extractor.identity import InputSnapshot, bytes_sha256, installed_versions
from .inspection import InspectionRefused, check_out
from .policy_text import PolicyCandidates, read_policy_items
from .register import load_pending_register, version_for_snapshot

CLASSIFICATIONS = {"policy_candidate", "procedure_candidate", "charter_candidate", "form", "curriculum_proposal_candidate"}


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


@dataclass(frozen=True)
class ProcedureField:
    item_id: str
    kind: str
    raw_text: str
    printed_marker: str | None = None


@dataclass(frozen=True)
class SlideUnit:
    item_id: str
    label: str
    source_text: str
    slide_index: int | None
    slide_indices: tuple[int, ...]
    shape_id: int | str | None
    raw_provenance_json: str
    provenance_gaps: tuple[str, ...]
    rejection_reason: str = "pending_locator_contract"

    @property
    def anchored(self) -> bool:
        return False

    @property
    def spans(self) -> tuple:
        return ()


@dataclass(frozen=True)
class TableCandidate:
    table_id: str
    raw_table_json: str
    raw_geometry_json: str
    rejection_reason: str

    @property
    def anchored(self) -> bool:
        return False

    @property
    def spans(self) -> tuple:
        return ()


@dataclass(frozen=True)
class ProcedureCandidates:
    version: SourceDocumentVersion
    classification: str
    source_format: str
    raw_item_count: int
    raw_table_count: int
    pdf: PolicyCandidates | None
    fields: tuple[ProcedureField, ...]
    pptx_units: tuple[SlideUnit, ...]
    tables: tuple[TableCandidate, ...]
    reading_order: tuple[str, ...]
    reading_order_basis: str
    slide_geometry_json: str | None
    raw_reading_order_json: str

    def check_invariants(self) -> None:
        if self.classification not in CLASSIFICATIONS:
            raise ValueError("unsupported candidate classification")
        if self.source_format == "pdf" and self.pdf is not None and not self.pptx_units:
            self.pdf.check_invariants()
            if self.pdf.version != self.version or self.raw_item_count != self.pdf.raw_item_count:
                raise ValueError("PDF item accounting or source version mismatch")
        elif self.source_format == "pptx" and self.pdf is None:
            ids = [u.item_id for u in self.pptx_units]
            if (len(ids) != self.raw_item_count or set(ids) != {f"text-{i}" for i in range(self.raw_item_count)}
                    or any(u.rejection_reason != "pending_locator_contract" for u in self.pptx_units)):
                raise ValueError("PPTX item accounting or locator rejection is invalid")
        else:
            raise ValueError("candidate format and PDF/slide representations disagree")
        ids = [t.table_id for t in self.tables]
        if len(ids) != self.raw_table_count or set(ids) != {f"table-{i}" for i in range(self.raw_table_count)}:
            raise ValueError("raw table accounting is incomplete")
        expected = {f"#/texts/{i}" for i in range(self.raw_item_count)} | {
            f"#/tables/{i}" for i in range(self.raw_table_count)}
        if len(self.reading_order) != len(expected) or set(self.reading_order) != expected:
            raise ValueError("raw reading order does not account for every text and table")

    def as_dict(self) -> dict[str, Any]:
        return {"source_version": self.version.model_dump(mode="json"),
            "classification": self.classification, "source_format": self.source_format,
            "raw_item_count": self.raw_item_count, "raw_table_count": self.raw_table_count,
            "pdf": self.pdf.as_dict() if self.pdf is not None else None,
            "fields": [{"item_id": f.item_id, "kind": f.kind, "raw_text": f.raw_text,
                        "printed_marker": f.printed_marker} for f in self.fields],
            "pptx_units": [{"item_id": u.item_id, "label": u.label, "source_text": u.source_text,
                "slide_index": u.slide_index, "slide_indices": list(u.slide_indices), "shape_id": u.shape_id,
                "raw_provenance_json": u.raw_provenance_json, "provenance_gaps": list(u.provenance_gaps),
                "anchored": False, "spans": [], "rejection_reason": u.rejection_reason} for u in self.pptx_units],
            "tables": [{"table_id": t.table_id, "raw_table_json": t.raw_table_json,
                "raw_geometry_json": t.raw_geometry_json, "anchored": False, "spans": [],
                "rejection_reason": t.rejection_reason} for t in self.tables],
            "reading_order": list(self.reading_order), "reading_order_basis": self.reading_order_basis,
            "slide_geometry_json": self.slide_geometry_json,
            "raw_reading_order_json": self.raw_reading_order_json}


def _reading_refs(raw: Mapping[str, Any], text_count: int, table_count: int) -> tuple[str, ...]:
    expected = [f"#/texts/{i}" for i in range(text_count)] + [f"#/tables/{i}" for i in range(table_count)]
    if "body" not in raw:
        return tuple(expected)
    refs: list[str] = []
    active: set[str] = set()

    def walk(node: Mapping[str, Any]) -> None:
        if not isinstance(node, Mapping) or not isinstance(node.get("children", []), list):
            raise ValueError("invalid raw reading-order node")
        for child in node.get("children", []):
            ref = child.get("cref", child.get("$ref")) if isinstance(child, Mapping) else None
            if isinstance(child, Mapping) and "cref" in child and "$ref" in child and child["cref"] != child["$ref"]:
                raise ValueError("conflicting raw reading-order reference")
            if not isinstance(ref, str):
                raise ValueError("invalid raw reading-order reference")
            if ref.startswith(("#/texts/", "#/tables/")):
                if ref not in expected or ref in refs:
                    raise ValueError("duplicate or invalid raw reading-order reference")
                refs.append(ref)
                collection, index = ref.removeprefix("#/").split("/")
                walk(raw[collection][int(index)])
            elif ref.startswith("#/groups/"):
                if not re.fullmatch(r"#/groups/(0|[1-9]\d*)", ref):
                    raise ValueError("invalid raw reading-order group")
                if ref in active:
                    raise ValueError("cyclic raw reading-order group")
                active.add(ref)
                try:
                    walk(raw["groups"][int(ref.rsplit("/", 1)[1])])
                except (KeyError, IndexError, TypeError) as exc:
                    raise ValueError("unresolved raw reading-order group") from exc
                active.remove(ref)
    walk(raw["body"])
    if "furniture" in raw:
        walk(raw["furniture"])
    if set(refs) != set(expected):
        raise ValueError("raw reading order omits text or tables")
    return tuple(refs)


def _fields(items: Sequence[Any], texts: list[Mapping[str, Any]]) -> tuple[ProcedureField, ...]:
    fields = []
    printed = r"\s*(office|requirements?|fees?|processing\s+time)\s*:\s*\S"
    for item in items:
        raw = texts[int(item.item_id.removeprefix("text-"))]
        marker = raw.get("marker")
        if raw.get("enumerated") is True and isinstance(marker, str) and marker.strip():
            fields.append(ProcedureField(item.item_id, "step", item.source_text, marker))
            continue
        for line in item.source_text.splitlines(keepends=True):
            match = re.match(printed, line, re.I)
            if re.match(r"\s*\d+[.)]\s+\S", line):
                kind = "step"
            elif match:
                kind = {"office": "office", "requirement": "requirements", "requirements": "requirements",
                        "fee": "fees", "fees": "fees", "processing time": "processing_time"}[
                            " ".join(match[1].lower().split())]
            else:
                continue
            fields.append(ProcedureField(item.item_id, kind, line))
    return tuple(fields)


def read_procedure_items(raw: Mapping[str, Any], version: SourceDocumentVersion, *,
                         source_format: str = "pdf", classification: str = "procedure_candidate",
                         printed_page_labels: Mapping[int, str] | None = None) -> ProcedureCandidates:
    """Classifications and labelled fields are caller/printed candidates, never authority."""
    version = load_pending_register([version])[0]
    if (not isinstance(classification, str) or classification not in CLASSIFICATIONS
            or not isinstance(source_format, str) or source_format not in {"pdf", "pptx"}):
        raise ValueError("unsupported source format or candidate classification")
    if not isinstance(raw, Mapping):
        raise ValueError("raw Docling document must be an object")
    reject_foreign_ids(raw, "institutional")
    texts, tables, geometry = raw.get("texts"), raw.get("tables", []), raw.get("pages", {})
    if not isinstance(texts, list) or not isinstance(tables, list) or not isinstance(geometry, dict):
        raise ValueError("raw document needs text/table arrays and geometry object")
    if any(not isinstance(t, Mapping) for t in tables):
        raise ValueError("invalid raw table")
    order = _reading_refs(raw, len(texts), len(tables))
    pdf, slides = None, []
    if source_format == "pdf":
        pdf = read_policy_items(raw, version, printed_page_labels=printed_page_labels)
    else:
        if printed_page_labels:
            raise ValueError("PPTX cannot carry printed PDF page labels")
        if geometry and set(geometry) != {str(i) for i in range(1, len(geometry) + 1)}:
            raise ValueError("raw slide geometry must be contiguous and one-based")
        for ref in order:
            if not ref.startswith("#/texts/"):
                continue
            index = int(ref.rsplit("/", 1)[1])
            item = texts[index]
            if (not isinstance(item, Mapping) or not isinstance(item.get("text"), str)
                    or not isinstance(item.get("label"), str) or not isinstance(item.get("prov", []), list)):
                raise ValueError("invalid raw slide text item")
            provs, indices, shapes = item.get("prov", []), [], []
            for prov in provs:
                if not isinstance(prov, Mapping):
                    raise ValueError("invalid raw slide provenance")
                slide, shape = prov.get("page_no"), prov.get("shape_id")
                if slide is not None:
                    if type(slide) is not int or slide < 1 or (geometry and str(slide) not in geometry):
                        raise ValueError("invalid raw slide index")
                    indices.append(slide)
                if shape is not None:
                    if not ((type(shape) is int and shape > 0) or (isinstance(shape, str) and shape.strip())):
                        raise ValueError("invalid raw shape id")
                    shapes.append(shape)
            indices = list(dict.fromkeys(indices))
            gaps = []
            slide = indices[0] if len(indices) == 1 and all(p.get("page_no") is not None for p in provs) else None
            shape = shapes[0] if shapes and len(shapes) == len(provs) and len(set(shapes)) == 1 else None
            if slide is None:
                gaps.append("slide_index_not_exported" if not indices else "ambiguous_slide_index")
            if shape is None:
                gaps.append("shape_id_not_exported" if not shapes else "ambiguous_shape_id")
            slides.append(SlideUnit(f"text-{index}", item["label"], item["text"], slide, tuple(indices),
                                    shape, _json(provs), tuple(gaps)))
    table_candidates = tuple(TableCandidate(f"table-{i}", _json(table), _json(geometry),
                             "unresolved_table_span_coverage" if source_format == "pdf" else "pending_locator_contract")
                             for i, table in enumerate(tables))
    result = ProcedureCandidates(version, classification, source_format, len(texts), len(tables), pdf,
             () if classification == "policy_candidate" else _fields(pdf.units if pdf is not None else slides, texts),
             tuple(slides), table_candidates, order,
             "raw_body" if "body" in raw else "raw_arrays_no_interleaving_evidence",
             _json(geometry) if source_format == "pptx" else None,
             _json({k: raw[k] for k in ("body", "groups", "furniture") if k in raw}))
    result.check_invariants()
    return result


def extract_procedure(snapshot: InputSnapshot,
                      register: Sequence[SourceDocumentVersion | Mapping[str, Any]], *,
                      input_root: Path, out: Path, converter: Any = None,
                      classification: str = "procedure_candidate",
                      printed_page_labels: Mapping[int, str] | None = None) -> ProcedureCandidates:
    """Byte-bound installed conversion, explicit external output, completion manifest last."""
    root, out = Path(input_root).resolve(), Path(out).resolve()
    if not isinstance(snapshot, InputSnapshot) or root not in snapshot.path.parents:
        raise ValueError("snapshot must belong to the explicit input root")
    source_format = snapshot.path.suffix.lower().lstrip(".")
    if source_format not in {"pdf", "pptx"} or not snapshot.path.is_file():
        raise ValueError("procedure candidates require a PDF or PPTX file")
    if not isinstance(classification, str) or classification not in CLASSIFICATIONS:
        raise ValueError("unsupported candidate classification")
    if source_format == "pptx" and printed_page_labels:
        raise ValueError("PPTX cannot carry printed PDF page labels")
    try:
        check_out(root, out)
    except InspectionRefused as exc:
        raise ValueError(str(exc)) from exc
    version = version_for_snapshot(snapshot, register)
    # Import before the PDF loader can reach its legacy interpreter-relaunch helper.
    api = loader.load_docling()
    importlib.import_module("docling")
    importlib.import_module("docling_core")
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="stage-", dir=out) as stage:
        if source_format == "pdf":
            converted = loader.load_document_result(snapshot.path, converter=converter,
                raw_json_path=out / "raw_docling.json", stage_dir=Path(stage), snapshot=snapshot)
            raw_bytes, meta_bytes = converted.raw_json_bytes, converted.meta_bytes
            if not isinstance(raw_bytes, bytes) or bytes_sha256(raw_bytes) != converted.raw_json_sha256:
                raise ValueError("conversion raw bytes do not match their digest")
        else:
            from docling.datamodel.base_models import DocumentStream
            active = converter if converter is not None else api["DocumentConverter"](
                allowed_formats=[api["InputFormat"].PPTX])
            converted = active.convert(DocumentStream(name=snapshot.path.name, stream=BytesIO(snapshot.data)))
            if loader._conversion_errors(converted):
                raise RuntimeError("Docling returned conversion errors; partial PPTX candidates refused")
            raw_bytes = _json(converted.document.export_to_dict()).encode("utf-8")
            settings = {"input_format": "pptx", "backend": "docling_native_pptx", "versions": installed_versions()}
            identity = bytes_sha256(_json({"source_sha256": snapshot.sha256, "settings": settings}).encode())
            meta_bytes = _json({"source_sha256": snapshot.sha256, "conversion_settings": settings,
                "conversion_identity": identity, "raw_json_sha256": bytes_sha256(raw_bytes)}).encode("utf-8")
        if not isinstance(meta_bytes, bytes):
            raise ValueError("conversion identity metadata is absent")
        # Retain diagnostic conversion bytes if candidate interpretation is refused.
        # Without the completion manifest these files are never a consumable bundle.
        snapshot.verify_unchanged()
        for name, data in {"raw_docling.json": raw_bytes, "raw_docling.meta.json": meta_bytes}.items():
            loader._write_bytes_atomic(out / name, data)
        result = read_procedure_items(json.loads(raw_bytes), version, source_format=source_format,
                    classification=classification, printed_page_labels=printed_page_labels)
        snapshot.verify_unchanged()
        candidate_bytes = (_json(result.as_dict()) + "\n").encode("utf-8")
        loader._write_bytes_atomic(out / "procedure_candidates.json", candidate_bytes)
        outputs = {"raw_docling.json": raw_bytes, "raw_docling.meta.json": meta_bytes,
                   "procedure_candidates.json": candidate_bytes}
        snapshot.verify_unchanged()
        manifest = {"complete": True, "source_sha256": snapshot.sha256, "version_id": version.version_id,
                    "source_unchanged": True, "files": {n: bytes_sha256(b) for n, b in outputs.items()}}
        loader._write_bytes_atomic(out / "manifest.json", (_json(manifest) + "\n").encode("utf-8"))
    return result
