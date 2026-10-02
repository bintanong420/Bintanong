"""Lecture, laboratory and total unit parsing."""

from __future__ import annotations

from typing import Any
import re

from .text import clean_str
from .footnotes import TRAILING_FRACTION, TWO_TRAILING_INTS


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
