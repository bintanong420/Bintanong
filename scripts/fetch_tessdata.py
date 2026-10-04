#!/usr/bin/env python3
"""Fetch and verify the pinned Tesseract models (Q13) into a folder outside Git.

    python scripts/fetch_tessdata.py [--dest DIR] [--check]

Downloads `fil` and `eng` from tessdata_best at one pinned commit, checks SHA-256, and prints the
`TESSDATA_PREFIX` to set. Nothing unverified is ever left in DEST. Default DEST is a per-user data
folder (never inside the repository): %LOCALAPPDATA%\\bintanong\\tessdata on Windows,
~/Library/Application Support/bintanong/tessdata on macOS, $XDG_DATA_HOME or ~/.local/share
/bintanong/tessdata elsewhere. Exit codes: 0 ok, 1 --check found a missing or corrupt file or a
download failed verification, 2 download error.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BEST = "https://github.com/tesseract-ocr/tessdata_best/raw/e2aad9b983032bb1beff9133104a67cdbb87ca4d"  # tag 4.1.0
MODELS = {
    "fil.traineddata": (f"{BEST}/fil.traineddata", "04a7d20dcd2e1869375cbf47b59d8ed4ceea98c7f01706269eced3945b763647"),
    "eng.traineddata": (f"{BEST}/eng.traineddata", "8280aed0782fe27257a68ea10fe7ef324ca0f8d85bd2fd145d1c2b560bcb66ba"),
}


class HashMismatch(RuntimeError):
    pass


def default_dest() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "bintanong" / "tessdata"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check(dest: Path, models=None) -> dict:
    """name -> ok | missing | corrupt, without downloading."""
    result = {}
    for name, (_url, digest) in (models or MODELS).items():
        path = Path(dest) / name
        result[name] = "missing" if not path.exists() else "ok" if _sha256(path) == digest else "corrupt"
    return result


def fetch(dest: Path, models=None) -> dict:
    """Download each model not already present and correct; name -> present | downloaded."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    status = {}
    for name, (url, digest) in (models or MODELS).items():
        target = dest / name
        if target.exists() and _sha256(target) == digest:
            status[name] = "present"
            continue
        part = dest / f"{name}.part"
        try:
            with urllib.request.urlopen(url, timeout=120) as response, part.open("wb") as out:
                for block in iter(lambda: response.read(1 << 20), b""):
                    out.write(block)
            if _sha256(part) != digest:
                raise HashMismatch(f"{name}: downloaded file does not match the pinned SHA-256 {digest}")
            part.replace(target)
        finally:
            part.unlink(missing_ok=True)
        status[name] = "downloaded"
    return status


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dest", type=Path, default=default_dest())
    parser.add_argument("--check", action="store_true", help="only verify what is there")
    args = parser.parse_args(argv)
    if args.check:
        result = check(args.dest)
    else:
        try:
            result = fetch(args.dest)
        except (HashMismatch, OSError) as error:
            print(f"failed: {error}", file=sys.stderr)
            return 1 if isinstance(error, HashMismatch) else 2
    for name, state in result.items():
        print(f"{name}: {state}")
    print(f"set TESSDATA_PREFIX={args.dest}")
    return 0 if all(s in ("ok", "present", "downloaded") for s in result.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
