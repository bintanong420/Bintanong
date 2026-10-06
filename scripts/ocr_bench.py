#!/usr/bin/env python3
"""OCR measurement driver (plans/2026-10-04-prospectus-ocr-measurement.md).

    python scripts/ocr_bench.py simulate --pdf-dir PDFS --out OUT [--seed N] [--conditions a,b] [--dpi 150] [--pages 1,2] [--max-pdfs N]
    python scripts/ocr_bench.py ocr --list
    python scripts/ocr_bench.py ocr --config tesseract-fil --images DIR --out DIR
    python scripts/ocr_bench.py score --reference DIR --candidate DIR --out DIR

`simulate` renders every PDF under PDFS and writes seeded phone-photo JPEGs plus
simulate_manifest.json. `ocr` runs one configuration of the grid; it exits 3 with "engine not
installed" until an engine and its adapter exist. `score` pairs <name>.json files in the reference
and candidate folders and writes ocr_score.json and ocr_score.md (LF). Exit codes: 0 ok or supported,
1 not supported, 2 bad usage, 3 engine not installed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.bintanong_tools.ocr_bench import engines, score, simulate  # noqa: E402

DEFAULT_SEED = 20261004


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))  # LF on every OS


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_simulate(args) -> int:
    names = [n for n in args.conditions.split(",") if n] if args.conditions else sorted(simulate.CONDITIONS)
    unknown = [n for n in names if n not in simulate.CONDITIONS]
    if unknown:
        print(f"unknown condition(s): {', '.join(unknown)}; use {', '.join(sorted(simulate.CONDITIONS))}", file=sys.stderr)
        return 2
    pages = [int(p) for p in args.pages.split(",")] if args.pages else None
    pdfs = sorted(Path(args.pdf_dir).rglob("*.pdf"))
    if args.max_pdfs:
        pdfs = pdfs[: args.max_pdfs]
    if not pdfs:
        print(f"no PDFs under {args.pdf_dir}", file=sys.stderr)
        return 2
    out = Path(args.out)
    images = []
    for pdf in pdfs:
        for path in simulate.simulate_pdf(pdf, out, names, seed=args.seed, dpi=args.dpi, pages=pages):
            images.append({"image": path.name, "source_pdf": pdf.name})
    manifest = {"seed": args.seed, "dpi": args.dpi, "conditions": names, "images": images}
    _write_text(out / "simulate_manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(images)} image(s) from {len(pdfs)} PDF(s) to {out}")
    return 0


def cmd_ocr(args) -> int:
    if args.list:
        for config in engines.GRID:
            ok, reason = engines.availability(config)
            print(f"{config.id:20} {'available' if ok else 'unavailable'}: {reason}")
        return 0
    config = engines.find_config(args.config or "")
    if config is None:
        print(f"unknown config {args.config!r}; use one of {', '.join(c.id for c in engines.GRID)}", file=sys.stderr)
        return 2
    ok, reason = engines.availability(config)
    if not ok:
        print(f"engine not installed for {config.id}: {reason}", file=sys.stderr)
        return 3
    try:
        engines.run_ocr(config, Path(args.images), Path(args.out))
    except engines.EngineNotInstalled as error:
        print(str(error), file=sys.stderr)
        return 3
    return 0


def render_markdown(report: dict) -> str:
    corpus = report["corpus"]
    verdict = corpus["verdict"]
    lines = ["# OCR score", "", f"Verdict: {'SUPPORTED' if verdict['supported'] else 'NOT SUPPORTED'}", ""]
    for name, ok in verdict.get("criteria", {}).items():
        lines.append(f"- {name}: {'pass' if ok else 'FAIL'}")
    lines += [""] + [f"- {f}" for f in verdict["failures"]]
    worst = corpus.get("worst_document")
    lines += ["", f"Documents: {corpus['documents']}. Critical fields exact: {corpus['critical']['exact']}/{corpus['critical']['total']}"
              f" ({corpus['critical']['rate']:.2%}).",
              f"Worst document CER: {worst['cer']:.2%} ({worst['name']})." if worst else "", "",
              "| document | missing | invented | critical exact | CER | silent | supported |", "|---|---|---|---|---|---|---|"]
    for name, r in report["documents"].items():
        lines.append(f"| {name} | {len(r['missing'])} | {len(r['invented'])} | {r['critical']['rate']:.2%} | "
                     f"{r['cer']['rate']:.2%} | {r['silent_critical']} | {'yes' if r['verdict']['supported'] else 'no'} |")
    for name, r in report["documents"].items():
        if r["disagreements"]:
            lines += ["", f"## {name}: disagreements", ""]
            lines += [f"- {d['kind']} {d['code']} {d['field']}: reference {d['reference']!r}, candidate {d['candidate']!r}"
                      f"{' (SILENT)' if d['silent'] else ' (flagged)'}" for d in r["disagreements"]]
    return "\n".join(lines) + "\n"


def cmd_score(args) -> int:
    ref_dir, cand_dir, out = Path(args.reference), Path(args.candidate), Path(args.out)
    refs = sorted(ref_dir.glob("*.json"))
    if not refs:
        print(f"no reference *.json in {ref_dir}", file=sys.stderr)
        return 2
    documents = {}
    for ref_path in refs:
        cand_path = cand_dir / ref_path.name
        candidate = _load(cand_path) if cand_path.exists() else {"courses": [], "audit": {}}
        documents[ref_path.stem] = score.score_document(_load(ref_path), candidate, name=ref_path.stem)
        if not cand_path.exists():
            documents[ref_path.stem]["note"] = "no candidate file; every reference course counts as missing"
    report = {"corpus": score.score_corpus(documents), "documents": documents}
    _write_text(out / "ocr_score.json", json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    _write_text(out / "ocr_score.md", render_markdown(report))
    print(f"{'SUPPORTED' if report['corpus']['verdict']['supported'] else 'NOT SUPPORTED'}: "
          f"{'; '.join(report['corpus']['verdict']['failures']) or 'all four Q11 criteria pass'} -> {out}")
    return 0 if report["corpus"]["verdict"]["supported"] else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("simulate")
    s.add_argument("--pdf-dir", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--seed", type=int, default=DEFAULT_SEED)
    s.add_argument("--conditions", default="")
    s.add_argument("--dpi", type=int, default=150)
    s.add_argument("--pages", default="")
    s.add_argument("--max-pdfs", type=int, default=0)
    o = sub.add_parser("ocr")
    o.add_argument("--list", action="store_true")
    o.add_argument("--config")
    o.add_argument("--images")
    o.add_argument("--out")
    c = sub.add_parser("score")
    c.add_argument("--reference", required=True)
    c.add_argument("--candidate", required=True)
    c.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    return {"simulate": cmd_simulate, "ocr": cmd_ocr, "score": cmd_score}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
