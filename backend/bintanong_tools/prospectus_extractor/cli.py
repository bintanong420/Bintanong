"""Command-line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence
import argparse
import sys

from .paths import DEFAULT_SEMANTIC_DOC, DEFAULT_TARGET_PDF, find_default_output_root
from .loader import dump_grid, load_document
from .pipeline import process_prospectus
from .batch import BatchConfig, run_batch
from .selftest import run_self_tests
from .tui import ProspectusTUI


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PalSU prospectus extractor: Docling -> audited JSON, Prolog and RAG corpus.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s --self-test\n"
            "  %(prog)s -i prospectus.pdf --export-pl --export-csv --export-jsonl\n"
            "  %(prog)s -i prospectus_docling.json --dump-grid\n"
            "  %(prog)s -i \"D:/dump/Tiniguiban - Main\" --batch --strict\n"
        ),
    )
    parser.add_argument("-i", "--input", type=Path, default=None, help="PDF, *_docling.json, or folder")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output JSON path (or batch root)")
    parser.add_argument("--tui", action="store_true", help="Launch the interactive menu")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in regression suite")
    parser.add_argument("--dump-grid", action="store_true", help="Print the reconstructed table grid and exit")
    parser.add_argument("--device", choices=["auto", "cuda", "cpu"], default="auto")
    parser.add_argument("--export-pl", action="store_true", help="Also write the Prolog knowledge base")
    parser.add_argument("--export-jsonl", action="store_true", help="Also write the RAG JSONL corpus")
    parser.add_argument("--export-csv", action="store_true", help="Also write the review CSV")
    parser.add_argument("--export-all", action="store_true", help="Write .pl, .jsonl and .csv companions")
    parser.add_argument("--batch", action="store_true", help="Treat the input as a folder")
    parser.add_argument("--pattern", action="append", default=None, help="Glob for batch mode (repeatable)")
    parser.add_argument("--skip-existing", action="store_true", help="Batch: skip files already extracted")
    parser.add_argument("--force", action="store_true", help="Process PDFs even with --skip-existing")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when the audit reports an error")
    parser.add_argument(
        "--semantic-doc",
        type=Path,
        default=DEFAULT_SEMANTIC_DOC,
        help="College/program reference markdown",
    )
    parser.add_argument("--no-semantic-doc", action="store_true", help="Ignore the semantic reference map")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_cli()
    args = parser.parse_args(argv)

    if args.self_test:
        return 1 if run_self_tests() else 0

    if args.tui or (args.input is None and len(sys.argv) == 1):
        tui = ProspectusTUI()
        tui.config.device = args.device
        if args.no_semantic_doc:
            tui.config.semantic_doc = None
        tui.main_menu()
        return 0

    semantic_doc = None if args.no_semantic_doc else args.semantic_doc
    export_pl = args.export_pl or args.export_all
    export_jsonl = args.export_jsonl or args.export_all
    export_csv = args.export_csv or args.export_all

    input_path: Path = args.input or DEFAULT_TARGET_PDF

    if args.dump_grid:
        output_dir = Path(args.output).parent if args.output else find_default_output_root()
        document, _ = load_document(
            input_path, device=args.device, force_reconvert=True,
            raw_json_path=output_dir / f"{Path(input_path).stem}_docling.json",
        )
        text = dump_grid(document)
        print(text)
        out_path = Path(args.output) if args.output else output_dir / f"{Path(input_path).stem}_grid_dump.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"[+] Grid dump -> {out_path}")
        return 0

    if args.batch or input_path.is_dir():
        config = BatchConfig(
            input_root=input_path,
            output_root=args.output or find_default_output_root(),
            write_pl=export_pl,
            write_jsonl=export_jsonl,
            write_csv=export_csv,
            skip_existing=args.skip_existing,
            force_reconvert=args.force,
            device=args.device,
            strict=args.strict,
            semantic_doc=semantic_doc,
            include_patterns=args.pattern or ["*.pdf"],
        )
        summary = run_batch(config)
        print(
            f"[*] Batch: {summary['succeeded']} extracted, {summary['audit_failed']} failed audit, "
            f"{summary['skipped']} skipped, {summary['failed']} errored."
        )
        if summary.get("manifest_path"):
            print(f"[*] Manifest: {summary['manifest_path']}")
        if args.strict and (summary["failed"] or summary["audit_failed"]):
            return 1
        return 0 if summary["succeeded"] or summary["skipped"] else 1

    payload = process_prospectus(
        input_path,
        output_path=args.output,
        export_pl=export_pl,
        export_jsonl=export_jsonl,
        export_csv=export_csv,
        device=args.device,
        semantic_doc_path=semantic_doc,
        force_reconvert=True,
    )
    if args.strict and payload["audit"]["status"] == "error":
        return 1
    return 0
