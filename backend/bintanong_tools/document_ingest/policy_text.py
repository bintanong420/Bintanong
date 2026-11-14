"""Raw policy candidates, with pending-register preflight and external-only publication."""
from __future__ import annotations

import importlib
import json
import re
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ...bintanong_contracts.base import reject_foreign_ids
from ...bintanong_contracts.governance import SourceDocumentVersion
from ...bintanong_contracts.source import SourceSpan, check_span_binding
from ..prospectus_extractor import loader
from ..prospectus_extractor.identity import InputSnapshot, bytes_sha256
from .inspection import InspectionRefused, check_out
from .register import load_pending_register, version_for_snapshot


@dataclass(frozen=True)
class PolicyUnit:
    item_id: str
    label: str
    source_text: str
    pages: tuple[int, ...]
    raw_provenance_json: str
    heading_path: tuple[str, ...]
    printed_scope: str | None
    exception_to: str | None
    spans: tuple[SourceSpan, ...]
    rejection_reason: str | None

    @property
    def anchored(self) -> bool:
        return bool(self.spans) and self.rejection_reason is None


@dataclass(frozen=True)
class ItemOmission:
    item_id: str
    reason: str
    raw_text: str
    pages: tuple[int, ...]
    raw_provenance_json: str


@dataclass(frozen=True)
class PolicyCandidates:
    version: SourceDocumentVersion
    raw_item_count: int
    page_count: int
    units: tuple[PolicyUnit, ...]
    item_omissions: tuple[ItemOmission, ...]
    page_omissions: tuple[tuple[int, str], ...]

    def check_invariants(self) -> None:
        ids = [u.item_id for u in self.units] + [o.item_id for o in self.item_omissions]
        expected = {f"text-{i}" for i in range(self.raw_item_count)}
        if len(ids) != self.raw_item_count or set(ids) != expected:
            raise ValueError("raw item accounting is not exactly one unit or item omission")
        covered = {p for item in (*self.units, *self.item_omissions) for p in item.pages}
        omitted = [p for p, reason in self.page_omissions if reason == "scanned_no_text_layer"]
        if (len(omitted) != len(set(omitted)) or len(omitted) != len(self.page_omissions)
                or covered | set(omitted) != set(range(1, self.page_count + 1))):
            raise ValueError("physical page accounting is incomplete or invalid")

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_version": self.version.model_dump(mode="json"),
            "raw_item_count": self.raw_item_count, "page_count": self.page_count,
            "units": [{"item_id": u.item_id, "label": u.label, "source_text": u.source_text,
                       "pages": list(u.pages), "raw_provenance_json": u.raw_provenance_json,
                       "heading_path": list(u.heading_path), "printed_scope": u.printed_scope,
                       "exception_to": u.exception_to, "anchored": u.anchored,
                       "spans": [s.model_dump(mode="json") for s in u.spans],
                       "rejection_reason": u.rejection_reason} for u in self.units],
            "item_omissions": [{"item_id": o.item_id, "reason": o.reason, "raw_text": o.raw_text,
                                "pages": list(o.pages), "raw_provenance_json": o.raw_provenance_json}
                               for o in self.item_omissions],
            "page_omissions": [{"page": p, "reason": r} for p, r in self.page_omissions],
        }


def _reading_order(raw: Mapping[str, Any], count: int) -> list[int]:
    if "body" not in raw:
        return list(range(count))
    order: list[int] = []
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
            if ref.startswith("#/texts/"):
                if not re.fullmatch(r"#/texts/(0|[1-9]\d*)", ref):
                    raise ValueError("invalid text reading-order reference")
                index = int(ref.rsplit("/", 1)[1])
                if not 0 <= index < count or index in order:
                    raise ValueError("duplicate or invalid text reading-order reference")
                order.append(index)
                walk(raw["texts"][index])
            elif ref.startswith("#/tables/"):
                if not re.fullmatch(r"#/tables/(0|[1-9]\d*)", ref):
                    raise ValueError("invalid table reading-order reference")
                if ref in active:
                    raise ValueError("cyclic raw reading-order table")
                active.add(ref)
                try:
                    walk(raw["tables"][int(ref.rsplit("/", 1)[1])])
                except (KeyError, IndexError, TypeError) as exc:
                    raise ValueError("unresolved raw reading-order table") from exc
                active.remove(ref)
            elif ref.startswith(("#/groups/", "#/pictures/")):
                collection = ref.split("/")[1]
                kind = "group" if collection == "groups" else "picture"
                if not re.fullmatch(r"#/(groups|pictures)/(0|[1-9]\d*)", ref):
                    raise ValueError(f"invalid raw reading-order {kind}")
                if ref in active:
                    raise ValueError(f"cyclic raw reading-order {kind}")
                active.add(ref)
                try:
                    walk(raw[collection][int(ref.rsplit("/", 1)[1])])
                except (KeyError, IndexError, TypeError) as exc:
                    raise ValueError(f"unresolved raw reading-order {kind}") from exc
                active.remove(ref)
    walk(raw["body"])
    if "furniture" in raw:
        walk(raw["furniture"])
    if set(order) != set(range(count)):
        raise ValueError("raw reading order does not account for every text item")
    return order


