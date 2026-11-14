#!/usr/bin/env python3
"""Download the RapidOCR models of the bake-off's RapidOCR configs ahead of time, and record their SHA-256.

    python scripts/fetch_rapidocr_models.py [--manifest PATH]

RapidOCR fetches a model from ModelScope the first time an engine is built and checks it against the
SHA-256 listed in its own `default_models.yaml`. Building each RapidOCR config once here (CPU, no
inference) puts every model on disk, so a Docker image or a CI cache can run offline. The hashes of
the files actually present are printed and, with --manifest, written as JSON (LF) for the decision
record. Exit 0 when at least one model is present, 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.bintanong_tools.ocr_bench import engines  # noqa: E402


def models_dir() -> Path:
    import rapidocr

    return Path(rapidocr.__file__).parent / "models"


def build_engine(config) -> None:
    engines._rapidocr_engine(config, False)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(build, folder: Path) -> dict:
    for config in engines.GRID:
        if config.engine == "rapidocr":
            build(config)
    return {p.name: _sha256(p) for p in sorted(Path(folder).glob("*.onnx"))}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args(argv)
    hashes = fetch(build_engine, models_dir())
    for name, digest in hashes.items():
        print(f"{digest}  {name}")
    if args.manifest:
        args.manifest.write_bytes((json.dumps(hashes, indent=2) + "\n").encode("utf-8"))
    return 0 if hashes else 1


if __name__ == "__main__":
    raise SystemExit(main())
