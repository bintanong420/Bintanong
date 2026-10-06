"""Program, college and school-year metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import re

from .text import clean_str


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
    college_basis = college_evidence = None
    for part in Path(source_path).parts:
        if part in semantic_map:
            college_code, college_name = part, semantic_map[part]["name"]
            college_basis, college_evidence = "path_segment", part
            break
    if not college_code:
        for code, info in semantic_map.items():
            if re.search(rf"(?<![A-Za-z]){re.escape(code)}(?![A-Za-z])", path_str):
                college_code, college_name = code, info["name"]
                college_basis, college_evidence = "path_pattern", code
                break

    program_name = None
    degree = None
    program_basis = program_evidence = None
    for code, info in semantic_map.items():
        for program in info["programs"]:
            name, abbrev = program["program_name"], program["degree"]
            if name.lower() in haystack.lower() or (len(abbrev) > 4 and abbrev.lower() in haystack.lower()):
                program_name, degree = name, abbrev
                program_basis = "semantic_map_match"
                program_evidence = name if name.lower() in haystack.lower() else abbrev
                if not college_code:
                    college_basis, college_evidence = "semantic_map_program_match", name
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
            program_basis, program_evidence = "document_heading", clean_str(match.group(1))
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
    sy_evidence = clean_str(sy_match.group(0)) if sy_match else None
    if not school_year:
        warnings.append("Effective school year not found; left null rather than guessed.")

    def find(pattern: str) -> str | None:
        match = re.search(pattern, head, flags=re.IGNORECASE)
        return clean_str(match.group(1)) if match else None

    def observed(value, basis, evidence):
        return {
            "value": value,
            "basis": basis if value else None,
            "evidence": evidence if value else None,
            "status": "candidate",
        }

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
        # A later phase may add source_kind (for example "ocr") and per-cell confidence here.
        "observations": {
            "campus": observed("Tiniguiban - Main", "extractor_default", None),
            "college_code": observed(college_code, college_basis, college_evidence),
            "program_name": observed(program_name, program_basis, program_evidence),
            "effective_school_year": observed(school_year, "path_or_document_head", sy_evidence),
        },
    }
    return metadata, warnings
