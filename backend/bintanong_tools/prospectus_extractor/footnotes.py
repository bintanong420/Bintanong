"""Footnote marker detection and stripping."""

from __future__ import annotations

from collections import Counter
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Sequence
import re

from .text import clean_str


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
