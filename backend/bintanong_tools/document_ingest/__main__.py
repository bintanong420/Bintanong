"""Explicit single-document candidate ingestion; see --help."""
from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path

from .procedure_text import CLASSIFICATIONS


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Convert one registered document to pending candidate chunks and a report.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--root", type=Path, required=True, help="Explicit input root")
    parser.add_argument("--out", type=Path, required=True, help="New/empty external output folder")
    parser.add_argument("--locator", required=True, help="Logical acquisition locator, never a local path")
    parser.add_argument("--classification", required=True, choices=sorted(CLASSIFICATIONS | {"prospectus_candidate"}))
    args = parser.parse_args(argv)
    from ..prospectus_extractor.identity import InputSnapshot
    from .pipeline import run_ingestion
    from .register import pending_version
    from .bundle import load_candidate_bundle
    try:
        snapshot = InputSnapshot(args.path)
        version = pending_version(snapshot, args.locator)
        with contextlib.redirect_stdout(sys.stderr):
            if args.classification == "prospectus_candidate":
                from .prospectus import run_prospectus_ingestion
                run_prospectus_ingestion(snapshot, [version], input_root=args.root, out=args.out)
            else:
                run_ingestion(snapshot, [version], input_root=args.root, out=args.out,
                              classification=args.classification)
            report = load_candidate_bundle(args.out)["report"]
    except (ValueError, OSError, RuntimeError, ImportError) as exc:
        print(f"Ingestion incomplete: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"candidate_only": True, "accounting_complete": report["accounting_complete"],
                      "counts": report["counts"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
