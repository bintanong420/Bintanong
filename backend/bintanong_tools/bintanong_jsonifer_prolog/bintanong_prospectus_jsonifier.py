#!/usr/bin/env python3
"""
PalSU Prospectus Extractor  (v3.0)
==================================
Extracts structured curricula from PalSU prospectus PDFs (via Docling) or from
previously-saved raw Docling JSON, producing:

  1. Raw Docling JSON            <stem>_docling.json   (PDF input only)
  2. Enriched prospectus JSON    <stem>_prospectus.json
       - document metadata (college / program / degree / SY / governance)
       - course catalog with year + semester, lecture/lab units,
         footnote-cleaned titles, RESOLVED prerequisites
       - elective pools linked to the curriculum rows that consume them
       - Prolog knowledge base (facts + query rules)
       - hybrid RAG chunks (semantic advising chunks + Docling layout chunks)
       - an AUDIT that fails loudly instead of emitting plausible garbage
  3. Optional companions:  .pl (Prolog), _rag.jsonl (RAG corpus),
     _review.csv (human review), batch_manifest.json

Why v3 exists
-------------
Earlier versions flattened Docling tables into string grids. A merged year
banner therefore became many copied strings, source topology was lost, and a
mutable parser state could silently assign later courses to the wrong term.

v3 makes evidence and trust boundaries explicit:

  * raw Docling ``table_cells`` become immutable ``NormalizedCell`` objects;
    merged cells retain their row/column spans and page boxes;
  * live PDF conversion and cached Docling JSON use the same evidence adapter;
  * structural tokens and explicit ``CurriculumSection`` objects replace year
    and semester defaults;
  * adjacent-cell reconstruction supports wrapped and shifted course rows;
  * a document-wide source-code inventory detects valid courses the parser did
    not claim;
  * every course carries source-cell provenance suitable for audit/highlight;
  * optional semantic repair receives only anomaly windows, must cite evidence,
    and is rejected unless deterministic validation proves it grounded;
  * an ERROR audit produces review JSON/CSV but zero production Prolog or RAG.

Compatibility
-------------
``LoadedDocument`` remains an alias of ``ProspectusEvidence`` and
``parse_curriculum_grids`` is a compatibility adapter. The canonical API is
``evidence_adapter`` plus ``parse_curriculum_evidence``. Existing batch, TUI,
metadata, prerequisite, elective, Prolog and RAG interfaces remain available.

Usage
-----
  python palsu_prospectus_extractor.py --self-test
  python palsu_prospectus_extractor.py -i prospectus.pdf --export-pl --export-csv
  python palsu_prospectus_extractor.py -i prospectus_docling.json --dump-grid
  python palsu_prospectus_extractor.py --tui
  python palsu_prospectus_extractor.py -i "C:/dump/Tiniguiban - Main" --batch --strict

Remember, this is a command-line tool, but it has not been adjusted to work with this codebase yet, so you will need to run it from the Windows command line environment with the appropriate arguments. 
The tool is designed to extract structured curricula from PalSU prospectus PDFs or previously-saved raw Docling JSON, producing various output files including enriched prospectus JSON, Prolog knowledge base, and RAG corpus.

Limitations:
The code hasn't been adjusted to work with the greater Bintanong codebase yet, so you will need to run it from the Windows command line environment with the appropriate arguments.
However, when run from Windows, it should also ask you for the path to the PDF or JSON file you want to process, and it will generate the output files in the same directory as the input file.

Future work:
Integration testing + code refinement will be done later on since Codex had been down, oh god.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import traceback
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol, Sequence

SCHEMA_VERSION = "palsu-prospectus-v3.0"
MANIFEST_SCHEMA_VERSION = "palsu-prospectus-batch-manifest-v3.0"

try:  # optional pretty terminal output
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import track
    from rich.prompt import Confirm, Prompt
    from rich.table import Table

    RICH_AVAILABLE = True
    console: Any = Console()
except Exception:  # pragma: no cover - cosmetic only
    RICH_AVAILABLE = False
    console = None


# =============================================================================
# 1. Environment bootstrap.  Docling is imported LAZILY so that the pure
#    parsing layer, --help, --self-test and --dump-grid all work without it.
# =============================================================================
class DoclingUnavailable(RuntimeError):
    """Raised when a PDF must be converted but Docling is not importable."""


def _venv_python() -> Path | None:
    """Locate a sibling .docling-venv interpreter (Windows or POSIX layout)."""
    root = Path(__file__).resolve().parent / ".docling-venv"
    for rel in ("Scripts/python.exe", "bin/python", "bin/python3"):
        candidate = root / rel
        if candidate.exists():
            return candidate
    return None


def _docling_importable() -> bool:
    try:
        import docling  # noqa: F401
        import docling_core  # noqa: F401

        return True
    except Exception:
        return False


def ensure_docling_env() -> None:
    """Re-exec inside .docling-venv once, if Docling is missing here but present there.

    v1 had two competing relaunch mechanisms guarded by two different env
    vars, which could double-launch. This is the single entry point, and it is
    only called when a PDF actually has to be converted.
    """
    if _docling_importable() or os.environ.get("_PALSU_RELAUNCHED"):
        return
    venv_py = _venv_python()
    if not venv_py:
        return
    env = os.environ.copy()
    env["_PALSU_RELAUNCHED"] = "1"
    print(f"[*] Docling not available here; re-launching via {venv_py}", flush=True)
    sys.exit(subprocess.call([str(venv_py), str(Path(__file__).resolve())] + sys.argv[1:], env=env))


_DOCLING_CACHE: dict[str, Any] = {}



def _version_tuple(value: str) -> tuple[int, ...]:
    nums = re.findall(r"\d+", value or "")
    return tuple(int(n) for n in nums[:4]) or (0,)


def _require_safe_docling_parse() -> str:
    try:
        installed = package_version("docling-parse")
    except PackageNotFoundError as exc:
        raise DoclingUnavailable(
            "docling-parse is not installed. Run repair_docling_env.ps1 or install "
            "`docling==2.129.0` and `docling-parse>=7.20,<8` in .docling-venv."
        ) from exc
    if _version_tuple(installed) < (7, 12, 0):
        raise DoclingUnavailable(
            f"docling-parse {installed} is affected by the native preprocess memory bug "
            "that manifests as repeated std::bad_alloc. Upgrade to >=7.12; "
            "Bintanong pins >=7.20."
        )
    return installed


def load_docling() -> dict[str, Any]:
    if _DOCLING_CACHE:
        return _DOCLING_CACHE
    _require_safe_docling_parse()
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import (
            AcceleratorDevice,
            AcceleratorOptions,
            PdfPipelineOptions,
            TableFormerMode,
        )
        from docling.document_converter import DocumentConverter, PdfFormatOption
        from docling.backend.docling_parse_v4_backend import DoclingParseV4DocumentBackend
        from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
        from docling_core.transforms.chunker import HierarchicalChunker
        from docling_core.types.doc import DoclingDocument
    except ImportError as exc:
        raise DoclingUnavailable(
            "Docling is required to convert PDFs. Rebuild .docling-venv with "
            "`docling==2.129.0` / `docling-parse>=7.20,<8`."
        ) from exc

    _DOCLING_CACHE.update(
        {
            "InputFormat": InputFormat,
            "AcceleratorDevice": AcceleratorDevice,
            "AcceleratorOptions": AcceleratorOptions,
            "PdfPipelineOptions": PdfPipelineOptions,
            "TableFormerMode": TableFormerMode,
            "DocumentConverter": DocumentConverter,
            "PdfFormatOption": PdfFormatOption,
            "DoclingParseV4DocumentBackend": DoclingParseV4DocumentBackend,
            "PyPdfiumDocumentBackend": PyPdfiumDocumentBackend,
            "HierarchicalChunker": HierarchicalChunker,
            "DoclingDocument": DoclingDocument,
        }
    )
    return _DOCLING_CACHE



def check_cuda_environment() -> dict[str, Any]:
    """Inspect GPU hardware and PyTorch CUDA capability with honest diagnostics."""
    info: dict[str, Any] = {
        "has_gpu_hardware": False,
        "gpu_name": None,
        "torch_available": False,
        "torch_version": None,
        "cuda_available": False,
        "cuda_device_count": 0,
        "cuda_device_name": None,
        "status_message": "",
    }
    try:
        import torch
    except Exception:
        torch = None  # type: ignore[assignment]

    if torch is not None:
        info["torch_available"] = True
        info["torch_version"] = getattr(torch, "__version__", None)
        if hasattr(torch, "cuda") and torch.cuda.is_available():
            info["has_gpu_hardware"] = True
            info["cuda_available"] = True
            info["cuda_device_count"] = torch.cuda.device_count()
            info["cuda_device_name"] = (
                torch.cuda.get_device_name(0) if info["cuda_device_count"] else "CUDA Device"
            )
            info["gpu_name"] = info["cuda_device_name"]
            info["status_message"] = (
                f"CUDA active: {info['cuda_device_name']} (PyTorch {info['torch_version']})"
            )
            return info

    try:
        smi = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=15,
        ).strip()
        names = [line.strip() for line in smi.splitlines() if line.strip()]
        if names:
            info["has_gpu_hardware"] = True
            info["gpu_name"] = names[0]
    except Exception:
        pass

    if info["has_gpu_hardware"]:
        info["status_message"] = (
            f"NVIDIA GPU detected ({info['gpu_name']}), but PyTorch "
            f"({info['torch_version'] or 'not installed'}) has no CUDA support. Using CPU."
        )
    else:
        info["status_message"] = "No CUDA GPU available. Using CPU."
    return info



def get_pipeline_options(device: str = "auto") -> Any:
    dl = load_docling()
    options = dl["PdfPipelineOptions"]()
    env = check_cuda_environment()
    want = (device or "auto").strip().lower()

    if want == "cpu":
        chosen = dl["AcceleratorDevice"].CPU
        print("[*] Acceleration: CPU (explicitly selected).")
    elif env["cuda_available"]:
        chosen = dl["AcceleratorDevice"].CUDA
        print(f"[+] Acceleration: CUDA ({env['cuda_device_name']}).")
    else:
        chosen = dl["AcceleratorDevice"].CPU
        print("[*] Acceleration: CPU. " + env["status_message"])

    options.accelerator_options = dl["AcceleratorOptions"](device=chosen)
    options.do_ocr = False
    options.force_backend_text = True
    options.do_table_structure = True
    options.table_structure_options.mode = dl["TableFormerMode"].ACCURATE

    raw = os.environ.get("PALSU_DOCLING_CELL_MATCHING", "true").strip().lower()
    options.table_structure_options.do_cell_matching = raw in {"1", "true", "yes", "on"}

    for attr in ("generate_page_images", "generate_picture_images"):
        if hasattr(options, attr):
            setattr(options, attr, False)
    return options



_SHARED_CONVERTERS: dict[tuple[str, str], Any] = {}



def get_shared_converter(device: str = "auto", backend: str = "docling_parse") -> Any:
    dl = load_docling()
    dev = (device or "auto").strip().lower()
    backend_key = (backend or "docling_parse").strip().lower()
    key = (dev, backend_key)
    if key not in _SHARED_CONVERTERS:
        opts = get_pipeline_options(device=dev)
        backend_cls = (
            dl["PyPdfiumDocumentBackend"]
            if backend_key == "pypdfium2"
            else dl["DoclingParseV4DocumentBackend"]
        )
        _SHARED_CONVERTERS[key] = dl["DocumentConverter"](
            format_options={
                dl["InputFormat"].PDF: dl["PdfFormatOption"](
                    pipeline_options=opts,
                    backend=backend_cls,
                )
            }
        )
    return _SHARED_CONVERTERS[key]



# =============================================================================
# 2. Text normalisation helpers
# =============================================================================
DASHES = "\u2010\u2011\u2012\u2013\u2014\u2015"
SUPERSCRIPTS = str.maketrans(
    "\u00b9\u00b2\u00b3\u2070\u2074\u2075\u2076\u2077\u2078\u2079",
    "1230456789",
)


def clean_str(value: Any) -> str:
    """Collapse whitespace, drop soft hyphens/NBSP, normalise dashes and superscripts."""
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\u00ad", "").replace("\xa0", " ")
    text = text.translate(SUPERSCRIPTS)
    for dash in DASHES:
        text = text.replace(dash, "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def norm_key(code: str) -> str:
    """Strict comparison key for a course code: upper-case alphanumerics only."""
    return re.sub(r"[^A-Z0-9]", "", clean_str(code).upper())


def relaxed_key(code: str) -> str:
    """Looser key that ignores a trailing lab marker, so 'BT-2' matches 'BT-2/L'."""
    key = norm_key(code)
    if len(key) > 2 and key.endswith("L") and not key.endswith("LL"):
        return key[:-1]
    return key


YEAR_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(?:FIRST|1ST)\s+YEAR\b"), "1st Year"),
    (re.compile(r"\b(?:SECOND|2ND)\s+YEAR\b"), "2nd Year"),
    (re.compile(r"\b(?:THIRD|3RD)\s+YEAR\b"), "3rd Year"),
    (re.compile(r"\b(?:FOURTH|4TH)\s+YEAR\b"), "4th Year"),
    (re.compile(r"\b(?:FIFTH|5TH)\s+YEAR\b"), "5th Year"),
]

SEMESTER_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(?:FIRST|1ST)\s+SEM(?:ESTER)?\b"), "1st Semester"),
    (re.compile(r"\b(?:SECOND|2ND)\s+SEM(?:ESTER)?\b"), "2nd Semester"),
    (re.compile(r"\bSUMMER\b"), "Summer"),
    (re.compile(r"\bMID[\s-]?YEAR\b"), "Mid-Year"),
]

YEAR_ORDER = {"1st Year": 1, "2nd Year": 2, "3rd Year": 3, "4th Year": 4, "5th Year": 5}
SEMESTER_ORDER = {"1st Semester": 1, "2nd Semester": 2, "Summer": 3, "Mid-Year": 3}
INLINE_SEMESTER_PREFIX = re.compile(
    r"^(?:(?:FIRST|1ST|SECOND|2ND|THIRD|3RD)\s+SEM(?:ESTER)?|SUMMER|MID[\s-]?YEAR)\b\s+(.+)$",
    re.IGNORECASE,
)

BANNER_WORDS = {
    "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH",
    "1ST", "2ND", "3RD", "4TH", "5TH",
    "YEAR", "SEMESTER", "SEM", "SUMMER", "MIDYEAR", "MID-YEAR", "TERM",
}


def match_year_label(text: str) -> str | None:
    """Return a year label found in `text`, ignoring 'Nth Year Standing' prerequisites."""
    upper = clean_str(text).upper()
    if not upper:
        return None
    
    # Prerequisite-like or rule-like exclusions:
    if re.search(r"\b(?:STANDING|ENROLLED|PASSED|TAKEN|MUST\s+HAVE|PREREQUISITE)\b", upper):
        return None
        
    for pattern, label in YEAR_PATTERNS:
        if pattern.search(upper):
            return label
    return None


def match_semester_labels(text: str) -> list[tuple[int, str]]:
    """All semester labels in `text`, as (position, label), left to right."""
    upper = clean_str(text).upper()
    found: list[tuple[int, str]] = []
    for pattern, label in SEMESTER_PATTERNS:
        for match in pattern.finditer(upper):
            found.append((match.start(), label))
    found.sort(key=lambda item: item[0])
    deduped: list[tuple[int, str]] = []
    for pos, label in found:
        if not deduped or deduped[-1][1] != label:
            deduped.append((pos, label))
    return deduped


def is_banner_text(text: str) -> bool:
    """True when every alphabetic token is a year/semester banner word."""
    cleaned = clean_str(text).upper().replace(":", " ")
    tokens = [tok for tok in re.split(r"[\s,]+", cleaned) if tok]
    if not tokens:
        return False
    alpha = [tok for tok in tokens if re.search(r"[A-Z]", tok)]
    if not alpha:
        return False
    return all(tok.strip(".") in BANNER_WORDS for tok in alpha)


def term_index(year_level: str, semester: str) -> int:
    """Sortable index so prerequisite ordering can be checked."""
    return YEAR_ORDER.get(year_level, 99) * 10 + SEMESTER_ORDER.get(semester, 9)


# =============================================================================
# 3. Footnote engine (document-gated, not hard-coded)
# =============================================================================
TWO_TRAILING_INTS = re.compile(r"^(.*?)\s+(\d{1,2})\s+(\d{1,2})$")
ONE_TRAILING_INT = re.compile(r"^(.*?)\s+(\d{1,2})$")
TRAILING_FRACTION = re.compile(r"^(.*?)\s+(\d{1,2}\s*/\s*\d{1,2})$")


@dataclass
class FootnoteContext:
    """Decides whether trailing integers in a title are footnote markers.

    v1 stripped any trailing integer >= 3, which is correct for the CS
    prospectus (superscript endnote markers 1..26) and destructive for the
    Architecture prospectus ("History of Architecture 3" -> "History of
    Architecture").  This class gates the behaviour on evidence found in the
    document being parsed, and records every strip for audit.
    """

    enabled: bool = False
    evidence: int = 0
    families: dict[str, set[int]] = field(default_factory=dict)
    markers: list[int] = field(default_factory=list)
    stripped: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @staticmethod
    def _family_base(title: str) -> tuple[str, int | None]:
        match = ONE_TRAILING_INT.match(title)
        if not match:
            return title, None
        return match.group(1).strip(), int(match.group(2))

    @classmethod
    def build(cls, raw_titles: Sequence[str], unit_cells: Sequence[str]) -> "FootnoteContext":
        ctx = cls()
        titles = [clean_str(t) for t in raw_titles if clean_str(t)]

        # Evidence 1: titles ending in two integers ("Discrete Structures 1 1").
        double_hits = sum(1 for t in titles if TWO_TRAILING_INTS.match(t))
        # Evidence 2: unit cells carrying a leading marker ("23 3" -> 3 units).
        unit_hits = sum(
            1 for u in unit_cells if re.match(r"^\d{1,2}\s+\d{1,2}(?:\s*/\s*\d{1,2})?$", clean_str(u))
        )
        ctx.evidence = double_hits + unit_hits
        ctx.enabled = ctx.evidence >= 2

        # Title families: "History of Architecture" {1,2,3,4} means the trailing
        # integer is a series number, not a marker.
        families: dict[str, set[int]] = defaultdict(set)
        for title in titles:
            base, num = cls._family_base(title)
            if num is not None:
                families[base.lower()].add(num)
            double = TWO_TRAILING_INTS.match(title)
            if double:
                families[double.group(1).strip().lower()].add(int(double.group(2)))
        ctx.families = {k: v for k, v in families.items() if len(v) > 1}

        if ctx.enabled:
            ctx.notes.append(
                f"Footnote markers detected (evidence={ctx.evidence}); trailing markers stripped."
            )
        else:
            ctx.notes.append(
                f"No footnote markers detected (evidence={ctx.evidence}); titles kept verbatim."
            )
        return ctx

    def _is_series_number(self, base: str) -> bool:
        return base.strip().lower() in self.families

    def clean_title(self, raw_title: str, unit_raw: str = "") -> tuple[str, int | None]:
        """Return (clean_title, stripped_marker_or_None)."""
        title = clean_str(raw_title)
        if not title:
            return "", None

        # Drop a repeated-header artefact such as "FIRST SEMESTER Information Management 2".
        title = re.sub(
            r"^(?:FIRST|SECOND|THIRD|FOURTH|FIFTH|1ST|2ND|3RD|4TH|5TH)\s+(?:YEAR|SEMESTER)\s+",
            "",
            title,
            flags=re.IGNORECASE,
        ).strip()
        title = re.sub(
            r"^(?:FIRST\s+(?!AID\b)|SECOND\s+)",
            "",
            title,
            flags=re.IGNORECASE,
        ).strip()

        marker: int | None = None
        double = TWO_TRAILING_INTS.match(title)
        if double and self.enabled:
            # "Science, Technology and Society 23 3" with a unit cell of 3:
            # the last token is a unit bleed, the one before it is the marker.
            base, first_num, second_num = double.group(1).strip(), double.group(2), double.group(3)
            unit_clean = clean_str(unit_raw).replace(" ", "")
            if unit_clean and unit_clean == second_num:
                title = f"{base} {first_num}".strip()
                inner = ONE_TRAILING_INT.match(title)
                if inner and not self._is_series_number(inner.group(1)):
                    marker = int(inner.group(2))
                    title = inner.group(1).strip()
            else:
                marker = int(second_num)
                title = f"{base} {first_num}".strip()
            self._record(raw_title, title, marker)
            return title, marker

        single = ONE_TRAILING_INT.match(title)
        if single and self.enabled:
            base, num = single.group(1).strip(), int(single.group(2))
            if not self._is_series_number(base):
                marker = num
                title = base
                self._record(raw_title, title, marker)
                return title, marker

        return title, None

    def _record(self, raw: str, cleaned: str, marker: int | None) -> None:
        if marker is None:
            return
        self.markers.append(marker)
        self.stripped.append({"raw_title": clean_str(raw), "clean_title": cleaned, "marker": marker})

    def audit(self) -> dict[str, Any]:
        counts = Counter(self.markers)
        duplicates = sorted(m for m, c in counts.items() if c > 1)
        gaps: list[int] = []
        if self.markers:
            highest = max(self.markers)
            gaps = [n for n in range(1, highest + 1) if n not in counts]
        return {
            "enabled": self.enabled,
            "evidence": self.evidence,
            "markers_stripped": sorted(counts),
            "duplicate_markers": duplicates,
            "missing_markers": gaps,
            "series_families": sorted(self.families),
            "notes": self.notes,
            "details": self.stripped,
        }


# =============================================================================
# 4. Unit parsing
# =============================================================================
def parse_units(raw: Any) -> dict[str, Any]:
    """Parse a unit cell into lecture/lab/total. Accepts '3', '2/1', '(3)', '23 3'."""
    text = clean_str(raw)
    empty = {"raw": text, "lecture": None, "lab": None, "total": None}
    if not text:
        return empty

    text = text.replace("(", " ").replace(")", " ")
    text = re.sub(r"\bunits?\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()

    # Leading footnote marker glued onto the unit cell: "23 3" or "3 1/2".
    glued = re.match(r"^\d{1,2}\s+(\d{1,2}\s*/\s*\d{1,2}|\d{1,2})$", text)
    if glued:
        text = glued.group(1)

    fraction = re.match(r"^(\d{1,2})\s*/\s*(\d{1,2})$", text)
    if fraction:
        lecture, lab = int(fraction.group(1)), int(fraction.group(2))
        return {"raw": text, "lecture": lecture, "lab": lab, "total": lecture + lab}

    whole = re.match(r"^(\d{1,2})$", text)
    if whole:
        value = int(whole.group(1))
        return {"raw": text, "lecture": value, "lab": 0, "total": value}

    loose = re.search(r"(\d{1,2})\s*/\s*(\d{1,2})", text)
    if loose:
        lecture, lab = int(loose.group(1)), int(loose.group(2))
        return {"raw": text, "lecture": lecture, "lab": lab, "total": lecture + lab}

    single = re.search(r"(\d{1,2})", text)
    if single:
        value = int(single.group(1))
        return {"raw": text, "lecture": value, "lab": 0, "total": value}

    return {"raw": text, "lecture": None, "lab": None, "total": None}


def rescue_units_from_title(title: str, unit_raw: str) -> tuple[str, str]:
    """Pull units that bled into the title cell when the unit cell is empty.

    Only fires on unambiguous shapes: a trailing fraction ('... 2/1'), or two
    trailing integers where the first is a footnote marker. A lone trailing
    integer is left alone, because 'History of Architecture 3' is a title.
    """
    title_clean = clean_str(title)
    if clean_str(unit_raw):
        return title_clean, clean_str(unit_raw)

    fraction = TRAILING_FRACTION.match(title_clean)
    if fraction:
        return fraction.group(1).strip(), fraction.group(2).replace(" ", "")

    double = TWO_TRAILING_INTS.match(title_clean)
    if double and int(double.group(3)) <= 6:
        return f"{double.group(1).strip()} {double.group(2)}".strip(), double.group(3)

    return title_clean, ""


# =============================================================================
# 5. Prerequisite tokenising and resolution
# =============================================================================
NULL_TOKENS = {"", "-", "--", "n/a", "na", "none", "nil", "no prereq", "no prerequisite"}

STANDING_PATTERNS = [
    re.compile(r"\bstanding\b", re.IGNORECASE),
    re.compile(r"%"),
    re.compile(r"\bpercent\b", re.IGNORECASE),
    re.compile(r"total\s+(?:number|units)", re.IGNORECASE),
    re.compile(r"all\s+(?:major|course|subject)", re.IGNORECASE),
    re.compile(r"\bgraduating\b", re.IGNORECASE),
    re.compile(r"past\s+semester", re.IGNORECASE),
    re.compile(r"\bconsent\b", re.IGNORECASE),
    re.compile(r"\bunits\s+earned\b", re.IGNORECASE),
]

CODE_RANGE = re.compile(r"^([A-Za-z][A-Za-z\-\.\s]{0,12}?)\s*(\d{1,3})\s*-\s*(\d{1,3})$")


def is_standing_rule(text: str) -> bool:
    return any(pattern.search(text) for pattern in STANDING_PATTERNS)


def split_prereq_fragments(raw: str) -> list[str]:
    """Split a prerequisite cell into fragments on commas, semicolons, '&', 'and', newlines."""
    text = clean_str(raw)
    if not text or text.lower() in NULL_TOKENS:
        return []
    parts = re.split(r"[;,&]|\band\b|\n", text, flags=re.IGNORECASE)
    fragments: list[str] = []
    for part in parts:
        candidate = clean_str(part)
        if candidate and candidate.lower() not in NULL_TOKENS:
            fragments.append(candidate)
    return fragments


class CodeIndex:
    """Resolves free-text prerequisite tokens to codes present in the document."""

    def __init__(self, codes: Iterable[str]) -> None:
        self.codes: list[str] = []
        self._exact: dict[str, str] = {}
        self._relaxed: dict[str, list[str]] = defaultdict(list)
        for code in codes:
            cleaned = clean_str(code)
            if not cleaned or cleaned in self.codes:
                continue
            self.codes.append(cleaned)
            self._exact.setdefault(norm_key(cleaned), cleaned)
            self._relaxed[relaxed_key(cleaned)].append(cleaned)
        self._max_tokens = max((len(c.split()) for c in self.codes), default=1) + 1

    def resolve(self, token: str) -> str | None:
        key = norm_key(token)
        if not key:
            return None
        if key in self._exact:
            return self._exact[key]
        candidates = self._relaxed.get(relaxed_key(token), [])
        if len(candidates) == 1:
            return candidates[0]
        return None

    def split_run(self, fragment: str) -> tuple[list[str], list[str]]:
        """Greedy left-to-right split of a run like 'CS 6/L CS 10/L' into known codes."""
        tokens = clean_str(fragment).split()
        resolved: list[str] = []
        leftovers: list[str] = []
        i = 0
        pending: list[str] = []
        while i < len(tokens):
            matched = False
            for width in range(min(self._max_tokens, len(tokens) - i), 0, -1):
                candidate = " ".join(tokens[i : i + width])
                hit = self.resolve(candidate)
                if hit:
                    if pending:
                        leftovers.append(" ".join(pending))
                        pending = []
                    resolved.append(hit)
                    i += width
                    matched = True
                    break
            if not matched:
                pending.append(tokens[i])
                i += 1
        if pending:
            leftovers.append(" ".join(pending))
        return resolved, leftovers

    def expand_range(self, fragment: str) -> list[str] | None:
        """'MATH 19-20' -> ['Math 19', 'Math 20'] when both exist in the document."""
        match = CODE_RANGE.match(clean_str(fragment))
        if not match:
            return None
        prefix, start, end = match.group(1).strip(), int(match.group(2)), int(match.group(3))
        if end < start or end - start > 8:
            return None
        found: list[str] = []
        for number in range(start, end + 1):
            hit = self.resolve(f"{prefix} {number}")
            if not hit:
                return None
            found.append(hit)
        return found or None


ADMIN_METADATA_PATTERN = re.compile(
    r"\b(?:Doc\.?\s*Ref\.?\s*No\.?|PSU-CIM-CUR|PalSU-OP-QA|Revision\s*No\.?|Effective\s*Date|BOR\s*Res(?:olution)?)\b",
    re.IGNORECASE,
)

POLICY_NOTE_PATTERN = re.compile(
    r"^(?:NOTE\b|Important\b|Specialization\s*Courses|Subjects\s*(?:printed\s*)?in\s*italics)|"
    r"\b(?:specialization\s*courses\s*for\s*the|major\s*courses\s*from\s*1st|units\s*to\s*be\s*enrolled)\b",
    re.IGNORECASE,
)

TOTAL_ROW_PATTERN = re.compile(
    r"\b(?:TOTAL(?:\s*NO\.?\s*OF\s*UNITS)?|SUBTOTAL)\b",
    re.IGNORECASE,
)

DISQUALIFYING_CODE_WORDS = re.compile(
    r"\b(TOTAL|SUBTOTAL|YEAR|SEMESTER|DOC\.?|REF\.?|REVISION|EFFECTIVE|NOTE|ITALICS|SPECIALIZATION|UNITS?|GRADE|HOURS|PAGE|CAMPUS|CHED|CMO|RESOLUTION|BOR|STUDIES\s*\d+\s*TOTAL)\b",
    re.IGNORECASE,
)


def is_code_like_token(text: str) -> bool:
    t = clean_str(text)
    if not t or len(t) > 25:
        return False
    if DISQUALIFYING_CODE_WORDS.search(t):
        return False
    return bool(
        re.match(
            r"^(?:[A-Za-z]{1,8}[\s\-]*(?:Fit\s*)?\d{1,4}[A-Za-z]?|[A-Za-z]{1,4}\s*\d{3,4}|GE[\s\-]+[A-Za-z]{2,6})$",
            t,
            re.IGNORECASE,
        )
    )


def is_unit_like_token(text: str) -> bool:
    t = clean_str(text)
    return bool(re.match(r"^\d{1,2}(?:\s*/\s*\d{1,2})?$", t))


@dataclass
class PrereqResolution:
    resolved: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    standing_rules: list[str] = field(default_factory=list)


def resolve_prerequisites(raw: str, index: CodeIndex, current_course_code: str = "") -> PrereqResolution:
    """Turn a prerequisite cell into resolved course codes plus policy rules."""
    out = PrereqResolution()
    for fragment in split_prereq_fragments(raw):
        if is_standing_rule(fragment):
            out.standing_rules.append(fragment if fragment.endswith(".") else fragment + ".")
            continue

        direct = index.resolve(fragment)
        if direct:
            if current_course_code and norm_key(direct) == norm_key(current_course_code):
                continue
            if direct not in out.resolved:
                out.resolved.append(direct)
            continue

        expanded = index.expand_range(fragment)
        if expanded:
            for code in expanded:
                if current_course_code and norm_key(code) == norm_key(current_course_code):
                    continue
                if code not in out.resolved:
                    out.resolved.append(code)
            continue

        codes, leftovers = index.split_run(fragment)
        for code in codes:
            if current_course_code and norm_key(code) == norm_key(current_course_code):
                continue
            if code not in out.resolved:
                out.resolved.append(code)
        for leftover in leftovers:
            token = clean_str(leftover).strip(".,")
            if not token or token.lower() in NULL_TOKENS:
                continue
            if DISQUALIFYING_CODE_WORDS.search(token) or POLICY_NOTE_PATTERN.search(token):
                continue
            if is_standing_rule(token):
                out.standing_rules.append(token)
            elif token not in out.unresolved:
                out.unresolved.append(token)
    return out


# =============================================================================
# 6. Table layout detection
# =============================================================================
@dataclass
class ColumnGroup:
    """One semester block of columns inside a two-up prospectus table."""

    index: int
    code_idx: int
    title_idx: int
    unit_idx: int
    prereq_idx: int

    def span(self) -> range:
        indices = [self.code_idx, self.title_idx, self.unit_idx, self.prereq_idx]
        return range(min(indices), max(indices) + 1)

    def as_dict(self) -> dict[str, int]:
        return {
            "index": self.index,
            "code_idx": self.code_idx,
            "title_idx": self.title_idx,
            "unit_idx": self.unit_idx,
            "prereq_idx": self.prereq_idx,
        }


def infer_column_groups_from_content(grid: list[list[str]]) -> list[ColumnGroup]:
    if not grid or len(grid) < 2:
        return []
    num_cols = max(len(r) for r in grid)
    code_scores = [0] * num_cols
    unit_scores = [0] * num_cols
    for row in grid:
        for c, cell in enumerate(row):
            if is_code_like_token(cell):
                code_scores[c] += 1
            if is_unit_like_token(cell):
                unit_scores[c] += 1

    unit_cols = [c for c in range(num_cols) if unit_scores[c] > 0]
    two_up_unit_pairs = []
    for i in range(len(unit_cols)):
        for j in range(i + 1, len(unit_cols)):
            u1, u2 = unit_cols[i], unit_cols[j]
            if u2 - u1 >= 3:
                two_up_unit_pairs.append((u1, u2))

    if two_up_unit_pairs:
        best_u_pair = max(two_up_unit_pairs, key=lambda p: unit_scores[p[0]] + unit_scores[p[1]])
        u1, u2 = best_u_pair
        c1_candidates = [c for c in range(u1) if code_scores[c] > 0]
        c1 = max(c1_candidates, key=lambda c: code_scores[c]) if c1_candidates else 0
        c2_candidates = [c for c in range(u1 + 1, u2) if code_scores[c] > 0]
        if c2_candidates:
            c2 = max(c2_candidates, key=lambda c: (code_scores[c], -abs((u2 - c) - (u1 - c1))))
        else:
            c2 = u1 + (u2 - u1) // 2
        prereq1 = u1 + 1 if c2 > u1 + 1 else u1
        prereq2 = u2 + 1 if num_cols > u2 + 1 else u2
        g1 = ColumnGroup(0, c1, c1 + 1, u1, prereq1)
        g2 = ColumnGroup(1, c2, c2 + 1 if u2 > c2 + 1 else c2, u2, prereq2)
        return [g1, g2]

    code_cols = [
        c
        for c in range(num_cols)
        if code_scores[c] >= 2 or (code_scores[c] >= 1 and len(grid) <= 8)
    ]
    if not code_cols:
        return []

    two_up_pairs = []
    for i in range(len(code_cols)):
        for j in range(i + 1, len(code_cols)):
            c1, c2 = code_cols[i], code_cols[j]
            if c2 - c1 >= 3:
                two_up_pairs.append((c1, c2))

    if two_up_pairs:
        best_pair = max(two_up_pairs, key=lambda p: code_scores[p[0]] + code_scores[p[1]])
        c1, c2 = best_pair
        u1_candidates = [c for c in range(c1 + 1, c2) if unit_scores[c] > 0]
        u1 = max(u1_candidates, key=lambda c: unit_scores[c]) if u1_candidates else c1 + 2
        u2_candidates = [c for c in range(c2 + 1, num_cols) if unit_scores[c] > 0]
        u2 = max(u2_candidates, key=lambda c: unit_scores[c]) if u2_candidates else min(c2 + 2, num_cols - 1)

        g1 = ColumnGroup(
            index=0,
            code_idx=c1,
            title_idx=c1 + 1 if u1 > c1 + 1 else c1 + 1,
            unit_idx=u1,
            prereq_idx=u1 + 1 if u1 + 1 < c2 else u1,
        )
        g2 = ColumnGroup(
            index=1,
            code_idx=c2,
            title_idx=c2 + 1 if u2 > c2 + 1 else c2 + 1,
            unit_idx=u2,
            prereq_idx=u2 + 1 if u2 + 1 < num_cols else u2,
        )
        return [g1, g2]
    else:
        c1 = code_cols[0]
        u1_candidates = [c for c in range(c1 + 1, num_cols) if unit_scores[c] > 0]
        u1 = max(u1_candidates, key=lambda c: unit_scores[c]) if u1_candidates else min(c1 + 2, num_cols - 1)

        right_units = [c for c in range(u1 + 1, num_cols) if unit_scores[c] > 0]
        if num_cols >= 6 and right_units:
            u2 = max(right_units, key=lambda c: unit_scores[c])
            prereq1_idx = u1 + 1 if (u2 - u1) >= 3 else u1
            c2 = u2 - 1 if u2 > u1 + 1 else u1 + 1
            return [
                ColumnGroup(
                    index=0,
                    code_idx=c1,
                    title_idx=c1 + 1,
                    unit_idx=u1,
                    prereq_idx=prereq1_idx,
                ),
                ColumnGroup(
                    index=1,
                    code_idx=c2,
                    title_idx=c2,
                    unit_idx=u2,
                    prereq_idx=u2,
                ),
            ]

        return [
            ColumnGroup(
                index=0,
                code_idx=c1,
                title_idx=c1 + 1,
                unit_idx=u1,
                prereq_idx=min(u1 + 1, num_cols - 1),
            )
        ]


def classify_header_cell(text: str) -> str:
    """Map a header cell to code/title/units/prereq/grade/other."""
    squashed = re.sub(r"[^a-z]", "", clean_str(text).lower())
    if not squashed:
        return "other"
    if "code" in squashed or squashed in ("course", "courses", "subcode", "subjectcode"):
        return "code"
    if "grade" in squashed:
        return "grade"
    if "title" in squashed or "descriptive" in squashed or "subject" in squashed:
        return "title"
    if "unit" in squashed or "credit" in squashed:
        return "units"
    if "prereq" in squashed or "prerequisite" in squashed or squashed.startswith("prereq"):
        return "prereq"
    if squashed.startswith("pre") and "req" in squashed:
        return "prereq"
    return "other"


def find_header_row(grid: Sequence[Sequence[str]], search_depth: int = 6) -> int:
    """Index of the column-header row, or -1 when the table has none."""
    if len(grid) >= 2:
        combo = [f"{grid[0][c]} {grid[1][c]}".strip() for c in range(min(len(grid[0]), len(grid[1])))]
        kinds = [classify_header_cell(cell) for cell in combo]
        if "code" in kinds and "title" in kinds and kinds.count("code") >= 2:
            return 0

    for row_index in range(min(search_depth, len(grid))):
        kinds = [classify_header_cell(cell) for cell in grid[row_index]]
        if "code" in kinds and "title" in kinds:
            return row_index
    for row_index in range(min(search_depth, len(grid))):
        kinds = [classify_header_cell(cell) for cell in grid[row_index]]
        if kinds.count("title") >= 1 and kinds.count("units") >= 1:
            return row_index
    return -1


def fallback_groups(num_cols: int) -> list[ColumnGroup]:
    """Positional layouts for tables whose header row did not survive extraction."""
    if num_cols >= 10:
        return [ColumnGroup(0, 1, 2, 3, 4), ColumnGroup(1, 6, 7, 8, 9)]
    if num_cols >= 8:
        return [ColumnGroup(0, 0, 1, 2, 3), ColumnGroup(1, 4, 5, 6, 7)]
    if num_cols == 5:
        return [ColumnGroup(0, 1, 2, 3, 4)]
    if num_cols == 4:
        return [ColumnGroup(0, 0, 1, 2, 3)]
    return []


def detect_column_groups(grid: Sequence[Sequence[str]]) -> tuple[list[ColumnGroup], int]:
    """Derive semester column groups from the header row."""
    if not grid:
        return [], -1

    header_index = find_header_row(grid)
    width = max((len(row) for row in grid), default=0)
    if header_index < 0:
        inferred = infer_column_groups_from_content([[clean_str(c) for c in r] for r in grid])
        if inferred:
            return inferred, -1
        return fallback_groups(width), -1

    header = list(grid[header_index])
    h_kinds = [classify_header_cell(c) for c in header]
    if (h_kinds.count("code") < 2 or "title" not in h_kinds) and header_index + 1 < len(grid):
        next_row = list(grid[header_index + 1])
        next_text = " ".join(next_row).upper()
        if not any(w in next_text for w in ["YEAR", "SEMESTER"]):
            max_c = min(len(header), len(next_row))
            merged = [f"{header[c]} {next_row[c]}".strip() for c in range(max_c)]
            m_kinds = [classify_header_cell(c) for c in merged]
            if m_kinds.count("code") >= h_kinds.count("code") and "title" in m_kinds:
                header = merged

    groups: list[ColumnGroup] = []
    current: dict[str, int] = {}

    def flush() -> None:
        if "code" not in current:
            return
        code_idx = current["code"]
        groups.append(
            ColumnGroup(
                index=len(groups),
                code_idx=code_idx,
                title_idx=current.get("title", code_idx + 1),
                unit_idx=current.get("units", code_idx + 2),
                prereq_idx=current.get("prereq", code_idx + 3),
            )
        )

    for col_index, cell in enumerate(header):
        kind = classify_header_cell(cell)
        if kind == "code":
            flush()
            current = {"code": col_index}
        elif kind in {"title", "units", "prereq"} and current:
            current.setdefault(kind, col_index)
    flush()

    width = max((len(row) for row in grid), default=len(header))
    valid = [g for g in groups if g.prereq_idx < width and g.code_idx < width]
    if not valid:
        inferred = infer_column_groups_from_content([[clean_str(c) for c in r] for r in grid])
        if inferred:
            return inferred, header_index
        return fallback_groups(width), header_index
    data_rows = grid[header_index + 1:]
    def code_count(group: ColumnGroup) -> int:
        return sum(
            group.code_idx < len(row) and is_probable_course_code(row[group.code_idx])
            for row in data_rows
        )
    if all(code_count(group) == 0 for group in valid):
        inferred = infer_column_groups_from_content([[clean_str(c) for c in r] for r in grid])
        if inferred and all(code_count(group) >= 2 for group in inferred):
            return inferred, header_index
    return valid, header_index


def is_header_row(cells: Sequence[str]) -> bool:
    """True for the column-header row and for its repeats after a page break."""
    kinds = [classify_header_cell(cell) for cell in cells]
    return kinds.count("code") >= 1 and kinds.count("title") >= 1


# =============================================================================
# 7. Normalized Docling evidence IR
# =============================================================================
@dataclass(frozen=True)
class SourceBBox:
    """A source-space box. Coordinates retain Docling's native orientation."""

    page: int | None
    left: float | None
    top: float | None
    right: float | None
    bottom: float | None

    def is_complete(self) -> bool:
        return None not in (self.left, self.top, self.right, self.bottom)

    def as_list(self) -> list[float] | None:
        if not self.is_complete():
            return None
        return [float(self.left), float(self.top), float(self.right), float(self.bottom)]

    def as_dict(self) -> dict[str, Any]:
        return {
            "page": self.page,
            "bbox": self.as_list(),
        }


@dataclass(frozen=True)
class NormalizedCell:
    """One Docling table cell, including its original span and source box."""

    cell_id: str
    table_index: int
    raw_text: str
    text: str
    row_start: int
    row_end: int
    col_start: int
    col_end: int
    bbox: SourceBBox | None = None

    @property
    def row_span(self) -> int:
        return max(0, self.row_end - self.row_start)

    @property
    def col_span(self) -> int:
        return max(0, self.col_end - self.col_start)

    def overlaps(self, row: int, col: int | None = None) -> bool:
        if not (self.row_start <= row < self.row_end):
            return False
        return col is None or self.col_start <= col < self.col_end

    def as_evidence_dict(self) -> dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "table_index": self.table_index,
            "text": self.text,
            "raw_text": self.raw_text,
            "row_start": self.row_start,
            "row_end": self.row_end,
            "col_start": self.col_start,
            "col_end": self.col_end,
            "page": self.bbox.page if self.bbox else None,
            "bbox": self.bbox.as_list() if self.bbox else None,
        }


