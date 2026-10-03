#!/usr/bin/env python3
"""Course-level audit of prospectus extractor output across JSON, markup (.md) and the source PDF.

    python scripts/prospectus_course_audit.py --runs RUNS --golden GOLDEN --out OUT [--pdf-root DIR] [--limit N]

RUNS holds NN/ folders, each with source.txt (the cached Docling JSON the run read),
candidate.json and candidate_prospectus.md. GOLDEN holds isolated_manifest.json (source PDF path
and SHA-256 per input). It only measures: no extractor behaviour or course value is changed.

Checks, per course unless noted (status values: match, loose, transformed, fail, empty,
not_checked; C and D use silent / flagged):
  A  JSON -> MD   A_prov every provenance cell id is in the .md; A_code A_title A_lecture A_lab
                  A_total A_prereq: the field value is in the text of the course's .md cells.
  B  JSON -> PDF  B_code B_title in the page text layer; B_units: the PDF characters inside the
                  units cell's box read as the units string (else not_checked).
  C  PDF -> JSON  (per printed candidate) code-like strings in the PDF text that no course's
                  cells account for: silent, or flagged when the audit lists them.
  D  MD -> JSON   (per cell) code-like .md cells that no course claims: silent, or flagged.

Normalisation (strict tier): Unicode NFC, then every whitespace run becomes one space, then trim.
PDF text additionally maps U+FFFE and U+00AD (pdfium's hyphen artefacts) to "-" and "" before that.
Loose tier (reported apart from match): strict form with all whitespace and hyphen/dash
characters removed, so line-wrap and hyphenation differences are ignored. Case is never folded
for A and B. "transformed" means the parser changed the value on purpose (title with footnote
marker stripped; units parsed or derived from the printed units string) and the printed source
text was found; it is neither a match nor an error.

Reuse for OCR output: call audit_file(payload, md_text, pdf_pages) with pdf_pages =
{page_no: PdfPage(text, chars, height)} from any source (pdfium, an OCR engine, a fixture).
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

# The checks live in the package so the year/semester verifier reuses them; the names below are
# re-exported so this script and its tests keep one import surface.
from backend.bintanong_tools.prospectus_extractor.course_checks import (  # noqa: E402,F401
    DASHES, MdDoc, PdfPage, audit_file, check_course_md, check_course_pdf, check_md_unclaimed,
    check_pdf_missed, course_roles, load_pdf_pages, loose, manifest_index, normalise, parse_markup,
    pdf_candidates, pdf_clean, resolve_pdf, sha256, text_in_box,
)

DEFAULT_PDF_ROOT = Path(r"E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump")


def run_all(runs: Path, golden: Path, pdf_root: Path, limit=None):
    index = manifest_index(golden)
    files, pdf_cache = [], {}
    for folder in sorted(p for p in runs.iterdir() if p.is_dir() and (p / "candidate.json").exists()):
        if limit and len(files) >= limit:
            break
        source = (folder / "source.txt").read_text(encoding="utf-8").strip()
        record = index.get(re.sub(r"[()]", "_", source))
        info = {"n": folder.name, "input": source, "pdf": None, "pdf_sha256": None, "pdf_sha_ok": False, "unmapped": None}
        pages = None
        if record is None:
            info["unmapped"] = "input not in manifest"
        else:
            path, ok = resolve_pdf(record, pdf_root)
            if path is None:
                info["unmapped"] = "PDF file not found"
            else:
                info.update(pdf=str(path), pdf_sha256=record["pdf_sha256"], pdf_sha_ok=ok)
                if not ok:
                    info["unmapped"] = "PDF SHA-256 differs from manifest"
                else:
                    pages = pdf_cache.get(path) or pdf_cache.setdefault(path, load_pdf_pages(path))
        payload = json.loads((folder / "candidate.json").read_text(encoding="utf-8"))
        md_text = (folder / "candidate_prospectus.md").read_text(encoding="utf-8")
        result = audit_file(payload, md_text, pages)
        info["pdf_page_sizes"] = {p: v.height for p, v in (pages or {}).items()}
        files.append({"info": info, "summary": result["summary"], "records": result["records"]})
    return files


# ---------------------------------------------------------------- reporting

CHECKS = ["A_prov", "A_code", "A_title", "A_lecture", "A_lab", "A_total", "A_prereq", "B_code", "B_title", "B_units", "C", "D"]


def tally(files):
    table = {c: Counter() for c in CHECKS}
    for f in files:
        for r in f["records"]:
            table[r["check"]][r["status"]] += 1
    return table


def distinct(files):
    seen, out = set(), []
    for f in files:
        key = f["info"]["pdf_sha256"] or f["info"]["input"]
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def _tally_table(title, files):
    t = tally(files)
    statuses = ["match", "loose", "transformed", "fail", "empty", "not_checked", "silent", "flagged"]
    lines = [f"### {title}", "", "| check | total | " + " | ".join(statuses) + " |", "|---|---|" + "---|" * len(statuses)]
    for c in CHECKS:
        total = sum(t[c].values())
        lines.append(f"| {c} | {total} | " + " | ".join(str(t[c].get(s, 0) or "") for s in statuses) + " |")
    return "\n".join(lines)


def _cell(text, n=70) -> str:
    return normalise(text).replace("|", "\\|")[:n]


def write_reports(files, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    with (out / "course_audit.jsonl").open("w", encoding="utf-8") as fh:
        for f in files:
            i = f["info"]
            fh.write(json.dumps({"check": "file", "n": i["n"], "pdf": i["pdf"], "pdf_sha256": i["pdf_sha256"], "unmapped": i["unmapped"], **f["summary"]}, ensure_ascii=False) + "\n")
            for r in f["records"]:
                fh.write(json.dumps({"n": i["n"], "pdf_sha256": i["pdf_sha256"]} | r, ensure_ascii=False) + "\n")
    uniq = distinct(files)
    L = ["# Course-level audit (JSON, markup, PDF)", "",
         f"Inputs: {len(files)} paths, {len(uniq)} distinct PDFs (by SHA-256). Unmapped inputs: "
         + (", ".join(f"{f['info']['n']} ({f['info']['unmapped']})" for f in files if f["info"]["unmapped"]) or "none") + ".", "",
         _tally_table(f"All {len(files)} paths", files), "", _tally_table(f"{len(uniq)} distinct PDFs", uniq), "",
         "A* rows: strict = value in the .md cell text; loose = only ignoring spaces/hyphens; transformed = parser changed the value, printed text found; fail = value not in the course's cells. "
         "B* rows: same against the PDF text layer (B_units reads the PDF characters at the units cell). C: printed code-like strings no course accounts for (silent unless the audit lists them). D: code-like .md cells no course claims.", "",
         "## Per file", "", "| n | pdf | audit | courses | md=evidence cells | A fail | B fail | C silent | C flagged | D silent | D flagged |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for f in files:
        c = Counter((r["check"][0], r["status"]) for r in f["records"])
        s, i = f["summary"], f["info"]
        L.append(f"| {i['n']} | {Path(i['pdf']).name if i['pdf'] else '-'} | {s['audit_status']} | {s['courses']} | {s['md_cells']}/{s['evidence_cells']}{'' if s['md_cells_equal_evidence'] else ' DIFF'} | "
                 f"{c[('A', 'fail')]} | {c[('B', 'fail')]} | {c[('C', 'silent')]} | {c[('C', 'flagged')]} | {c[('D', 'silent')]} | {c[('D', 'flagged')]} |")
    L += ["", "## Examples per category (first 3 each, distinct PDFs)", ""]
    for check in CHECKS:
        for status in ("match", "loose", "transformed", "fail", "not_checked", "silent", "flagged"):
            ex = [(f, r) for f in uniq for r in f["records"] if r["check"] == check and r["status"] == status][:3]
            for f, r in ex:
                L.append(f"- {check}/{status} file {f['info']['n']} p{r.get('page')} {r.get('course_code') or r.get('cell') or ''}: json={_cell(r['json'], 60)!r} md={_cell(r['md'], 60)!r} pdf={_cell(r['pdf'], 60)!r} {_cell(r['detail'], 80)}")
    L += ["", "## Silent problems (distinct PDFs): A/B failures and C/D silent", "",
          "| file | page | code | check | JSON value | MD cell text | PDF snippet |", "|---|---|---|---|---|---|---|"]
    for f in uniq:
        for r in f["records"]:
            if r["status"] == "fail" or (r["check"] in ("C", "D") and r["status"] == "silent"):
                L.append(f"| {f['info']['n']} | {r.get('page') or ''} | {_cell(r.get('course_code') or r.get('cell') or '', 20)} | {r['check']} | {_cell(r['json'], 50)} | {_cell(r['md'], 60)} | {_cell(r['pdf'], 70)} |")
    (out / "course_audit_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", required=True, type=Path)
    ap.add_argument("--golden", required=True, type=Path)
    ap.add_argument("--pdf-root", type=Path, default=DEFAULT_PDF_ROOT)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args(argv)
    files = run_all(args.runs, args.golden, args.pdf_root, args.limit)
    write_reports(files, args.out)
    t = tally(files)
    for c in CHECKS:
        print(c, dict(t[c]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
