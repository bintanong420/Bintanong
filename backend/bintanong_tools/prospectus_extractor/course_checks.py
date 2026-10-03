"""Course-level checks of prospectus extractor output against its markup twin and the source PDF.

Pure functions; the only I/O is `load_pdf_pages`, `sha256`, `manifest_index` and `resolve_pdf`. The
audit script (scripts/prospectus_course_audit.py) and the year/semester verifier (verify.py) both
call them, so a check is written once.

Checks, per course unless noted (status values: match, loose, transformed, fail, empty,
not_checked; C and D use silent / flagged):
  A  JSON -> MD   A_prov A_code A_title A_lecture A_lab A_total A_prereq
  B  JSON -> PDF  B_code B_title B_units
  C  PDF -> JSON  (per printed candidate) code-like strings no course accounts for
  D  MD -> JSON   (per cell) code-like .md cells that no course claims

Normalisation (strict tier): Unicode NFC, whitespace runs to one space, trim. PDF text also maps
U+FFFE and U+00AD to "-" and "". Loose tier: whitespace and hyphen/dash characters removed.
Reuse for OCR output: pass pdf_pages = {page_no: PdfPage(text, chars, height)} from any source.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .grid import is_probable_course_code

DASHES = "-\u2010\u2011\u2012\u2013\u2014\u2212\ufffe\u00ad"


# ---------------------------------------------------------------- normalisation

def normalise(text) -> str:
    return " ".join(unicodedata.normalize("NFC", "" if text is None else str(text)).split())


def pdf_clean(text) -> str:
    return normalise(str(text or "").replace("\ufffe", "-").replace("\u00ad", ""))


def loose(text) -> str:
    return re.sub(f"[\\s{re.escape(DASHES)}]+", "", normalise(text))


# ---------------------------------------------------------------- markup parsing

@dataclass
class MdDoc:
    cells: dict = field(default_factory=dict)  # cell id -> text (table cells and unplaced cells)
    items: dict = field(default_factory=dict)  # text item id -> text (headings, paragraphs)


def _md_text(raw: str) -> str:
    return html.unescape(re.sub(r"</?small>", "", raw.replace("<br>", "\n")))


def parse_markup(md: str) -> MdDoc:
    doc = MdDoc()
    for m in re.finditer(r'<(td|th) data-cell="([^"]*)"[^>]*>(.*?)</\1>', md, re.S):
        doc.cells[html.unescape(m.group(2))] = _md_text(m.group(3))
    for m in re.finditer(r'<p data-unplaced-cell="([^"]*)"[^>]*>(.*?)</p>', md, re.S):
        doc.cells[html.unescape(m.group(1))] = _md_text(m.group(2))
    for m in re.finditer(r'<(h\d|p) data-item="([^"]*)"[^>]*>(.*?)</\1>', md, re.S):
        doc.items[html.unescape(m.group(2))] = _md_text(m.group(3))
    return doc


# ---------------------------------------------------------------- helpers

def _row(check, status, js="", md="", pdf="", detail="", tier=""):
    return {"check": check, "status": status, "tier": tier, "json": js, "md": md, "pdf": pdf, "detail": detail}


def _found(value, texts, joined_texts):
    """Strict then loose search for VALUE in single texts and in joined variants. Returns tier or None."""
    needle = normalise(value)
    if not needle:
        return None
    pools = [normalise(t) for t in texts] + [normalise(t) for t in joined_texts]
    if any(needle in p for p in pools):
        return "strict"
    key = loose(value)
    if key and any(key in loose(p) for p in pools):
        return "loose"
    return None


def _fmt(value) -> str:
    return f"{value:g}" if isinstance(value, float) else str(value)


def _snippet(page_text: str, code: str, width: int = 90) -> str:
    text, key = pdf_clean(page_text), loose(code)
    if not key:
        return ""
    # locate the code in the loose text, then map back by scanning the strict text
    seen, flat = [], []
    for i, ch in enumerate(text):
        if not ch.isspace() and ch not in DASHES:
            flat.append(ch)
            seen.append(i)
    at = "".join(flat).find(key)
    if at < 0:
        return ""
    start = seen[at]
    return text[max(0, start - 10): start + width]


def course_roles(course, layout) -> dict:
    """role -> [source cell dicts], using the table's column group for this course. {} when unknown."""
    src = course.get("_source") or {}
    table = next((t for t in layout or [] if t.get("table_index") == src.get("table_index")), None)
    groups = (table or {}).get("column_groups") or []
    group = next((g for g in groups if g.get("index") == src.get("column_group")), None)
    if not group:
        return {}
    wanted = {"code": group.get("code_idx"), "title": group.get("title_idx"),
              "unit": group.get("unit_idx"), "prereq": group.get("prereq_idx")}
    cells = (course.get("provenance") or {}).get("source_cells") or []
    return {role: [c for c in cells if c.get("col_start") == idx] for role, idx in wanted.items() if idx is not None}


