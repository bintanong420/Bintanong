"""Course-code recognition, total rows and the parse result container."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Iterable
import re

from .text import clean_str, is_banner_text
from .footnotes import FootnoteContext
from .prerequisites import DISQUALIFYING_CODE_WORDS, TOTAL_ROW_PATTERN, is_code_like_token


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


MULTIPART_CODE = re.compile(
    r"^(?:"
    r"[A-Za-z]{1,8}(?:[\s-]+[A-Z]{1,6})?[\s-]*\d{1,4}[A-Za-z]*(?:/[A-Za-z0-9]+(?:\s+\d{1,2})?)?"
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


def _two_course_codes_in_cell(text: str) -> tuple[str, str] | None:
    def strong_code(value: str) -> bool:
        elective = re.fullmatch(r"[A-Za-z]{2,8}\s+Elect(?:ive)?s?", value, re.IGNORECASE)
        return bool(elective or (is_probable_course_code(value) and (
            re.search(r"\d", value) or re.fullmatch(r"GE\s*-\s*[A-Z]{2,8}", value)
        )))

    words = clean_str(text).split()
    for boundary in range(1, len(words)):
        first, second = " ".join(words[:boundary]), " ".join(words[boundary:])
        if strong_code(first) and strong_code(second) and re.match(r"[A-Za-z]{2,}", second):
            return first, second
    return None
