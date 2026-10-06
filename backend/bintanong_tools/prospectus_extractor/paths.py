"""Default input and output locations."""

from __future__ import annotations

from pathlib import Path


DATA_ROOT = Path(__file__).resolve().parent.parent


SOURCE_PDF_ROOT = DATA_ROOT / "PalSU Undergraduate Prospectus Website Dump"


DEFAULT_SEMANTIC_DOC = (
    DATA_ROOT
    / "PalSU Undergraduate Prospectus Website Dump"
    / "Tiniguiban - Main"
    / "palsu_main_undergrad_program_college_meaning.md"
)


DEFAULT_TARGET_PDF = (
    SOURCE_PDF_ROOT
    / "Tiniguiban - Main"
    / "CS"
    / "Computer Science"
    / "New Curriculum (2025-2026)"
    / "1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025.pdf"
)


def find_default_input_root() -> Path:
    return SOURCE_PDF_ROOT.resolve()


# The longest real artifact adds 216 characters to the root; Windows paths must stay under 260.
MAX_DEFAULT_ROOT_CHARS = 40


def find_default_output_root() -> Path:
    """~/Bintanong/output, or <drive>/Bintanong/output when the home path would make paths too long."""
    root = Path.home() / "Bintanong" / "output"
    if len(str(root)) <= MAX_DEFAULT_ROOT_CHARS:
        return root
    return Path(root.anchor) / "Bintanong" / "output"