def _provenance_texts(course, md: MdDoc):
    ids = (course.get("provenance") or {}).get("source_cell_ids") or []
    present = [i for i in ids if i in md.cells]
    in_order = [md.cells[i] for i in present]
    by_number = sorted(present, key=lambda i: [int(n) for n in re.findall(r"\d+", i)])
    return present, in_order, [" ".join(in_order), " ".join(md.cells[i] for i in by_number)]


# ---------------------------------------------------------------- check A

def _text_field(check, value, raw, changed, texts, joined, where):
    shown = _fmt(value)
    if changed:
        tier = _found(raw if raw else value, texts, joined)
        return _row(check, "transformed" if tier else "fail", shown, detail=f"parsed value differs from printed {raw!r}" if tier else f"printed text {raw!r} not in {where}", tier=tier or "")
    tier = _found(value, texts, joined)
    if tier == "strict":
        return _row(check, "match", shown, tier="strict")
    if tier == "loose":
        return _row(check, "loose", shown, tier="loose", detail="found only ignoring spaces/hyphens")
    return _row(check, "fail", shown, detail=f"not in {where}")


def _unit_rows(prefix, units, raw_texts, raw_found):
    raw = normalise(units.get("raw"))
    lec, lab, total = units.get("lecture"), units.get("lab"), units.get("total")
    rows = []
    for name, value in (("lecture", lec), ("lab", lab), ("total", total)):
        check = f"{prefix}_{name}"
        if value is None:
            rows.append(_row(check, "empty", "", detail="no value"))
            continue
        s = _fmt(value)
        if not raw_found:
            rows.append(_row(check, "fail", s, detail=f"printed units {raw!r} not in the units cell(s)"))
        elif s == raw:
            rows.append(_row(check, "match", s))
        elif s in re.findall(r"\d+(?:\.\d+)?", raw):
            rows.append(_row(check, "transformed", s, detail=f"parsed from printed {raw!r}"))
        elif name == "lab" and value == 0:
            rows.append(_row(check, "transformed", s, detail=f"lab defaulted to 0; printed {raw!r}"))
        elif name == "total" and lec is not None and lab is not None and lec + lab == total:
            rows.append(_row(check, "transformed", s, detail=f"lecture+lab; printed {raw!r}"))
        else:
            rows.append(_row(check, "fail", s, detail=f"not derivable from printed {raw!r}"))
    return rows