def _span(item_id: str, text: str, prov: Mapping[str, Any], raw_pages: Mapping[str, Any],
          version: SourceDocumentVersion, labels: Mapping[int, str]) -> SourceSpan:
    page = prov["page_no"]
    box = prov["bbox"]
    size = raw_pages[str(page)]["size"]
    span = SourceSpan.parse({
        "schema_version": SourceSpan.SCHEMA_VERSION, "byte_sha256": version.byte_sha256,
        "version_id": version.version_id, "page": page, "printed_page_label": labels.get(page),
        "locator": {"kind": "text_item", "table_index": None, "cell_ids": [],
                    "item_ids": [item_id], "ref": None},
        "text": text, "bbox": [box[k] for k in ("l", "t", "r", "b")],
        "bbox_origin": box["coord_origin"], "page_size": [size["width"], size["height"]],
        "extraction": {"source_kind": "docling_raw_json", "resolution_method": "raw_item_provenance",
                       "repair_id": None, "ocr_confidence": None},
    })
    check_span_binding(span, version)
    return span


def _item_spans(item_id: str, text: str, provs: list[Mapping[str, Any]], raw_pages: Mapping[str, Any],
                version: SourceDocumentVersion, labels: Mapping[int, str]) -> tuple[SourceSpan, ...]:
    if not provs:
        raise ValueError("no raw provenance")
    ranges = []
    for prov in provs:
        bounds = prov.get("charspan")
        if bounds is None and len(provs) == 1:
            bounds = [0, len(text)]
        if (not isinstance(bounds, (list, tuple)) or len(bounds) != 2
                or any(type(n) is not int for n in bounds) or not 0 <= bounds[0] < bounds[1] <= len(text)):
            raise ValueError("missing or invalid raw character range; cannot assign text to pages")
        ranges.append(tuple(bounds))
    end = 0
    for start, stop in sorted(ranges):
        if start > end:
            raise ValueError("raw character ranges leave text unlocated")
        end = max(end, stop)
    if end != len(text):
        raise ValueError("raw character ranges leave text unlocated")
    return tuple(_span(item_id, text[start:stop], prov, raw_pages, version, labels)
                 for prov, (start, stop) in zip(provs, ranges))


def _located_text(item: Mapping[str, Any]) -> str:
    text, orig, marker = item["text"], item.get("orig"), item.get("marker")
    provs = item.get("prov", [])
    # Docling list postprocessing removes the marker from text while retaining
    # provenance over orig. Preserve that exact original, without remapping spans.
    if (item["label"] == "list_item" and text.strip() and isinstance(orig, str)
            and isinstance(marker, str) and marker.strip()
            and orig == marker + " " + text and len(provs) == 1
            and isinstance(provs[0], Mapping)):
        bounds = provs[0].get("charspan")
        if (isinstance(bounds, (list, tuple)) and len(bounds) == 2
                and all(type(n) is int for n in bounds) and tuple(bounds) == (0, len(orig))):
            return orig
    return text