@dataclass
class NormalizedTable:
    table_index: int
    num_rows: int
    num_cols: int
    cells: list[NormalizedCell] = field(default_factory=list)

    def cell_map(self) -> dict[str, NormalizedCell]:
        return {cell.cell_id: cell for cell in self.cells}

    def cells_on_row(self, row: int) -> list[NormalizedCell]:
        return sorted(
            (cell for cell in self.cells if cell.row_start <= row < cell.row_end),
            key=lambda cell: (cell.col_start, cell.col_end, cell.cell_id),
        )


@dataclass
class ProspectusEvidence:
    """Canonical evidence passed from Docling to curriculum interpretation.

    ``tables`` is authoritative. ``grids`` below is a derived compatibility
    projection and must never be used to reconstruct provenance.
    """

    tables: list[NormalizedTable] = field(default_factory=list)
    text_items: list[dict[str, Any]] = field(default_factory=list)
    markdown: str = ""
    docling_document: Any = None
    source_kind: str = ""
    table_year_hints: dict[int, str] = field(default_factory=dict)
    table_year_hint_sources: dict[int, str] = field(default_factory=dict)

    @property
    def docling_doc(self) -> Any:  # compatibility for the layout chunker
        return self.docling_document

    @property
    def grids(self) -> list[list[list[str]]]:  # compatibility/debug view only
        return [project_table_to_grid(table) for table in self.tables]

    def all_cells(self) -> dict[str, NormalizedCell]:
        return {cell.cell_id: cell for table in self.tables for cell in table.cells}


# Kept as an import-compatible name. The canonical model is ProspectusEvidence.
LoadedDocument = ProspectusEvidence


def project_table_to_grid(table: NormalizedTable, repeat_spans: bool = True) -> list[list[str]]:
    """Derive a grid for layout detection and diagnostics without mutating the IR."""
    grid = [["" for _ in range(table.num_cols)] for _ in range(table.num_rows)]
    for cell in sorted(table.cells, key=lambda c: (c.row_start, c.col_start, c.cell_id)):
        rows = range(cell.row_start, min(cell.row_end, table.num_rows))
        cols = range(cell.col_start, min(cell.col_end, table.num_cols))
        for row in rows:
            for col in cols:
                if not repeat_spans and (row != cell.row_start or col != cell.col_start):
                    continue
                if not grid[row][col]:
                    grid[row][col] = cell.text
    return grid


def normalized_table_from_grid(
    grid: Sequence[Sequence[Any]], table_index: int = 0
) -> NormalizedTable:
    """Fixture/compatibility adapter that collapses contiguous duplicate spans.

    Production loading never uses this helper; production tables come from
    Docling ``table_cells`` through ``docling_to_normalized_table``.
    """
    rows = [[clean_str(value) for value in row] for row in grid]
    num_rows = len(rows)
    num_cols = max((len(row) for row in rows), default=0)
    cells: list[NormalizedCell] = []
    cell_number = 0
    for row_index, row in enumerate(rows):
        col = 0
        while col < num_cols:
            value = row[col] if col < len(row) else ""
            if not value:
                col += 1
                continue
            end = col + 1
            while end < num_cols and end < len(row) and row[end] == value:
                end += 1
            cells.append(
                NormalizedCell(
                    cell_id=f"t{table_index}-c{cell_number}",
                    table_index=table_index,
                    raw_text=value,
                    text=value,
                    row_start=row_index,
                    row_end=row_index + 1,
                    col_start=col,
                    col_end=end,
                    bbox=None,
                )
            )
            cell_number += 1
            col = end
    return NormalizedTable(table_index, num_rows, num_cols, cells)


# =============================================================================
# 8. Legacy grid parser (compatibility reference; v3 does not call it)
# =============================================================================
TOTAL_ROW = re.compile(r"^total\b", re.IGNORECASE)
GRAND_TOTAL = re.compile(
    r"\btotal\b[^0-9]{0,30}?:\s*(\d{2,4})\b|\btotal\s+no\.?\s*of\s*units\s*:?\s*(\d{2,4})\b",
    re.IGNORECASE,
)
NON_COURSE_CODES = {
    "COURSE CODE", "CODE", "GRADE", "TOTAL", "SUBTOTAL", "COURSE TITLE", "TITLE",
    "UNIT", "UNITS", "UNIT/S", "PREREQUISITE", "PRE-REQ", "PRE REQ", "DESCRIPTIVE TITLE",
}


def canonicalize_course_code(code: str, title: str) -> str:
    c = clean_str(code)
    c = re.sub(
        r"^([A-Z]{2,8}\s+[A-Z]{2,8})(\d{1,3})(/[A-Z]+)?$",
        lambda match: f"{match.group(1)} {match.group(2)}{match.group(3) or ''}",
        c,
        flags=re.IGNORECASE,
    )
    t = clean_str(title).lower()
    upper = c.upper()
    if upper in {"PATH", "PATH-FIT", "FIT"}:
        if "movement" in t:
            return "PATH-Fit 1"
        elif "fitness" in t:
            return "PATH-Fit 2"
        elif any(w in t for w in ["dance", "sport", "swimming"]):
            return "PATH-Fit 3"
        elif any(w in t for w in ["recreation", "martial", "outdoor"]):
            return "PATH-Fit 4"
    elif upper == "FORENSIC" and "ballistics" in t:
        return "Forensic 6"
    elif upper == "PETE" and "integration" in t:
        return "PetE 42INT/L"
    return c


def looks_like_course(code: str, title: str, unit: str) -> bool:
    """A group holds a course when it has a usable code and some payload."""
    code_clean = clean_str(code)
    if not code_clean:
        return False
    if code_clean.upper() in NON_COURSE_CODES:
        return False
    if TOTAL_ROW_PATTERN.search(code_clean):
        return False
    if DISQUALIFYING_CODE_WORDS.search(code_clean):
        return False
    if is_banner_text(code_clean):
        return False
    if len(code_clean) > 25:
        return False
    if not re.search(r"[A-Za-z0-9]", code_clean):
        return False
    return bool(clean_str(title) or clean_str(unit))


def extract_grand_total(text: str) -> int | None:
    match = GRAND_TOTAL.search(clean_str(text))
    if not match:
        return None
    raw = match.group(1) or match.group(2)
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    return value if 30 <= value <= 400 else None


def _first_int(values: Iterable[str]) -> int | None:
    for value in values:
        match = re.search(r"\b(\d{1,3})\b", clean_str(value))
        if match:
            return int(match.group(1))
    return None


@dataclass
class GridParseResult:
    courses: list[dict[str, Any]] = field(default_factory=list)
    declared_term_units: dict[tuple[str, str], int] = field(default_factory=dict)
    declared_grand_total: int | None = None
    footnotes: FootnoteContext = field(default_factory=FootnoteContext)
    layout: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    policy_notes: list[str] = field(default_factory=list)
    admin_metadata: dict[str, Any] = field(default_factory=dict)
    sections: list[dict[str, Any]] = field(default_factory=list)
    structural_tokens: list[dict[str, Any]] = field(default_factory=list)
    source_course_candidates: list[dict[str, Any]] = field(default_factory=list)
    unclaimed_course_candidates: list[dict[str, Any]] = field(default_factory=list)
    anomalies: list[dict[str, Any]] = field(default_factory=list)
    repair_packets: list[dict[str, Any]] = field(default_factory=list)
    repairs: list[dict[str, Any]] = field(default_factory=list)
    invalid_repairs: list[dict[str, Any]] = field(default_factory=list)


def extract_table_year_contexts(data: dict[str, Any]) -> dict[int, str]:
    table_years: dict[int, str] = {}
    for g in data.get("groups", []) or []:
        curr_year = None
        for child in g.get("children", []) or []:
            cref = child.get("cref", "")
            if cref.startswith("#/texts/"):
                try:
                    t_idx = int(cref.split("/")[-1])
                    t_text = (data.get("texts") or [])[t_idx].get("text", "")
                    for yr_num, name in [
                        ("FIRST", "1st Year"),
                        ("SECOND", "2nd Year"),
                        ("THIRD", "3rd Year"),
                        ("FOURTH", "4th Year"),
                        ("FIFTH", "5th Year"),
                        ("1ST", "1st Year"),
                        ("2ND", "2nd Year"),
                        ("3RD", "3rd Year"),
                        ("4TH", "4th Year"),
                        ("5TH", "5th Year"),
                    ]:
                        if re.search(rf"\b{yr_num}\s+YEAR\b", t_text, re.IGNORECASE):
                            curr_year = name
                            break
                except (IndexError, ValueError):
                    pass
            elif cref.startswith("#/tables/"):
                try:
                    tbl_idx = int(cref.split("/")[-1])
                    if curr_year:
                        table_years[tbl_idx] = curr_year
                except (IndexError, ValueError):
                    pass

    curr_year = None
    for child in (data.get("body", {}) or {}).get("children", []) or []:
        cref = child.get("cref", "")
        if cref.startswith("#/texts/"):
            try:
                t_idx = int(cref.split("/")[-1])
                t_text = (data.get("texts") or [])[t_idx].get("text", "")
                for yr_num, name in [
                    ("FIRST", "1st Year"),
                    ("SECOND", "2nd Year"),
                    ("THIRD", "3rd Year"),
                    ("FOURTH", "4th Year"),
                    ("FIFTH", "5th Year"),
                    ("1ST", "1st Year"),
                    ("2ND", "2nd Year"),
                    ("3RD", "3rd Year"),
                    ("4TH", "4th Year"),
                    ("5TH", "5th Year"),
                ]:
                    if re.search(rf"\b{yr_num}\s+YEAR\b", t_text, re.IGNORECASE):
                        curr_year = name
                        break
            except (IndexError, ValueError):
                pass
        elif cref.startswith("#/tables/"):
            try:
                tbl_idx = int(cref.split("/")[-1])
                if curr_year and tbl_idx not in table_years:
                    table_years[tbl_idx] = curr_year
            except (IndexError, ValueError):
                pass

    return table_years


def _parse_curriculum_grids_legacy(
    grids: Sequence[Sequence[Sequence[str]]],
    table_year_hints: dict[int, str] | None = None,
) -> GridParseResult:
    """Deprecated name retained for imports; delegates to the fail-closed v3 parser."""
    return parse_curriculum_evidence(evidence_from_grids(grids, table_year_hints))


# =============================================================================
# 9. V3 structural tokenizer, explicit sections and course reconstruction
# =============================================================================
class TokenType(str, Enum):
    YEAR_MARKER = "YEAR_MARKER"
    SEMESTER_MARKER = "SEMESTER_MARKER"
    HEADER = "HEADER"
    COURSE_CODE_CANDIDATE = "COURSE_CODE_CANDIDATE"
    COURSE_TITLE_CANDIDATE = "COURSE_TITLE_CANDIDATE"
    UNIT_CANDIDATE = "UNIT_CANDIDATE"
    PREREQUISITE_CANDIDATE = "PREREQUISITE_CANDIDATE"
    TERM_TOTAL = "TERM_TOTAL"
    PROGRAM_TOTAL = "PROGRAM_TOTAL"
    CONTINUATION = "CONTINUATION"
    FOOTNOTE = "FOOTNOTE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class StructuralToken:
    token_type: TokenType
    table_index: int
    row_start: int
    row_end: int
    col_start: int
    col_end: int
    cell_id: str
    text: str
    value: str | None = None
    group_index: int | None = None
    confidence: str = "high"
    reasons: tuple[str, ...] = ()
    supporting_cell_ids: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "type": self.token_type.value,
            "table_index": self.table_index,
            "row_start": self.row_start,
            "row_end": self.row_end,
            "col_start": self.col_start,
            "col_end": self.col_end,
            "cell_id": self.cell_id,
            "text": self.text,
            "value": self.value,
            "group_index": self.group_index,
            "confidence": self.confidence,
            "reasons": list(self.reasons),
            "supporting_cell_ids": list(self.supporting_cell_ids),
        }


@dataclass
class FieldCandidate:
    value: str
    evidence_cell_ids: list[str] = field(default_factory=list)
    confidence_flags: list[str] = field(default_factory=list)

    def append(self, value: str, cell_ids: Sequence[str], separator: str = " ") -> None:
        value = clean_str(value)
        if value:
            self.value = clean_str(f"{self.value}{separator}{value}") if self.value else value
        for cell_id in cell_ids:
            if cell_id not in self.evidence_cell_ids:
                self.evidence_cell_ids.append(cell_id)


@dataclass
class CourseCandidate:
    candidate_id: str
    table_index: int
    group_index: int
    row_start: int
    row_end: int
    code: FieldCandidate | None = None
    title: FieldCandidate | None = None
    units: FieldCandidate | None = None
    prerequisites: FieldCandidate | None = None
    year_level: FieldCandidate | None = None
    semester: FieldCandidate | None = None
    source_cell_ids: list[str] = field(default_factory=list)
    confidence_flags: list[str] = field(default_factory=list)
    discarded_fragments: list[dict[str, Any]] = field(default_factory=list)

    def absorb(self, field_name: str, candidate: FieldCandidate | None) -> None:
        if candidate is None or not candidate.value:
            return
        current = getattr(self, field_name)
        if current is None:
            setattr(self, field_name, candidate)
        else:
            current.append(candidate.value, candidate.evidence_cell_ids)
            if "adjacent_row_continuation" not in current.confidence_flags:
                current.confidence_flags.append("adjacent_row_continuation")
        for cell_id in candidate.evidence_cell_ids:
            if cell_id not in self.source_cell_ids:
                self.source_cell_ids.append(cell_id)


@dataclass
class CurriculumSection:
    table_index: int
    year_level: str
    semester_by_group: dict[int, str]
    start_row: int
    end_row: int
    evidence_cells: list[str] = field(default_factory=list)
    confidence_flags: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "table_index": self.table_index,
            "year_level": self.year_level,
            "semester_by_group": {str(k): v for k, v in self.semester_by_group.items()},
            "start_row": self.start_row,
            "end_row": self.end_row,
            "evidence_cells": list(self.evidence_cells),
            "confidence_flags": list(self.confidence_flags),
        }


class SemanticRepairProvider(Protocol):
    """Callable boundary for an optional evidence-constrained repair model."""

    def __call__(self, packet: Mapping[str, Any]) -> Mapping[str, Any] | str: ...


MULTIPART_CODE = re.compile(
    r"^(?:"
    r"[A-Za-z]{1,8}(?:[\s-]+[A-Z]{1,6})?[\s-]*\d{1,4}[A-Za-z]*(?:/[A-Za-z0-9]+)?"
    r"|[A-Za-z]{1,8}\s+Elect(?:ive)?\s+\d{1,2}(?:/L)?"
    r"|GE\s*[-:]\s*[A-Za-z]{2,8}"
    r")$",
    re.IGNORECASE,
)


