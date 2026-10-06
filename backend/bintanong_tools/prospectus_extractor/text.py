"""Text cleaning, course-code keys, year and semester labels."""

from __future__ import annotations

from typing import Any
import re


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


_ORDINAL = r"(?:FIRST|SECOND|THIRD|FOURTH|FIFTH|1ST|2ND|3RD|4TH|5TH)"
_BANNER_UNIT = rf"(?:{_ORDINAL}\s+YEAR|{_ORDINAL}\s+(?:SEMESTER|SEM\.?)|SEMESTER|SUMMER|MID[\s-]?YEAR)"


# Exact, upper-case printed banner phrases ("FIRST YEAR", "SECOND SEMESTER", "SUMMER", ...).
# Upper case only, so a real title such as "First Aid" or "Summer Internship" never matches.
BANNER_PHRASE = re.compile(rf"\b{_BANNER_UNIT}(?!\w)")


# A bare ordinal is only a wrapped banner tail when a capitalised word follows ("FIRST Ethics") or
# nothing does; "FIRST AID" in an all-caps title keeps its FIRST.
_LEADING_BANNER = re.compile(rf"^(?:(?:{_BANNER_UNIT}(?!\w)|{_ORDINAL}\b(?=\s+[A-Z][a-z]|\s*$))\s*)+")


_TRAILING_BANNER = re.compile(rf"\s+{_BANNER_UNIT}\s*$")


_LEADING_ORDINAL_WORD = re.compile(rf"^{_ORDINAL}\s+(?=[A-Z][a-z])")


def has_banner_text(text: str) -> bool:
    """True when `text` carries a printed banner phrase, or starts with an upper-case ordinal
    word glued to a capitalised word ("FIRST Ethics", the tail of a wrapped "FIRST SEMESTER")."""
    value = clean_str(text)
    return bool(BANNER_PHRASE.search(value) or _LEADING_ORDINAL_WORD.match(value))


def leading_banner(text: str) -> tuple[str, str]:
    """Split `text` into (banner, rest): the run of banner phrases at its start and what follows.
    ("", text) when it does not start with one. rest is "" when the whole text is banner."""
    value = clean_str(text)
    match = _LEADING_BANNER.match(value)
    if not match:
        return "", value
    return match.group().strip(), clean_str(value[match.end():])


def trailing_banner(text: str) -> tuple[str, str]:
    """Split `text` into (rest, banner): banner phrases at its end. (text, "") when none."""
    value = clean_str(text)
    banner = ""
    while True:
        match = _TRAILING_BANNER.search(value)
        if not match:
            return value, banner
        banner = clean_str(f"{match.group().strip()} {banner}")
        value = value[: match.start()]


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
