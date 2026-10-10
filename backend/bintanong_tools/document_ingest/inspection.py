"""Read-only inspection of an originals tree (master 7.1 step 2).

    py -3.13 -m backend.bintanong_tools.document_ingest.inspection --root ORIGINALS --out NEW_OR_EMPTY_FOLDER

Files are only read as bytes. Reports go to --out, which must be outside every git repository and
outside the originals root. Nothing here converts, OCRs, or approves anything.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

from ..prospectus_extractor.publish import write_text_lf

REPORT = "inspection_report.json"
SOURCE_MANIFEST = "source_manifest.json"
MANIFEST = "manifest.json"
MAX_PATH = 260
NATIVE_MIN, SCAN_MAX = 100, 20  # text-layer characters per page (plan defaults)
MAGIC = {".pdf": b"%PDF-", ".jpg": b"\xff\xd8\xff", ".jpeg": b"\xff\xd8\xff", ".pptx": b"PK\x03\x04"}
FORM_TYPES = {0: "none", 1: "acroform", 2: "xfa_full", 3: "xfa_foreground"}
NS_A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
NS_P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
NS_DC = "{http://purl.org/dc/elements/1.1/}"
UNDETERMINED = {"value": "undetermined", "status": "undetermined"}


class InspectionRefused(Exception):
    pass


def _fs(path: str | Path) -> str:
    """Extended-length form on Windows so paths over 260 characters can be read."""
    p = os.path.abspath(str(path))
    return "\\\\?\\" + p if os.name == "nt" and not p.startswith("\\\\") else p


def _read(path: str) -> bytes:
    with open(path, "rb") as fh:  # never opened for writing
        return fh.read()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------- --out safety ----------
def check_out(root: Path, out: Path) -> None:
    root, out = root.resolve(), out.resolve()
    if not root.is_dir():
        raise InspectionRefused("root is not a folder")
    if out == root or root in out.parents:
        raise InspectionRefused("--out is inside the originals root")
    for parent in (out, *out.parents):
        if (parent / ".git").exists():  # a worktree's .git is a file
            raise InspectionRefused("--out is inside a git repository")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise InspectionRefused("--out must be new or empty")


# ---------- classification ----------
def page_class(chars: int, images: int) -> str:
    if chars >= NATIVE_MIN:
        return "native"
    if chars < SCAN_MAX:
        return "scanned" if images else "blank"
    return "unknown"


def document_class(c: dict[str, int]) -> str:
    nonblank = c["native"] + c["scanned"] + c["unknown"]
    if nonblank and c["native"] == nonblank:
        return "native"
    if nonblank and c["scanned"] == nonblank:
        return "scanned"
    return "mixed" if c["native"] and c["scanned"] else "unknown"


def _inspect_pdf(data: bytes) -> tuple[str, dict[str, Any] | None]:
    import pypdfium2 as pdfium
    import pypdfium2.raw as raw

    try:
        pdf = pdfium.PdfDocument(data)
    except pdfium.PdfiumError as exc:
        # pdfium refuses a valid zero-page file with error code 0 ("Success"), found by probing; 4 is a password.
        code = getattr(exc, "err_code", None)
        return {4: "encrypted", 0: "zero_pages"}.get(code, "unreadable"), None
    n = len(pdf)
    if n == 0:
        return "zero_pages", {"page_count": 0}
    classes = {"native": 0, "scanned": 0, "blank": 0, "unknown": 0}
    sizes, errors, images_total = set(), 0, 0
    for i in range(n):
        try:
            page = pdf[i]
            chars = len(page.get_textpage().get_text_range().strip())
            images = len(list(page.get_objects(filter=[raw.FPDF_PAGEOBJ_IMAGE])))
            sizes.add(tuple(round(v) for v in page.get_size()))
            images_total += images
            classes[page_class(chars, images)] += 1
        except Exception:
            errors += 1
            classes["unknown"] += 1
    labels = [pdf.get_page_label(i) for i in range(n)]
    try:
        form = FORM_TYPES.get(pdf.get_formtype(), "unknown")
    except Exception:
        form = "unknown"
    return "ok", {
        "page_count": n,
        "page_classes": classes,
        "document_class": document_class(classes),
        "invariant_ok": sum(classes.values()) == n,
        "page_errors": errors,
        "distinct_page_sizes": len(sizes),
        "image_objects": images_total,
        "form_type": form,
        "pdf_page_labels": labels if any(labels) else None,
        "printed_folio": "undetermined",
        "tables": "not_determined",
    }


def _inspect_jpg(data: bytes) -> tuple[str, dict[str, Any] | None]:
    from PIL import Image

    try:
        with Image.open(io.BytesIO(data)) as img:
            img.load()
            return "ok", {"width": img.width, "height": img.height}
    except Exception:
        return "unreadable", None


def _inspect_pptx(data: bytes) -> tuple[str, dict[str, Any] | None, dict[str, str]]:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names = z.namelist()
            slides = [n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
            tables = pictures = 0
            for n in slides:
                root = ET.fromstring(z.read(n))
                tables += len(root.findall(f".//{NS_A}tbl"))
                pictures += len(root.findall(f".//{NS_P}pic"))
            language = UNDETERMINED
            if "docProps/core.xml" in names:
                el = ET.fromstring(z.read("docProps/core.xml")).find(f".//{NS_DC}language")
                if el is not None and (el.text or "").strip():
                    language = {"value": el.text.strip(), "status": "observed"}
    except (zipfile.BadZipFile, ET.ParseError, KeyError, OSError):
        return "unreadable", None, UNDETERMINED
    return "ok", {"slides": len(slides), "tables": tables, "pictures": pictures}, language


def inspect_file(rel: str, data: bytes) -> dict[str, Any]:
    ext = Path(rel).suffix.lower()
    rec: dict[str, Any] = {"path": rel, "extension": ext, "size": len(data), "sha256": _sha(data),
                           "language": UNDETERMINED, "health": "ok"}
    magic = MAGIC.get(ext)
    if magic and magic not in data[:1024 if ext == ".pdf" else 4]:
        rec["health"] = "extension_mismatch"
    elif ext == ".pdf":
        rec["health"], rec["pdf"] = _inspect_pdf(data)
    elif ext in (".jpg", ".jpeg"):
        rec["health"], rec["image"] = _inspect_jpg(data)
    elif ext == ".pptx":
        rec["health"], rec["pptx"], rec["language"] = _inspect_pptx(data)
    for key in ("pdf", "image", "pptx"):
        if rec.get(key, 0) is None:
            del rec[key]
    return rec


# ---------- tree walk ----------
def _walk(root: Path) -> list[tuple[str, str]]:
    """(root-relative posix path, readable filesystem path), sorted."""
    base = _fs(root)
    found = []
    def refuse(error: OSError) -> None:
        raise InspectionRefused(f"cannot enumerate source tree: {error}") from error

    for folder, _dirs, files in os.walk(base, onerror=refuse):
        for name in files:
            full = os.path.join(folder, name)
            found.append((os.path.relpath(full, base).replace("\\", "/"), full))
    return sorted(found)


def source_manifest(entries: list[tuple[str, str]]) -> list[dict[str, Any]]:
    out = []
    for rel, full in entries:
        st = os.stat(full)
        out.append({"path": rel, "size": st.st_size, "mtime_ns": st.st_mtime_ns, "sha256": _sha(_read(full))})
    return out


def _group(files: list[dict[str, Any]]) -> dict[str, Any]:
    by_sha: dict[str, list[str]] = {}
    by_name: dict[str, set[str]] = {}
    for f in files:
        by_sha.setdefault(f["sha256"], []).append(f["path"])
        by_name.setdefault(Path(f["path"]).name, set()).add(f["sha256"])
    groups = sorted(({"sha256": s, "paths": sorted(p)} for s, p in by_sha.items() if len(p) > 1),
                    key=lambda g: g["paths"][0])
    same_name = [{"name": n, "identities": len(s)} for n, s in sorted(by_name.items()) if len(s) > 1]
    return {"byte_identical_groups": groups, "same_name_different_bytes": same_name}


def _pilots(files: list[dict[str, Any]]) -> dict[str, Any]:
    def names(pred):
        return sorted(f["path"] for f in files if pred(f, Path(f["path"]).name.lower()))

    pdf_pages = sorted(((f["pdf"]["page_count"], f["path"]) for f in files if "pdf" in f),
                       key=lambda t: (-t[0], t[1]))
    return {
        "status": "candidates_for_owner_not_selected",
        "handbook_editions": names(lambda f, n: "handbook" in n and f["extension"] == ".pdf"),
        "usg_constitution": names(lambda f, n: "constitution" in n),
        "election_code": names(lambda f, n: "election" in n),
        "pptx": names(lambda f, n: f["extension"] == ".pptx"),
        "jpg_poster": names(lambda f, n: f["extension"] in (".jpg", ".jpeg"))[:1],
        "form": names(lambda f, n: "form" in n)[:1],
        "largest_pdf_by_pages": [{"path": p, "pages": c} for c, p in pdf_pages[:1]],
    }


def _counts(files: list[dict[str, Any]], longest: int) -> dict[str, Any]:
    def tally(keys):
        out: dict[str, int] = {}
        for k in keys:
            out[k] = out.get(k, 0) + 1
        return dict(sorted(out.items()))

    prosp = sum(1 for f in files if "prospectus" in f["path"].split("/")[0].lower())
    return {
        "total": len(files),
        "by_extension": tally(f["extension"] for f in files),
        "by_health": tally(f["health"] for f in files),
        "pdf_document_class": tally(f["pdf"]["document_class"] for f in files if "document_class" in f.get("pdf", {})),
        "unique_byte_identities": len({f["sha256"] for f in files}),
        "prospectus_workstream": prosp,
        "non_prospectus": len(files) - prosp,
        "longest_path_chars": longest,
    }


def _dump(obj: Any) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def run(root: Path, out: Path) -> int:
    root = Path(root).resolve()
    check_out(root, Path(out))
    entries = _walk(root)
    before = source_manifest(entries)
    files, longest, unreachable = [], 0, 0
    for rel, full in entries:
        length = len(str(root)) + 1 + len(rel)
        longest = max(longest, length)
        data = _read(full)
        if length > MAX_PATH:
            rec = {"path": rel, "extension": Path(rel).suffix.lower(), "size": len(data), "sha256": _sha(data),
                   "language": UNDETERMINED, "health": "path_unreachable"}
            unreachable += 1
        else:
            rec = inspect_file(rel, data)
        files.append(rec)
    after = source_manifest(_walk(root))
    if after != before:
        print("failed: a source file changed during the run; no manifest written", file=sys.stderr)
        return 1
    bad_invariant = [f["path"] for f in files if "pdf" in f and f["pdf"].get("invariant_ok") is False]
    report = {"files": files, "counts": _counts(files, longest), "duplicates": _group(files),
              "pilot_candidates": _pilots(files),
              "findings": {"path_unreachable": unreachable, "invariant_violations": bad_invariant},
              "note": "Candidates only. Nothing here approves a source or a curriculum."}
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    texts = {REPORT: _dump(report), SOURCE_MANIFEST: _dump(before)}
    for name, text in texts.items():
        write_text_lf(out / name, text)
    manifest = {"complete": True, "files": {n: _sha(t.encode("utf-8")) for n, t in texts.items()},
                "source_manifest_before_equals_after": True, "source_files": len(before)}
    write_text_lf(out / MANIFEST, _dump(manifest))  # last: no manifest means an incomplete run
    c = report["counts"]
    print(f"inspected {c['total']} files, {c['unique_byte_identities']} unique, "
          f"{unreachable} unreachable, {len(bad_invariant)} invariant violations")
    return 1 if unreachable or bad_invariant else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    try:
        return run(args.root, args.out)
    except InspectionRefused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
