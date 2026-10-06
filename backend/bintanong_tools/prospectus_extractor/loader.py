"""Docling-to-evidence adapter, conversion cache and document loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from typing import Mapping
from typing import Sequence
import hashlib
import json
import os
import tempfile
import time

from .docling_env import _docling_importable, ensure_docling_env, get_shared_converter, load_docling
from .identity import IDENTITY_VERSION, conversion_identity, conversion_settings, file_sha256
from .text import clean_str, match_semester_labels, match_year_label
from .grid import extract_table_year_contexts
from .layout import detect_column_groups, is_header_row
from .evidence import LoadedDocument, NormalizedCell, NormalizedTable, ProspectusEvidence, SourceBBox, normalized_table_from_grid, project_table_to_grid


def _page_from_mapping(value: Any, default: int | None = None) -> int | None:
    if not isinstance(value, Mapping):
        return default
    for key in ("page", "page_no", "page_number"):
        if value.get(key) is not None:
            try:
                return int(value[key])
            except (TypeError, ValueError):
                pass
    return default


def _source_bbox(value: Any, default_page: int | None = None) -> SourceBBox | None:
    """Accept the bbox spellings used across Docling serialisation versions."""
    if not isinstance(value, Mapping):
        return None
    page = _page_from_mapping(value, default_page)
    bbox = value.get("bbox") if isinstance(value.get("bbox"), Mapping) else value
    key_sets = (
        ("l", "t", "r", "b"),
        ("left", "top", "right", "bottom"),
        ("x0", "y0", "x1", "y1"),
    )
    for left_key, top_key, right_key, bottom_key in key_sets:
        if all(bbox.get(key) is not None for key in (left_key, top_key, right_key, bottom_key)):
            try:
                return SourceBBox(
                    page,
                    float(bbox[left_key]),
                    float(bbox[top_key]),
                    float(bbox[right_key]),
                    float(bbox[bottom_key]),
                    str(bbox["coord_origin"]) if bbox.get("coord_origin") else None,
                )
            except (TypeError, ValueError):
                return None
    return None


def _default_table_page(table_wrapper: Mapping[str, Any]) -> int | None:
    for prov in table_wrapper.get("prov", []) or []:
        page = _page_from_mapping(prov)
        if page is not None:
            return page
    return _page_from_mapping(table_wrapper)


def docling_to_normalized_table(
    table_data: Mapping[str, Any],
    table_index: int,
    table_wrapper: Mapping[str, Any] | None = None,
) -> NormalizedTable:
    """The one production table adapter. Merged cells remain one cell."""
    wrapper = table_wrapper or {}
    raw_cells = table_data.get("table_cells") or []
    if not raw_cells and isinstance(table_data.get("grid"), list):
        # Compatibility with hand-authored/synthetic Docling-like dictionaries.
        return normalized_table_from_grid(table_data.get("grid") or [], table_index)

    default_page = _default_table_page(wrapper)
    normalized: list[NormalizedCell] = []
    max_row = 0
    max_col = 0
    for cell_index, raw in enumerate(raw_cells):
        if not isinstance(raw, Mapping):
            continue
        row_start = int(raw.get("start_row_offset_idx", raw.get("row_index", 0)) or 0)
        row_end = int(raw.get("end_row_offset_idx", row_start + 1) or row_start + 1)
        col_start = int(raw.get("start_col_offset_idx", raw.get("col_index", 0)) or 0)
        col_end = int(raw.get("end_col_offset_idx", col_start + 1) or col_start + 1)
        if row_end <= row_start:
            row_end = row_start + 1
        if col_end <= col_start:
            col_end = col_start + 1

        bbox = _source_bbox(raw, default_page)
        if bbox is None:
            for prov in raw.get("prov", []) or []:
                bbox = _source_bbox(prov, default_page)
                if bbox is not None:
                    break
        raw_text = str(raw.get("text", "") or "")
        normalized.append(
            NormalizedCell(
                cell_id=f"t{table_index}-c{cell_index}",
                table_index=table_index,
                raw_text=raw_text,
                text=clean_str(raw_text),
                row_start=row_start,
                row_end=row_end,
                col_start=col_start,
                col_end=col_end,
                bbox=bbox,
            )
        )
        max_row = max(max_row, row_end)
        max_col = max(max_col, col_end)

    num_rows = int(table_data.get("num_rows") or max_row)
    num_cols = int(table_data.get("num_cols") or max_col)
    return NormalizedTable(table_index, num_rows, num_cols, normalized)


def grid_from_table_cells(table_data: dict[str, Any]) -> list[list[str]]:
    """Compatibility/debug projection; not a canonical representation."""
    return project_table_to_grid(docling_to_normalized_table(table_data, 0))


def _table_year_hint_sources(data: Mapping[str, Any]) -> dict[int, str]:
    sources: dict[int, str] = {}

    def consume(children: Sequence[Mapping[str, Any]]) -> None:
        current_source = ""
        current_year: str | None = None
        for child in children:
            cref = str(child.get("cref", ""))
            if cref.startswith("#/texts/"):
                try:
                    index = int(cref.rsplit("/", 1)[1])
                    text = clean_str((data.get("texts") or [])[index].get("text", ""))
                except (IndexError, TypeError, ValueError, AttributeError):
                    continue
                hit = match_year_label(text)
                if hit:
                    current_year = hit
                    current_source = f"text-{index}"
            elif cref.startswith("#/tables/") and current_year:
                try:
                    table_index = int(cref.rsplit("/", 1)[1])
                except ValueError:
                    continue
                sources.setdefault(table_index, current_source)

    for group in data.get("groups", []) or []:
        if isinstance(group, Mapping):
            consume(group.get("children", []) or [])
    body = data.get("body", {}) or {}
    if isinstance(body, Mapping):
        consume(body.get("children", []) or [])
    return sources


def evidence_adapter(
    raw_dict: Mapping[str, Any],
    docling_document: Any = None,
    source_kind: str = "docling-json",
) -> ProspectusEvidence:
    """Canonical adapter shared by live conversion and cached raw JSON."""
    tables: list[NormalizedTable] = []
    for table_index, wrapper in enumerate(raw_dict.get("tables", []) or []):
        if not isinstance(wrapper, Mapping):
            continue
        table_data = wrapper.get("data")
        if not isinstance(table_data, Mapping):
            continue
        table = docling_to_normalized_table(table_data, table_index, wrapper)
        if table.cells and table.num_rows > 0 and table.num_cols > 0:
            tables.append(table)

    text_items: list[dict[str, Any]] = []
    for index, item in enumerate(raw_dict.get("texts", []) or []):
        if not isinstance(item, Mapping):
            continue
        value = clean_str(item.get("text", ""))
        if not value:
            continue
        bbox = None
        for prov in item.get("prov", []) or []:
            bbox = _source_bbox(prov)
            if bbox:
                break
        text_items.append(
            {
                "item_id": f"text-{index}",
                "label": str(item.get("label", "text")),
                "text": value,
                "raw_text": str(item.get("text", "") or ""),
                "page": bbox.page if bbox else None,
                "bbox": bbox.as_list() if bbox else None,
                "origin": bbox.origin if bbox else None,
            }
        )

    page_sizes: dict[int, tuple[float, float]] = {}
    for key, page in (raw_dict.get("pages") or {}).items():
        size = page.get("size") if isinstance(page, Mapping) else None
        try:
            page_sizes[int(key)] = (float(size["width"]), float(size["height"]))
        except (TypeError, ValueError, KeyError):
            continue

    try:
        markdown = docling_document.export_to_markdown() if docling_document is not None else ""
    except Exception:
        markdown = ""
    if not markdown:
        lines = [item["text"] for item in text_items]
        for table in tables:
            for row in project_table_to_grid(table, repeat_spans=False):
                joined = " ".join(cell for cell in row if cell)
                if joined:
                    lines.append(joined)
        markdown = "\n".join(lines)

    try:
        table_year_hints = extract_table_year_contexts(dict(raw_dict))
    except Exception:
        table_year_hints = {}
    return ProspectusEvidence(
        tables=tables,
        text_items=text_items,
        markdown=markdown,
        docling_document=docling_document,
        source_kind=source_kind,
        table_year_hints=table_year_hints,
        table_year_hint_sources=_table_year_hint_sources(raw_dict),
        page_sizes=page_sizes,
    )


def normalize_evidence(value: ProspectusEvidence | Mapping[str, Any]) -> dict[str, Any]:
    """Stable, serialisable evidence signature for live-vs-cached regressions."""
    evidence = value if isinstance(value, ProspectusEvidence) else evidence_adapter(value)
    return {
        "tables": [
            {
                "table_index": table.table_index,
                "num_rows": table.num_rows,
                "num_cols": table.num_cols,
                "cells": [cell.as_evidence_dict() for cell in table.cells],
            }
            for table in evidence.tables
        ],
        "text_items": evidence.text_items,
        "markdown": evidence.markdown,
        "table_year_hints": evidence.table_year_hints,
        "table_year_hint_sources": evidence.table_year_hint_sources,
    }


def _load_from_rehydrated_docling_document(
    doc: Any,
    source_kind: str,
    raw_dict: dict[str, Any] | None = None,
) -> ProspectusEvidence:
    raw = raw_dict
    if raw is None:
        raw = doc.export_to_dict() if hasattr(doc, "export_to_dict") else doc.model_dump(mode="json")
    return evidence_adapter(raw, doc, source_kind)


def load_from_raw_json(data: dict[str, Any]) -> ProspectusEvidence:
    if _docling_importable():
        dl = load_docling()
        doc = dl["DoclingDocument"].model_validate(data)
        return evidence_adapter(data, doc, "docling-json")
    return evidence_adapter(data, None, "docling-json-degraded")


def load_from_docling_document(doc: Any) -> ProspectusEvidence:
    dl = load_docling()
    raw = doc.export_to_dict() if hasattr(doc, "export_to_dict") else doc.model_dump(mode="json")
    rehydrated = dl["DoclingDocument"].model_validate(raw)
    return evidence_adapter(raw, rehydrated, "docling-document")


def _conversion_has_bad_alloc(result: Any) -> bool:
    for err in getattr(result, "errors", None) or []:
        rendered = f"{clean_str(err)} {clean_str(getattr(err, 'error_message', ''))}".lower()
        if "bad_alloc" in rendered or "bad allocation" in rendered:
            return True
    return False


def _conversion_errors(result: Any) -> list[str]:
    return [clean_str(e) for e in (getattr(result, "errors", None) or []) if clean_str(e)]


def _cache_meta_path(raw_json_path: Path) -> Path:
    return raw_json_path.with_name(raw_json_path.stem + ".meta.json")


class ReplaceFailed(OSError):
    """A finished file could not be moved over its target (on Windows: the target stayed locked)."""


REPLACE_ATTEMPTS = 5
REPLACE_DELAY_SECONDS = 0.2


def replace_file(source: Path, target: Path) -> None:
    """os.replace with a short retry: Windows scanners and indexers briefly lock fresh files.

    After the last attempt the source is removed and ReplaceFailed names both paths;
    the target keeps whatever it held before.
    """
    for attempt in range(REPLACE_ATTEMPTS):
        try:
            os.replace(source, target)
            return
        except PermissionError as exc:
            if attempt == REPLACE_ATTEMPTS - 1:
                Path(source).unlink(missing_ok=True)
                raise ReplaceFailed(
                    f"could not replace {target} with {source} after {REPLACE_ATTEMPTS} "
                    f"attempts (the target stayed locked): {exc}"
                ) from exc
            time.sleep(REPLACE_DELAY_SECONDS * (attempt + 1))


def _write_bytes_atomic(path: Path, data: bytes) -> None:
    """Write a temp file of this call's own beside the target, then replace: a reader
    never sees half a file and two writers never share a temp file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    temp = Path(temp_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
        replace_file(temp, path)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def load_reusable_cache(
    raw_json_path: Path, meta_path: Path, pdf_sha256: str, settings: Mapping[str, Any]
) -> tuple[LoadedDocument | None, str]:
    """The cached raw Docling JSON as a document when it may stand in for a fresh
    conversion, else (None, reason). Any doubt is a miss, never an error.

    The record's `pdf_sha256` and `conversion_settings` must each equal the current ones
    and its `conversion_identity` must be the identity of exactly those. The JSON is read
    once; the digest is checked on those bytes and those same bytes are parsed, so a
    writer replacing the file meanwhile cannot slip other content in.
    """
    expected_identity = conversion_identity(pdf_sha256, settings)
    try:
        meta = json.loads(Path(meta_path).read_bytes().decode("utf-8"))
    except FileNotFoundError:
        return None, "cached Docling JSON has no identity record"
    except (OSError, ValueError):
        return None, "identity record is unreadable"
    if (
        not isinstance(meta, dict)
        or meta.get("identity_version") != IDENTITY_VERSION
        or "conversion_identity" not in meta
    ):
        return None, "identity record is from an older version"
    if meta["conversion_identity"] != expected_identity:
        return None, "PDF bytes or conversion settings changed"
    if meta.get("pdf_sha256") != pdf_sha256:
        return None, "identity record names other PDF bytes"
    if meta.get("conversion_settings") != dict(settings):
        return None, "identity record names other conversion settings"
    try:
        raw_bytes = Path(raw_json_path).read_bytes()
    except FileNotFoundError:
        return None, "no cached Docling JSON"
    except OSError:
        return None, "cached Docling JSON is unreadable"
    if meta.get("raw_json_sha256") != hashlib.sha256(raw_bytes).hexdigest():
        return None, "cached JSON does not match its identity record"
    try:
        data = json.loads(raw_bytes.decode("utf-8"))
        if not isinstance(data, dict):
            return None, "cached Docling JSON is not a document"
        return load_from_raw_json(data), "identity matches"
    except ValueError as exc:  # bad UTF-8, bad JSON, or a dict Docling rejects
        return None, f"cached Docling JSON is corrupt ({type(exc).__name__})"


def load_document(
    input_path: Path,
    device: str = "auto",
    force_reconvert: bool = True,
    converter: Any = None,
    raw_json_path: Path | None = None,
    stage_dir: Path | None = None,
) -> tuple[LoadedDocument, Path | None]:
    """Load a PDF (convert or reuse an identity-matched cache) or a raw Docling JSON.

    A Docling JSON given as the input is a review input: nothing verifies which PDF
    or settings produced it. When `stage_dir` is given, a fresh conversion is written
    there and the returned path is where it will be published; the caller publishes it.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    suffix = input_path.suffix.lower()
    if suffix == ".json":
        data = json.loads(input_path.read_text(encoding="utf-8"))
        print(f"[*] Loading Docling JSON: {input_path.name} (review input; source PDF not verified)")
        return load_from_raw_json(data), input_path

    if suffix != ".pdf":
        raise ValueError(f"Unsupported input type: {input_path.suffix}")

    ensure_docling_env()
    load_docling()

    raw_json_path = Path(raw_json_path).resolve() if raw_json_path else input_path.parent / f"{input_path.stem}_docling.json"
    meta_path = _cache_meta_path(raw_json_path)
    settings = conversion_settings()
    pdf_hash = file_sha256(input_path)
    expected = conversion_identity(pdf_hash, settings)

    if not force_reconvert:
        cached, reason = load_reusable_cache(raw_json_path, meta_path, pdf_hash, settings)
        if cached is not None:
            print(f"[*] Reusing raw Docling JSON with matching identity: {raw_json_path.name}")
            return cached, raw_json_path
        if raw_json_path.exists():
            print(f"[*] Ignoring cached Docling JSON ({reason}); reconverting.")

    print(f"[*] Converting with Docling ({device.upper()}): {input_path.name}")
    active = converter or get_shared_converter(
        device=device, backend="docling_parse", settings=settings)
    result = active.convert(str(input_path))

    if _conversion_has_bad_alloc(result):
        print(
            "[!] Native Docling PDF backend hit std::bad_alloc; retrying through "
            "Docling's PyPdfium backend (NOT PyMuPDF)."
        )
        result = get_shared_converter(
            device=device, backend="pypdfium2", settings=settings).convert(str(input_path))

    if _conversion_has_bad_alloc(result):
        raise MemoryError(
            "Docling still reported std::bad_alloc after backend retry. Confirm "
            "docling-parse>=7.12 (Bintanong pins >=7.20) and a Windows pagefile."
        )

    remaining_errors = _conversion_errors(result)
    if remaining_errors:
        raise RuntimeError(
            "Docling returned conversion errors; refusing to build a partial institutional artifact: "
            + " | ".join(remaining_errors[:6])
        )

    doc = result.document
    raw = doc.export_to_dict() if hasattr(doc, "export_to_dict") else doc.model_dump(mode="json")
    raw_bytes = json.dumps(raw, indent=2, ensure_ascii=False).encode("utf-8")
    meta = {
        "identity_version": IDENTITY_VERSION,
        "pdf_sha256": pdf_hash,
        "conversion_settings": settings,
        "conversion_identity": expected,
        "raw_json_sha256": hashlib.sha256(raw_bytes).hexdigest(),
    }
    write_dir = Path(stage_dir) if stage_dir else raw_json_path.parent
    # raw JSON first, meta second: a crash between them leaves a pair that fails the sha check.
    _write_bytes_atomic(write_dir / raw_json_path.name, raw_bytes)
    _write_bytes_atomic(write_dir / meta_path.name, json.dumps(meta, indent=2).encode("utf-8"))
    print(f"[+] Raw Docling JSON -> {write_dir / raw_json_path.name}")

    rehydrated = load_docling()["DoclingDocument"].model_validate(raw)
    return _load_from_rehydrated_docling_document(
        rehydrated, "docling-document", raw
    ), raw_json_path

def dump_grid(document: LoadedDocument) -> str:
    """Human-readable dump of every reconstructed table row - the debugging tool v1 lacked."""
    lines: list[str] = []
    for table in document.tables:
        table_index = table.table_index
        grid = project_table_to_grid(table)
        groups, header_index = detect_column_groups(grid)
        lines.append(
            f"== Table {table_index}: {len(grid)} rows x {max((len(r) for r in grid), default=0)} cols, "
            f"header row {header_index}, {len(groups)} column group(s), "
            f"{len(table.cells)} canonical cell(s)"
        )
        for group in groups:
            lines.append(f"   group {group.index}: {group.as_dict()}")
        for row_index, row in enumerate(grid):
            rendered = " | ".join(cell if cell else "." for cell in row)
            marker = ""
            if is_header_row(row):
                marker = "  <-- header"
            elif match_year_label(" ".join(row)):
                marker = f"  <-- YEAR BANNER: {match_year_label(' '.join(row))}"
            elif match_semester_labels(" ".join(row)):
                marker = f"  <-- SEMESTER BANNER: {[l for _p, l in match_semester_labels(' '.join(row))]}"
            lines.append(f"  [{row_index:3d}] {rendered}{marker}")
        lines.append("   canonical spans:")
        for cell in table.cells:
            lines.append(
                f"     {cell.cell_id} r[{cell.row_start},{cell.row_end}) "
                f"c[{cell.col_start},{cell.col_end}) page="
                f"{cell.bbox.page if cell.bbox else '-'} text={cell.text!r}"
            )
        lines.append("")
    return "\n".join(lines)
