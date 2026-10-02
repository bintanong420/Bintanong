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


def find_default_output_root() -> Path:
    return (Path(__file__).resolve().parent / "docling_jsonified_output").resolve()
