"""Phase A gate: the package is a 1:1 move of the monolith at BASE.

Every top-level definition of the old file must exist, AST-identical, in exactly
one package module, and the package must define nothing else. Delete this test
when Phase B starts changing behavior.
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BASE = "7591264"
MONOLITH = "backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py"
PACKAGE = REPO / "backend" / "bintanong_tools" / "prospectus_extractor"
HAND_WRITTEN = {"__init__.py", "__main__.py"}
# Definitions whose body was changed on purpose. Each one is explained in
# docs/decisions/prospectus-extractor-package.md.
DEVIATIONS = {"ensure_docling_env"}


def _definitions(source: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names = [node.name]
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names = [node.target.id]
        elif isinstance(node, ast.Try):
            names = ["<optional-rich-import>"]
        else:
            continue  # imports, docstring, `if` guards
        for name in names:
            found.setdefault(name, []).append(ast.dump(node))
    return found


def _monolith() -> dict[str, list[str]]:
    shown = subprocess.run(
        ["git", "show", f"{BASE}:{MONOLITH}"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
    )
    if shown.returncode != 0:
        pytest.skip(f"git cannot show {BASE}: {shown.stderr.strip()}")
    return _definitions(shown.stdout)


def _package() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for path in sorted(PACKAGE.glob("*.py")):
        if path.name in HAND_WRITTEN:
            continue
        for name, dumps in _definitions(path.read_text(encoding="utf-8")).items():
            found.setdefault(name, []).extend(dumps)
    return found


def test_every_definition_moved_unchanged():
    old, new = _monolith(), _package()
    assert sorted(old) == sorted(new), {
        "missing": sorted(set(old) - set(new)),
        "extra": sorted(set(new) - set(old)),
    }
    changed = [
        name for name in old
        if name not in DEVIATIONS and sorted(old[name]) != sorted(new[name])
    ]
    assert changed == []


def test_deviations_are_real():
    old, new = _monolith(), _package()
    assert [name for name in DEVIATIONS if old[name] == new[name]] == []
