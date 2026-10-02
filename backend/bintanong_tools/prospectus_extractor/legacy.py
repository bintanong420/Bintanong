"""Deprecated names kept for reference; nothing in the package calls them."""

from __future__ import annotations

from typing import Sequence

from .grid import GridParseResult
from .parse import evidence_from_grids, parse_curriculum_evidence


def _parse_curriculum_grids_legacy(
    grids: Sequence[Sequence[Sequence[str]]],
    table_year_hints: dict[int, str] | None = None,
) -> GridParseResult:
    """Deprecated name retained for imports; delegates to the fail-closed v3 parser."""
    return parse_curriculum_evidence(evidence_from_grids(grids, table_year_hints))
