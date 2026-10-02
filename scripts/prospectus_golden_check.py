#!/usr/bin/env python3
"""Phase A gate: old monolith and new package give the same outputs.

For every *_docling.json under GOLDEN the old code runs twice (A, B) and the new
package once (C). Anything that differs between A and B is run-to-run noise
(timestamps, output paths) and is ignored; everything else in C must equal A.

    python scripts/prospectus_golden_check.py GOLDEN WORK [--semantic-doc MAP] [--limit N]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASE = "7591264"
MONOLITH = "backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py"
# Same depth below backend/bintanong_tools as the original, so DATA_ROOT matches.
OLD_COPY = REPO / "backend" / "bintanong_tools" / "_golden_old" / "old_monolith.py"
NEW = ["-m", "backend.bintanong_tools.prospectus_extractor"]


def differing(a, b, path=()):
    """Paths at which two JSON-like values differ."""
    if type(a) is not type(b):
        return {path}
    if isinstance(a, dict):
        out = set()
        for key in set(a) | set(b):
            out |= differing(a.get(key), b.get(key), path + (key,)) if key in a and key in b else {path + (key,)}
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return {path}
        out = set()
        for index, (x, y) in enumerate(zip(a, b)):
            out |= differing(x, y, path + (index,))
        return out
    return set() if a == b else {path}


def load(path: Path):
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix == ".json" else text.splitlines()


def run(entry: list[str], source: Path, out_dir: Path, extra: list[str]) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8")
    command = [sys.executable, *entry, "-i", str(source), "-o", str(out_dir / "candidate.json"),
               "--export-all", "--device", "cpu", *extra]
    return subprocess.run(command, cwd=REPO, env=env, capture_output=True).returncode


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("golden", type=Path)
    cli.add_argument("work", type=Path)
    cli.add_argument("--semantic-doc", type=Path)
    cli.add_argument("--limit", type=int)
    args = cli.parse_args()

    OLD_COPY.parent.mkdir(parents=True, exist_ok=True)
    OLD_COPY.write_bytes(subprocess.run(["git", "show", f"{BASE}:{MONOLITH}"], cwd=REPO,
                                        check=True, capture_output=True).stdout)
    extra = ["--semantic-doc", str(args.semantic_doc)] if args.semantic_doc else ["--no-semantic-doc"]
    sources = sorted(args.golden.rglob("*_docling.json"))[: args.limit]
    if not sources:
        cli.error(f"no *_docling.json under {args.golden}")

    failures = 0
    for number, source in enumerate(sources, 1):
        dirs = {tag: args.work / f"{number:02d}" / tag for tag in "ABC"}
        codes = {
            "A": run([str(OLD_COPY)], source, dirs["A"], extra),
            "B": run([str(OLD_COPY)], source, dirs["B"], extra),
            "C": run(NEW, source, dirs["C"], extra),
        }
        problems = []
        if codes["A"] != codes["C"]:
            problems.append(f"exit old={codes['A']} new={codes['C']}")
        names = {tag: sorted(p.name for p in dirs[tag].iterdir()) for tag in "ABC"}
        if names["A"] != names["C"]:
            problems.append(f"files old={names['A']} new={names['C']}")
        noise_total = 0
        for name in names["A"]:
            if name not in names["C"] or name not in names["B"]:
                continue
            a, b, c = (load(dirs[tag] / name) for tag in "ABC")
            noise = differing(a, b)
            noise_total += len(noise)
            real = [p for p in differing(a, c) if not any(p[: len(n)] == n for n in noise)]
            if real:
                problems.append(f"{name}: {len(real)} differing paths, first {sorted(map(str, real))[:5]}")
        failures += bool(problems)
        print(f"{number}/{len(sources)} {'FAIL' if problems else 'ok'} exit={codes['A']} "
              f"noise={noise_total} {source.name}", flush=True)
        for problem in problems:
            print(f"    {problem}", flush=True)
    print(f"{len(sources) - failures}/{len(sources)} identical")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