def check_course_md(course, md: MdDoc, layout=None) -> list:
    present, texts, joined = _provenance_texts(course, md)
    ids = (course.get("provenance") or {}).get("source_cell_ids") or []
    missing = [i for i in ids if i not in md.cells]
    rows = [_row("A_prov", "fail" if missing or not ids else "match", ",".join(ids), detail=f"missing from md: {missing}" if missing else ("no provenance" if not ids else ""))]
    where = "its md cells"
    code = course.get("course_code")
    rows.append(_text_field("A_code", code, None, False, texts, joined, where))
    title, raw_title = course.get("course_title"), course.get("title_raw")
    changed = bool(course.get("footnote_marker")) or (raw_title is not None and normalise(raw_title) != normalise(title))
    rows.append(_text_field("A_title", title, raw_title, changed, texts, joined, where))
    units = course.get("units") or {}
    roles = course_roles(course, layout)
    unit_ids = [c["cell_id"] for c in roles.get("unit", []) if c["cell_id"] in md.cells]
    unit_texts = [md.cells[i] for i in unit_ids] if roles else texts
    raw = normalise(units.get("raw"))
    if raw:
        rows += _unit_rows("A", units, unit_texts, any(raw in normalise(t) for t in unit_texts))
        for r in rows[-3:]:
            r["md"] = " | ".join(normalise(t) for t in unit_texts)[:80]
    else:
        rows += [_row(f"A_{n}", "empty", detail="no printed units") for n in ("lecture", "lab", "total")]
    prereq = course.get("prerequisites_raw")
    if normalise(prereq):
        rows.append(_text_field("A_prereq", prereq, None, False, texts, joined, where))
    else:
        rows.append(_row("A_prereq", "empty"))
    everything = " | ".join(normalise(t) for t in texts)[:200]
    for r in rows:
        r["md"] = r["md"] or everything
    return rows


# ---------------------------------------------------------------- check B

def text_in_box(chars, bbox, page_height, pad=1.5) -> str:
    """Characters whose centre is inside BBOX. CHARS are (ch, left, bottom, right, top) in PDF
    points (y up); BBOX is [left, top, right, bottom] in a top-left frame (Docling)."""
    left, top, right, bottom = bbox
    lo, hi = page_height - bottom - pad, page_height - top + pad
    hit = [c for c in chars if not c[0].isspace() and left - pad <= (c[1] + c[3]) / 2 <= right + pad and lo <= (c[2] + c[4]) / 2 <= hi]
    return "".join(c[0] for c in hit)


def check_course_pdf(course, page_text, chars, page_height, layout=None) -> list:
    rows = []
    if page_text is None:
        return [_row(f"B_{n}", "not_checked", detail="no PDF text for this page") for n in ("code", "title", "units")]
    texts = [pdf_clean(page_text)]
    code = course.get("course_code")
    tier = _found(code, [], texts)
    rows.append(_row("B_code", {"strict": "match", "loose": "loose"}.get(tier, "fail"), _fmt(code), pdf="" if tier == "strict" else _snippet(page_text, code), tier=tier or ""))
    title, raw_title = course.get("course_title"), course.get("title_raw")
    changed = bool(course.get("footnote_marker")) or (raw_title is not None and normalise(raw_title) != normalise(title))
    row = _text_field("B_title", title, None, False, [], texts, "the PDF page text")
    if row["status"] == "fail" and changed and _found(raw_title, [], texts):
        row = _row("B_title", "transformed", _fmt(title), detail=f"stored title not in the PDF, printed {raw_title!r} is")
    row["pdf"] = _snippet(page_text, code, 130) if row["status"] in ("fail", "loose") else ""
    rows.append(row)
    units_raw = normalise((course.get("units") or {}).get("raw"))
    cells = course_roles(course, layout).get("unit", []) if layout is not None else None
    if cells is None:  # no layout given: take the cell whose text is the printed units
        cells = [c for c in (course.get("provenance") or {}).get("source_cells") or [] if normalise(c.get("text")) == units_raw]
    box = next((c["bbox"] for c in cells if c.get("bbox") and normalise(c.get("text")) == units_raw), None) or next((c["bbox"] for c in cells if c.get("bbox")), None)
    if not units_raw or box is None or chars is None or not page_height:
        rows.append(_row("B_units", "not_checked", units_raw, detail="no units cell box, PDF characters or printed units"))
    else:
        got = text_in_box(chars, box, page_height)
        want = re.sub(r"\s", "", units_raw)
        if not got:
            rows.append(_row("B_units", "not_checked", units_raw, detail="no PDF characters inside the units cell box"))
        elif got == want:
            rows.append(_row("B_units", "match", units_raw, pdf=got, tier="strict"))
        elif want in got:
            rows.append(_row("B_units", "loose", units_raw, pdf=got, tier="loose", detail="units cell box also holds other text"))
        else:
            rows.append(_row("B_units", "fail", units_raw, pdf=got, detail="PDF characters at the units cell differ"))
    return rows