def is_probable_course_code(text: str) -> bool:
    value = clean_str(text)
    if not value or len(value) > 30 or DISQUALIFYING_CODE_WORDS.search(value):
        return False
    if value.upper() in NON_COURSE_CODES or is_banner_text(value):
        return False
    if is_code_like_token(value):
        return True
    if not MULTIPART_CODE.match(value):
        return False
    # Multi-word codes must look like abbreviations. This rejects titles such
    # as "History of Architecture 3" while retaining "COMM RE 12".
    words = re.findall(r"[A-Za-z]+", value)
    if len(words) >= 2 and words[0].istitle() and words[1].islower():
        return False
    return True


def _cell_for_column(table: NormalizedTable, row: int, col: int) -> NormalizedCell | None:
    candidates = [cell for cell in table.cells if cell.overlaps(row, col)]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda cell: (
            cell.row_span * cell.col_span,
            0 if cell.row_start == row else 1,
            cell.col_start,
            cell.cell_id,
        ),
    )


def _cells_in_group_row(
    table: NormalizedTable, row: int, group: ColumnGroup
) -> list[NormalizedCell]:
    left, right = min(group.span()), max(group.span()) + 1
    return sorted(
        (
            cell
            for cell in table.cells_on_row(row)
            if cell.col_start < right and cell.col_end > left
        ),
        key=lambda cell: (cell.col_start, cell.col_end, cell.cell_id),
    )


def _field_at(table: NormalizedTable, row: int, col: int) -> FieldCandidate | None:
    cell = _cell_for_column(table, row, col)
    if cell is None or not cell.text:
        return None
    return FieldCandidate(cell.text, [cell.cell_id])


def _split_year_banners(
    table: NormalizedTable, groups: Sequence[ColumnGroup]
) -> list[tuple[NormalizedCell, NormalizedCell, str]]:
    """Find year headings split at the boundary between two course groups."""
    if len(groups) < 2:
        return []
    ordinal_words = {"FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH",
                     "1ST", "2ND", "3RD", "4TH", "5TH"}
    found: list[tuple[NormalizedCell, NormalizedCell, str]] = []
    for ordinal in table.cells:
        if (clean_str(ordinal.text).upper() not in ordinal_words
                or not groups[0].unit_idx < ordinal.col_start <= groups[1].code_idx):
            continue
        for year_cell in table.cells:
            next_row = year_cell.row_start == ordinal.row_start + 1
            adjacent = (year_cell.col_start == ordinal.col_end if not next_row
                        else ordinal.col_start <= year_cell.col_start < ordinal.col_end)
            if (year_cell.row_start not in (ordinal.row_start, ordinal.row_start + 1)
                    or not adjacent or not re.match(r"^YEAR\b", year_cell.text, re.IGNORECASE)):
                continue
            year = match_year_label(f"{ordinal.text} {year_cell.text}")
            if year:
                found.append((ordinal, year_cell, year))
                break
    return found


def tokenize_table(table: NormalizedTable, groups: Sequence[ColumnGroup]) -> list[StructuralToken]:
    """Classify immutable source cells. Interpretations never replace source text."""
    tokens: list[StructuralToken] = []
    group_for_col: dict[int, int] = {}
    for group in groups:
        for col in group.span():
            group_for_col[col] = group.index

    for cell in table.cells:
        text = cell.text
        if not text:
            continue
        span_ratio = cell.col_span / max(table.num_cols, 1)
        year = match_year_label(text)
        semesters = match_semester_labels(text)
        header_kind = classify_header_cell(text)
        group_index = group_for_col.get(cell.col_start)
        common = dict(
            table_index=table.table_index,
            row_start=cell.row_start,
            row_end=cell.row_end,
            col_start=cell.col_start,
            col_end=cell.col_end,
            cell_id=cell.cell_id,
            text=text,
            group_index=group_index,
        )

        overlaps = _groups_overlapping_cell(cell, groups)
        row_has_course = any(
            other.cell_id != cell.cell_id
            and other.row_start == cell.row_start
            and is_probable_course_code(other.text)
            and any(other.col_start in group.span() for group in overlaps)
            for other in table.cells_on_row(cell.row_start)
        )
        structural = span_ratio >= 0.45 or (
            cell.col_span >= 2 and is_banner_text(text) and not row_has_course
        )

        if year and structural:
            tokens.append(
                StructuralToken(
                    TokenType.YEAR_MARKER,
                    value=year,
                    reasons=("year_text", "wide_span" if span_ratio >= 0.45 else "pure_banner"),
                    **common,
                )
            )
        inline_semester = bool(
            INLINE_SEMESTER_PREFIX.match(text)
            and any(cell.col_start in (group.code_idx, group.title_idx) for group in groups)
        )
        standalone_semester = bool(
            is_banner_text(text) and not row_has_course
            and len(overlaps) == 1
            and cell.col_start in (overlaps[0].code_idx, overlaps[0].title_idx)
            and not any(
                other.text and not is_banner_text(other.text)
                and any(other.col_start <= group.code_idx < other.col_end for group in groups)
                for other in table.cells_on_row(cell.row_start)
            )
        )
        if semesters and (structural or inline_semester or standalone_semester):
            for _position, semester in semesters:
                tokens.append(
                    StructuralToken(
                        TokenType.SEMESTER_MARKER,
                        value=semester,
                        reasons=("semester_text", "inline_course_heading" if inline_semester else
                                 "standalone_banner" if standalone_semester else "geometric_span"),
                        **common,
                    )
                )
        if header_kind != "other":
            tokens.append(StructuralToken(TokenType.HEADER, value=header_kind, **common))
        elif extract_grand_total(text) is not None:
            tokens.append(StructuralToken(TokenType.PROGRAM_TOTAL, value=text, **common))
        elif TOTAL_ROW_PATTERN.search(text):
            tokens.append(StructuralToken(TokenType.TERM_TOTAL, value=text, **common))
        elif is_probable_course_code(text):
            tokens.append(StructuralToken(TokenType.COURSE_CODE_CANDIDATE, value=text, **common))
        elif is_unit_like_token(text):
            tokens.append(StructuralToken(TokenType.UNIT_CANDIDATE, value=text, **common))
        elif not year and not semesters and header_kind == "other":
            tokens.append(
                StructuralToken(TokenType.UNKNOWN, value=text, confidence="unclassified", **common)
            )
    for ordinal, year_cell, year in _split_year_banners(table, groups):
        marker_row = year_cell.row_start
        if not any(
            (code := _field_at(table, marker_row, group.code_idx))
            and is_probable_course_code(re.sub(r"^YEAR\b\s*", "", code.value,
                                           count=1, flags=re.IGNORECASE))
            for group in groups
        ):
            marker_row = min(marker_row + 1, table.num_rows)
        if any(token.token_type == TokenType.YEAR_MARKER and token.row_start == marker_row
               and token.value == year for token in tokens):
            continue
        tokens.append(StructuralToken(
            TokenType.YEAR_MARKER, table.table_index,
            marker_row, marker_row,
            ordinal.col_start, year_cell.col_end,
            ordinal.cell_id, f"{ordinal.text} {year_cell.text}",
            value=year, confidence="structural",
            reasons=("split_year_banner",), supporting_cell_ids=(year_cell.cell_id,),
        ))
    return tokens


def _groups_overlapping_cell(
    cell: NormalizedCell, groups: Sequence[ColumnGroup]
) -> list[ColumnGroup]:
    out: list[ColumnGroup] = []
    for group in groups:
        left, right = min(group.span()), max(group.span()) + 1
        if cell.col_start < right and cell.col_end > left:
            out.append(group)
    return out


def _semester_mapping_at_row(
    table: NormalizedTable,
    row: int,
    groups: Sequence[ColumnGroup],
    tokens: Sequence[StructuralToken],
) -> tuple[dict[int, str], list[str], list[str]]:
    """Map semester evidence to groups; never fan one label across many groups."""
    mapping: dict[int, str] = {}
    evidence: list[str] = []
    problems: list[str] = []
    token_cells = {
        token.cell_id
        for token in tokens
        if token.token_type == TokenType.SEMESTER_MARKER and token.row_start == row
    }
    cells_by_id = table.cell_map()
    for cell_id in sorted(token_cells):
        cell = cells_by_id[cell_id]
        labels = [label for _position, label in match_semester_labels(cell.text)]
        overlaps = _groups_overlapping_cell(cell, groups)
        if len(labels) == len(overlaps) and labels:
            for group, label in zip(overlaps, labels):
                mapping[group.index] = label
            evidence.append(cell_id)
        elif len(labels) == 1 and len(overlaps) == 1:
            mapping[overlaps[0].index] = labels[0]
            evidence.append(cell_id)
        elif len(labels) == 1 and len(overlaps) > 1:
            label = labels[0]
            label_lower = label.lower()
            if "1st" in label_lower or "first" in label_lower:
                mapping[overlaps[0].index] = label
                if len(overlaps) >= 2:
                    mapping[overlaps[1].index] = "2nd Semester"
            elif ("2nd" in label_lower or "second" in label_lower) and len(overlaps) >= 2:
                mapping[overlaps[0].index] = "1st Semester"
                mapping[overlaps[1].index] = label
            elif ("3rd" in label_lower or "third" in label_lower) and len(overlaps) >= 3:
                mapping[overlaps[0].index] = "1st Semester"
                mapping[overlaps[1].index] = "2nd Semester"
                mapping[overlaps[2].index] = label
            else:
                for group in overlaps:
                    mapping[group.index] = label
            evidence.append(cell_id)
        else:
            problems.append(
                f"semester cell {cell_id} has {len(labels)} label(s) for "
                f"{len(overlaps)} column group(s)"
            )
    for group in groups:
        if group.index in mapping:
            continue
        code = _field_at(table, row, group.code_idx)
        title = _field_at(table, row, group.title_idx)
        if code and title and re.match(r"^FIRST\b", code.value, re.IGNORECASE) and re.match(
            r"^SEMESTER\b", title.value, re.IGNORECASE
        ):
            mapping[group.index] = "1st Semester"
            evidence.extend([code.evidence_cell_ids[0], title.evidence_cell_ids[0]])
    return mapping, evidence, problems


def build_curriculum_sections(
    evidence: ProspectusEvidence,
    table: NormalizedTable,
    groups: Sequence[ColumnGroup],
    tokens: Sequence[StructuralToken],
) -> tuple[list[CurriculumSection], list[dict[str, Any]]]:
    """Build explicit year/semester-bounded sections from structural evidence."""
    anomalies: list[dict[str, Any]] = []
    year_tokens: list[StructuralToken] = []
    seen_year_rows: set[tuple[int, str]] = set()
    for token in sorted(tokens, key=lambda t: (t.row_start, t.col_start, t.cell_id)):
        if token.token_type != TokenType.YEAR_MARKER or not token.value:
            continue
        key = (token.row_start, token.value)
        if key not in seen_year_rows:
            year_tokens.append(token)
            seen_year_rows.add(key)

    if year_tokens and year_tokens[0].row_start > 0:
        early_semesters = [t for t in tokens if t.token_type == TokenType.SEMESTER_MARKER and t.row_start < year_tokens[0].row_start]
        if early_semesters:
            year_tokens.insert(0, StructuralToken(
                TokenType.YEAR_MARKER,
                table.table_index,
                0,
                0,
                0,
                table.num_cols,
                "",
                "1st Year",
                value="1st Year",
                confidence="inferred",
                reasons=("inferred_from_early_semesters",)
            ))

    if not year_tokens and table.table_index in evidence.table_year_hints:
        year = evidence.table_year_hints[table.table_index]
        source_id = evidence.table_year_hint_sources.get(table.table_index, "")
        year_tokens.append(
            StructuralToken(
                TokenType.YEAR_MARKER,
                table.table_index,
                0,
                0,
                0,
                table.num_cols,
                source_id,
                year,
                value=year,
                confidence="document_order",
                reasons=("preceding_docling_text",),
            )
        )

    # Two-up prospectuses close both terms before starting the next year.
    # Docling sometimes omits the intervening year banner while retaining totals.
    for row in range(table.num_rows - 1):
        if any(token.row_start in (row, row + 1) for token in year_tokens):
            continue
        if not groups or not all(_is_total_row_for_group(table, row, group) for group in groups):
            continue
        code_columns = {group.code_idx for group in groups}
        if not any(
            is_probable_course_code(cell.text)
            and any(cell.col_start <= col < cell.col_end for col in code_columns)
            for next_row in range(row + 1, min(row + 3, table.num_rows))
            for cell in table.cells_on_row(next_row)
        ):
            continue
        previous = max((token for token in year_tokens if token.row_start < row),
                       key=lambda token: token.row_start, default=None)
        next_order = YEAR_ORDER.get(previous.value, 0) + 1 if previous else 0
        next_year = next((label for label, order in YEAR_ORDER.items() if order == next_order), None)
        following = min((token for token in year_tokens if token.row_start > row + 1),
                        key=lambda token: token.row_start, default=None)
        if not next_year or not following or YEAR_ORDER.get(following.value, 0) <= next_order:
            continue
        source = next((cell for cell in table.cells_on_row(row) if TOTAL_ROW_PATTERN.search(cell.text)), None)
        year_tokens.append(StructuralToken(
            TokenType.YEAR_MARKER, table.table_index, row + 1, row + 1,
            0, table.num_cols, source.cell_id if source else "", next_year,
            value=next_year, confidence="structural",
            reasons=("preceding_two_term_totals",),
        ))
    year_tokens.sort(key=lambda token: token.row_start)

    if not year_tokens:
        anomalies.append(
            {
                "id": f"t{table.table_index}-missing-year",
                "type": "missing_year_marker",
                "table_index": table.table_index,
                "row": 0,
                "reason": "table contains no verified year marker",
                "source_cell_ids": [],
            }
        )
        return [], anomalies

    sections: list[CurriculumSection] = []
    last_mapping: dict[int, str] = {}
    for year_pos, year_token in enumerate(year_tokens):
        year_mapping: dict[int, str] = {}
        year_search_start = max(0, year_token.row_start)
        year_end = (
            year_tokens[year_pos + 1].row_start
            if year_pos + 1 < len(year_tokens)
            else table.num_rows
        )
        semester_rows = sorted(
            {
                token.row_start
                for token in tokens
                if token.token_type == TokenType.SEMESTER_MARKER
                and year_search_start <= token.row_start < year_end
            }
        )
        events: list[tuple[int, int, dict[int, str], list[str]]] = []
        for semester_row in semester_rows:
            mapping, semester_evidence, problems = _semester_mapping_at_row(
                table, semester_row, groups, tokens
            )
            for problem in problems:
                anomalies.append(
                    {
                        "id": f"t{table.table_index}-r{semester_row}-semester-ambiguous",
                        "type": "semester_mapping_ambiguous",
                        "table_index": table.table_index,
                        "row": semester_row,
                        "reason": problem,
                        "source_cell_ids": semester_evidence,
                    }
                )
            row_end = max(
                (
                    token.row_end
                    for token in tokens
                    if token.token_type == TokenType.SEMESTER_MARKER
                    and token.row_start == semester_row
                ),
                default=semester_row + 1,
            )
            if any(
                "inline_course_heading" in token.reasons
                for token in tokens
                if token.token_type == TokenType.SEMESTER_MARKER and token.row_start == semester_row
            ):
                row_end = semester_row
            if year_token.row_start == semester_row:
                row_end = max(row_end, year_token.row_end)
            if mapping:
                year_mapping.update(mapping)
                last_mapping = year_mapping.copy()
                events.append((semester_row, row_end, year_mapping.copy(), semester_evidence))

        if not events:
            if last_mapping:
                # Inherit mapping from the previous section
                start = year_search_start if year_token.row_end == year_token.row_start else year_search_start + 1
                events.append((year_search_start, start, last_mapping.copy(), []))
            else:
                anomalies.append(
                    {
                        "id": f"t{table.table_index}-r{year_search_start}-missing-semester",
                        "type": "missing_semester_marker",
                        "table_index": table.table_index,
                        "row": year_search_start,
                        "reason": f"{year_token.value} has no verified semester mapping",
                        "source_cell_ids": [year_token.cell_id, *year_token.supporting_cell_ids]
                        if year_token.cell_id else [],
                    }
                )
                sections.append(
                    CurriculumSection(
                        table.table_index,
                        year_token.value or "",
                        {},
                        year_token.row_end,
                        year_end,
                        [year_token.cell_id, *year_token.supporting_cell_ids]
                        if year_token.cell_id else [],
                        ["missing_semester_mapping"],
                    )
                )
                continue

        for event_pos, (event_row, event_end, mapping, semester_evidence) in enumerate(events):
            section_end = events[event_pos + 1][0] if event_pos + 1 < len(events) else year_end
            missing_groups = [group.index for group in groups if group.index not in mapping]
            flags: list[str] = []
            if missing_groups:
                flags.append("incomplete_semester_mapping")
                anomalies.append(
                    {
                        "id": f"t{table.table_index}-r{event_row}-missing-groups",
                        "type": "missing_semester_for_group",
                        "table_index": table.table_index,
                        "row": event_row,
                        "reason": f"semester not verified for column group(s) {missing_groups}",
                        "source_cell_ids": semester_evidence,
                    }
                )
            cells = [year_token.cell_id] if year_token.cell_id else []
            cells.extend(year_token.supporting_cell_ids)
            cells.extend(cell_id for cell_id in semester_evidence if cell_id not in cells)
            sections.append(
                CurriculumSection(
                    table.table_index,
                    year_token.value or "",
                    mapping,
                    event_end,
                    section_end,
                    cells,
                    flags,
                )
            )
    return sections, anomalies


def _row_field_candidates(
    table: NormalizedTable, row: int, group: ColumnGroup,
    groups: Sequence[ColumnGroup],
) -> dict[str, FieldCandidate | None]:
    fields: dict[str, FieldCandidate | None] = {
        "code": _field_at(table, row, group.code_idx),
        "title": _field_at(table, row, group.title_idx),
        "units": _field_at(table, row, group.unit_idx),
        "prerequisites": _field_at(table, row, group.prereq_idx),
    }
    split_years = _split_year_banners(table, groups)
    for ordinal, year_cell, _year in split_years:
        for name, field in fields.items():
            if field is None:
                continue
            if ordinal.row_start == row and ordinal.cell_id in field.evidence_cell_ids:
                fields[name] = None
            elif year_cell.row_start == row and year_cell.cell_id in field.evidence_cell_ids:
                remainder = re.sub(r"^YEAR\b\s*", "", field.value, count=1, flags=re.IGNORECASE)
                fields[name] = (FieldCandidate(remainder, field.evidence_cell_ids,
                                               ["split_year_banner"]) if remainder else None)
    code, title = fields["code"], fields["title"]
    if not code and title and fields["units"] and is_unit_like_token(fields["units"].value):
        fused = re.match(
            r"^([A-Z]{2,8}(?:[\s-]+[A-Z]{2,8})?[\s-]*\d{1,4}(?:/[A-Z0-9]+)?)\s+(.+)$",
            title.value,
        )
        if fused and is_probable_course_code(fused.group(1)):
            fields["code"] = FieldCandidate(fused.group(1), title.evidence_cell_ids, ["fused_code_title"])
            fields["title"] = FieldCandidate(fused.group(2), title.evidence_cell_ids, ["fused_code_title"])
            code, title = fields["code"], fields["title"]
    if code and title and re.match(r"^SEMESTER\s+", title.value, re.IGNORECASE):
        first = re.match(r"^FIRST\s+(.+)$", code.value, re.IGNORECASE)
        if first and is_probable_course_code(first.group(1)):
            fields["code"] = FieldCandidate(first.group(1), code.evidence_cell_ids, ["split_semester_heading"])
            fields["title"] = FieldCandidate(
                re.sub(r"^SEMESTER\s+", "", title.value, flags=re.IGNORECASE),
                title.evidence_cell_ids, ["split_semester_heading"],
            )
    code = fields["code"]
    inline = INLINE_SEMESTER_PREFIX.match(code.value) if code else None
    if inline:
        parts = inline.group(1).split()
        for length in range(min(3, len(parts)), 0, -1):
            possible_code = " ".join(parts[:length])
            if is_probable_course_code(possible_code):
                fields["code"] = FieldCandidate(possible_code, code.evidence_cell_ids, ["inline_course_heading"])
                remainder = " ".join(parts[length:])
                if remainder:
                    fields["title"] = FieldCandidate(remainder, code.evidence_cell_ids, ["inline_course_heading"])
                break
    code = fields["code"]
    numeric_prefix = re.match(r"^\d{1,3}\s+(.+)$", code.value) if code else None
    if numeric_prefix and is_probable_course_code(numeric_prefix.group(1)):
        fields["code"] = FieldCandidate(
            numeric_prefix.group(1), code.evidence_cell_ids, ["leading_numeric_bleed"]
        )
    code = fields["code"]
    if code and not is_probable_course_code(code.value) and not TOTAL_ROW_PATTERN.search(code.value):
        parts = code.value.split()
        for length in range(len(parts) - 1, 0, -1):
            possible_code = " ".join(parts[:length])
            if is_probable_course_code(possible_code):
                fields["code"] = FieldCandidate(possible_code, code.evidence_cell_ids, ["fused_code_title"])
                prefix = " ".join(parts[length:])
                old_title = fields["title"]
                fields["title"] = FieldCandidate(
                    clean_str(f"{prefix} {old_title.value if old_title else ''}"),
                    list(dict.fromkeys(code.evidence_cell_ids + (old_title.evidence_cell_ids if old_title else []))),
                    ["fused_code_title"],
                )
                break
    title = fields["title"]
    inline = INLINE_SEMESTER_PREFIX.match(title.value) if title else None
    if inline:
        fields["title"] = FieldCandidate(inline.group(1), title.evidence_cell_ids, ["inline_course_heading"])
    prereq = fields["prerequisites"]
    fused_unit = re.match(r"^(\d+(?:/\d+)?)\s+(.+)$", prereq.value) if prereq else None
    if not fields["units"] and fused_unit:
        fields["units"] = FieldCandidate(fused_unit.group(1), prereq.evidence_cell_ids, ["fused_unit_prerequisite"])
        fields["prerequisites"] = FieldCandidate(
            fused_unit.group(2), prereq.evidence_cell_ids, ["fused_unit_prerequisite"]
        )
    cells = _cells_in_group_row(table, row, group)
    structural_ids = {
        cell.cell_id
        for cell in cells
        if match_year_label(cell.text)
        or match_semester_labels(cell.text)
        or classify_header_cell(cell.text) != "other"
    }
    structural_ids.update(cell.cell_id for ordinal, year_cell, _year in split_years
                          for cell in (ordinal, year_cell)
                          if cell.row_start == row and (cell == ordinal or clean_str(cell.text).upper() == "YEAR"))

    code = fields["code"]
    if code is None or not code.value:
        hits = [
            cell for cell in cells
            if cell.cell_id not in structural_ids
            and cell.col_start in (group.code_idx, group.title_idx)
            and is_probable_course_code(cell.text)
        ]
        if len(hits) == 1:
            fields["code"] = FieldCandidate(
                hits[0].text, [hits[0].cell_id], ["geometry_recovered_code"]
            )

    units = fields["units"]
    if units is None or not is_unit_like_token(units.value):
        hits = [cell for cell in cells if cell.cell_id not in structural_ids and is_unit_like_token(cell.text)]
        if len(hits) == 1:
            fields["units"] = FieldCandidate(
                hits[0].text, [hits[0].cell_id], ["geometry_recovered_units"]
            )

    used = {
        cell_id
        for candidate in fields.values()
        if candidate is not None
        for cell_id in candidate.evidence_cell_ids
    }
    title = fields["title"]
    if title is None or any(cell_id in structural_ids for cell_id in title.evidence_cell_ids):
        remaining = [
            cell
            for cell in cells
            if cell.cell_id not in used
            and cell.cell_id not in structural_ids
            and not is_probable_course_code(cell.text)
            and not is_unit_like_token(cell.text)
            and not TOTAL_ROW_PATTERN.search(cell.text)
        ]
        if remaining:
            best = max(remaining, key=lambda cell: (len(cell.text), -cell.col_start))
            fields["title"] = FieldCandidate(
                best.text, [best.cell_id], ["geometry_recovered_title"]
            )
    return fields


def _candidate_has_payload(fields: Mapping[str, FieldCandidate | None]) -> bool:
    return any(candidate is not None and candidate.value for candidate in fields.values())


def _is_total_row_for_group(table: NormalizedTable, row: int, group: ColumnGroup) -> bool:
    cells = _cells_in_group_row(table, row, group)
    if any(
        TOTAL_ROW_PATTERN.search(cell.text)
        for cell in cells
        if cell.text and cell.col_start <= group.code_idx < cell.col_end
    ):
        return True
    # A damaged TOTAL label may survive only in the opposite group; a bare
    # numeric unit cell on that same row is still a checksum, not a course.
    unit = _field_at(table, row, group.unit_idx)
    code = _field_at(table, row, group.code_idx)
    return bool(
        unit and is_unit_like_token(unit.value)
        and (not code or not code.value)
        and any(
            TOTAL_ROW_PATTERN.search(cell.text)
            and cell.col_start not in group.span()
            for cell in table.cells_on_row(row)
        )
    )


def _strip_structural_prerequisite_bleed(
    raw: str, year_level: str, evidence_ids: Sequence[str]
) -> tuple[str, list[dict[str, Any]]]:
    """Remove a year word only when it prefixes a code-like prerequisite run."""
    ordinal = {
        "1st Year": "FIRST",
        "2nd Year": "SECOND",
        "3rd Year": "THIRD",
        "4th Year": "FOURTH",
        "5th Year": "FIFTH",
    }.get(year_level)
    value = clean_str(raw)
    if not ordinal or not value:
        return value, []
    pattern = re.compile(
        rf"^({ordinal}(?:\s+YEAR)?)\s+(?=[A-Z]{{1,8}}(?:[\s-]+[A-Z]{{1,6}})?[\s-]*\d)",
        re.IGNORECASE,
    )
    match = pattern.match(value)
    if not match:
        return value, []
    cleaned = clean_str(value[match.end() :])
    return cleaned, [
        {
            "text": match.group(1),
            "source_cell_ids": list(evidence_ids),
            "reason": "structural year-banner bleed before prerequisite code",
        }
    ]


def _union_bbox(cells: Sequence[NormalizedCell]) -> tuple[int | None, list[float] | None]:
    boxes = [cell.bbox for cell in cells if cell.bbox and cell.bbox.is_complete()]
    if not boxes:
        return None, None
    pages = {box.page for box in boxes}
    page = next(iter(pages)) if len(pages) == 1 else None
    if page is None:
        return None, None
    return page, [
        min(float(box.left) for box in boxes if box.left is not None),
        min(float(box.top) for box in boxes if box.top is not None),
        max(float(box.right) for box in boxes if box.right is not None),
        max(float(box.bottom) for box in boxes if box.bottom is not None),
    ]


def _make_provenance(
    evidence: ProspectusEvidence,
    table_index: int,
    source_cell_ids: Sequence[str],
    resolution_method: str = "deterministic",
    repair_id: str | None = None,
) -> dict[str, Any]:
    all_cells = evidence.all_cells()
    unique_ids = list(dict.fromkeys(cell_id for cell_id in source_cell_ids if cell_id))
    cells = [all_cells[cell_id] for cell_id in unique_ids if cell_id in all_cells]
    page, bbox = _union_bbox(cells)
    return {
        "source_document": None,
        "raw_docling_json": None,
        "table_index": table_index,
        "source_cell_ids": unique_ids,
        "source_cells": [cell.as_evidence_dict() for cell in cells],
        "page": page,
        "bbox": bbox,
        "resolution_method": resolution_method,
        "repair_id": repair_id,
        "valid": bool(unique_ids) and len(cells) == len(unique_ids),
        "highlightable": page is not None and bbox is not None,
    }