def read_policy_items(raw: Mapping[str, Any], version: SourceDocumentVersion, *,
                      printed_page_labels: Mapping[int, str] | None = None) -> PolicyCandidates:
    """Keep every raw item, all provenance, and raw punctuation. No heading depth is inferred."""
    version = load_pending_register([version])[0]
    if not isinstance(raw, Mapping):
        raise ValueError("raw Docling document must be an object")
    reject_foreign_ids(raw, "institutional")
    texts, raw_pages = raw.get("texts"), raw.get("pages")
    if not isinstance(texts, list) or not isinstance(raw_pages, dict) or not raw_pages:
        raise ValueError("raw document needs text items and nonzero physical pages")
    if set(raw_pages) != {str(i) for i in range(1, len(raw_pages) + 1)}:
        raise ValueError("raw physical pages must be contiguous and one-based")
    labels = printed_page_labels or {}
    if any(type(p) is not int or str(p) not in raw_pages or not isinstance(label, str) or not label.strip()
           for p, label in labels.items()):
        raise ValueError("printed folios need known physical pages and nonempty labels")
    records = []
    furniture_pages: dict[str, set[int]] = {}
    text_pages: set[int] = set()
    for index in _reading_order(raw, len(texts)):
        item = texts[index]
        if (not isinstance(item, Mapping) or not isinstance(item.get("text"), str)
                or not isinstance(item.get("label"), str) or not isinstance(item.get("prov", []), list)):
            raise ValueError("invalid raw text item")
        text, provs = _located_text(item), item.get("prov", [])
        pages = []
        for prov in provs:
            if not isinstance(prov, Mapping):
                raise ValueError("invalid raw provenance")
            page = prov.get("page_no")
            if page is not None and (type(page) is not int or str(page) not in raw_pages):
                raise ValueError("raw provenance names an invalid physical page")
            if page is not None:
                pages.append(page)
        spans: tuple[SourceSpan, ...] = ()
        rejection = None
        if text.strip():
            text_pages.update(pages)
            try:
                spans = _item_spans(f"text-{index}", text, provs, raw_pages, version, labels)
            except (KeyError, TypeError, ValueError) as exc:
                rejection = f"unlocatable:{type(exc).__name__}:{exc}"
        normalized = " ".join(text.split()).casefold()
        marginal = bool(spans) and all(
            (max(s.bbox[1], s.bbox[3]) <= s.page_size[1] * .1
             or min(s.bbox[1], s.bbox[3]) >= s.page_size[1] * .9) for s in spans)
        if normalized and marginal:
            furniture_pages.setdefault(normalized, set()).update(pages)
        records.append((index, item, tuple(dict.fromkeys(pages)), spans, rejection, normalized, marginal))
    units, omissions, heading_path = [], [], []
    previous_clause = None
    for index, item, pages, spans, rejection, normalized, marginal in records:
        item_id, text, label = f"text-{index}", _located_text(item), item["label"]
        provenance = json.dumps(item.get("prov", []), ensure_ascii=False, sort_keys=True, allow_nan=False)
        reason = ("empty_text_item" if not text.strip() else "repeated_header_footer"
                  if marginal and len(furniture_pages.get(normalized, ())) >= 3 else None)
        if reason:
            omissions.append(ItemOmission(item_id, reason, text, pages, provenance))
            continue
        if label == "section_header":
            heading_path.append(text)
            previous_clause = None
        exception = previous_clause if re.match(r"\s*(except\b|unless\b|provided\b)", item["text"], re.I) else None
        scope = text if label == "scope" or (label != "section_header" and heading_path
                    and heading_path[-1].strip().casefold() in {"scope", "coverage", "applicability"}) else None
        units.append(PolicyUnit(item_id, label, text, pages, provenance, tuple(heading_path), scope,
                                exception, spans, rejection))
        if label != "section_header" and exception is None:
            previous_clause = item_id
    result = PolicyCandidates(version, len(texts), len(raw_pages), tuple(units), tuple(omissions),
                              tuple((p, "scanned_no_text_layer") for p in range(1, len(raw_pages) + 1)
                                    if p not in text_pages))
    result.check_invariants()
    return result


def extract_policy(snapshot: InputSnapshot, register: Sequence[SourceDocumentVersion | Mapping[str, Any]], *,
                   input_root: Path, out: Path, converter: Any = None,
                   printed_page_labels: Mapping[int, str] | None = None) -> PolicyCandidates:
    """Convert a registered PDF using installed Docling only; completion manifest is written last."""
    root, out = Path(input_root).resolve(), Path(out).resolve()
    if not isinstance(snapshot, InputSnapshot) or root not in snapshot.path.parents:
        raise ValueError("snapshot must belong to the explicit input root")
    if snapshot.path.suffix.lower() != ".pdf" or not snapshot.path.is_file():
        raise ValueError("policy candidates require a PDF file")
    try:
        check_out(root, out)
    except InspectionRefused as exc:
        raise ValueError(str(exc)) from exc
    version = version_for_snapshot(snapshot, register)
    # Import first: a missing installed environment fails before the loader's relaunch helper.
    loader.load_docling()
    importlib.import_module("docling")
    importlib.import_module("docling_core")
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="stage-", dir=out) as stage:
        converted = loader.load_document_result(snapshot.path, converter=converter,
                    raw_json_path=out / "raw_docling.json", stage_dir=Path(stage), snapshot=snapshot)
        if (not isinstance(converted.raw_json_bytes, bytes)
                or bytes_sha256(converted.raw_json_bytes) != converted.raw_json_sha256):
            raise ValueError("conversion raw bytes do not match their digest")
        result = read_policy_items(json.loads(converted.raw_json_bytes), version,
                                   printed_page_labels=printed_page_labels)
        snapshot.verify_unchanged()
        payload = (json.dumps(result.as_dict(), ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        outputs = {"raw_docling.json": converted.raw_json_bytes,
                   "raw_docling.meta.json": converted.meta_bytes, "policy_candidates.json": payload}
        if not isinstance(converted.meta_bytes, bytes):
            raise ValueError("conversion identity metadata is absent")
        for name, data in outputs.items():
            loader._write_bytes_atomic(out / name, data)
        snapshot.verify_unchanged()
        manifest = {"complete": True, "source_sha256": snapshot.sha256, "version_id": version.version_id,
                    "source_unchanged": True, "files": {n: bytes_sha256(b) for n, b in outputs.items()}}
        loader._write_bytes_atomic(out / "manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())
    return result