# ---------------------------------------------------------------- check C and D

NOT_CODE_WORDS = {"no", "date", "dated", "page", "revision", "effective", "sy", "resolution", "jan", "feb", "mar", "apr",
                  "may", "june", "july", "aug", "sept", "oct", "nov", "dec"}


def _first_token_ok(token: str) -> bool:
    """Reject title tails and header words that merely look like codes ("Design 4", "of 1",
    "Graphics 2", "No 62", "July 2019")."""
    head = re.match(r"[A-Za-z]+", token)
    if not head or token[0].islower() or head.group().lower() in NOT_CODE_WORDS:
        return False
    return head.group().isupper() or len(head.group()) <= 4 or "-" in token or "/" in token


def pdf_candidates(text) -> list:
    """Code-like spans in PDF text: whitespace tokens (edge punctuation trimmed), longest of 3, 2
    or 1 consecutive tokens that the extractor's is_probable_course_code accepts and whose first
    token passes _first_token_ok."""
    tokens = [t.strip(",;:.()[]") for t in pdf_clean(text).split(" ")]
    tokens = [t for t in tokens if t]
    out, i = [], 0
    while i < len(tokens):
        for n in (3, 2, 1):
            span = " ".join(tokens[i:i + n])
            if (len(tokens[i:i + n]) == n and _first_token_ok(tokens[i]) and not re.fullmatch(r"\d/\d", tokens[i + n - 1])
                    and is_probable_course_code(span)):  # a trailing d/d is a units cell, not part of a code
                out.append(span)
                i += n
                break
        else:
            i += 1
    return out


def _key(text) -> str:
    return loose(text).casefold()


def _audit_flagged(audit_block) -> tuple:
    """(flagged cell ids, flagged texts) from the audit's unclaimed candidates and anomalies."""
    ids, texts = set(), []
    for item in (audit_block or {}).get("unclaimed_course_candidates") or []:
        ids.update(item.get("cell_ids") or [])
        texts.append(item.get("code") or "")
    for item in (audit_block or {}).get("structural_anomalies") or []:
        ids.update(item.get("source_cell_ids") or [])
        texts += list(item.get("candidate_codes") or [])
        texts += [c.get("text") or "" for c in item.get("source_cells") or []]
    return ids, texts


def _md_location(key, md: MdDoc | None) -> str:
    if md is None:  # no markup twin available (the verifier works from the JSON alone)
        return "unknown"
    for cid, text in md.cells.items():
        if key in _key(text):
            return f"table_cell:{cid}"
    for iid, text in md.items.items():
        if key in _key(text):
            return f"text_item:{iid}"
    return "absent_from_md"


def check_pdf_missed(courses, audit_block, page_text, md: MdDoc, page_no) -> list:
    """Printed code-like strings on one page that no course's cells account for.

    A candidate occurrence is accounted for when its loose key occurs at least as many times in
    the per-course joined texts (code, title, units, prerequisites, source cell texts) as it has
    occurred so far in the PDF page. Else: flagged if the audit lists it, otherwise silent."""
    pool = []
    for c in courses:
        if (c.get("provenance") or {}).get("page") != page_no:
            continue
        cells = (c.get("provenance") or {}).get("source_cells") or []
        cells = sorted(cells, key=lambda x: [int(n) for n in re.findall(r"\d+", x.get("cell_id", ""))])
        pool.append(_key(" ".join([str(c.get("course_code") or ""), str(c.get("course_title") or ""), str(c.get("prerequisites_raw") or "")] + [x.get("text") or "" for x in cells])))
    _ids, flag_texts = _audit_flagged(audit_block)
    flag_keys = [_key(t) for t in flag_texts if _key(t)]
    seen, rows = Counter(), []
    for span in pdf_candidates(page_text):
        key = _key(span)
        seen[key] += 1
        if sum(p.count(key) for p in pool) >= seen[key]:
            continue
        status = "flagged" if any(key in f or f in key for f in flag_keys) else "silent"
        where = _md_location(key, md)
        rows.append(_row("C", status, span, md=where, pdf=_snippet(page_text, span, 100), detail=f"occurrence {seen[key]} on page {page_no}") | {"page": page_no, "md_location": where, "occurrence": seen[key]})
    return rows