def _assemble_section_candidates(
    evidence: ProspectusEvidence,
    table: NormalizedTable,
    groups: Sequence[ColumnGroup],
    section: CurriculumSection,
    result: GridParseResult,
) -> list[CourseCandidate]:
    candidates: list[CourseCandidate] = []
    pending: dict[int, CourseCandidate] = {}
    grid = project_table_to_grid(table)

    def flush(group_index: int) -> None:
        candidate = pending.pop(group_index, None)
        if candidate is not None:
            candidates.append(candidate)

    for row in range(section.start_row, section.end_row):
        row_cells = table.cells_on_row(row)
        if not row_cells:
            continue
        row_text = " ".join(dict.fromkeys(cell.text for cell in row_cells if cell.text))
        projected = grid[row] if row < len(grid) else []
        if is_header_row(projected) or ADMIN_METADATA_PATTERN.search(row_text):
            continue
        if any(
            cell.col_span / max(table.num_cols, 1) >= 0.45
            and (match_year_label(cell.text) or match_semester_labels(cell.text))
            for cell in row_cells
        ):
            continue
        if POLICY_NOTE_PATTERN.search(row_text):
            note = clean_str(row_text)
            if note and note not in result.policy_notes:
                result.policy_notes.append(note)

        for group in groups:
            if any(
                extract_grand_total(cell.text) is not None
                and cell.col_start <= group.code_idx < cell.col_end
                for cell in row_cells
            ):
                flush(group.index)
                continue
            code_cell = _field_at(table, row, group.code_idx)
            if (not code_cell or not is_probable_course_code(code_cell.value)) and any(
                POLICY_NOTE_PATTERN.search(cell.text)
                for cell in _cells_in_group_row(table, row, group)
            ):
                flush(group.index)
                continue
            previous = pending.get(group.index)
            leading_number = re.match(r"^(\d{1,3})\s+(.+)$", code_cell.value) if code_cell else None
            if (
                previous and previous.code
                and not is_probable_course_code(previous.code.value)
                and not re.search(r"\d", previous.code.value)
                and leading_number and is_probable_course_code(leading_number.group(2))
            ):
                previous.absorb(
                    "code", FieldCandidate(leading_number.group(1), code_cell.evidence_cell_ids,
                                           ["adjacent_code_suffix"])
                )
            fields = _row_field_candidates(table, row, group, groups)
            suffix_and_code = re.fullmatch(r"([A-Z]{2,3})\s+(.+)", fields["code"].value) if fields["code"] else None
            if (
                previous and previous.row_end == row and previous.code
                and previous.code.value.endswith(":") and suffix_and_code
                and suffix_and_code.group(2).isupper()
                and is_probable_course_code(suffix_and_code.group(2))
            ):
                previous.absorb("code", FieldCandidate(suffix_and_code.group(1), fields["code"].evidence_cell_ids))
                fields["code"] = FieldCandidate(
                    suffix_and_code.group(2), fields["code"].evidence_cell_ids, ["adjacent_code_suffix"]
                )
            semester = section.semester_by_group.get(group.index)
            mixed_total = None
            if _is_total_row_for_group(table, row, group):
                existing = pending.get(group.index)
                code_fragment = fields.get("code")
                units_fragment = fields.get("units")
                course_prefix = re.match(r"^(.+?)\s+TOTAL\b", code_fragment.value, re.IGNORECASE) if code_fragment else None
                split_units = re.fullmatch(r"(\d+(?:/\d+)?)\s+(\d{1,3})", units_fragment.value) if units_fragment else None
                if course_prefix and split_units and is_probable_course_code(course_prefix.group(1)):
                    fields["code"] = FieldCandidate(course_prefix.group(1), code_fragment.evidence_cell_ids)
                    fields["units"] = FieldCandidate(split_units.group(1), units_fragment.evidence_cell_ids)
                    mixed_total = int(split_units.group(2))
                else:
                    suffix = re.match(r"^(\d{1,3})\s+TOTAL\b", code_fragment.value, re.IGNORECASE) if code_fragment else None
                    if (
                        course_prefix and existing and existing.code
                        and norm_key(existing.code.value) == norm_key(course_prefix.group(1))
                        and not existing.prerequisites and fields.get("prerequisites")
                    ):
                        existing.absorb("prerequisites", fields["prerequisites"])
                    if suffix and existing and existing.code and not re.search(r"\d", existing.code.value):
                        existing.absorb("code", FieldCandidate(suffix.group(1), code_fragment.evidence_cell_ids))
                        for name in ("title", "prerequisites"):
                            fragment = fields.get(name)
                            if fragment and fragment.value and not TOTAL_ROW_PATTERN.search(fragment.value):
                                existing.absorb(name, fragment)
                        existing.row_end = row + 1
                    declared = _first_int(
                        candidate.value
                        for candidate in (
                            fields.get("units"),
                            fields.get("prerequisites"),
                            fields.get("title"),
                            fields.get("code"),
                        )
                        if candidate is not None
                    )
                    if declared is not None and semester:
                        result.declared_term_units[(section.year_level, semester)] = declared
                    flush(group.index)
                    continue
            if mixed_total is not None and semester:
                result.declared_term_units[(section.year_level, semester)] = mixed_total

            prior = pending.get(group.index)
            if (
                prior and prior.units and prior.row_end == row
                and fields.get("code") and is_probable_course_code(fields["code"].value)
                and fields.get("title") and not fields.get("units")
            ):
                spill = re.fullmatch(r"([1-9])\s+([1-9])", prior.units.value)
                if spill:
                    evidence_ids = prior.units.evidence_cell_ids
                    prior.units = FieldCandidate(spill.group(1), evidence_ids, ["adjacent_unit_spillover"])
                    fields["units"] = FieldCandidate(spill.group(2), evidence_ids, ["adjacent_unit_spillover"])
            if (
                prior and prior.title and prior.units
                and not fields.get("code") and fields.get("title") and fields.get("units")
                and row + 1 < section.end_row
                and _is_total_row_for_group(table, row + 1, group)
            ):
                following_code = _field_at(table, row + 1, group.code_idx)
                mixed_code = re.fullmatch(r"(.+?)\s+TOTAL", following_code.value, re.IGNORECASE) if following_code else None
                if mixed_code and is_probable_course_code(mixed_code.group(1)):
                    fragment = fields.get("prerequisites")
                    if (
                        prior.prerequisites and fragment
                        and re.fullmatch(r"[A-Z]{2,8}(?:\s+[A-Z]{2,8})?", prior.prerequisites.value)
                        and re.fullmatch(r"\d{1,3}(?:/[A-Z])?", fragment.value)
                        and is_probable_course_code(f"{prior.prerequisites.value} {fragment.value}")
                    ):
                        prior.absorb("prerequisites", fragment)
                        fields["prerequisites"] = None
                    flush(group.index)
                    fields["code"] = FieldCandidate(
                        mixed_code.group(1), following_code.evidence_cell_ids,
                        ["adjacent_code_on_total_row"],
                    )
                    if not fields.get("prerequisites"):
                        fields["prerequisites"] = _field_at(table, row + 1, group.prereq_idx)

            code = fields.get("code")
            title = fields.get("title")
            units = fields.get("units")
            prereq = fields.get("prerequisites")
            looks_course = bool(
                code
                and not re.search(r"[.!?]$", code.value)
                and looks_like_course(
                    code.value,
                    title.value if title else "",
                    units.value if units else "",
                )
            )
            starts_split_course = bool(code and is_probable_course_code(code.value))
            if looks_course or starts_split_course:
                existing = pending.get(group.index)
                if (
                    existing is not None and existing.row_end == row and existing.prerequisites
                    and re.fullmatch(r"(?:[1-5](?:ST|ND|RD|TH)|FIRST|SECOND|THIRD|FOURTH|FIFTH) YEAR",
                                     existing.prerequisites.value, re.IGNORECASE)
                    and prereq and re.match(r"^STANDING\b", prereq.value, re.IGNORECASE)
                ):
                    existing.absorb("prerequisites", FieldCandidate("Standing", prereq.evidence_cell_ids))
                    remainder = re.sub(r"^STANDING\b\s*", "", prereq.value, count=1, flags=re.IGNORECASE)
                    fields["prerequisites"] = prereq = (
                        FieldCandidate(remainder, prereq.evidence_cell_ids) if remainder else None
                    )
                if existing is not None and existing.row_end == row and existing.prerequisites and prereq:
                    previous_prereq = existing.prerequisites.value
                    carried = None
                    if re.fullmatch(r"[A-Z]{2,8}(?:\s+[A-Z]{2,8})?", previous_prereq):
                        fragment = re.match(r"^(\d{1,3}(?:/[A-Z])?)(?:\s+(.+))?$", prereq.value)
                        if fragment and is_probable_course_code(f"{previous_prereq} {fragment.group(1)}"):
                            carried = fragment
                    elif previous_prereq.endswith("&"):
                        carried = re.match(
                            r"^([A-Z]{1,8}(?:\s+[A-Z]{1,8})?\s*\d{1,3}(?:/[A-Z])?)(?:\s+(.+))?$",
                            prereq.value,
                        )
                        if carried and not is_probable_course_code(carried.group(1)):
                            carried = None
                    if carried:
                        existing.absorb("prerequisites", FieldCandidate(carried.group(1), prereq.evidence_cell_ids))
                        fields["prerequisites"] = prereq = (
                            FieldCandidate(carried.group(2), prereq.evidence_cell_ids)
                            if carried.group(2) else None
                        )
                if existing is not None and existing.row_end == row and existing.title and title:
                    if existing.title.value.count("(") > existing.title.value.count(")"):
                        wrapped = re.match(r"^([^()]*\))\s+(.+)$", title.value)
                        if wrapped:
                            separator = "" if existing.title.value.endswith("-") else " "
                            existing.title.append(wrapped.group(1), title.evidence_cell_ids, separator)
                            for cell_id in title.evidence_cell_ids:
                                if cell_id not in existing.source_cell_ids:
                                    existing.source_cell_ids.append(cell_id)
                            title = FieldCandidate(
                                wrapped.group(2), title.evidence_cell_ids,
                                ["adjacent_title_wrap"],
                            )
                            fields["title"] = title
                if (
                    existing is not None and existing.row_end == row
                    and existing.prerequisites and existing.prerequisites.value.endswith(",")
                    and prereq and re.fullmatch(r"[A-Za-z][A-Za-z0-9/-]{1,18}", prereq.value)
                ):
                    existing.absorb("prerequisites", prereq)
                    fields["prerequisites"] = prereq = None
                if (
                    existing is not None and existing.row_end == row
                    and all(
                        (getattr(existing, name).value if getattr(existing, name) else "")
                        == (fields[name].value if fields[name] else "")
                        for name in ("code", "title", "units", "prerequisites")
                    )
                ):
                    existing.row_end = row + 1
                    continue
                flush(group.index)
                candidate = CourseCandidate(
                    candidate_id=f"t{table.table_index}-r{row}-g{group.index}",
                    table_index=table.table_index,
                    group_index=group.index,
                    row_start=row,
                    row_end=row + 1,
                    code=code,
                    title=title,
                    units=units,
                    prerequisites=prereq,
                    year_level=FieldCandidate(section.year_level, section.evidence_cells[:1]),
                    semester=(
                        FieldCandidate(semester, section.evidence_cells[1:]) if semester else None
                    ),
                )
                for field_value in (code, title, units, prereq):
                    if field_value:
                        for cell_id in field_value.evidence_cell_ids:
                            if cell_id not in candidate.source_cell_ids:
                                candidate.source_cell_ids.append(cell_id)
                for cell_id in section.evidence_cells:
                    if cell_id and cell_id not in candidate.source_cell_ids:
                        candidate.source_cell_ids.append(cell_id)
                if not semester:
                    candidate.confidence_flags.append("semester_unverified")
                    result.anomalies.append(
                        {
                            "id": f"{candidate.candidate_id}-semester",
                            "type": "course_without_verified_semester",
                            "candidate_id": candidate.candidate_id,
                            "table_index": table.table_index,
                            "row": row,
                            "reason": "course lies in a section without a verified semester mapping",
                            "source_cell_ids": candidate.source_cell_ids,
                        }
                    )
                pending[group.index] = candidate
                if mixed_total is not None:
                    flush(group.index)
                continue

            existing = pending.get(group.index)
            continuation_fields = {
                "title": title,
                "units": units,
                "prerequisites": prereq,
            }
            if (
                existing is not None 
                and any(item is not None and item.value for item in continuation_fields.values())
                and not (code and code.value and code.value.strip())
            ):
                for field_name, field_value in continuation_fields.items():
                    if field_value is None:
                        continue
                    # A projected code/title value can point to the same wide
                    # structural cell. Never append structural evidence.
                    if match_year_label(field_value.value) or match_semester_labels(field_value.value):
                        continue
                    existing.absorb(field_name, field_value)
                existing.row_end = max(existing.row_end, row + 1)
                if "adjacent_row_reconstruction" not in existing.confidence_flags:
                    existing.confidence_flags.append("adjacent_row_reconstruction")
            elif _candidate_has_payload(fields) and not _is_total_row_for_group(table, row, group):
                payload_ids = list(
                    dict.fromkeys(
                        cell_id
                        for item in fields.values()
                        if item is not None
                        for cell_id in item.evidence_cell_ids
                    )
                )
                if any(
                    is_probable_course_code(item.value)
                    for item in fields.values()
                    if item is not None
                ):
                    result.anomalies.append(
                        {
                            "id": f"t{table.table_index}-r{row}-g{group.index}-orphan",
                            "type": "unassembled_course_fragment",
                            "table_index": table.table_index,
                            "row": row,
                            "reason": "course-like evidence could not be assembled deterministically",
                            "source_cell_ids": payload_ids,
                        }
                    )

    for group in groups:
        flush(group.index)
    return candidates


def _candidate_to_raw_course(
    candidate: CourseCandidate,
    evidence: ProspectusEvidence,
    footnotes: FootnoteContext,
) -> dict[str, Any]:
    code_raw = candidate.code.value if candidate.code else ""
    title_raw = candidate.title.value if candidate.title else ""
    unit_raw = candidate.units.value if candidate.units else ""
    prereq_raw = candidate.prerequisites.value if candidate.prerequisites else ""
    title_with_units, unit_text = rescue_units_from_title(title_raw, unit_raw)
    title, marker = footnotes.clean_title(title_with_units, unit_text)
    year = candidate.year_level.value if candidate.year_level else None
    semester = candidate.semester.value if candidate.semester else None
    cleaned_prereq, discarded = _strip_structural_prerequisite_bleed(
        prereq_raw,
        year or "",
        candidate.prerequisites.evidence_cell_ids if candidate.prerequisites else [],
    )
    candidate.discarded_fragments.extend(discarded)
    code = canonicalize_course_code(code_raw, title)
    provenance = _make_provenance(
        evidence, candidate.table_index, candidate.source_cell_ids, "deterministic"
    )
    if discarded:
        provenance["discarded_fragments"] = discarded
        provenance["resolution_method"] = "deterministic_repair"
    return {
        "_candidate_id": candidate.candidate_id,
        "year_level": year,
        "semester": semester,
        "term_index": term_index(year or "", semester or ""),
        "course_code": code,
        "course_title": title,
        "title_raw": clean_str(title_raw),
        "footnote_marker": marker,
        "units": parse_units(unit_text),
        "prerequisites_raw": cleaned_prereq,
        "confidence_flags": list(candidate.confidence_flags),
        "provenance": provenance,
        "_source": {
            "table_index": candidate.table_index,
            "row_index": candidate.row_start,
            "column_group": candidate.group_index,
        },
    }


def detect_source_course_candidates(
    evidence: ProspectusEvidence,
    layouts: Mapping[int, Sequence[ColumnGroup]],
) -> list[dict[str, Any]]:
    """Permissive document-wide inventory constrained by code-column geometry."""
    found: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for table in evidence.tables:
        groups = layouts.get(table.table_index, [])
        code_columns = {group.code_idx for group in groups}
        for cell in table.cells:
            if not any(cell.col_start <= col < cell.col_end for col in code_columns):
                continue
            code = clean_str(cell.text)
            if not is_probable_course_code(code):
                continue
            key = (norm_key(code), cell.cell_id)
            if key in seen:
                continue
            seen.add(key)
            found.append(
                {
                    "code": code,
                    "normalized_code": norm_key(code),
                    "cell_ids": [cell.cell_id],
                    "table_index": table.table_index,
                    "page": cell.bbox.page if cell.bbox else None,
                    "bbox": cell.bbox.as_list() if cell.bbox else None,
                    "confidence": "high",
                }
            )
    return found


def _repair_packet_for_anomaly(
    anomaly: Mapping[str, Any], evidence: ProspectusEvidence, courses: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    table_index = int(anomaly.get("table_index", 0))
    row = int(anomaly.get("row", 0))
    table = next((t for t in evidence.tables if t.table_index == table_index), None)
    cells = []
    if table:
        cells = [
            cell.as_evidence_dict()
            for cell in table.cells
            if max(0, row - 2) <= cell.row_start < min(table.num_rows, row + 3)
        ]
    candidate_id = anomaly.get("candidate_id")
    deterministic = next(
        (course for course in courses if course.get("_candidate_id") == candidate_id), {}
    )
    return {
        "repair_id": f"repair-{anomaly.get('id')}",
        "anomaly_id": anomaly.get("id"),
        "candidate_id": candidate_id,
        "table_index": table_index,
        "row_window": [max(0, row - 2), row + 2],
        "reason": [anomaly.get("type")],
        "cells": cells,
        "deterministic_candidate": {
            key: deterministic.get(key)
            for key in (
                "course_code",
                "course_title",
                "units",
                "prerequisites_raw",
                "year_level",
                "semester",
            )
            if key in deterministic
        },
        "contract": {
            "allowed_fields": [
                "course_code",
                "course_title",
                "units_raw",
                "prerequisites_raw",
                "year_level",
                "semester",
            ],
            "evidence_required_for_every_non_null_field": True,
            "external_knowledge_forbidden": True,
            "ambiguity_must_be_returned_instead_of_guessing": True,
        },
    }


def _normalised_contains(haystack: str, needle: str) -> bool:
    h = re.sub(r"[^A-Z0-9]", "", clean_str(haystack).upper())
    n = re.sub(r"[^A-Z0-9]", "", clean_str(needle).upper())
    return bool(n) and n in h


def validate_repair_decision(
    packet: Mapping[str, Any],
    decision: Mapping[str, Any],
    evidence: ProspectusEvidence,
) -> tuple[bool, list[str]]:
    """Prove that every proposed field is supported by cited source cells."""
    errors: list[str] = []
    if not isinstance(decision.get("ambiguous"), bool):
        errors.append("decision.ambiguous must be a boolean")
    fields = decision.get("fields")
    if not isinstance(fields, Mapping):
        errors.append("decision.fields must be an object")
        return False, errors
    allowed = set(packet.get("contract", {}).get("allowed_fields", []))
    all_cells = evidence.all_cells()
    packet_ids = {cell.get("cell_id") for cell in packet.get("cells", [])}
    for field_name, proposal in fields.items():
        if field_name not in allowed:
            errors.append(f"unsupported repair field: {field_name}")
            continue
        if not isinstance(proposal, Mapping):
            errors.append(f"{field_name} must be an object")
            continue
        value = proposal.get("value")
        cited = proposal.get("evidence")
        if value is None:
            continue
        if not isinstance(cited, list) or not cited:
            errors.append(f"{field_name} has no evidence cell IDs")
            continue
        invalid = [cell_id for cell_id in cited if cell_id not in all_cells or cell_id not in packet_ids]
        if invalid:
            errors.append(f"{field_name} cites cells outside the packet: {invalid}")
            continue
        combined = " ".join(all_cells[cell_id].text for cell_id in cited)
        if field_name == "year_level":
            if not any(match_year_label(all_cells[cell_id].text) == value for cell_id in cited):
                errors.append("year_level is not supported by cited structural evidence")
        elif field_name == "semester":
            labels = [
                label
                for cell_id in cited
                for _position, label in match_semester_labels(all_cells[cell_id].text)
            ]
            if value not in labels:
                errors.append("semester is not supported by cited structural evidence")
        elif not _normalised_contains(combined, str(value)):
            errors.append(f"{field_name} value is not present in cited source text")
        elif field_name == "prerequisites_raw":
            source_prefix = re.match(
                r"^\s*((?:FIRST|SECOND|THIRD|FOURTH|FIFTH)(?:\s+YEAR)?)\b",
                combined,
                re.IGNORECASE,
            )
            value_prefix = re.match(
                r"^\s*(?:FIRST|SECOND|THIRD|FOURTH|FIFTH)(?:\s+YEAR)?\b",
                str(value),
                re.IGNORECASE,
            )
            if source_prefix and not value_prefix:
                recorded = any(
                    isinstance(item, Mapping)
                    and clean_str(item.get("text", "")).upper()
                    == clean_str(source_prefix.group(1)).upper()
                    and item.get("source_cell") in cited
                    for item in decision.get("discarded_fragments", []) or []
                )
                if not recorded:
                    errors.append("removed structural prerequisite prefix was not recorded")

    for discarded in decision.get("discarded_fragments", []) or []:
        if not isinstance(discarded, Mapping):
            errors.append("discarded fragment must be an object")
            continue
        cell_id = discarded.get("source_cell")
        text = discarded.get("text")
        if cell_id not in all_cells or cell_id not in packet_ids:
            errors.append(f"discarded fragment cites invalid cell {cell_id}")
        elif not _normalised_contains(all_cells[cell_id].text, str(text or "")):
            errors.append("discarded fragment is absent from its source cell")
    return not errors, errors


def _apply_valid_repair(
    packet: Mapping[str, Any],
    decision: Mapping[str, Any],
    courses: list[dict[str, Any]],
    evidence: ProspectusEvidence,
) -> bool:
    candidate_id = packet.get("candidate_id")
    course = next((item for item in courses if item.get("_candidate_id") == candidate_id), None)
    if course is None:
        return False
    mapping = {
        "course_code": "course_code",
        "course_title": "course_title",
        "prerequisites_raw": "prerequisites_raw",
        "year_level": "year_level",
        "semester": "semester",
    }
    cited_ids: list[str] = []
    for field_name, proposal in decision.get("fields", {}).items():
        if not isinstance(proposal, Mapping) or proposal.get("value") is None:
            continue
        if field_name == "units_raw":
            course["units"] = parse_units(proposal["value"])
        elif field_name in mapping:
            course[mapping[field_name]] = clean_str(proposal["value"])
        cited_ids.extend(proposal.get("evidence", []))
    course["term_index"] = term_index(course.get("year_level") or "", course.get("semester") or "")
    existing = course.get("provenance", {}).get("source_cell_ids", [])
    provenance = _make_provenance(
        evidence,
        int(packet.get("table_index", 0)),
        [*existing, *cited_ids],
        "llm_repair",
        str(packet.get("repair_id")),
    )
    provenance["discarded_fragments"] = list(decision.get("discarded_fragments", []) or [])
    course["provenance"] = provenance
    return True


def apply_semantic_repairs(
    result: GridParseResult,
    evidence: ProspectusEvidence,
    repair_provider: SemanticRepairProvider | None,
) -> None:
    """Call a model only for anomaly packets; invalid output never reaches courses."""
    result.repair_packets = [
        _repair_packet_for_anomaly(anomaly, evidence, result.courses)
        for anomaly in result.anomalies
    ]
    if repair_provider is None:
        return

    resolved_anomaly_ids: set[str] = set()
    for packet in result.repair_packets:
        try:
            raw = repair_provider(packet)
            decision = json.loads(raw) if isinstance(raw, str) else dict(raw)
        except Exception as exc:
            result.invalid_repairs.append(
                {
                    "repair_id": packet["repair_id"],
                    "errors": [f"repair provider failed: {type(exc).__name__}: {exc}"],
                }
            )
            continue
        valid, errors = validate_repair_decision(packet, decision, evidence)
        if decision.get("ambiguous") is True:
            valid = False
            errors.append("repair model returned ambiguous=true")
        if valid and _apply_valid_repair(packet, decision, result.courses, evidence):
            result.repairs.append(
                {
                    "repair_id": packet["repair_id"],
                    "anomaly_id": packet["anomaly_id"],
                    "status": "accepted",
                    "decision": decision,
                }
            )
            resolved_anomaly_ids.add(str(packet["anomaly_id"]))
        else:
            if valid:
                errors.append("repair target was not an existing deterministic candidate")
            result.invalid_repairs.append(
                {"repair_id": packet["repair_id"], "errors": errors, "decision": decision}
            )
    if resolved_anomaly_ids:
        result.anomalies = [
            anomaly
            for anomaly in result.anomalies
            if str(anomaly.get("id")) not in resolved_anomaly_ids
        ]


def parse_curriculum_evidence(
    evidence: ProspectusEvidence,
    repair_provider: SemanticRepairProvider | None = None,
) -> GridParseResult:
    """Parse canonical Docling evidence without year or semester defaults."""
    result = GridParseResult()
    layouts: dict[int, list[ColumnGroup]] = {}
    candidates: list[CourseCandidate] = []
    all_tokens: list[StructuralToken] = []

    for table in evidence.tables:
        grid = project_table_to_grid(table)
        groups, header_index = detect_column_groups(grid)
        layouts[table.table_index] = groups
        result.layout.append(
            {
                "table_index": table.table_index,
                "rows": table.num_rows,
                "columns": table.num_cols,
                "header_row": header_index,
                "column_groups": [group.as_dict() for group in groups],
                "canonical_cell_count": len(table.cells),
            }
        )
        if not groups:
            result.warnings.append(
                f"Table {table.table_index}: no usable column layout; table skipped."
            )
            continue
        if not any(
            is_probable_course_code(cell.text)
            and any(cell.col_start <= group.code_idx < cell.col_end for group in groups)
            for cell in table.cells
        ):
            continue
        if header_index < 0:
            result.warnings.append(
                f"Table {table.table_index}: no header row found; layout inferred from cell geometry/content."
            )
        tokens = tokenize_table(table, groups)
        all_tokens.extend(tokens)
        sections, anomalies = build_curriculum_sections(evidence, table, groups, tokens)
        result.anomalies.extend(anomalies)
        result.sections.extend(section.as_dict() for section in sections)
        for section in sections:
            candidates.extend(
                _assemble_section_candidates(evidence, table, groups, section, result)
            )
        for cell in table.cells:
            grand = extract_grand_total(cell.text)
            if grand is not None:
                result.declared_grand_total = grand
        for row in range(table.num_rows):
            grand = extract_grand_total(" ".join(cell.text for cell in table.cells_on_row(row)))
            if grand is not None:
                result.declared_grand_total = grand

    result.structural_tokens = [token.as_dict() for token in all_tokens]
    result.source_course_candidates = detect_source_course_candidates(evidence, layouts)

    titles = [candidate.title.value for candidate in candidates if candidate.title]
    units = [candidate.units.value for candidate in candidates if candidate.units]
    result.footnotes = FootnoteContext.build(titles, units)
    result.courses = [
        _candidate_to_raw_course(candidate, evidence, result.footnotes)
        for candidate in candidates
        if candidate.code and candidate.code.value
    ]

    parsed_keys = {norm_key(course["course_code"]) for course in result.courses}
    result.unclaimed_course_candidates = [
        candidate
        for candidate in result.source_course_candidates
        if candidate["normalized_code"] not in parsed_keys
    ]
    for index, candidate in enumerate(result.unclaimed_course_candidates):
        result.anomalies.append(
            {
                "id": f"unclaimed-{candidate['table_index']}-{index}-{candidate['normalized_code']}",
                "type": "unclaimed_course_candidate",
                "table_index": candidate["table_index"],
                "row": next(
                    (
                        cell.row_start
                        for table in evidence.tables
                        for cell in table.cells
                        if cell.cell_id in candidate["cell_ids"]
                    ),
                    0,
                ),
                "reason": f"high-confidence course code {candidate['code']} was not claimed",
                "source_cell_ids": candidate["cell_ids"],
            }
        )

    apply_semantic_repairs(result, evidence, repair_provider)
    return result


def evidence_from_grids(
    grids: Sequence[Sequence[Sequence[Any]]],
    table_year_hints: Mapping[int, str] | None = None,
) -> ProspectusEvidence:
    """Compatibility adapter for callers that still provide grid fixtures."""
    return ProspectusEvidence(
        tables=[normalized_table_from_grid(grid, index) for index, grid in enumerate(grids)],
        source_kind="grid-compatibility",
        table_year_hints=dict(table_year_hints or {}),
    )


def parse_curriculum_grids(
    grids: Sequence[Sequence[Sequence[str]]],
    table_year_hints: dict[int, str] | None = None,
) -> GridParseResult:
    """Temporary API-compatible wrapper over the canonical evidence parser."""
    return parse_curriculum_evidence(evidence_from_grids(grids, table_year_hints))


# =============================================================================
# 10. Post-processing: prerequisite resolution, electives, classification
# =============================================================================
ELECTIVE_OPTION = re.compile(
    r"^([A-Za-z][A-Za-z\.\s]{0,20}?Elect(?:ive)?\.?\s*(\d{1,2})\s*/\s*[A-Za-z0-9]+)\s*[\.\)]\s*(.+)$",
    re.IGNORECASE,
)


def sort_courses(courses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        courses,
        key=lambda c: (
            c.get("term_index", 99),
            c.get("_source", {}).get("table_index", 0),
            c.get("_source", {}).get("column_group", 0),
            c.get("_source", {}).get("row_index", 0),
        ),
    )


def classify_course(code: str, title: str) -> dict[str, Any]:
    """Flag electives, GE courses, NSTP/PE and thesis/practicum rows."""
    upper_code = clean_str(code).upper()
    upper_title = clean_str(title).upper()
    is_elective = bool(re.match(r"^(?:GE[- :]+)?(?:[A-Z]{1,8}\\s+)?ELECT(?:IVE)?(?:\\s*[:.-]?\\s*\\d{1,2})?(?:/L)?$", upper_code, re.IGNORECASE)) or bool(re.search(r"\\bELECTIVE\\b", upper_title))
    if upper_code.startswith("GE"):
        category = "General Education"
    elif upper_code.startswith(("NSTP", "PATH", "CWTS", "ROTC")):
        category = "NSTP / PATHFit"
    elif "THESIS" in upper_code or "PRACTICUM" in upper_code or "THESIS" in upper_title:
        category = "Capstone / Practicum"
    else:
        category = "Core / Major"
    return {
        "is_elective": is_elective,
        "elective_kind": ("General Education" if is_elective and upper_code.startswith("GE") else "Major")
        if is_elective
        else None,
        "category": category,
    }


def finalize_courses(
    courses: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], CodeIndex, list[dict[str, Any]]]:
    """Resolve prerequisites against the document's own codes and add flat fields."""
    index = CodeIndex(c["course_code"] for c in courses)
    finalized: list[dict[str, Any]] = []

    for course in courses:
        resolution = resolve_prerequisites(
            course.get("prerequisites_raw", ""),
            index,
            current_course_code=course.get("course_code", ""),
        )
        units = course.get("units") or parse_units("")
        classification = classify_course(course["course_code"], course["course_title"])

        record = dict(course)
        record.pop("_candidate_id", None)
        record.update(
            {
                "code": course["course_code"],
                "title": course["course_title"],
                "units": units,
                "total_units": units.get("total"),
                "lecture_units": units.get("lecture"),
                "lab_units": units.get("lab"),
                "prerequisites": resolution.resolved,
                "prerequisites_unresolved": resolution.unresolved,
                "standing_requirements": resolution.standing_rules,
                "elective_group": None,
                **classification,
            }
        )
        finalized.append(record)

    finalized = sort_courses(finalized)

    counts = Counter(c["course_code"] for c in finalized)
    duplicates = [
        {
            "course_code": code,
            "occurrences": [
                {"year_level": c["year_level"], "semester": c["semester"], "source": c["_source"]}
                for c in finalized
                if c["course_code"] == code
            ],
        }
        for code, count in counts.items()
        if count > 1
    ]
    return finalized, index, duplicates


