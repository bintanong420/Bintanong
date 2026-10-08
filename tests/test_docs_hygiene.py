"""Control characters in plans, decision records and knowledge manifests.

A backslash escape that reached a shell or an editor unescaped turns "\\t", "\\b", "\\f" or "\\r" into
a real control character and eats the letter after it (a path then reads "ests/..." or "ackend/...").
Only LF, a CR directly before LF, and a TAB inside a fenced code block are legitimate.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCANNED = [ROOT / "plans", ROOT / "docs" / "decisions", ROOT / "knowledge"]
SUFFIXES = {".md", ".json", ".txt"}
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def control_character_report(text: str, suffix: str = ".md") -> list[str]:
    """Return one entry per offending control character: 'line N: U+00XX'."""
    found, in_fence = [], False
    for number, line in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
        if suffix == ".md" and line.lstrip().startswith("```"):
            in_fence = not in_fence
        found += [f"line {number}: U+{ord(c):04X}" for c in CONTROL.findall(line)]
        found += [f"line {number}: U+0009" for _ in re.findall(r"\t", line) if not in_fence]
        found += [f"line {number}: U+000D" for _ in re.findall(r"\r", line)]
    return found


def _files():
    return sorted(p for base in SCANNED for p in base.rglob("*") if p.is_file() and p.suffix in SUFFIXES)


def test_scan_covers_the_governed_directories():
    assert any(p.name == "phase-01-checkpoint.md" for p in _files())
    assert any(p.name == "governance-vocabulary.json" for p in _files())
    assert any(p.parent.name == "decisions" for p in _files())


@pytest.mark.parametrize("path", _files(), ids=lambda p: p.relative_to(ROOT).as_posix())
def test_no_control_characters(path):
    text = path.read_bytes().decode("utf-8")
    assert control_character_report(text, path.suffix) == []


@pytest.mark.parametrize("text,count", [
    ("fine\nline\r\nnext\n", 0),
    ("a\tb\n", 1),
    ("```\na\tb\n```\n", 0),
    ("```\n```\na\tb\n", 1),
    ("x\x08ackend/\n", 1),
    ("x\x0cixer\n", 1),
    ("lone\rcr\n", 1),
    ("nul\x00\n", 1),
])
def test_the_scanner_itself_catches_what_it_should(text, count):
    assert len(control_character_report(text)) == count