def check_md_unclaimed(courses, audit_block, md: MdDoc) -> list:
    claimed = {i for c in courses for i in (c.get("provenance") or {}).get("source_cell_ids") or []}
    flagged_ids, _texts = _audit_flagged(audit_block)
    rows = []
    for cid, text in md.cells.items():
        value = normalise(text).strip(",;:")
        if cid in claimed or not value or not _first_token_ok(value) or not is_probable_course_code(value):
            continue
        rows.append(_row("D", "flagged" if cid in flagged_ids else "silent", md=normalise(text)) | {"cell": cid})
    return rows


# ---------------------------------------------------------------- whole-file audit

@dataclass
class PdfPage:
    text: str
    chars: list | None = None  # (ch, left, bottom, right, top), y up
    height: float | None = None


def audit_file(payload, md_text, pdf_pages=None) -> dict:
    """All checks for one extractor output. PDF_PAGES: {page_no: PdfPage} or None (B and C not checked)."""
    md = parse_markup(md_text)
    courses = payload.get("courses") or []
    layout = (payload.get("audit") or {}).get("table_layout")
    audit_block = payload.get("audit") or {}
    records = []
    for index, c in enumerate(courses):
        page = (c.get("provenance") or {}).get("page")
        base = {"course_index": index, "course_code": c.get("course_code"), "page": page}
        page_rows = check_course_md(c, md, layout)
        pdf = (pdf_pages or {}).get(page)
        page_rows += check_course_pdf(c, pdf.text if pdf else None, pdf.chars if pdf else None, pdf.height if pdf else None, layout)
        records += [base | r for r in page_rows]
    if pdf_pages:
        for page_no, pdf in sorted(pdf_pages.items()):
            records += [{"course_index": None, "course_code": None, "page": page_no} | r
                        for r in check_pdf_missed(courses, audit_block, pdf.text, md, page_no)]
    records += [{"course_index": None, "course_code": None, "page": None} | r for r in check_md_unclaimed(courses, audit_block, md)]
    evidence_cells = (payload.get("evidence") or {}).get("canonical_cell_count")
    return {
        "records": records,
        "summary": {
            "audit_status": audit_block.get("status"), "courses": len(courses),
            "md_cells": len(md.cells), "evidence_cells": evidence_cells,
            "md_cells_equal_evidence": len(md.cells) == evidence_cells,
        },
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_index(golden: Path) -> dict:
    """Docling JSON path (as the runs recorded it) -> manifest record. The manifest names the
    *_prospectus.json output and writes ' (2)' as ' _2_', so both are normalised to match."""
    records = json.loads((golden / "isolated_manifest.json").read_text(encoding="utf-8"))["records"]
    return {re.sub(r"[()]", "_", r["json_path"]).replace("_prospectus.json", "_docling.json"): r for r in records}


def resolve_pdf(record, pdf_root: Path):
    """(path, sha_ok) for a manifest record; falls back to a same-name search under PDF_ROOT."""
    path = Path(record["source"])
    if not path.exists():
        path = next(iter(pdf_root.rglob(path.name)), path)
    if not path.exists():
        return None, False
    return path, sha256(path) == record["pdf_sha256"]


def load_pdf_pages(path: Path) -> dict:
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(str(path))
    pages = {}
    for number in range(len(pdf)):
        page = pdf[number]
        textpage = page.get_textpage()
        text = textpage.get_text_range()
        chars = []
        for i in range(textpage.count_chars()):
            left, bottom, right, top = textpage.get_charbox(i)
            chars.append((text[i] if i < len(text) else "", left, bottom, right, top))
        pages[number + 1] = PdfPage(text, chars, page.get_size()[1])
        textpage.close()
        page.close()
    pdf.close()
    return pages