def _iter_text_pairs(text_items: Sequence[Any]) -> Iterable[tuple[str, str]]:
    for item in text_items:
        if isinstance(item, Mapping):
            yield str(item.get("label", "text")), clean_str(item.get("text", ""))
        elif isinstance(item, (tuple, list)) and len(item) >= 2:
            yield str(item[0]), clean_str(item[1])


def parse_elective_tracks(text_items: Sequence[Any]) -> list[dict[str, Any]]:
    """Collect elective pools such as 'CS Elect 4/La. ...' into grouped options.

    Grouping keys off the elective number inside each option code, so a missing
    or reordered section header can no longer scramble the pools (v1 relied on
    header ordering and auto-created groups mid-stream).
    """
    grouped: dict[str, list[dict[str, str]]] = {}
    order: list[str] = []

    for _label, text in _iter_text_pairs(text_items):
        line = clean_str(text)
        if not line:
            continue
        for candidate in re.split(r"(?<=[a-z\)])\s{2,}", line):
            match = ELECTIVE_OPTION.match(clean_str(candidate))
            if not match:
                continue
            option_code = clean_str(match.group(1))
            number = match.group(2)
            title = clean_str(match.group(3))
            prefix_match = re.match(r"^([A-Za-z]+)", option_code)
            prefix = prefix_match.group(1).upper() if prefix_match else "CS"
            group_name = f"{prefix} Elective {number}"
            if group_name not in grouped:
                grouped[group_name] = []
                order.append(group_name)
            if not any(o["course_code"] == option_code for o in grouped[group_name]):
                grouped[group_name].append({"course_code": option_code, "course_title": title})

    return [
        {
            "group": name,
            "elective_number": int(re.search(r"(\d{1,2})", name).group(1)),
            "options": grouped[name],
        }
        for name in order
        if grouped[name]
    ]


