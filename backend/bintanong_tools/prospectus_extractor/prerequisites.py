"""Prerequisite tokenising and resolution."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from typing import Iterable
import re

from .text import clean_str, norm_key, relaxed_key


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


# One state per course, describing how completely the extractor understood its
# prerequisite cell. The parser keeps no record of whether an empty cell was
# printed blank, missing, or unreadable (sections._field_at returns None for all
# three), so "reviewed_empty" is reserved for a human review decision and is
# never emitted here.
PREREQUISITE_STATES = (
    "resolved",
    "stated_none",
    "reviewed_empty",
    "blank_unreviewed",
    "standing_condition",
    "unresolved_reference",
    "alternative_or_exception",
    "unreadable",
)

# Only these may satisfy eligible/2. Everything else is excluded from executable rules.
EXECUTABLE_PREREQUISITE_STATES = frozenset({"resolved", "stated_none", "reviewed_empty"})

# Audit anomaly types that name a prerequisite cell the parser could not assign.
PREREQUISITE_AMBIGUITY_TYPES = frozenset({"ambiguous_adjacent_prerequisite_fragment"})

ALTERNATIVE_OR_EXCEPTION = re.compile(
    r"\b(?:or|either|except(?:ion|ing)?|unless|equivalent|provided|if)\b", re.IGNORECASE
)


# A leftover that states a units or grade condition (it needs a number: "18 units", "grade of 85").
CONDITION_LEFTOVER = re.compile(r"\b(?:units?|grades?)\b", re.IGNORECASE)


def _code_pattern(code: str) -> re.Pattern[str]:
    """Matches a resolved code as printed: spacing, hyphens and a lab marker may differ."""
    runs = re.findall(r"[A-Za-z0-9]+", code)
    if len(runs) > 1 and runs[-1].upper() == "L":
        runs = runs[:-1]
    # Any separator (or none) between characters, an optional leading zero before a number,
    # and an optional lab marker: "PATH Fit 1", "Res 01/L" and "Bio 108/L" all read as their codes.
    text = "".join(runs)
    chars = [
        ("0*" if char.isdigit() and (i == 0 or not text[i - 1].isdigit()) else "") + re.escape(char)
        for i, char in enumerate(text)
    ]
    body = r"[\s\-\./]*".join(chars) + r"(?:[\s\-\./]*L)?"
    return re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", re.IGNORECASE)


def unconsumed_prerequisite_text(course: dict) -> str:
    """What is left of prerequisites_raw after the resolved codes, recognised standing conditions
    and separators are taken out. Anything left was dropped or never understood."""
    codes = list(course.get("prerequisites") or [])
    known = {norm_key(code) for code in codes}
    left: list[str] = []
    for fragment in split_prereq_fragments(clean_str(course.get("prerequisites_raw"))):
        if is_standing_rule(fragment):
            continue
        span = CODE_RANGE.match(fragment)
        if span:
            first, last = int(span.group(2)), int(span.group(3))
            prefix = span.group(1).strip()
            if first <= last and all(norm_key(f"{prefix} {n}") in known for n in range(first, last + 1)):
                continue
        rest = fragment
        for code in sorted(codes, key=len, reverse=True):
            rest = _code_pattern(code).sub(" ", rest)
        rest = re.sub(r"[\s.,;:]+", " ", rest).strip()
        if rest:
            left.append(rest)
    return " ".join(left)


def classify_prerequisite_state(course: dict, ambiguous_cell_ids: frozenset = frozenset()) -> str:
    """Worst-case state of one finalized course; the order below is the precedence."""
    raw = clean_str(course.get("prerequisites_raw"))
    cells = set((course.get("provenance") or {}).get("source_cell_ids") or ())
    if cells & ambiguous_cell_ids:
        return "unreadable"
    if ALTERNATIVE_OR_EXCEPTION.search(raw):
        return "alternative_or_exception"
    if course.get("prerequisites_unresolved"):
        return "unresolved_reference"
    if course.get("standing_requirements"):
        return "standing_condition"
    if not raw:
        return "blank_unreviewed"
    if raw.lower() in NULL_TOKENS:
        return "stated_none"
    if not course.get("prerequisites"):
        return "unreadable"  # text was printed but nothing in it was recognised
    leftover = unconsumed_prerequisite_text(course)
    if not leftover:
        return "resolved"
    if re.search(r"[|/]", leftover):
        return "alternative_or_exception"  # codes joined by | or /, which would run as AND
    if CONDITION_LEFTOVER.search(leftover) and re.search(r"\d", leftover):
        return "standing_condition"  # a units or grade condition the parser dropped
    return "unreadable"  # printed text no resolved code, standing rule or separator accounts for


def annotate_prerequisite_states(courses, anomalies=()) -> None:
    """Set course['prerequisite_state'] on every course, in place."""
    ambiguous = frozenset(
        cell_id
        for anomaly in anomalies
        if anomaly.get("type") in PREREQUISITE_AMBIGUITY_TYPES
        for cell_id in anomaly.get("source_cell_ids", ())
    )
    for item in courses:
        item["prerequisite_state"] = classify_prerequisite_state(item, ambiguous)