def link_elective_tracks(
    courses: list[dict[str, Any]], tracks: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Attach each elective pool to the curriculum row that consumes it."""
    for track in tracks:
        number = track["elective_number"]
        prefix = track["group"].split()[0]
        wanted = {norm_key(f"{prefix} Elect {number}"), norm_key(f"{prefix} Elect {number} L"),
                  norm_key(f"{prefix} Elective {number}")}
        slots: list[str] = []
        for course in courses:
            key = norm_key(course["course_code"])
            if key in wanted or relaxed_key(course["course_code"]) in {norm_key(f"{prefix} Elect {number}")}:
                course["elective_group"] = track["group"]
                course["elective_option_count"] = len(track["options"])
                slots.append(course["course_code"])
        track["curriculum_slots"] = slots
    return tracks


# =============================================================================
# 9. Document metadata
# =============================================================================
CONNECTORS = {"of", "in", "and", "the", "for", "to", "a", "an", "with"}


def titlecase_program(name: str) -> str:
    words = clean_str(name).split()
    out: list[str] = []
    for position, word in enumerate(words):
        lower = word.lower()
        if position > 0 and lower in CONNECTORS:
            out.append(lower)
        elif word.isupper() and len(word) <= 4 and not word.isalpha():
            out.append(word)
        else:
            out.append(lower.capitalize())
    return " ".join(out)


def derive_degree_code(program_name: str) -> str | None:
    match = re.match(r"Bachelor of (Science|Arts|Secondary Education|Elementary Education)\b(?: in )?(.*)",
                     clean_str(program_name), flags=re.IGNORECASE)
    if not match:
        return None
    kind = match.group(1).lower()
    tail = clean_str(match.group(2))
    prefix = {"science": "BS", "arts": "BA", "secondary education": "BSEd", "elementary education": "BEEd"}.get(
        kind, "B"
    )
    return f"{prefix} {tail}".strip() if tail else prefix


def parse_semantic_markdown(path: Path) -> dict[str, dict[str, Any]]:
    """Parse the college/program reference markdown into {code: {name, programs}}."""
    colleges: dict[str, dict[str, Any]] = {}
    if not path or not Path(path).exists():
        return colleges

    current_code = ""
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        college = re.search(r"^#+\s*(College of [A-Za-z\s&,\-]+?)\s*\(([A-Za-z]+)\)", line)
        if college:
            current_code = college.group(2).strip()
            colleges[current_code] = {"name": college.group(1).strip(), "programs": []}
            continue
        program = re.search(r"^[\*\-]\s*([^\(]+)\s*\(([^\)]+)\)", line)
        if program and current_code in colleges:
            colleges[current_code]["programs"].append(
                {"program_name": clean_str(program.group(1)), "degree": clean_str(program.group(2))}
            )
    return colleges


def resolve_metadata(
    source_path: Path,
    doc_text: str = "",
    semantic_map: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Resolve college/program/degree/SY/governance without inventing defaults.

    v1 fell back to 'CS / BS Computer Science / SY 2025-2026' whenever detection
    failed, which silently relabelled other colleges' prospectuses. v2 returns
    None and records a warning instead.
    """
    semantic_map = semantic_map or {}
    warnings: list[str] = []
    path_str = str(source_path).replace("\\", "/")
    head = clean_str(doc_text)[:6000]
    haystack = f"{path_str} {head}"

    college_code = None
    college_name = None
    for part in Path(source_path).parts:
        if part in semantic_map:
            college_code, college_name = part, semantic_map[part]["name"]
            break
    if not college_code:
        for code, info in semantic_map.items():
            if re.search(rf"(?<![A-Za-z]){re.escape(code)}(?![A-Za-z])", path_str):
                college_code, college_name = code, info["name"]
                break

    program_name = None
    degree = None
    for code, info in semantic_map.items():
        for program in info["programs"]:
            name, abbrev = program["program_name"], program["degree"]
            if name.lower() in haystack.lower() or (len(abbrev) > 4 and abbrev.lower() in haystack.lower()):
                program_name, degree = name, abbrev
                college_code = college_code or code
                college_name = college_name or info["name"]
                break
        if program_name:
            break

    if not program_name:
        match = re.search(r"\b(BACHELOR OF [A-Za-z][A-Za-z\s]{3,70})", head, flags=re.IGNORECASE)
        if match:
            raw = re.split(
                r"\b(?:PROGRAM|CURRICULUM|PROSPECTUS|MAJOR|BOR|EFFECTIVE|PROPOSED|OF STUDY)\b",
                match.group(1),
                flags=re.IGNORECASE,
            )[0]
            program_name = titlecase_program(raw)
            degree = derive_degree_code(program_name)
    if not program_name:
        warnings.append("Program name could not be determined from the document or path.")
    if not college_code:
        warnings.append("College could not be determined; provide the semantic map or folder layout.")

    sy_match = re.search(
        r"(?:Effective\s*SY|Effective\s*S\.Y\.|SY|A\.?Y\.?)\s*:?\s*(\d{4}\s*-\s*\d{4})",
        haystack,
        flags=re.IGNORECASE,
    )
    school_year = sy_match.group(1).replace(" ", "") if sy_match else None
    if not school_year:
        warnings.append("Effective school year not found; left null rather than guessed.")

    def find(pattern: str) -> str | None:
        match = re.search(pattern, head, flags=re.IGNORECASE)
        return clean_str(match.group(1)) if match else None

    metadata = {
        "campus": "Tiniguiban - Main",
        "college_code": college_code,
        "college_name": college_name,
        "program_name": program_name,
        "degree": degree,
        "effective_school_year": school_year,
        "bor_resolution": find(r"BOR\s*(?:Resolution|Res\.?)\s*(No\.?[^\n]{0,40}?)(?:\s*Dated|\s*\||$)"),
        "bor_date": find(r"Dated\s+([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})"),
        "doc_ref_no": find(r"Doc\.?\s*Ref\.?\s*No\.?\s*:?\s*([A-Z0-9\-]+)"),
        "revision_no": find(r"Revision\s*No\.?\s*:?\s*([0-9]{1,3})"),
        "effective_date": find(r"Effective\s*Date\s*:?\s*([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})"),
        "implementation_note": find(r"(Proposed Date of Implementation:[^\n]{0,80})"),
        "source_file": Path(source_path).name,
        "source_path": str(Path(source_path).resolve()),
    }
    return metadata, warnings


# =============================================================================
# 10. Audit: fail loudly instead of emitting plausible garbage
# =============================================================================
def find_prerequisite_cycles(courses: Sequence[dict[str, Any]]) -> list[list[str]]:
    # Accumulate per code: a duplicated course row must not overwrite the edges
    # contributed by its twin, or a real cycle can hide behind the duplicate.
    graph: dict[str, list[str]] = defaultdict(list)
    for course in courses:
        code = course["course_code"]
        for prereq in course.get("prerequisites", []):
            if prereq != code and norm_key(prereq) != norm_key(code):
                if prereq not in graph[code]:
                    graph[code].append(prereq)
        graph.setdefault(code, graph[code])
    cycles: list[list[str]] = []
    state: dict[str, int] = defaultdict(int)  # 0 unvisited, 1 in stack, 2 done
    stack: list[str] = []

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for neighbour in graph.get(node, []):
            if neighbour not in graph:
                continue
            if state[neighbour] == 0:
                visit(neighbour)
            elif state[neighbour] == 1:
                cycle = stack[stack.index(neighbour) :] + [neighbour]
                if cycle not in cycles:
                    cycles.append(cycle)
        stack.pop()
        state[node] = 2

    for code in list(graph.keys()):
        if state[code] == 0:
            visit(code)
    return cycles


def build_audit(
    courses: Sequence[dict[str, Any]],
    parse: GridParseResult,
    metadata: dict[str, Any],
    duplicates: Sequence[dict[str, Any]],
    extra_warnings: Sequence[str] = (),
) -> dict[str, Any]:
    """Cross-check the extraction against the document's own printed totals."""
    errors: list[str] = []
    warnings: list[str] = [*parse.warnings, *extra_warnings]
    structural = [w for w in warnings if clean_str(w).startswith("STRUCTURAL_ERROR:")]
    if structural:
        errors.extend(structural)
        warnings = [w for w in warnings if w not in structural]

    years = sorted(
        {c.get("year_level") for c in courses if c.get("year_level")},
        key=lambda y: YEAR_ORDER.get(y, 99),
    )
    terms = sorted(
        {
            (c.get("year_level"), c.get("semester"))
            for c in courses
            if c.get("year_level") and c.get("semester")
        },
        key=lambda t: term_index(t[0] or "", t[1] or ""),
    )
    years_present = {c.get("year_level") for c in courses}

    if not courses:
        errors.append("No courses extracted.")
    elif len(years_present) <= 1 and len(courses) >= 20:
        errors.append(
            f"All {len(courses)} courses landed in '{list(years_present)[0]}' - the year banner rows were not "
            "recognised. Run with --dump-grid and check the banner detection."
        )
    elif len(terms) < 2 and len(courses) >= 20:
        errors.append("All courses landed in a single term; semester banners were not recognised.")

    missing_year = [c.get("course_code") for c in courses if not c.get("year_level")]
    missing_semester = [c.get("course_code") for c in courses if not c.get("semester")]
    if missing_year:
        errors.append(f"{len(missing_year)} course(s) have no verified year: {missing_year}.")
    if missing_semester:
        errors.append(
            f"{len(missing_semester)} course(s) have no verified semester: {missing_semester}."
        )

    computed_terms: dict[tuple[str, str], int] = defaultdict(int)
    for course in courses:
        if course.get("year_level") and course.get("semester"):
            computed_terms[(course["year_level"], course["semester"])] += course.get("total_units") or 0

    term_audit: list[dict[str, Any]] = []
    for term in terms:
        declared = parse.declared_term_units.get(term)
        computed = computed_terms.get(term, 0)
        matches = declared is None or declared == computed
        term_audit.append(
            {
                "year_level": term[0],
                "semester": term[1],
                "declared_units": declared,
                "computed_units": computed,
                "course_count": sum(
                    1 for c in courses if (c["year_level"], c["semester"]) == term
                ),
                "matches": matches,
            }
        )
        if not matches:
            errors.append(
                f"Unit checksum mismatch for {term[0]} {term[1]}: document says {declared}, "
                f"extracted {computed}."
            )

    for term, declared in parse.declared_term_units.items():
        if term not in computed_terms:
            errors.append(
                f"Document declares a total for {term[0]} {term[1]} but no courses were extracted there."
            )

    computed_total = sum(c.get("total_units") or 0 for c in courses)
    declared_total = parse.declared_grand_total
    if declared_total is not None and declared_total != computed_total:
        errors.append(
            f"Grand total mismatch: document says {declared_total} units, extracted {computed_total}."
        )

    unresolved = [
        {"course_code": c["course_code"], "token": token, "raw": c.get("prerequisites_raw", "")}
        for c in courses
        for token in c.get("prerequisites_unresolved", [])
    ]
    if unresolved:
        warnings.append(
            f"{len(unresolved)} prerequisite token(s) could not be matched to a course code in this "
            "document; see unresolved_prerequisites."
        )

    ordering: list[dict[str, Any]] = []
    positions = {c["course_code"]: c.get("term_index", 99) for c in courses}
    for course in courses:
        for prereq in course.get("prerequisites", []):
            if prereq in positions and positions[prereq] >= course.get("term_index", 99):
                ordering.append(
                    {
                        "course_code": course["course_code"],
                        "course_term": f"{course['year_level']} {course['semester']}",
                        "prerequisite": prereq,
                        "prerequisite_term": next(
                            f"{c['year_level']} {c['semester']}"
                            for c in courses
                            if c["course_code"] == prereq
                        ),
                    }
                )
    if ordering:
        warnings.append(
            f"{len(ordering)} prerequisite(s) are scheduled at or after the course that requires them."
        )

    cycles = find_prerequisite_cycles(courses)
    if cycles:
        errors.append(f"Prerequisite graph contains {len(cycles)} cycle(s): {cycles}.")

    missing_units = [c["course_code"] for c in courses if c.get("total_units") is None]
    if missing_units:
        errors.append(f"{len(missing_units)} course(s) have no parsed units: {missing_units}.")

    if duplicates:
        errors.append(
            f"{len(duplicates)} course code(s) appear more than once: "
            f"{[d['course_code'] for d in duplicates]}."
        )

    if parse.unclaimed_course_candidates:
        errors.append(
            f"{len(parse.unclaimed_course_candidates)} high-confidence source course code(s) "
            "were not claimed by the parser."
        )

    if parse.anomalies:
        errors.append(
            f"{len(parse.anomalies)} unresolved structural ambiguity/anomaly item(s) remain; "
            "see audit.structural_anomalies."
        )
        if any(item.get("type") == "missing_year_marker" for item in parse.anomalies) and any(
            item.get("type") == "unclaimed_course_candidate" for item in parse.anomalies
        ):
            errors.append(
                "Course rows started before any year banner; they were left unclaimed rather than guessed."
            )

    if parse.invalid_repairs:
        errors.append(
            f"{len(parse.invalid_repairs)} semantic repair result(s) failed evidence validation."
        )

    invalid_provenance: list[dict[str, Any]] = []
    unhighlightable: list[str] = []
    for course in courses:
        provenance = course.get("provenance") or {}
        if not provenance.get("valid") or not provenance.get("source_cell_ids"):
            invalid_provenance.append(
                {"course_code": course.get("course_code"), "provenance": provenance}
            )
        elif not provenance.get("highlightable"):
            unhighlightable.append(course.get("course_code"))
    if invalid_provenance:
        errors.append(
            f"{len(invalid_provenance)} course(s) have invalid source-cell provenance."
        )
    if unhighlightable:
        warnings.append(
            f"{len(unhighlightable)} course(s) have source cells but no page bbox; "
            "viewer highlighting is unavailable for those rows."
        )

    contamination: list[dict[str, str]] = []
    leading_bleed = re.compile(
        r"^(?:FIRST|SECOND|THIRD|FOURTH|FIFTH)(?:\s+YEAR)?\s+"
        r"(?=[A-Z]{1,8}(?:[\s-]+[A-Z]{1,6})?[\s-]*\d)",
        re.IGNORECASE,
    )
    for course in courses:
        for field_name in ("course_code", "course_title", "prerequisites_raw"):
            value = clean_str(course.get(field_name, ""))
            if not value:
                continue
            if field_name == "prerequisites_raw" and is_standing_rule(value):
                continue
            contaminated = bool(match_year_label(value) or match_semester_labels(value))
            contaminated = contaminated or bool(leading_bleed.search(value))
            if contaminated:
                contamination.append(
                    {
                        "course_code": course.get("course_code", ""),
                        "field": field_name,
                        "value": value,
                    }
                )
    if contamination:
        errors.append(
            f"{len(contamination)} canonical course field(s) contain structural marker contamination."
        )

    schema_errors: list[str] = []
    required_fields = ("course_code", "course_title", "units", "provenance")
    for index, course in enumerate(courses):
        for field_name in required_fields:
            if field_name not in course:
                schema_errors.append(f"courses[{index}] is missing {field_name}")
    if schema_errors:
        errors.append(f"Canonical course schema has {len(schema_errors)} error(s).")

    for key in ("program_name", "degree", "effective_school_year", "college_code"):
        if not metadata.get(key):
            warnings.append(f"Metadata field '{key}' is null.")

    status = "error" if errors else ("warn" if warnings else "ok")
    return {
        "status": status,
        "promotion_status": "REVIEW_REQUIRED" if errors else "VERIFIED",
        "errors": errors,
        "warnings": warnings,
        "total_courses": len(courses),
        "years_detected": years,
        "terms_detected": [f"{y} {s}" for y, s in terms],
        "term_unit_audit": term_audit,
        "declared_total_units": declared_total,
        "computed_total_units": computed_total,
        "total_units_match": None if declared_total is None else declared_total == computed_total,
        "unresolved_prerequisites": unresolved,
        "prerequisite_ordering_violations": ordering,
        "prerequisite_cycles": cycles,
        "duplicate_course_codes": duplicates,
        "courses_without_units": missing_units,
        "courses_without_verified_year": missing_year,
        "courses_without_verified_semester": missing_semester,
        "source_course_candidates": parse.source_course_candidates,
        "unclaimed_course_candidates": parse.unclaimed_course_candidates,
        "structural_anomalies": parse.anomalies,
        "repair_packets": parse.repair_packets,
        "repairs": parse.repairs,
        "invalid_repairs": parse.invalid_repairs,
        "invalid_provenance": invalid_provenance,
        "unhighlightable_courses": unhighlightable,
        "structural_contamination": contamination,
        "schema_errors": schema_errors,
        "footnotes": parse.footnotes.audit(),
        "table_layout": parse.layout,
        "curriculum_sections": parse.sections,
    }


# =============================================================================
# 11. Derived views: term tree, prerequisite graph, review CSV
# =============================================================================
def build_curriculum_by_term(courses: Sequence[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    tree: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for course in sorted(courses, key=lambda c: c.get("term_index", 99)):
        tree.setdefault(course["year_level"], {}).setdefault(course["semester"], []).append(course)
    return tree


def make_prerequisite_edges(courses: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for course in courses:
        for prereq in course.get("prerequisites", []):
            edges.append({"from": prereq, "to": course["course_code"], "resolved": True})
        for token in course.get("prerequisites_unresolved", []):
            edges.append({"from": token, "to": course["course_code"], "resolved": False})
    return edges


def build_unlocks_map(courses: Sequence[dict[str, Any]]) -> dict[str, list[str]]:
    unlocks: dict[str, list[str]] = defaultdict(list)
    for course in courses:
        for prereq in course.get("prerequisites", []):
            unlocks[prereq].append(course["course_code"])
    return dict(unlocks)


def write_review_csv(courses: Sequence[dict[str, Any]], output_path: Path) -> None:
    """Human-reviewable flat table - the artefact a registrar can actually check."""
    fields = [
        "year_level", "semester", "course_code", "course_title", "units_total",
        "units_lecture", "units_lab", "prerequisites_resolved", "prerequisites_unresolved",
        "standing_requirements", "category", "elective_group", "prerequisites_raw",
        "title_raw", "footnote_marker", "table_index", "row_index", "column_group",
        "source_cell_ids", "page", "bbox", "resolution_method", "repair_id",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for course in courses:
            source = course.get("_source", {})
            provenance = course.get("provenance", {})
            writer.writerow(
                {
                    "year_level": course.get("year_level", ""),
                    "semester": course.get("semester", ""),
                    "course_code": course.get("course_code", ""),
                    "course_title": course.get("course_title", ""),
                    "units_total": course.get("total_units", ""),
                    "units_lecture": course.get("lecture_units", ""),
                    "units_lab": course.get("lab_units", ""),
                    "prerequisites_resolved": ", ".join(course.get("prerequisites", [])),
                    "prerequisites_unresolved": ", ".join(course.get("prerequisites_unresolved", [])),
                    "standing_requirements": " | ".join(course.get("standing_requirements", [])),
                    "category": course.get("category", ""),
                    "elective_group": course.get("elective_group") or "",
                    "prerequisites_raw": course.get("prerequisites_raw", ""),
                    "title_raw": course.get("title_raw", ""),
                    "footnote_marker": course.get("footnote_marker") if course.get("footnote_marker") else "",
                    "table_index": source.get("table_index", ""),
                    "row_index": source.get("row_index", ""),
                    "column_group": source.get("column_group", ""),
                    "source_cell_ids": " | ".join(provenance.get("source_cell_ids", [])),
                    "page": provenance.get("page") if provenance.get("page") is not None else "",
                    "bbox": json.dumps(provenance.get("bbox"), ensure_ascii=False)
                    if provenance.get("bbox") is not None
                    else "",
                    "resolution_method": provenance.get("resolution_method", ""),
                    "repair_id": provenance.get("repair_id") or "",
                }
            )


# =============================================================================
# 12. Prolog knowledge base
# =============================================================================
def pl_atom(value: Any) -> str:
    """Quote a Prolog atom, doubling single quotes per ISO rules."""
    text = clean_str(value)
    return "'" + text.replace("\\", "\\\\").replace("'", "''") + "'"


PROLOG_RULES = """
% --------------------------------------------------------------------------
% Query helpers
% --------------------------------------------------------------------------
unlocks(Prereq, Course) :- prerequisite(Course, Prereq).

prereq_closure(Course, Prereq) :- prerequisite(Course, Prereq).
prereq_closure(Course, Prereq) :-
    prerequisite(Course, Middle),
    prereq_closure(Middle, Prereq).

% eligible(+Course, +PassedCodes): every prerequisite has been passed.
eligible(Course, Passed) :-
    course(Course, _, _, _, _, _, _, _),
    \\+ ( prerequisite(Course, Prereq), \\+ memberchk(Prereq, Passed) ).

% offered_in(+Course, -Year, -Semester)
offered_in(Course, Year, Semester) :-
    course(Course, _, _, _, _, Year, Semester, _).

% term_load(+Year, +Semester, -Units)
term_load(Year, Semester, Units) :-
    findall(U, course(_, _, U, _, _, Year, Semester, _), List),
    sum_list(List, Units).

% curriculum_units(-Units): total units in the program of study.
curriculum_units(Units) :-
    findall(U, course(_, _, U, _, _, _, _, _), List),
    sum_list(List, Units).

% remaining(+PassedCodes, -Course): not yet taken.
remaining(Passed, Course) :-
    course(Course, _, _, _, _, _, _, _),
    \\+ memberchk(Course, Passed).

% next_eligible(+PassedCodes, -Course): take-able right now.
next_eligible(Passed, Course) :-
    remaining(Passed, Course),
    eligible(Course, Passed).
""".strip()


def generate_prolog_knowledge(
    metadata: dict[str, Any],
    courses: Sequence[dict[str, Any]],
    elective_tracks: Sequence[dict[str, Any]],
    term_units: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Emit consult-ready Prolog plus a mirrored relational view for other tools."""
    clauses: list[str] = []
    add = clauses.append

    add("% ===========================================================================")
    add(f"% PalSU prospectus knowledge base: {metadata.get('degree') or metadata.get('program_name')}")
    add(f"% Curriculum SY: {metadata.get('effective_school_year')}")
    add(f"% Source: {metadata.get('source_file')}")
    add(f"% Generated: {datetime.now().isoformat(timespec='seconds')} by {SCHEMA_VERSION}")
    add("% ===========================================================================")
    add("")
    add(":- discontiguous course/8.")
    add(":- discontiguous prerequisite/2.")
    add(":- discontiguous standing_requirement/2.")
    add(":- discontiguous elective_option/3.")
    add(":- discontiguous elective_slot/2.")
    add(":- discontiguous term_units/3.")
    add("")

    total_units = sum(c.get("total_units") or 0 for c in courses)
    add("% program(CollegeCode, Degree, ProgramName, CollegeName, SchoolYear, TotalUnits).")
    add(
        "program({}, {}, {}, {}, {}, {}).".format(
            pl_atom(metadata.get("college_code") or "UNKNOWN"),
            pl_atom(metadata.get("degree") or "UNKNOWN"),
            pl_atom(metadata.get("program_name") or "UNKNOWN"),
            pl_atom(metadata.get("college_name") or "UNKNOWN"),
            pl_atom(metadata.get("effective_school_year") or "UNKNOWN"),
            total_units,
        )
    )
    add("")

    add("% course(Code, Title, TotalUnits, LectureUnits, LabUnits, YearLevel, Semester, TermIndex).")
    relational_courses: list[dict[str, Any]] = []
    for course in courses:
        units = course.get("units", {})
        add(
            "course({}, {}, {}, {}, {}, {}, {}, {}).".format(
                pl_atom(course["course_code"]),
                pl_atom(course["course_title"]),
                units.get("total") or 0,
                units.get("lecture") or 0,
                units.get("lab") or 0,
                pl_atom(course["year_level"]),
                pl_atom(course["semester"]),
                course.get("term_index", 99),
            )
        )
        relational_courses.append(
            {
                "code": course["course_code"],
                "title": course["course_title"],
                "total_units": units.get("total") or 0,
                "lecture_units": units.get("lecture") or 0,
                "lab_units": units.get("lab") or 0,
                "year_level": course["year_level"],
                "semester": course["semester"],
                "term_index": course.get("term_index"),
                "category": course.get("category"),
            }
        )

    add("")
    add("% course_category(Code, Category).")
    for course in courses:
        add(f"course_category({pl_atom(course['course_code'])}, {pl_atom(course.get('category'))}).")

    add("")
    add("% prerequisite(Course, RequiredCourse).")
    relational_prereqs: list[dict[str, str]] = []
    for course in courses:
        for prereq in course.get("prerequisites", []):
            add(f"prerequisite({pl_atom(course['course_code'])}, {pl_atom(prereq)}).")
            relational_prereqs.append({"course": course["course_code"], "requires": prereq})

    add("")
    add("% standing_requirement(Course, PolicyRule).")
    relational_rules: list[dict[str, str]] = []
    for course in courses:
        for rule in course.get("standing_requirements", []):
            add(f"standing_requirement({pl_atom(course['course_code'])}, {pl_atom(rule)}).")
            relational_rules.append({"course": course["course_code"], "rule": rule})

    add("")
    add("% elective_option(Group, OptionCode, OptionTitle).")
    for track in elective_tracks:
        for option in track["options"]:
            add(
                "elective_option({}, {}, {}).".format(
                    pl_atom(track["group"]), pl_atom(option["course_code"]), pl_atom(option["course_title"])
                )
            )
    add("")
    add("% elective_slot(CurriculumCode, Group).")
    for track in elective_tracks:
        for slot in track.get("curriculum_slots", []):
            add(f"elective_slot({pl_atom(slot)}, {pl_atom(track['group'])}).")

    add("")
    add("% term_units(YearLevel, Semester, Units).")
    for term in term_units:
        add(
            "term_units({}, {}, {}).".format(
                pl_atom(term["year_level"]), pl_atom(term["semester"]), term["computed_units"]
            )
        )

    add("")
    add(PROLOG_RULES)

    return {
        "clauses": clauses,
        "relations": {
            "courses": relational_courses,
            "prerequisites": relational_prereqs,
            "standing_requirements": relational_rules,
            "elective_tracks": list(elective_tracks),
        },
    }


# =============================================================================
# 13. Hybrid RAG chunks
# =============================================================================
def build_semantic_rag_chunks(
    metadata: dict[str, Any],
    courses: Sequence[dict[str, Any]],
    elective_tracks: Sequence[dict[str, Any]],
    term_units: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Advising-shaped chunks: one per course, per term, per elective pool, plus an overview."""
    chunks: list[dict[str, Any]] = []
    degree = metadata.get("degree") or metadata.get("program_name") or "the program"
    college = metadata.get("college_name") or "PalSU"
    school_year = metadata.get("effective_school_year") or "n/a"
    source = metadata.get("source_file", "")
    unlocks = build_unlocks_map(courses)

    total_units = sum(c.get("total_units") or 0 for c in courses)
    overview = [
        f"### Program Overview: {metadata.get('program_name') or degree}",
        f"- **Degree**: {degree}",
        f"- **College**: {college} ({metadata.get('college_code') or 'n/a'}), {metadata.get('campus')}",
        f"- **Effective School Year**: {school_year}",
        f"- **Total Units**: {total_units} across {len(courses)} courses",
        "- **Terms**: " + ", ".join(
            "{0} {1}".format(t["year_level"], t["semester"]) for t in term_units
        ),
    ]
    if metadata.get("bor_resolution"):
        overview.append(f"- **BOR Resolution**: {metadata['bor_resolution']} {metadata.get('bor_date') or ''}".rstrip())
    chunks.append(
        {
            "id": "program::overview",
            "chunk_type": "program_overview",
            "college": metadata.get("college_code"),
            "program": degree,
            "text": "\n".join(overview) + "\n",
            "source": source,
        }
    )

    for course in courses:
        code = course["course_code"]
        prereqs = course.get("prerequisites", [])
        unresolved = course.get("prerequisites_unresolved", [])
        standing = course.get("standing_requirements", [])
        prereq_text = ", ".join(prereqs) if prereqs else "None"
        if unresolved:
            prereq_text += f" (unverified in this document: {', '.join(unresolved)})"
        if standing:
            prereq_text += f" (Policy: {'; '.join(standing)})"
        opened = unlocks.get(code, [])
        units = course.get("units", {})
        body = [
            f"### Course: {code} - {course['course_title']}",
            f"- **Program**: {degree} ({college}, SY {school_year})",
            f"- **When taken**: {course['year_level']}, {course['semester']}",
            f"- **Units**: {units.get('total') or 'n/a'} total "
            f"(lecture {units.get('lecture') or 0}, laboratory {units.get('lab') or 0})",
            f"- **Prerequisites**: {prereq_text}",
            f"- **Unlocks**: {', '.join(opened) if opened else 'No downstream course depends on it'}",
            f"- **Classification**: {course.get('category')}"
            + (f" / elective pool {course['elective_group']}" if course.get("elective_group") else ""),
        ]
        chunks.append(
            {
                "id": f"{code}::course",
                "chunk_type": "course",
                "course_code": code,
                "course_title": course["course_title"],
                "year_level": course["year_level"],
                "semester": course["semester"],
                "college": metadata.get("college_code"),
                "program": degree,
                "text": "\n".join(body) + "\n",
                "source": source,
            }
        )

    for term in term_units:
        year, semester = term["year_level"], term["semester"]
        term_courses = [c for c in courses if (c["year_level"], c["semester"]) == (year, semester)]
        lines = [
            f"  - **{c['course_code']}**: {c['course_title']} "
            f"({c.get('total_units')} units; prerequisites: "
            f"{', '.join(c.get('prerequisites', [])) or 'None'})"
            for c in term_courses
        ]
        declared = term.get("declared_units")
        checksum = (
            f"- **Printed total in prospectus**: {declared}\n" if declared is not None else ""
        )
        chunks.append(
            {
                "id": f"{year}_{semester}::term".replace(" ", "_"),
                "chunk_type": "term_schedule",
                "year_level": year,
                "semester": semester,
                "college": metadata.get("college_code"),
                "program": degree,
                "text": (
                    f"### Term Schedule: {degree} - {year}, {semester}\n"
                    f"- **College**: {college}\n"
                    f"- **Effective School Year**: {school_year}\n"
                    f"- **Courses**: {len(term_courses)}\n"
                    f"- **Total units this term**: {term['computed_units']}\n"
                    f"{checksum}"
                    "- **Course list**:\n" + "\n".join(lines) + "\n"
                ),
                "source": source,
            }
        )

    for track in elective_tracks:
        options = [f"  - **{o['course_code']}**: {o['course_title']}" for o in track["options"]]
        slots = track.get("curriculum_slots") or []
        chunks.append(
            {
                "id": f"{track['group']}::elective".replace(" ", "_"),
                "chunk_type": "elective_pool",
                "elective_group": track["group"],
                "college": metadata.get("college_code"),
                "program": degree,
                "text": (
                    f"### Elective Pool: {track['group']} ({degree})\n"
                    f"- **Taken as**: {', '.join(slots) if slots else 'see curriculum'}\n"
                    f"- **Choose one of**:\n" + "\n".join(options) + "\n"
                ),
                "source": source,
            }
        )

    policy_courses = [c for c in courses if c.get("standing_requirements")]
    if policy_courses:
        lines = [
            f"  - **{c['course_code']}** ({c['year_level']}, {c['semester']}): "
            f"{'; '.join(c['standing_requirements'])}"
            for c in policy_courses
        ]
        chunks.append(
            {
                "id": "program::policies",
                "chunk_type": "enrolment_policy",
                "college": metadata.get("college_code"),
                "program": degree,
                "text": (
                    f"### Enrolment Policies and Standing Requirements ({degree})\n"
                    "Some courses are gated by academic standing rather than by a specific course:\n"
                    + "\n".join(lines)
                    + "\n"
                ),
                "source": source,
            }
        )

    return chunks


# =============================================================================
# 14. Document loading (Docling optional for *_docling.json inputs)
# =============================================================================
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


def _page_from_mapping(value: Any, default: int | None = None) -> int | None:
    if not isinstance(value, Mapping):
        return default
    for key in ("page", "page_no", "page_number"):
        if value.get(key) is not None:
            try:
                return int(value[key])
            except (TypeError, ValueError):
                pass
    return default


def _source_bbox(value: Any, default_page: int | None = None) -> SourceBBox | None:
    """Accept the bbox spellings used across Docling serialisation versions."""
    if not isinstance(value, Mapping):
        return None
    page = _page_from_mapping(value, default_page)
    bbox = value.get("bbox") if isinstance(value.get("bbox"), Mapping) else value
    key_sets = (
        ("l", "t", "r", "b"),
        ("left", "top", "right", "bottom"),
        ("x0", "y0", "x1", "y1"),
    )
    for left_key, top_key, right_key, bottom_key in key_sets:
        if all(bbox.get(key) is not None for key in (left_key, top_key, right_key, bottom_key)):
            try:
                return SourceBBox(
                    page,
                    float(bbox[left_key]),
                    float(bbox[top_key]),
                    float(bbox[right_key]),
                    float(bbox[bottom_key]),
                )
            except (TypeError, ValueError):
                return None
    return None


def _default_table_page(table_wrapper: Mapping[str, Any]) -> int | None:
    for prov in table_wrapper.get("prov", []) or []:
        page = _page_from_mapping(prov)
        if page is not None:
            return page
    return _page_from_mapping(table_wrapper)


def docling_to_normalized_table(
    table_data: Mapping[str, Any],
    table_index: int,
    table_wrapper: Mapping[str, Any] | None = None,
) -> NormalizedTable:
    """The one production table adapter. Merged cells remain one cell."""
    wrapper = table_wrapper or {}
    raw_cells = table_data.get("table_cells") or []
    if not raw_cells and isinstance(table_data.get("grid"), list):
        # Compatibility with hand-authored/synthetic Docling-like dictionaries.
        return normalized_table_from_grid(table_data.get("grid") or [], table_index)

    default_page = _default_table_page(wrapper)
    normalized: list[NormalizedCell] = []
    max_row = 0
    max_col = 0
    for cell_index, raw in enumerate(raw_cells):
        if not isinstance(raw, Mapping):
            continue
        row_start = int(raw.get("start_row_offset_idx", raw.get("row_index", 0)) or 0)
        row_end = int(raw.get("end_row_offset_idx", row_start + 1) or row_start + 1)
        col_start = int(raw.get("start_col_offset_idx", raw.get("col_index", 0)) or 0)
        col_end = int(raw.get("end_col_offset_idx", col_start + 1) or col_start + 1)
        if row_end <= row_start:
            row_end = row_start + 1
        if col_end <= col_start:
            col_end = col_start + 1

        bbox = _source_bbox(raw, default_page)
        if bbox is None:
            for prov in raw.get("prov", []) or []:
                bbox = _source_bbox(prov, default_page)
                if bbox is not None:
                    break
        raw_text = str(raw.get("text", "") or "")
        normalized.append(
            NormalizedCell(
                cell_id=f"t{table_index}-c{cell_index}",
                table_index=table_index,
                raw_text=raw_text,
                text=clean_str(raw_text),
                row_start=row_start,
                row_end=row_end,
                col_start=col_start,
                col_end=col_end,
                bbox=bbox,
            )
        )
        max_row = max(max_row, row_end)
        max_col = max(max_col, col_end)

    num_rows = int(table_data.get("num_rows") or max_row)
    num_cols = int(table_data.get("num_cols") or max_col)
    return NormalizedTable(table_index, num_rows, num_cols, normalized)


def grid_from_table_cells(table_data: dict[str, Any]) -> list[list[str]]:
    """Compatibility/debug projection; not a canonical representation."""
    return project_table_to_grid(docling_to_normalized_table(table_data, 0))


def _table_year_hint_sources(data: Mapping[str, Any]) -> dict[int, str]:
    sources: dict[int, str] = {}

    def consume(children: Sequence[Mapping[str, Any]]) -> None:
        current_source = ""
        current_year: str | None = None
        for child in children:
            cref = str(child.get("cref", ""))
            if cref.startswith("#/texts/"):
                try:
                    index = int(cref.rsplit("/", 1)[1])
                    text = clean_str((data.get("texts") or [])[index].get("text", ""))
                except (IndexError, TypeError, ValueError, AttributeError):
                    continue
                hit = match_year_label(text)
                if hit:
                    current_year = hit
                    current_source = f"text-{index}"
            elif cref.startswith("#/tables/") and current_year:
                try:
                    table_index = int(cref.rsplit("/", 1)[1])
                except ValueError:
                    continue
                sources.setdefault(table_index, current_source)

    for group in data.get("groups", []) or []:
        if isinstance(group, Mapping):
            consume(group.get("children", []) or [])
    body = data.get("body", {}) or {}
    if isinstance(body, Mapping):
        consume(body.get("children", []) or [])
    return sources


def evidence_adapter(
    raw_dict: Mapping[str, Any],
    docling_document: Any = None,
    source_kind: str = "docling-json",
) -> ProspectusEvidence:
    """Canonical adapter shared by live conversion and cached raw JSON."""
    tables: list[NormalizedTable] = []
    for table_index, wrapper in enumerate(raw_dict.get("tables", []) or []):
        if not isinstance(wrapper, Mapping):
            continue
        table_data = wrapper.get("data")
        if not isinstance(table_data, Mapping):
            continue
        table = docling_to_normalized_table(table_data, table_index, wrapper)
        if table.cells and table.num_rows > 0 and table.num_cols > 0:
            tables.append(table)

    text_items: list[dict[str, Any]] = []
    for index, item in enumerate(raw_dict.get("texts", []) or []):
        if not isinstance(item, Mapping):
            continue
        value = clean_str(item.get("text", ""))
        if not value:
            continue
        bbox = None
        for prov in item.get("prov", []) or []:
            bbox = _source_bbox(prov)
            if bbox:
                break
        text_items.append(
            {
                "item_id": f"text-{index}",
                "label": str(item.get("label", "text")),
                "text": value,
                "page": bbox.page if bbox else None,
                "bbox": bbox.as_list() if bbox else None,
            }
        )

    try:
        markdown = docling_document.export_to_markdown() if docling_document is not None else ""
    except Exception:
        markdown = ""
    if not markdown:
        lines = [item["text"] for item in text_items]
        for table in tables:
            for row in project_table_to_grid(table, repeat_spans=False):
                joined = " ".join(cell for cell in row if cell)
                if joined:
                    lines.append(joined)
        markdown = "\n".join(lines)

    try:
        table_year_hints = extract_table_year_contexts(dict(raw_dict))
    except Exception:
        table_year_hints = {}
    return ProspectusEvidence(
        tables=tables,
        text_items=text_items,
        markdown=markdown,
        docling_document=docling_document,
        source_kind=source_kind,
        table_year_hints=table_year_hints,
        table_year_hint_sources=_table_year_hint_sources(raw_dict),
    )


def normalize_evidence(value: ProspectusEvidence | Mapping[str, Any]) -> dict[str, Any]:
    """Stable, serialisable evidence signature for live-vs-cached regressions."""
    evidence = value if isinstance(value, ProspectusEvidence) else evidence_adapter(value)
    return {
        "tables": [
            {
                "table_index": table.table_index,
                "num_rows": table.num_rows,
                "num_cols": table.num_cols,
                "cells": [cell.as_evidence_dict() for cell in table.cells],
            }
            for table in evidence.tables
        ],
        "text_items": evidence.text_items,
        "markdown": evidence.markdown,
        "table_year_hints": evidence.table_year_hints,
        "table_year_hint_sources": evidence.table_year_hint_sources,
    }


def _load_from_rehydrated_docling_document(
    doc: Any,
    source_kind: str,
    raw_dict: dict[str, Any] | None = None,
) -> ProspectusEvidence:
    raw = raw_dict
    if raw is None:
        raw = doc.export_to_dict() if hasattr(doc, "export_to_dict") else doc.model_dump(mode="json")
    return evidence_adapter(raw, doc, source_kind)


def load_from_raw_json(data: dict[str, Any]) -> ProspectusEvidence:
    if _docling_importable():
        dl = load_docling()
        doc = dl["DoclingDocument"].model_validate(data)
        return evidence_adapter(data, doc, "docling-json")
    return evidence_adapter(data, None, "docling-json-degraded")


def load_from_docling_document(doc: Any) -> ProspectusEvidence:
    dl = load_docling()
    raw = doc.export_to_dict() if hasattr(doc, "export_to_dict") else doc.model_dump(mode="json")
    rehydrated = dl["DoclingDocument"].model_validate(raw)
    return evidence_adapter(raw, rehydrated, "docling-document")



def build_hierarchical_rag_chunks(document: LoadedDocument, source_name: str) -> list[dict[str, Any]]:
    """Docling's own layout chunks when available, otherwise a labelled text fallback."""
    doc = document.docling_doc
    if doc is not None:
        try:
            dl = load_docling()
            chunker = dl["HierarchicalChunker"]()
            chunks: list[dict[str, Any]] = []
            for index, chunk in enumerate(chunker.chunk(doc)):
                text = clean_str(getattr(chunk, "text", ""))
                if not text:
                    continue
                meta = getattr(chunk, "meta", None)
                chunks.append(
                    {
                        "id": f"docling_hierarchical::{index}",
                        "chunk_index": index,
                        "chunk_type": "hierarchical_layout",
                        "text": text,
                        "source": source_name,
                        "metadata": meta.model_dump(mode="json") if hasattr(meta, "model_dump") else {},
                    }
                )
            if chunks:
                return chunks
        except Exception:
            pass

    return [
        {
            "id": f"layout_fallback::{index}",
            "chunk_index": index,
            "chunk_type": "hierarchical_layout_fallback",
            "text": text,
            "source": source_name,
            "metadata": {"label": label},
        }
        for index, (label, text) in enumerate(_iter_text_pairs(document.text_items))
    ]



def _conversion_has_bad_alloc(result: Any) -> bool:
    for err in getattr(result, "errors", None) or []:
        rendered = f"{clean_str(err)} {clean_str(getattr(err, 'error_message', ''))}".lower()
        if "bad_alloc" in rendered or "bad allocation" in rendered:
            return True
    return False


def _conversion_errors(result: Any) -> list[str]:
    return [clean_str(e) for e in (getattr(result, "errors", None) or []) if clean_str(e)]


def _docling_runtime_fingerprint() -> dict[str, Any]:
    return {
        "profile": "palsu-born-digital-v3",
        "docling": package_version("docling"),
        "docling_core": package_version("docling-core"),
        "docling_parse": package_version("docling-parse"),
        "cell_matching": os.environ.get("PALSU_DOCLING_CELL_MATCHING", "true").strip().lower(),
    }


def _cache_meta_path(raw_json_path: Path) -> Path:
    return raw_json_path.with_name(raw_json_path.stem + ".meta.json")


def load_document(
    input_path: Path,
    device: str = "auto",
    force_reconvert: bool = True,
    converter: Any = None,
    raw_json_path: Path | None = None,
) -> tuple[LoadedDocument, Path | None]:
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    suffix = input_path.suffix.lower()
    if suffix == ".json":
        data = json.loads(input_path.read_text(encoding="utf-8"))
        print(f"[*] Loading Docling JSON: {input_path.name}")
        return load_from_raw_json(data), input_path

    if suffix != ".pdf":
        raise ValueError(f"Unsupported input type: {input_path.suffix}")

    ensure_docling_env()
    load_docling()

    raw_json_path = Path(raw_json_path).resolve() if raw_json_path else input_path.parent / f"{input_path.stem}_docling.json"
    meta_path = _cache_meta_path(raw_json_path)
    fingerprint = _docling_runtime_fingerprint()

    cache_valid = False
    if raw_json_path.exists() and meta_path.exists() and not force_reconvert:
        try:
            cache_valid = json.loads(meta_path.read_text(encoding="utf-8")) == fingerprint
        except Exception:
            cache_valid = False

    if raw_json_path.exists() and cache_valid and not force_reconvert:
        print(f"[*] Reusing compatible raw Docling JSON: {raw_json_path.name}")
        data = json.loads(raw_json_path.read_text(encoding="utf-8"))
        return load_from_raw_json(data), raw_json_path

    if raw_json_path.exists() and not force_reconvert:
        print("[*] Existing raw Docling JSON is stale/unversioned; reconverting automatically.")

    print(f"[*] Converting with Docling ({device.upper()}): {input_path.name}")
    active = converter or get_shared_converter(device=device, backend="docling_parse")
    result = active.convert(str(input_path))

    if _conversion_has_bad_alloc(result):
        print(
            "[!] Native Docling PDF backend hit std::bad_alloc; retrying through "
            "Docling's PyPdfium backend (NOT PyMuPDF)."
        )
        result = get_shared_converter(device=device, backend="pypdfium2").convert(str(input_path))

    if _conversion_has_bad_alloc(result):
        raise MemoryError(
            "Docling still reported std::bad_alloc after backend retry. Confirm "
            "docling-parse>=7.12 (Bintanong pins >=7.20) and a Windows pagefile."
        )

    remaining_errors = _conversion_errors(result)
    if remaining_errors:
        raise RuntimeError(
            "Docling returned conversion errors; refusing to build a partial institutional artifact: "
            + " | ".join(remaining_errors[:6])
        )

    doc = result.document
    raw = doc.export_to_dict() if hasattr(doc, "export_to_dict") else doc.model_dump(mode="json")
    raw_json_path.parent.mkdir(parents=True, exist_ok=True)
    raw_json_path.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    meta_path.write_text(json.dumps(fingerprint, indent=2), encoding="utf-8")
    print(f"[+] Raw Docling JSON -> {raw_json_path.name}")

    rehydrated = load_docling()["DoclingDocument"].model_validate(raw)
    return _load_from_rehydrated_docling_document(
        rehydrated, "docling-document", raw
    ), raw_json_path



def dump_grid(document: LoadedDocument) -> str:
    """Human-readable dump of every reconstructed table row - the debugging tool v1 lacked."""
    lines: list[str] = []
    for table in document.tables:
        table_index = table.table_index
        grid = project_table_to_grid(table)
        groups, header_index = detect_column_groups(grid)
        lines.append(
            f"== Table {table_index}: {len(grid)} rows x {max((len(r) for r in grid), default=0)} cols, "
            f"header row {header_index}, {len(groups)} column group(s), "
            f"{len(table.cells)} canonical cell(s)"
        )
        for group in groups:
            lines.append(f"   group {group.index}: {group.as_dict()}")
        for row_index, row in enumerate(grid):
            rendered = " | ".join(cell if cell else "." for cell in row)
            marker = ""
            if is_header_row(row):
                marker = "  <-- header"
            elif match_year_label(" ".join(row)):
                marker = f"  <-- YEAR BANNER: {match_year_label(' '.join(row))}"
            elif match_semester_labels(" ".join(row)):
                marker = f"  <-- SEMESTER BANNER: {[l for _p, l in match_semester_labels(' '.join(row))]}"
            lines.append(f"  [{row_index:3d}] {rendered}{marker}")
        lines.append("   canonical spans:")
        for cell in table.cells:
            lines.append(
                f"     {cell.cell_id} r[{cell.row_start},{cell.row_end}) "
                f"c[{cell.col_start},{cell.col_end}) page="
                f"{cell.bbox.page if cell.bbox else '-'} text={cell.text!r}"
            )
        lines.append("")
    return "\n".join(lines)


# =============================================================================
# 15. Pipeline
# =============================================================================
def build_payload(
    document: LoadedDocument,
    input_path: Path,
    semantic_doc_path: Path | None = DEFAULT_SEMANTIC_DOC,
    raw_json_path: Path | None = None,
    repair_provider: SemanticRepairProvider | None = None,
) -> dict[str, Any]:
    """Evidence -> audited payload. Production artifacts require a passing audit."""
    semantic_map = parse_semantic_markdown(Path(semantic_doc_path)) if semantic_doc_path else {}
    metadata, metadata_warnings = resolve_metadata(
        Path(input_path), doc_text=document.markdown, semantic_map=semantic_map
    )

    parse = parse_curriculum_evidence(document, repair_provider=repair_provider)
    source_document = str(Path(input_path).resolve())
    raw_source = str(Path(raw_json_path).resolve()) if raw_json_path else None
    for raw_course in parse.courses:
        provenance = raw_course.get("provenance") or {}
        provenance["source_document"] = source_document
        provenance["raw_docling_json"] = raw_source
        raw_course["provenance"] = provenance
    courses, _index, duplicates = finalize_courses(parse.courses)
    tracks = link_elective_tracks(courses, parse_elective_tracks(document.text_items))

    audit = build_audit(courses, parse, metadata, duplicates, metadata_warnings)
    term_units = audit["term_unit_audit"]

    verified = audit["status"] != "error"
    if verified:
        prolog = generate_prolog_knowledge(metadata, courses, tracks, term_units)
        prolog["status"] = "verified"
        semantic_chunks = build_semantic_rag_chunks(metadata, courses, tracks, term_units)
        hierarchical_chunks = build_hierarchical_rag_chunks(document, Path(input_path).name)
    else:
        prolog = {
            "status": "blocked",
            "reason": "audit status is error; institutional facts require review",
            "clauses": [],
            "relations": {
                "courses": [],
                "prerequisites": [],
                "standing_requirements": [],
                "elective_tracks": [],
            },
        }
        semantic_chunks = []
        hierarchical_chunks = []

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "program": metadata.get("program_name"),
        "degree": metadata.get("degree"),
        "college": metadata.get("college_code"),
        "college_name": metadata.get("college_name"),
        "campus": metadata.get("campus"),
        "source_file": Path(input_path).name,
        "source_path": str(Path(input_path).resolve()),
        "metadata": metadata,
        "courses": courses,
        "curriculum_by_term": build_curriculum_by_term(courses),
        "prerequisite_edges": make_prerequisite_edges(courses),
        "unlocks": build_unlocks_map(courses),
        "elective_tracks": tracks,
        "policy_notes": parse.policy_notes,
        "evidence": {
            "source_kind": document.source_kind,
            "table_count": len(document.tables),
            "canonical_cell_count": sum(len(table.cells) for table in document.tables),
            "structural_tokens": parse.structural_tokens,
            "curriculum_sections": parse.sections,
        },
        "semantic_repair": {
            "provider_configured": repair_provider is not None,
            "packets": parse.repair_packets,
            "accepted": parse.repairs,
            "rejected": parse.invalid_repairs,
        },
        "prolog": prolog,
        "rag": {"semantic_chunks": semantic_chunks, "hierarchical_chunks": hierarchical_chunks},
        "audit": audit,
        "quality_report": {
            "status": audit["status"],
            "promotion_status": audit["promotion_status"],
            "production_artifacts_emitted": verified,
            "total_courses": len(courses),
            "total_units": audit["computed_total_units"],
            "declared_total_units": audit["declared_total_units"],
            "years_detected": audit["years_detected"],
            "terms_detected": audit["terms_detected"],
            "total_prerequisite_relations": len(prolog["relations"]["prerequisites"]),
            "total_standing_rules": len(prolog["relations"]["standing_requirements"]),
            "total_elective_tracks": len(tracks),
            "total_semantic_chunks": len(semantic_chunks),
            "total_hierarchical_chunks": len(hierarchical_chunks),
            "unresolved_prerequisites": len(audit["unresolved_prerequisites"]),
            "errors": audit["errors"],
            "warnings": audit["warnings"],
            "raw_docling_json_path": str(raw_json_path) if raw_json_path else None,
        },
    }
    return payload


def build_essentials(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Project an audited extraction into portable curriculum facts."""
    source_path = Path(payload["source_path"]).resolve()
    if source_path.suffix.lower() != ".pdf":
        raise ValueError("Essentials require a source PDF")
    try:
        source_pdf = source_path.relative_to(SOURCE_PDF_ROOT.resolve()).as_posix()
    except ValueError:
        source_pdf = source_path.name

    return {
        "schema_version": "palsu-prospectus-essentials-v1",
        "source_pdf": source_pdf,
        "extraction_status": payload["audit"]["promotion_status"],
        "audit_errors": payload["audit"]["errors"],
        "audit_warnings": payload["audit"]["warnings"],
        "program": payload["program"],
        "degree": payload["degree"],
        "college": payload["college"],
        "campus": payload["campus"],
        "effective_school_year": payload["metadata"].get("effective_school_year"),
        "courses": [
            {
                "course_code": course["course_code"],
                "course_title": course["course_title"],
                "year_level": course["year_level"],
                "semester": course["semester"],
                "total_units": course["total_units"],
                "lecture_units": course["lecture_units"],
                "lab_units": course["lab_units"],
                "prerequisites": course["prerequisites"],
                "prerequisites_raw": course["prerequisites_raw"],
                "prerequisites_unresolved": course["prerequisites_unresolved"],
                "standing_requirements": course["standing_requirements"],
                "category": course["category"],
                "is_elective": course["is_elective"],
                "elective_group": course["elective_group"],
                "source_page": course.get("provenance", {}).get("page"),
            }
            for course in payload["courses"]
        ],
        "elective_tracks": payload["elective_tracks"],
    }


def process_prospectus(
    input_path: Path,
    output_path: Path | None = None,
    export_pl: bool = False,
    export_jsonl: bool = False,
    export_csv: bool = False,
    device: str = "auto",
    semantic_doc_path: Path | None = DEFAULT_SEMANTIC_DOC,
    force_reconvert: bool = True,
    converter: Any = None,
    repair_provider: SemanticRepairProvider | None = None,
    quiet: bool = False,
) -> dict[str, Any]:
    """Full pipeline for one prospectus: convert, parse, audit, write."""
    input_path = Path(input_path).resolve()
    stem = input_path.stem
    if stem.endswith("_docling"):
        stem = stem[: -len("_docling")]
    if output_path:
        final_path = Path(output_path)
    elif input_path.suffix.lower() == ".pdf":
        try:
            relative_parent = input_path.relative_to(SOURCE_PDF_ROOT.resolve()).parent
        except ValueError:
            relative_parent = Path()
        final_path = find_default_output_root() / relative_parent / f"{stem}_prospectus.json"
    else:
        final_path = input_path.parent / f"{stem}_prospectus.json"
    if final_path.suffix.lower() != ".json" or final_path.resolve() == input_path:
        raise ValueError("Output must be a JSON file distinct from the source")
    base = final_path.stem.replace("_prospectus", "")
    essentials_path = final_path.with_name(f"{base}_essentials.json")
    for stale in (
        final_path,
        essentials_path,
        final_path.with_name(f"{base}_prospectus.pl"),
        final_path.with_name(f"{base}_rag.jsonl"),
        final_path.with_name(f"{base}_review.csv"),
    ):
        stale.unlink(missing_ok=True)
    raw_cache_path = final_path.parent / f"{stem}_docling.json" if input_path.suffix.lower() == ".pdf" else None
    document, raw_json_path = load_document(
        input_path, device=device, force_reconvert=force_reconvert,
        converter=converter, raw_json_path=raw_cache_path,
    )
    payload = build_payload(
        document,
        input_path,
        semantic_doc_path,
        raw_json_path,
        repair_provider=repair_provider,
    )

    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    if not quiet:
        print(f"[+] Prospectus JSON -> {final_path}")

    if input_path.suffix.lower() == ".pdf":
        essentials_path.write_text(
            json.dumps(build_essentials(payload), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        if not quiet:
            print(f"[+] Curriculum essentials -> {essentials_path}")

    if payload["audit"]["status"] == "error":
        if not quiet:
            print(f"[!] Audit failed with ERROR status. Blocking downstream exports (.pl, _rag.jsonl).")
    else:
        if export_pl:
            pl_path = final_path.with_name(f"{base}_prospectus.pl")
            pl_path.write_text("\n".join(payload["prolog"]["clauses"]) + "\n", encoding="utf-8")
            if not quiet:
                print(f"[+] Prolog knowledge base -> {pl_path}")
        if export_jsonl:
            jsonl_path = final_path.with_name(f"{base}_rag.jsonl")
            with jsonl_path.open("w", encoding="utf-8") as handle:
                for chunk in payload["rag"]["semantic_chunks"] + payload["rag"]["hierarchical_chunks"]:
                    handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            if not quiet:
                print(f"[+] RAG corpus -> {jsonl_path}")
    if export_csv:
        csv_path = final_path.with_name(f"{base}_review.csv")
        write_review_csv(payload["courses"], csv_path)
        if not quiet:
            print(f"[+] Review CSV -> {csv_path}")

    if not quiet:
        print_audit_summary(payload)
    return payload


def print_audit_summary(payload: dict[str, Any]) -> None:
    audit = payload["audit"]
    status = audit["status"].upper()
    print(
        f"[{status}] {payload.get('degree') or payload.get('program') or 'unknown program'}: "
        f"{audit['total_courses']} courses, {audit['computed_total_units']} units, "
        f"years {audit['years_detected']}"
    )
    for message in audit["errors"]:
        print(f"    ERROR: {message}")
    for message in audit["warnings"][:12]:
        print(f"    warn:  {message}")
    remaining = len(audit["warnings"]) - 12
    if remaining > 0:
        print(f"    ...and {remaining} more warning(s) in audit.warnings")


# =============================================================================
# 16. Batch engine
# =============================================================================
def safe_stem(path: Path) -> str:
    stem = Path(path).stem.strip()
    if stem.endswith("_docling"):  # batching saved Docling JSON should not double the suffix
        stem = stem[: -len("_docling")]
    stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", stem)
    return re.sub(r"\s+", " ", stem).strip() or "prospectus"


def find_default_input_root() -> Path:
    return SOURCE_PDF_ROOT.resolve()


def find_default_output_root() -> Path:
    return (Path(__file__).resolve().parent / "docling_jsonified_output").resolve()


@dataclass
class BatchConfig:
    input_root: Path = field(default_factory=find_default_input_root)
    output_root: Path = field(default_factory=find_default_output_root)
    recursive: bool = True
    preserve_structure: bool = True
    export_mode: str = "side_by_side"  # side_by_side | per_pdf_folder
    write_json: bool = True
    write_csv: bool = True
    write_pl: bool = True
    write_jsonl: bool = True
    write_manifest: bool = True
    skip_existing: bool = False
    force_reconvert: bool = False
    device: str = "auto"
    strict: bool = False
    semantic_doc: Path | None = DEFAULT_SEMANTIC_DOC
    include_patterns: list[str] = field(default_factory=lambda: ["*.pdf"])


@dataclass
class BatchItem:
    source_pdf: Path
    json_path: Path
    csv_path: Path
    pl_path: Path
    jsonl_path: Path

    @property
    def pdf_path(self) -> Path:
        return self.source_pdf


IGNORED_DIR_PARTS = {
    "palsu_jsonified_output", "docling_jsonified_output", ".venv", ".docling-venv",
    "__pycache__", ".git", "node_modules",
}


def scan_inputs(
    input_root: Path, recursive: bool = True, patterns: Sequence[str] | None = None
) -> list[Path]:
    root = Path(input_root).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Input folder does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Input path is not a folder: {root}")

    found: list[Path] = []
    for pattern in patterns or ["*.pdf"]:
        iterator = root.rglob(pattern) if recursive else root.glob(pattern)
        for path in iterator:
            if not path.is_file():
                continue
            if any(part.lower() in IGNORED_DIR_PARTS for part in path.parts):
                continue
            if path.name.endswith("_docling.json") and pattern == "*.json":
                pass  # explicitly requested
            if path not in found:
                found.append(path)
    return sorted(found)


# Backwards-compatible alias for callers that used the v1 name.
scan_pdfs = scan_inputs


def build_batch_items(paths: Sequence[Path], config: BatchConfig) -> list[BatchItem]:
    input_root = Path(config.input_root).expanduser().resolve()
    output_root = Path(config.output_root).expanduser().resolve()
    items: list[BatchItem] = []

    for source in paths:
        source = Path(source).resolve()
        try:
            relative = source.relative_to(input_root)
        except ValueError:
            relative = Path(source.name)
        base_dir = output_root / relative.parent if config.preserve_structure else output_root
        stem = safe_stem(source)

        if config.export_mode == "side_by_side":
            items.append(
                BatchItem(
                    source_pdf=source,
                    json_path=base_dir / f"{stem}_prospectus.json",
                    csv_path=base_dir / f"{stem}_review.csv",
                    pl_path=base_dir / f"{stem}_prospectus.pl",
                    jsonl_path=base_dir / f"{stem}_rag.jsonl",
                )
            )
        else:
            folder = base_dir / stem
            items.append(
                BatchItem(
                    source_pdf=source,
                    json_path=folder / "prospectus.json",
                    csv_path=folder / "review.csv",
                    pl_path=folder / "prospectus.pl",
                    jsonl_path=folder / "rag.jsonl",
                )
            )
    return items


def write_manifest(records: Sequence[dict[str, Any]], output_root: Path) -> Path:
    """Single, unambiguous manifest writer (v1 had two overlapping signatures)."""
    target = Path(output_root).resolve() / "batch_manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "total": len(records),
            "ok": sum(1 for r in records if r.get("status") == "ok"),
            "warn": sum(1 for r in records if r.get("status") == "warn"),
            "audit_failed": sum(1 for r in records if r.get("status") == "audit_error"),
            "skipped": sum(1 for r in records if r.get("status") == "skipped"),
            "failed": sum(1 for r in records if r.get("status") == "error"),
        },
        "records": records,
    }
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def run_batch(config: BatchConfig) -> dict[str, Any]:
    """Extract every prospectus under config.input_root, then write a manifest."""
    sources = scan_inputs(config.input_root, config.recursive, config.include_patterns)
    items = build_batch_items(sources, config)
    records: list[dict[str, Any]] = []

    converter = None
    if any(item.source_pdf.suffix.lower() == ".pdf" for item in items):
        needs_conversion = any(
            not config.skip_existing or config.force_reconvert or not item.json_path.exists()
            or not item.json_path.with_name(
                f"{item.json_path.stem.replace('_prospectus', '')}_essentials.json"
            ).exists()
            for item in items if item.source_pdf.suffix.lower() == ".pdf"
        )
        if needs_conversion:
            try:
                ensure_docling_env()
                converter = get_shared_converter(device=config.device)
            except Exception as exc:
                print(f"[!] Could not pre-warm Docling: {exc}")

    iterable: Iterable[BatchItem] = items
    if RICH_AVAILABLE and console and items:
        iterable = track(items, description="Extracting prospectuses...")

    for item in iterable:
        essentials_path = item.json_path.with_name(
            f"{item.json_path.stem.replace('_prospectus', '')}_essentials.json"
        )
        record: dict[str, Any] = {
            "source": str(item.source_pdf),
            "json_path": str(item.json_path),
            "csv_path": str(item.csv_path),
            "status": "pending",
        }
        try:
            if (config.skip_existing and not config.force_reconvert and item.json_path.exists()
                    and (item.source_pdf.suffix.lower() != ".pdf" or essentials_path.exists())):
                record.update({"status": "skipped", "reason": "output already exists"})
                records.append(record)
                continue

            payload = process_prospectus(
                item.source_pdf,
                output_path=item.json_path,
                export_pl=config.write_pl,
                export_jsonl=config.write_jsonl,
                export_csv=config.write_csv,
                device=config.device,
                semantic_doc_path=config.semantic_doc,
                converter=converter,
                force_reconvert=True,
                quiet=True,
            )
            audit = payload["audit"]
            record.update(
                {
                    "status": "audit_error" if audit["status"] == "error" else audit["status"],
                    "program": payload.get("program"),
                    "degree": payload.get("degree"),
                    "college": payload.get("college"),
                    "effective_school_year": payload["metadata"].get("effective_school_year"),
                    "course_count": audit["total_courses"],
                    "total_units": audit["computed_total_units"],
                    "declared_total_units": audit["declared_total_units"],
                    "years_detected": audit["years_detected"],
                    "errors": audit["errors"],
                    "warning_count": len(audit["warnings"]),
                    "essentials_path": str(essentials_path)
                    if item.source_pdf.suffix.lower() == ".pdf" else None,
                }
            )
        except Exception as exc:
            record.update(
                {
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "traceback": traceback.format_exc(limit=5),
                }
            )
        records.append(record)

    manifest_path = write_manifest(records, config.output_root) if config.write_manifest else None
    summary = {
        "total": len(records),
        "succeeded": sum(1 for r in records if r["status"] in {"ok", "warn"}),
        "audit_failed": sum(1 for r in records if r["status"] == "audit_error"),
        "skipped": sum(1 for r in records if r["status"] == "skipped"),
        "failed": sum(1 for r in records if r["status"] == "error"),
        "manifest_path": str(manifest_path) if manifest_path else None,
        "records": records,
    }
    return summary


# =============================================================================
# 17. Interactive terminal UI
# =============================================================================
def print_line(message: str = "") -> None:
    if RICH_AVAILABLE and console:
        console.print(message)
    else:
        print(
            re.sub(
                r"\[/?(?:bold|italic|dim|underline|red|green|blue|cyan|magenta|yellow|white|black)"
                r"[^\]]*\]",
                "",
                message,
            )
        )


def ask_text(prompt: str, default: str = "") -> str:
    try:
        if RICH_AVAILABLE:
            return Prompt.ask(prompt, default=default)
        suffix = f" [{default}]" if default else ""
        return input(f"{prompt}{suffix}: ").strip() or default
    except (EOFError, KeyboardInterrupt):
        return default


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    try:
        if RICH_AVAILABLE:
            return Confirm.ask(prompt, default=default)
        answer = input(f"{prompt} ({'Y/n' if default else 'y/N'}): ").strip().lower()
        return default if not answer else answer in {"y", "yes", "1", "true"}
    except (EOFError, KeyboardInterrupt):
        return default


class ProspectusTUI:
    """Menu-driven front end for batch and single-file extraction."""

    def __init__(self) -> None:
        self.config = BatchConfig()
        self.last_scan: list[Path] = []

    # -- helpers ----------------------------------------------------------
    def pause(self, message: str = "") -> None:
        if message:
            print_line(f"\n{message}")
        try:
            input("\nPress Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            pass

    def header(self) -> None:
        print("\n")
        title = f"PalSU Prospectus Extractor ({SCHEMA_VERSION})"
        subtitle = "Docling -> audited JSON, Prolog knowledge base and RAG corpus"
        if RICH_AVAILABLE and console:
            console.print(Panel.fit(f"[bold]{title}[/bold]\n{subtitle}", border_style="cyan"))
        else:
            print(title)
            print(subtitle)
            print("=" * len(title))

    def show_config(self) -> None:
        cfg = self.config
        rows = [
            ("Input root", str(cfg.input_root)),
            ("Output root", str(cfg.output_root)),
            ("Device", cfg.device.upper()),
            ("Recursive", str(cfg.recursive)),
            ("Preserve structure", str(cfg.preserve_structure)),
            ("Export mode", cfg.export_mode),
            ("Write CSV / PL / JSONL", f"{cfg.write_csv} / {cfg.write_pl} / {cfg.write_jsonl}"),
            ("Skip existing", str(cfg.skip_existing)),
            ("Semantic map", str(cfg.semantic_doc) if cfg.semantic_doc else "(none)"),
            ("Files in last scan", str(len(self.last_scan))),
        ]
        if RICH_AVAILABLE and console:
            table = Table(title="Current settings")
            table.add_column("Setting", style="bold")
            table.add_column("Value")
            for key, value in rows:
                table.add_row(key, value)
            console.print(table)
        else:
            print("\nCurrent settings:")
            for key, value in rows:
                print(f"  {key}: {value}")

    # -- menu -------------------------------------------------------------
    def main_menu(self) -> None:
        while True:
            self.header()
            self.show_config()
            print_line("\n[1] Set input folder")
            print_line("[2] Set output folder")
            print_line("[3] Scan for prospectuses")
            print_line("[4] Configure device and exports")
            print_line("[5] Preview batch plan")
            print_line("[6] Run batch extraction")
            print_line("[7] Single file extraction")
            print_line("[8] Inspect an extracted prospectus JSON")
            print_line("[9] Dump table grid (layout debugging)")
            print_line("[t] Run self-test suite")
            print_line("[0] Exit")

            choice = ask_text("Choose", "0").strip().lower()
            try:
                if choice == "1":
                    self.set_folder("input")
                elif choice == "2":
                    self.set_folder("output")
                elif choice == "3":
                    self.scan()
                elif choice == "4":
                    self.configure()
                elif choice == "5":
                    self.preview()
                elif choice == "6":
                    self.run_batch_interactive()
                elif choice == "7":
                    self.single_file()
                elif choice == "8":
                    self.inspect()
                elif choice == "9":
                    self.dump_grid_interactive()
                elif choice == "t":
                    failures = run_self_tests()
                    self.pause("Self-test passed." if not failures else f"{failures} self-test failure(s).")
                elif choice == "0":
                    print_line("Exiting. Review the *_review.csv before loading into Prolog or a vector store.")
                    return
                else:
                    self.pause("Invalid choice.")
            except Exception as exc:
                self.pause(f"Error: {type(exc).__name__}: {exc}")

    def set_folder(self, which: str) -> None:
        current = self.config.input_root if which == "input" else self.config.output_root
        value = ask_text(f"{which.title()} folder path", str(current)).strip().strip('"')
        path = Path(value).expanduser()
        if which == "input":
            if not path.is_dir():
                self.pause(f"Folder not found: {path}")
                return
            self.config.input_root = path.resolve()
            self.last_scan = []
        else:
            self.config.output_root = path.resolve()
        self.pause(f"{which.title()} folder updated.")

    def scan(self) -> None:
        self.last_scan = scan_inputs(
            self.config.input_root, self.config.recursive, self.config.include_patterns
        )
        print_line(f"\nFound {len(self.last_scan)} file(s):")
        for index, path in enumerate(self.last_scan[:15], start=1):
            try:
                shown = path.relative_to(self.config.input_root)
            except ValueError:
                shown = Path(path.name)
            print_line(f"  [{index:2d}] {shown}")
        if len(self.last_scan) > 15:
            print_line(f"  ...and {len(self.last_scan) - 15} more.")
        self.pause()

    def configure(self) -> None:
        cfg = self.config
        device = ask_text("Device [auto / cuda / cpu]", cfg.device).strip().lower()
        if device in {"auto", "cuda", "cpu"}:
            cfg.device = device
        patterns = ask_text("File patterns (comma separated)", ", ".join(cfg.include_patterns))
        cfg.include_patterns = [p.strip() for p in patterns.split(",") if p.strip()] or ["*.pdf"]
        cfg.recursive = ask_yes_no("Scan subfolders recursively?", cfg.recursive)
        cfg.preserve_structure = ask_yes_no("Mirror the input folder structure?", cfg.preserve_structure)
        print_line("\n[1] side_by_side  output/<rel>/<stem>_prospectus.json")
        print_line("[2] per_pdf_folder output/<rel>/<stem>/prospectus.json")
        mode = ask_text("Export mode", "1" if cfg.export_mode == "side_by_side" else "2").strip()
        cfg.export_mode = "side_by_side" if mode == "1" else "per_pdf_folder"
        cfg.write_csv = ask_yes_no("Write review CSV?", cfg.write_csv)
        cfg.write_pl = ask_yes_no("Write Prolog knowledge base?", cfg.write_pl)
        cfg.write_jsonl = ask_yes_no("Write RAG JSONL?", cfg.write_jsonl)
        cfg.write_manifest = ask_yes_no("Write batch manifest?", cfg.write_manifest)
        cfg.skip_existing = ask_yes_no("Skip files whose output already exists?", cfg.skip_existing)
        self.pause("Settings updated.")

    def preview(self) -> None:
        if not self.last_scan:
            self.last_scan = scan_inputs(
                self.config.input_root, self.config.recursive, self.config.include_patterns
            )
        items = build_batch_items(self.last_scan, self.config)
        print_line(f"\nBatch plan ({len(items)} file(s)):")
        for item in items[:10]:
            print_line(f"  IN : {item.source_pdf.name}")
            print_line(f"  OUT: {item.json_path}")
        if len(items) > 10:
            print_line(f"  ...and {len(items) - 10} more.")
        self.pause()

    def run_batch_interactive(self) -> None:
        if not self.last_scan:
            self.last_scan = scan_inputs(
                self.config.input_root, self.config.recursive, self.config.include_patterns
            )
        if not self.last_scan:
            self.pause("Nothing to process. Check the input folder and patterns.")
            return
        if not ask_yes_no(f"Process {len(self.last_scan)} file(s)?", default=False):
            self.pause("Cancelled.")
            return
        summary = run_batch(self.config)
        print_line(
            f"\nDone: {summary['succeeded']} extracted, {summary['audit_failed']} failed audit, "
            f"{summary['skipped']} skipped, {summary['failed']} errored."
        )
        if summary.get("manifest_path"):
            print_line(f"Manifest: {summary['manifest_path']}")
        self.pause()

    def _pick_file(self) -> Path | None:
        if not self.last_scan:
            try:
                self.last_scan = scan_inputs(
                    self.config.input_root, self.config.recursive, self.config.include_patterns
                )
            except Exception:
                self.last_scan = []
        if self.last_scan:
            print_line(f"\nAvailable files ({len(self.last_scan)}):")
            for index, path in enumerate(self.last_scan[:12], start=1):
                print_line(f"  [{index:2d}] {path.name}")
            if len(self.last_scan) > 12:
                print_line(f"  ...and {len(self.last_scan) - 12} more.")
        value = ask_text("Select # or enter a full path").strip().strip('"')
        if not value:
            return None
        if value.isdigit() and self.last_scan:
            index = int(value)
            if 1 <= index <= len(self.last_scan):
                return self.last_scan[index - 1]
            return None
        candidate = Path(value).expanduser()
        if candidate.exists():
            return candidate.resolve()
        matches = [p for p in self.last_scan if value.lower() in p.name.lower()]
        return matches[0] if matches else None

    def single_file(self) -> None:
        path = self._pick_file()
        if not path:
            self.pause("File not found.")
            return
        try:
            payload = process_prospectus(
                path,
                export_pl=self.config.write_pl,
                export_jsonl=self.config.write_jsonl,
                export_csv=self.config.write_csv,
                device=self.config.device,
                semantic_doc_path=self.config.semantic_doc,
            )
            self.pause(
                f"Extracted {payload['audit']['total_courses']} courses "
                f"({payload['audit']['status'].upper()})."
            )
        except Exception as exc:
            self.pause(f"Extraction failed: {type(exc).__name__}: {exc}")

    def dump_grid_interactive(self) -> None:
        path = self._pick_file()
        if not path:
            self.pause("File not found.")
            return
        document, _ = load_document(path, device=self.config.device)
        text = dump_grid(document)
        out_path = path.with_name(f"{path.stem}_grid_dump.txt")
        out_path.write_text(text, encoding="utf-8")
        print_line(text[:4000])
        self.pause(f"Full dump written to {out_path}")

    def inspect(self) -> None:
        value = ask_text("Path to *_prospectus.json").strip().strip('"')
        path = Path(value).expanduser()
        if not path.exists():
            self.pause(f"File not found: {path}")
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            self.pause(f"Could not read JSON: {exc}")
            return
        audit = data.get("audit", {})
        print_line(f"\nProgram: {data.get('program')}  ({data.get('degree')})")
        print_line(f"College: {data.get('college')} - {data.get('college_name')}")
        print_line(f"SY:      {data.get('metadata', {}).get('effective_school_year')}")
        print_line(f"Status:  {audit.get('status', 'unknown').upper()}")
        print_line(f"Courses: {audit.get('total_courses')}  Units: {audit.get('computed_total_units')}")
        print_line(f"Years:   {audit.get('years_detected')}")
        for term in audit.get("term_unit_audit", []):
            flag = "ok " if term["matches"] else "BAD"
            print_line(
                f"  [{flag}] {term['year_level']} {term['semester']}: "
                f"{term['computed_units']} units / declared {term['declared_units']}"
            )
        for message in audit.get("errors", []):
            print_line(f"  ERROR: {message}")
        for message in audit.get("warnings", [])[:10]:
            print_line(f"  warn:  {message}")
        self.pause()


# =============================================================================
# 18. Self-test suite
# =============================================================================
# Fixtures are transcriptions of the two prospectuses that broke v1:
#   * BS Computer Science, SY 2025-2026 (8-column table, merged banner rows,
#     superscript footnote markers, wrapped prerequisite text)
#   * BS Architecture, SY 2018-2019 (10-column table with Grade columns, five
#     year levels, series-numbered titles such as "History of Architecture 3")
# Merged cells are repeated across their span exactly as Docling renders them.
CS_HEADER = [
    "Course Code", "Course Title", "Unit", "Pre- requisite",
    "Course Code", "Course Title", "Unit", "Pre- requisite",
]


def _cs_row(left: Sequence[str], right: Sequence[str] = ("", "", "", "")) -> list[str]:
    return [*left, *right]


def _merged(text: str, width: int) -> list[str]:
    return [text] * width


def _cs_semester_row() -> list[str]:
    return ["FIRST SEMESTER"] * 4 + ["SECOND SEMESTER"] * 4


def cs_fixture_grid() -> list[list[str]]:
    grid: list[list[str]] = [CS_HEADER]

    grid.append(_merged("FIRST YEAR", 8))
    grid.append(_cs_semester_row())
    grid += [
        _cs_row(("CS 1", "Discrete Structures 1 1", "3", ""), ("CS 2", "Discrete Structures 2 2", "3", "CS 1")),
        _cs_row(("CC 1/L", "Introduction to Computing", "2/1", ""), ("CC 3/L", "Computer Programming 2", "2/1", "CC 2/L")),
        _cs_row(("CC 2/L", "Computer Programming 1", "2/1", ""), ("Electronics/L", "Fundamentals of Electronics 3", "1/2", "")),
        _cs_row(("GE-AA", "Art Appreciation", "3", ""), ("AMR 1", "Statistical Methods for Computer Science 4", "3", "")),
        _cs_row(("GE-PH", "Readings in Philippine History", "3", ""), ("GE-PC", "Purposive Communication", "3", "")),
        _cs_row(("GE-MMW", "Mathematics in the Modern World", "3", ""), ("GE-UTS", "Understanding the Self", "3", "")),
        _cs_row(("PATHFit 1", "Movement Competency Training", "2", ""), ("PATHFit 2", "Exercise-based Fitness Activities", "2", "PATH Fit 1")),
        _cs_row(("NSTP 1", "CWTS/ROTC 1", "3", ""), ("NSTP 2", "CWTS/ROTC 2", "3", "NSTP 1")),
        _cs_row(("Total", "", "23", ""), ("Total", "", "23", "")),
    ]

    grid.append(_merged("SECOND YEAR", 8))
    grid.append(_cs_semester_row())
    grid += [
        _cs_row(("CS 3", "Automata Theory and Formal Languages 5", "3", "CS 2, CC 2/L"), ("CS 6/L", "Computer Architecture and Organization", "2/1", "CC 4/L, CC 1/L")),
        _cs_row(("CS 4/L", "Web Systems and Technologies 6", "2/1", "CC 3/L, CC 1/L"), ("CS 7", "Algorithms and Complexities", "3", "CC 4/L, CS 3")),
        _cs_row(("CS 5/L", "Object Oriented Programming", "2/1", "CC 3/L"), ("CS 8/L", "Multimedia Technology 9", "2/1", "CC 1/L")),
        _cs_row(("CC 4/L", "Data Structures and Algorithms", "2/1", "CC 3/L, CS 2"), ("CS 9/L", "Software Engineering 1 10", "2/1", "CS 5/L, CC 5/L")),
        _cs_row(("CC 5/L", "Information Management 1 7", "2/1", "CC 3/L, CS 2"), ("GE-CW", "The Contemporary World 11", "3", "")),
        _cs_row(("AMR 2", "Calculus for Computer Science 8", "4", "GE: MMW"), ("GE-LWR", "Life and Works of Rizal", "3", "")),
        _cs_row(("GE-Elect: EM", "The Entrepreneurial Mind", "3", ""), ("GE-PS", "Palawan Studies", "3", "")),
        _cs_row(("PATHFit 3", "Dance and Sports", "2", "PATH Fit 2"), ("PATHFit 4", "Recreation", "2", "PATH Fit 2")),
        _cs_row(("Total", "", "24", ""), ("Total", "", "23", "")),
    ]

    grid.append(_merged("THIRD YEAR", 8))
    grid.append(_cs_semester_row())
    grid += [
        _cs_row(("CS 10/L", "Information Management 2 12", "2/1", "CC 5/L"), ("CS 12/L", "Software Engineering 2 18", "2/1", "CS 9/L")),
        _cs_row(("CS 11/L", "Programming Languages", "2/1", "CS 3"), ("CS 13/L", "Computer Security and Information Assurance", "2/1", "CS 6/L CS 10/L")),
        _cs_row(("CS Elect 1/L", "Intelligent Systems 1 13", "2/1", "CC 4/L, CS 3"), ("CS 14/L", "Operating Systems 19", "2/1", "CS 6/L, CS 7")),
        _cs_row(("CS Elect 2/L", "Graphics and Visual Computing 14", "2/1", "CS 5/L, CC 4/L,"), ("CS 15/L", "Networks and Communication 20", "2/1", "CC 4/L, CS 6/L")),
        _cs_row(("CC 6/L", "Application Development and Emerging Technologies", "2/1", "CS 4/L, CS 5/L"), ("CS Elect 3/L", "Intelligent Systems 2 21", "2/1", "CS Elect 1 CS 5/L AMR 1")),
        _cs_row(("GE-ET", "Ethics 15", "3", ""), ("CS Elect 4/L", "CS Elective 4 22", "2/1", "70% of the total units of the past")),
        # wrapped prerequisite continuation row, exactly as Docling emits it
        _cs_row(("", "", "", ""), ("", "", "", "semesters.")),
        _cs_row(("GE-Elect: ES", "Environmental Science 16", "3", ""), ("GE-STS", "Science, Technology and Society 23 3", "3", "")),
        _cs_row(("GE-IER", "Intensive English Review 17", "3", ""), ("Thesis 1", "Proposal Writing", "2", "CS 9/L, CS Elect 1/L")),
        _cs_row(("Total", "", "24", ""), ("Total", "", "23", "")),
    ]

    grid.append(_merged("FOURTH YEAR", 8))
    grid.append(_cs_semester_row())
    grid += [
        _cs_row(("CS 16/L", "Human Computer Interaction 24", "2/1", "CC 6/L"), ("PRACTICUM", "Practicum (300 hours)", "3", "90% of all major courses")),
        _cs_row(("CS 17", "Social Issues and Professional Practices", "3", "CC 5/L, CC 6/L"), ("Thesis 3", "Thesis Writing and Colloquium", "2", "Thesis 2")),
        _cs_row(("CS Elect 5/L", "CS Elective 5 25", "2/1", "70% of the total units of the past semesters.")),
        _cs_row(("GE-Elect: LIT", "Great Books 26", "3", "")),
        _cs_row(("Thesis 2", "Data Gathering and Writing", "2", "Thesis 1")),
        _cs_row(("Total", "", "14", ""), ("Total", "", "5", "")),
    ]

    grid.append(_merged("TOTAL: 159", 8))
    return grid


CS_TEXT_ITEMS: list[tuple[str, str]] = [
    ("section_header", "VIII. PROPOSED PROGRAM OF STUDY"),
    ("title", "PROPOSED BACHELOR OF SCIENCE IN COMPUTER SCIENCE PROGRAM OF STUDY"),
    ("text", "Proposed Date of Implementation: First Semester, SY 2025-2026"),
    ("text", "CS Elective 4 22"),
    ("text", "CS Elect 4/La. Mathematical Methods for Computational Science"),
    ("text", "CS Elect 4/Lb. IT Audits and Controls"),
    ("text", "CS Elect 4/Lc. Integrative Programming and Technologies 1"),
    ("text", "CS Elect 4/Ld. Platform Technologies"),
    ("text", "CS Elective 5 25"),
    ("text", "CS Elect 5/La. Parallel and Distributed Computing"),
    ("text", "CS Elect 5/Lb. IT Service Management"),
    ("text", "CS Elect 5/Lc. Event Driven Programming"),
    ("text", "CS Elect 5/Ld. Human Computer Interaction 2"),
    ("text", "Note: All major courses are written in italics."),
]

BSA_HEADER = [
    "Grade", "Course Code", "Course Title", "Unit/s", "Pre- Req",
    "Grade", "Course Code", "Course Title", "Unit/s", "Pre- Req",
]


def _bsa_row(left: Sequence[str], right: Sequence[str] = ("", "", "", "")) -> list[str]:
    return ["", *left, "", *right]


def _bsa_semester_row() -> list[str]:
    return ["FIRST SEMESTER"] * 5 + ["SECOND SEMESTER"] * 5


def bsa_fixture_grid() -> list[list[str]]:
    """Years 1, 2 and 5 of the Architecture prospectus (enough to pin the regressions)."""
    grid: list[list[str]] = [BSA_HEADER]

    grid.append(_merged("FIRST YEAR", 10))
    grid.append(_bsa_semester_row())
    grid += [
        _bsa_row(("AD-1/L", "Architectural Design 1-Introduction to Design", "1/1", ""), ("AD-2/L", "Architectural Design 2-Creative Design and Fundamentals", "1/1", "AD-1/L, TOA-1")),
        _bsa_row(("GR-1/L", "Architectural Visual Communications 1-Graphics 1", "1/2", ""), ("AR-INT/L", "Architectural Interiors", "2/1", "TOA-1")),
        _bsa_row(("TOA-1/L", "Theory of Architecture1", "2/1", ""), ("GR-2/L", "Architectural Visual Communications 3-Graphics 2", "1/2", "GR-1/L")),
        _bsa_row(("VT-1/L", "Architectural Visual Communications 2-Visual Techniques 1", "1/1", ""), ("VT-2/L", "Architectural Visual Communications 4-Visual Techniques 2", "1/1", "VT-1/L")),
        _bsa_row(("GE-PC", "Purposive Communication", "3", ""), ("TOA-2", "Theory of Architecture 2", "3", "TOA-1")),
        _bsa_row(("GE-PH", "Readings in Philippine History", "3", ""), ("GE-AA", "Art Appreciation", "3", "")),
        _bsa_row(("GE-UTS", "Understanding the Self", "3", ""), ("GE-MMW", "Mathematics in the Modern World", "3", "")),
        _bsa_row(("NSTP-1", "CWTS 1/ ROTC 1", "3", ""), ("Math 19", "Solid Mensuration", "2", "")),
        _bsa_row(("PATH-Fit 1", "Movement Enhancement", "2", ""), ("NSTP-2", "CWTS 2/ ROTC 2", "3", "NSTP-1")),
        _bsa_row(("", "", "", ""), ("PATH-Fit 2", "Fitness Exercises", "2", "PATH-Fit 1")),
        _bsa_row(("Total", "", "24", ""), ("Total", "", "26", "")),
    ]

    grid.append(_merged("SECOND YEAR", 10))
    grid.append(_bsa_semester_row())
    grid += [
        _bsa_row(("AD-3/L", "Architectural Design 3-Creative Design in Architectural Interiors", "1/2", "AD-2/L, TOA-2, AR-INT"), ("AD-4/L", "Architectural Design 4 - Space Planning 1", "1/2", "AD-3/L")),
        _bsa_row(("BT-1", "Building Technology 1 - Building Materials", "3", ""), ("BT-2/L", "Building Technology 2 - Construction Drawings in Wood, Steel and Concrete (1-Storey)", "2/1", "BT-1, BU-1/L")),
        _bsa_row(("BU-1/L", "Building Utilities 1-Plumbing and Sanitary Systems", "2/1", ""), ("HOA-2", "History of Architecture 2", "3", "HOA-1")),
        _bsa_row(("HOA-1", "History of Architecture 1", "3", ""), ("BES 1", "Statics of Rigid Bodies", "3", "MATH 20")),
        _bsa_row(("TD-1", "Tropical Design 1", "3", ""), ("CE 31/FB", "Elementary Surveying", "2", "MATH 19-20")),
        _bsa_row(("VT-3/L", "Architectural Visual Communications 5-Visual Techniques 3", "1/1", "VT-2/L"), ("GE-Elect: ES", "Environmental Science", "3", "")),
        _bsa_row(("Math 20", "Differential and Integral Calculus", "3", "MATH 19"), ("GE-CW", "The Contemporary World", "3", "")),
        _bsa_row(("PATH-Fit 3", "Dance and Sports", "2", "PATH-Fit 1"), ("PATH-Fit 4", "Recreation", "2", "PATH-Fit 1")),
        _bsa_row(("Total", "", "22", ""), ("Total", "", "23", "")),
    ]

    grid.append(_merged("FIFTH YEAR", 10))
    grid.append(_bsa_semester_row())
    grid += [
        _bsa_row(("AD-9/L", "Architectural Design 9 -Thesis Research Writing", "1/4", "AD-8/L"), ("D-10/L", "Architectural Design 9 - Thesis Research Application", "1/4", "AD-9/L")),
        _bsa_row(("Ar-CC 2", "Architectural Comprehensive Course 2", "3", "4th Year Standing, Arc 1"), ("PEC", "Professional Elective Course", "3", "")),
        _bsa_row(("BM/AA-1", "Business Management & Application for Architecture 1", "3", "PLN-2, PP-3"), ("SP-3", "Specialization 3 - Urban Design", "3", "D-7, PLN-2")),
        _bsa_row(("GE- PS", "Palawan Studies", "3", ""), ("BM/AA-2", "Business Management & Application for Architecture 2", "3", "PLN-2, PP-4")),
    ]
    return grid


BSA_TEXT_ITEMS: list[tuple[str, str]] = [
    ("title", "BACHELOR OF SCIENCE IN ARCHITECTURE CURRICULUM PROGRAM OF STUDY"),
    ("text", "Effective SY 2018-2019*"),
    ("text", "*BOR Resolution No. 62, s. 2019 Dated 3 July 2019"),
    ("text", "Doc. Ref. No: PSU-CIM-CUR-011B Revision No: 00 Effective Date: 11 June 2018"),
    ("text", "Total no. of units: 231"),
]


def fixture_document(grid: list[list[str]], text_items: list[tuple[str, str]]) -> LoadedDocument:
    markdown = "\n".join(text for _label, text in text_items)
    return ProspectusEvidence(
        tables=[normalized_table_from_grid(grid, 0)],
        text_items=[
            {"item_id": f"text-{index}", "label": label, "text": text, "page": None, "bbox": None}
            for index, (label, text) in enumerate(text_items)
        ],
        markdown=markdown,
        source_kind="fixture",
    )


def run_self_tests(verbose: bool = True) -> int:
    """Regression suite. Returns the number of failures (0 == healthy)."""
    failures: list[str] = []
    passed = 0

    def check(condition: bool, message: str) -> None:
        nonlocal passed
        if condition:
            passed += 1
        else:
            failures.append(message)
            if verbose:
                print(f"  FAIL: {message}")

    # ---------------- unit-level helpers --------------------------------
    check(match_year_label("SECOND YEAR") == "2nd Year", "upper-case banner must map to 2nd Year")
    check(match_year_label("Second Year") == "2nd Year", "title-case banner must map to 2nd Year")
    check(match_year_label("4th Year Standing") is None, "'4th Year Standing' must not be a banner")
    check(match_year_label("FOURTH YEAR") == "4th Year", "FOURTH YEAR must map to 4th Year")
    check(parse_units("2/1")["total"] == 3, "2/1 must parse to 3 units")
    check(parse_units("23 3")["total"] == 3, "footnote-prefixed unit cell must parse to 3")
    check(parse_units("1/2") == {"raw": "1/2", "lecture": 1, "lab": 2, "total": 3}, "1/2 lecture/lab split")
    check(split_prereq_fragments("CE 31/FB") == ["CE 31/FB"], "'/' must not split a course code")
    check(split_prereq_fragments("AD-2/L, TOA-2, AR-INT") == ["AD-2/L", "TOA-2", "AR-INT"], "comma split")
    check(is_standing_rule("70% of the total units"), "percentage rules are standing rules")
    check(relaxed_key("BT-2/L") == relaxed_key("BT-2"), "lab suffix must not break code matching")

    # ---------------- normalized evidence IR ---------------------------
    raw_ir_fixture = {
        "tables": [
            {
                "prov": [{"page_no": 1, "bbox": {"l": 0, "t": 0, "r": 800, "b": 600}}],
                "data": {
                    "num_rows": 2,
                    "num_cols": 8,
                    "table_cells": [
                        {
                            "text": "SECOND YEAR",
                            "start_row_offset_idx": 0,
                            "end_row_offset_idx": 1,
                            "start_col_offset_idx": 0,
                            "end_col_offset_idx": 8,
                            "bbox": {"l": 10, "t": 10, "r": 790, "b": 30},
                        },
                        {
                            "text": "COMM RE 12",
                            "start_row_offset_idx": 1,
                            "end_row_offset_idx": 2,
                            "start_col_offset_idx": 0,
                            "end_col_offset_idx": 1,
                            "bbox": {"l": 10, "t": 35, "r": 100, "b": 55},
                        },
                    ],
                },
            }
        ],
        "texts": [],
    }
    ir = evidence_adapter(raw_ir_fixture)
    check(len(ir.tables[0].cells) == 2, "IR: a merged cell must remain one canonical cell")
    check(
        ir.tables[0].cells[0].col_start == 0 and ir.tables[0].cells[0].col_end == 8,
        "IR: merged-cell column topology must be retained",
    )
    check(
        project_table_to_grid(ir.tables[0])[0] == ["SECOND YEAR"] * 8,
        "IR: grid projection may repeat a merged cell without changing the canonical IR",
    )
    check(
        ir.tables[0].cells[0].bbox is not None and ir.tables[0].cells[0].bbox.page == 1,
        "IR: table provenance must supply page information to cell bboxes",
    )
    check(
        normalize_evidence(raw_ir_fixture) == normalize_evidence(evidence_adapter(raw_ir_fixture)),
        "IR: serialized and already-adapted evidence must normalize identically",
    )

    raw_cells: list[dict[str, Any]] = []

    def raw_cell(text: str, row: int, col_start: int, col_end: int | None = None) -> None:
        raw_cells.append(
            {
                "text": text,
                "start_row_offset_idx": row,
                "end_row_offset_idx": row + 1,
                "start_col_offset_idx": col_start,
                "end_col_offset_idx": col_end if col_end is not None else col_start + 1,
                "bbox": {
                    "l": float(col_start * 100),
                    "t": float(row * 20),
                    "r": float((col_end if col_end is not None else col_start + 1) * 100),
                    "b": float((row + 1) * 20),
                },
            }
        )

    for column, value in enumerate(CS_HEADER):
        raw_cell(value, 0, column)
    raw_cell("FIRST YEAR", 1, 0, 8)
    raw_cell("FIRST SEMESTER", 2, 0, 4)
    raw_cell("SECOND SEMESTER", 2, 4, 8)
    for column, value in enumerate(
        ["AA 1", "Alpha", "3", "", "BB 1", "Beta", "2/1", "AA 1"]
    ):
        if value:
            raw_cell(value, 3, column)
    raw_docling_fixture = {
        "tables": [
            {
                "prov": [{"page_no": 2}],
                "data": {"num_rows": 4, "num_cols": 8, "table_cells": raw_cells},
            }
        ],
        "texts": [{"label": "title", "text": "BACHELOR OF SCIENCE IN TESTING"}],
    }
    raw_payload = build_payload(
        evidence_adapter(raw_docling_fixture),
        Path("raw_fixture_docling.json"),
        semantic_doc_path=None,
    )
    check(
        [(c["course_code"], c["semester"]) for c in raw_payload["courses"]]
        == [("AA 1", "1st Semester"), ("BB 1", "2nd Semester")],
        "raw Docling integration: structural spans must drive two-up term assignment",
    )
    check(
        all(c["provenance"]["highlightable"] for c in raw_payload["courses"]),
        "raw Docling integration: page/bbox provenance must be viewer-ready",
    )
    check(
        not raw_payload["audit"]["unclaimed_course_candidates"],
        "raw Docling integration: every high-confidence code cell must be claimed",
    )

    # ---------------- BS Computer Science (the document v1 broke) -------
    cs = build_payload(
        fixture_document(cs_fixture_grid(), CS_TEXT_ITEMS),
        Path("1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025.pdf"),
        semantic_doc_path=None,
    )
    audit = cs["audit"]
    courses = {c["course_code"]: c for c in cs["courses"]}
    terms = Counter((c["year_level"], c["semester"]) for c in cs["courses"])

    check(audit["total_courses"] == 55, f"CS: expected 55 courses, got {audit['total_courses']}")
    check(
        audit["years_detected"] == ["1st Year", "2nd Year", "3rd Year", "4th Year"],
        f"CS: year banners must yield four years, got {audit['years_detected']}",
    )
    check(
        terms[("1st Year", "1st Semester")] == 8 and terms[("4th Year", "2nd Semester")] == 2,
        f"CS: term distribution wrong: {sorted(terms.items())}",
    )
    check(audit["computed_total_units"] == 159, f"CS: expected 159 units, got {audit['computed_total_units']}")
    check(audit["declared_total_units"] == 159, "CS: grand total 'TOTAL: 159' must be captured")
    check(all(t["matches"] for t in audit["term_unit_audit"]), "CS: every term checksum must match")
    check(not audit["errors"], f"CS: audit errors: {audit['errors']}")
    check(courses["CS 1"]["course_title"] == "Discrete Structures 1", "CS: footnote marker stripped, series kept")
    check(courses["CS 8/L"]["course_title"] == "Multimedia Technology", "CS: single footnote marker stripped")
    check(
        courses["GE-STS"]["course_title"] == "Science, Technology and Society"
        and courses["GE-STS"]["total_units"] == 3,
        "CS: 'Science, Technology and Society 23 3' must clean to title + 3 units",
    )
    check(courses["PATHFit 2"]["prerequisites"] == ["PATHFit 1"], "CS: 'PATH Fit 1' must resolve to PATHFit 1")
    check(courses["AMR 2"]["prerequisites"] == ["GE-MMW"], "CS: 'GE: MMW' must resolve to GE-MMW")
    check(
        courses["CS 13/L"]["prerequisites"] == ["CS 6/L", "CS 10/L"],
        "CS: separator-less prerequisite run must split into two codes",
    )
    check(
        courses["CS Elect 3/L"]["prerequisites"] == ["CS Elect 1/L", "CS 5/L", "AMR 1"],
        "CS: 'CS Elect 1 CS 5/L AMR 1' must resolve to three codes",
    )
    check(not audit["unresolved_prerequisites"], f"CS: unresolved prerequisites: {audit['unresolved_prerequisites']}")
    check(
        courses["CS Elect 4/L"]["standing_requirements"]
        and "semesters" in courses["CS Elect 4/L"]["standing_requirements"][0],
        "CS: wrapped prerequisite text must be stitched back onto the course",
    )
    check(not audit["prerequisite_ordering_violations"], "CS: no prerequisite should follow its dependent")
    check(not audit["prerequisite_cycles"], "CS: prerequisite graph must be acyclic")
    check(len(cs["elective_tracks"]) == 2, "CS: two elective pools expected")
    check(
        all(len(t["options"]) == 4 for t in cs["elective_tracks"]),
        "CS: each elective pool has four options",
    )
    check(
        courses["CS Elect 4/L"]["elective_group"] == "CS Elective 4",
        "CS: elective pool must be linked to its curriculum slot",
    )
    check(cs["degree"] == "BS Computer Science", f"CS: degree detection, got {cs['degree']}")
    check(
        cs["metadata"]["effective_school_year"] == "2025-2026",
        f"CS: SY detection, got {cs['metadata']['effective_school_year']}",
    )
    check(
        all(c["provenance"]["source_cell_ids"] for c in cs["courses"]),
        "CS: every course must retain source-cell provenance",
    )
    check(
        courses["CS 1"]["year_level"] == "1st Year"
        and courses["CS 10/L"]["year_level"] == "3rd Year",
        "CS: known term assignments must survive the section parser",
    )
    check(
        courses["Electronics/L"]["is_elective"] is False,
        "CS: Electronics/L must not be classified as an elective",
    )
    check(
        "semesters" not in courses["GE-STS"]["prerequisites_raw"].lower(),
        "CS: wrapped standing text must not leak into GE-STS",
    )

    # ---------------- BS Architecture (must not regress) ----------------
    bsa = build_payload(
        fixture_document(bsa_fixture_grid(), BSA_TEXT_ITEMS),
        Path("BSA-for-student-new-version.pdf"),
        semantic_doc_path=None,
    )
    bsa_audit = bsa["audit"]
    bsa_courses = {c["course_code"]: c for c in bsa["courses"]}

    check(
        bsa_audit["years_detected"] == ["1st Year", "2nd Year", "5th Year"],
        f"BSA: year banners wrong: {bsa_audit['years_detected']}",
    )
    check(
        bsa_courses["Ar-CC 2"]["year_level"] == "5th Year",
        "BSA: '4th Year Standing' in a prerequisite must not move the year",
    )
    check(
        bsa_courses["HOA-2"]["course_title"] == "History of Architecture 2",
        "BSA: series numbers must survive (no footnote stripping in this document)",
    )
    check(
        bsa_audit["footnotes"]["enabled"] is False,
        "BSA: footnote stripping must stay disabled for a document without markers",
    )
    check(bsa_courses["AD-1/L"]["total_units"] == 2, "BSA: 1/1 must parse to 2 units")
    check(
        bsa_courses["CE 31/FB"]["prerequisites"] == ["Math 19", "Math 20"],
        "BSA: 'MATH 19-20' must expand to two codes",
    )
    check(
        bsa_courses["BT-2/L"]["prerequisites"] == ["BT-1", "BU-1/L"],
        "BSA: 'BT-1, BU-1/L' must resolve",
    )
    check(
        any("4th Year Standing" in rule for rule in bsa_courses["Ar-CC 2"]["standing_requirements"]),
        "BSA: standing requirement must be captured as a policy rule",
    )
    check(
        "Arc 1" in bsa_courses["Ar-CC 2"]["prerequisites_unresolved"],
        "BSA: an unmatched prerequisite must be reported, not silently emitted",
    )
    check(
        "PP-4" in bsa_courses["BM/AA-2"]["prerequisites_unresolved"],
        "BSA: PP-4 does not exist in this curriculum and must be flagged",
    )
    mismatch = [
        t for t in bsa_audit["term_unit_audit"]
        if (t["year_level"], t["semester"]) == ("2nd Year", "2nd Semester")
    ]
    check(
        bool(mismatch) and mismatch[0]["matches"] is False,
        "BSA: the printed 23-unit total for 2nd Year 2nd Semester must be flagged (courses sum to 22)",
    )
    check(
        bsa["metadata"]["bor_resolution"] is not None and "62" in bsa["metadata"]["bor_resolution"],
        f"BSA: BOR resolution detection, got {bsa['metadata'].get('bor_resolution')}",
    )
    check(
        bsa["metadata"]["effective_school_year"] == "2018-2019",
        f"BSA: SY detection, got {bsa['metadata'].get('effective_school_year')}",
    )
    check(bsa["degree"] == "BS Architecture", f"BSA: degree detection, got {bsa['degree']}")
    check(
        bsa_courses["AD-3/L"]["year_level"] == "2nd Year"
        and bsa_courses["AD-3/L"]["semester"] == "1st Semester",
        "BSA: AD-3/L must resolve to 2nd Year / 1st Semester",
    )

    # ---------------- the exact v1 failure mode -------------------------
    collapsed = build_payload(
        fixture_document(
            [row for row in cs_fixture_grid() if not match_year_label(" ".join(row))], CS_TEXT_ITEMS
        ),
        Path("no_banners.pdf"),
        semantic_doc_path=None,
    )
    check(
        collapsed["audit"]["status"] == "error",
        "A document whose year banners are missing must fail the audit, not pass silently",
    )

    # ---------------- layout and graph edge cases ------------------------
    header8 = ["Course Code", "Course Title", "Unit", "Pre- requisite"] * 2

    def tiny(grid: list[list[str]]) -> dict[str, Any]:
        return build_payload(
            fixture_document(grid, [("title", "BACHELOR OF SCIENCE IN TESTING")]),
            Path("edge.pdf"),
            semantic_doc_path=None,
        )

    architecture_bleed = tiny(
        [
            BSA_HEADER,
            _merged("SECOND YEAR", 10),
            _bsa_semester_row(),
            _bsa_row(
                (
                    "AD-3/L",
                    "Architectural Design 3-Creative Design in Architectural Interiors",
                    "1/2",
                    "SECOND AD-2/L, TOA-2",
                )
            ),
        ]
    )
    architecture_ad3 = architecture_bleed["courses"][0]
    check(
        architecture_ad3["year_level"] == "2nd Year"
        and architecture_ad3["semester"] == "1st Semester",
        "Architecture bleed: AD-3/L must retain the explicit 2Y1S section",
    )
    check(
        "SECOND" not in architecture_ad3["prerequisites_raw"].upper()
        and architecture_ad3["provenance"]["discarded_fragments"],
        "Architecture bleed: structural SECOND must be removed and recorded",
    )

    ab_communication = tiny(
        [
            header8,
            _merged("SECOND YEAR", 8),
            _cs_semester_row(),
            ["GE - STS", "Science, Technology and Society", "3", "", "", "", "", ""],
            _merged("THIRD YEAR", 8),
            _cs_semester_row(),
            [
                "COMM RE 12", "Communication Research 2", "3", "COMM RE 11",
                "COMM CRC 15", "Communication and Culture 15", "3", "",
            ],
        ]
    )
    ab_courses = {course["course_code"]: course for course in ab_communication["courses"]}
    check(
        ab_courses["GE - STS"]["year_level"] == "2nd Year"
        and ab_courses["GE - STS"]["semester"] == "1st Semester",
        "AB Communication: GE - STS must be recovered in 2Y1S",
    )
    check(
        ab_courses["COMM RE 12"]["year_level"] == "3rd Year"
        and ab_courses["COMM RE 12"]["semester"] == "1st Semester",
        "AB Communication: COMM RE 12 must be recovered in 3Y1S",
    )
    check(
        ab_courses["COMM CRC 15"]["year_level"] == "3rd Year"
        and ab_courses["COMM CRC 15"]["semester"] == "2nd Semester",
        "AB Communication: COMM CRC 15 must be recovered in 3Y2S",
    )

    no_semester = tiny(
        [
            ["Course Code", "Course Title", "Unit", "Pre-requisite"],
            _merged("FIRST YEAR", 4),
            ["ZZ 1", "Zulu", "3", ""],
        ]
    )
    check(
        no_semester["courses"][0]["semester"] is None
        and no_semester["audit"]["status"] == "error",
        "missing semester evidence must remain null and route the document to review",
    )
    check(
        not no_semester["prolog"]["clauses"]
        and not no_semester["rag"]["semantic_chunks"]
        and no_semester["audit"]["promotion_status"] == "REVIEW_REQUIRED",
        "failed audit must emit zero production Prolog/RAG artifacts",
    )

    no_semester_evidence = fixture_document(
        [
            ["Course Code", "Course Title", "Unit", "Pre-requisite"],
            _merged("FIRST YEAR", 4),
            ["ZZ 1", "Zulu", "3", ""],
        ],
        [("title", "BACHELOR OF SCIENCE IN TESTING")],
    )

    def unsupported_repair(packet: Mapping[str, Any]) -> Mapping[str, Any]:
        code_cell = next(
            cell["cell_id"] for cell in packet["cells"] if cell["text"] == "ZZ 1"
        )
        return {
            "fields": {
                "semester": {"value": "1st Semester", "evidence": [code_cell]},
            },
            "discarded_fragments": [],
            "ambiguous": False,
        }

    rejected_repair = build_payload(
        no_semester_evidence,
        Path("unsupported_repair.pdf"),
        semantic_doc_path=None,
        repair_provider=unsupported_repair,
    )
    check(
        rejected_repair["courses"][0]["semester"] is None
        and rejected_repair["audit"]["invalid_repairs"],
        "an LLM repair may not introduce a semester unsupported by structural evidence",
    )

    split_course = tiny(
        [
            ["Course Code", "Course Title", "Unit", "Pre-requisite"],
            _merged("FIRST YEAR", 4),
            _merged("FIRST SEMESTER", 4),
            ["AA 1", "", "", ""],
            ["", "Alpha", "3", ""],
        ]
    )
    check(
        len(split_course["courses"]) == 1
        and split_course["courses"][0]["course_title"] == "Alpha"
        and split_course["courses"][0]["total_units"] == 3,
        "course assembly must join a code row with adjacent title/unit evidence",
    )

    headerless = tiny(
        [
            _merged("FIRST YEAR", 8),
            _cs_semester_row(),
            ["AA 1", "Alpha", "3", "", "BB 1", "Beta", "2/1", "AA 1"],
            _merged("SECOND YEAR", 8),
            _cs_semester_row(),
            ["AA 2", "Alpha 2", "3", "AA 1", "", "", "", ""],
        ]
    )
    check(
        [c["year_level"] for c in headerless["courses"]] == ["1st Year", "1st Year", "2nd Year"],
        "a table with no header row must still fall back to a positional layout",
    )

    merged_semesters = tiny(
        [
            header8,
            _merged("FIRST YEAR", 8),
            _merged("FIRST SEMESTER SECOND SEMESTER", 8),
            ["AA 1", "Alpha", "3", "", "BB 1", "Beta", "3", ""],
            header8,  # header repeats after a page break
            _merged("SECOND YEAR", 8),
            _merged("FIRST SEMESTER SECOND SEMESTER", 8),
            ["AA 2", "Alpha 2", "3", "AA 1", "BB 2", "Beta 2", "3", "BB 1"],
        ]
    )
    check(
        [(c["year_level"], c["semester"]) for c in merged_semesters["courses"]]
        == [
            ("1st Year", "1st Semester"), ("1st Year", "2nd Semester"),
            ("2nd Year", "1st Semester"), ("2nd Year", "2nd Semester"),
        ],
        "a fully merged semester row must be assigned across the column groups in order",
    )

    summer = tiny(
        [
            ["Course Code", "Course Title", "Unit", "Pre-requisite"],
            _merged("THIRD YEAR", 4),
            _merged("SUMMER", 4),
            ["OJT 1", "Practicum", "3", "60% of all major courses"],
            ["Total", "", "3", ""],
        ]
    )
    check(
        summer["courses"][0]["semester"] == "Summer"
        and summer["courses"][0]["standing_requirements"] == ["60% of all major courses."],
        "single-block tables, Summer terms and percentage rules must all survive",
    )

    cyclic = tiny(
        [
            header8,
            _merged("FIRST YEAR", 8),
            _cs_semester_row(),
            ["AA 1", "Alpha", "3", "AA 2", "AA 2", "Bravo", "3", "AA 1"],
            ["AA 1", "Alpha duplicate", "3", "", "", "", "", ""],
        ]
    )
    check(
        cyclic["audit"]["prerequisite_cycles"] == [["AA 1", "AA 2", "AA 1"]],
        "a cycle must be reported even when a duplicated row would overwrite its edges",
    )
    check(
        [d["course_code"] for d in cyclic["audit"]["duplicate_course_codes"]] == ["AA 1"],
        "duplicated course codes must be reported",
    )
    check(cyclic["audit"]["status"] == "error", "a cyclic prerequisite graph must fail the audit")

    no_banner = tiny([header8, ["ZZ 1", "Zulu", "3", "", "", "", "", ""]])
    check(
        not no_banner["courses"]
        and no_banner["audit"]["status"] == "error"
        and any("before any year banner" in e for e in no_banner["audit"]["errors"]),
        "courses appearing before any banner must fail closed instead of guessing 1st Year",
    )

    # ---------------- Prolog escaping -----------------------------------
    check(pl_atom("Ethics") == "'Ethics'", "atom quoting")
    check(pl_atom("Bachelor's Degree") == "'Bachelor''s Degree'", "ISO quote doubling inside atoms")

    if verbose:
        total = passed + len(failures)
        print(f"\nSelf-test: {passed}/{total} checks passed.")
        if failures:
            print("Failures:")
            for message in failures:
                print(f"  - {message}")
    return len(failures)


# =============================================================================
# 19. CLI
# =============================================================================
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


if __name__ == "__main__":
    sys.exit(main())
