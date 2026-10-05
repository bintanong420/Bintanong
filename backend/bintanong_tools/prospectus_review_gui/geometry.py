"""Highlight boxes as fractions of the page (decision D9).

Candidate cell boxes and the verifier's unclaimed-item boxes are in the table-cell frame: [left, top, right, bottom]
in points, y down from the top of the page. A fraction of the page size is therefore the CSS percentage to draw, and
survives any zoom. A rotated page, or a page whose size disagrees with Docling's by more than one point, gets no
boxes and a warning: a wrong box is worse than none.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

SIZE_TOLERANCE_POINTS = 1.0
ROLES = ("code", "title", "unit", "prereq")


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value == value and abs(value) != float("inf")


def bbox_fraction(bbox: Any, page_size: Any) -> dict[str, float] | None:
    """{left, top, width, height} as fractions of the page, clamped to 0..1; None for an unusable box or page size."""
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4 or not all(_number(v) for v in bbox):
        return None
    if not isinstance(page_size, (list, tuple)) or len(page_size) != 2 or not all(_number(v) and v > 0 for v in page_size):
        return None
    width, height = page_size
    left, top, right, bottom = bbox
    if right <= left or bottom <= top:
        return None
    clamp = lambda v: min(1.0, max(0.0, v))   # noqa: E731
    x0, x1, y0, y1 = clamp(left / width), clamp(right / width), clamp(top / height), clamp(bottom / height)
    if x1 <= x0 or y1 <= y0:
        return None   # entirely off the page
    return {"left": x0, "top": y0, "width": x1 - x0, "height": y1 - y0}


def _warning(page_size, rotation, docling_size) -> str | None:
    if not page_size or not all(_number(v) and v > 0 for v in page_size):
        return "the page size is unknown, so no highlight is drawn"
    if rotation not in (0, None) and rotation % 360 != 0:
        return f"this PDF page is rotated {rotation} degrees, so no highlight is drawn"
    if docling_size is not None and any(abs(a - b) > SIZE_TOLERANCE_POINTS for a, b in zip(page_size, docling_size)):
        return ("the PDF page size differs from the size the extraction used "
                f"({page_size[0]:.1f} x {page_size[1]:.1f} against {docling_size[0]:.1f} x {docling_size[1]:.1f} points), "
                "so no highlight is drawn")
    return None


def boxes_for_question(
    question: Any, *, page: int, page_size: Sequence[float] | None, rotation: int = 0,
    docling_size: Sequence[float] | None = None, course: Mapping[str, Any] | None = None,
    role_cells: Mapping[str, Sequence[Mapping[str, Any]]] | None = None, item: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """{"boxes": [{role, strong, cell_id, fractions}], "warning": str | None} for the PDF page `page`.

    A course question draws the course's own code, title, unit and prerequisite cells strong (`role_cells` is
    verify.own_role_cells) and its other source cells, banner included, faint with role "context"; provenance.bbox is
    never drawn because it is the union with the banner. An unclaimed question draws the printed code's own box strong.
    A section question draws nothing."""
    kind = getattr(question, "kind", None)
    if kind == "section_confirm" or (kind == "course" and course is None) or (kind == "unclaimed" and item is None):
        return {"boxes": [], "warning": None}
    warning = _warning(page_size, rotation, docling_size)
    if warning:
        return {"boxes": [], "warning": warning}
    boxes: list[dict[str, Any]] = []

    def add(role: str, strong: bool, cell_id: Any, bbox: Any) -> None:
        fractions = bbox_fraction(bbox, page_size)
        if fractions:
            boxes.append({"role": role, "strong": strong, "cell_id": cell_id, "fractions": fractions})

    if kind == "unclaimed":
        if item.get("page") == page:
            add("code", True, (item.get("cell_ids") or [None])[0], item.get("bbox"))
        return {"boxes": boxes, "warning": None}
    own: dict[Any, str] = {}
    for role in ROLES:
        for cell in (role_cells or {}).get(role) or []:
            own[cell.get("cell_id")] = role
    for cell in (course.get("provenance") or {}).get("source_cells") or []:
        if cell.get("page") != page:
            continue
        cell_id = cell.get("cell_id")
        add(own.get(cell_id, "context"), cell_id in own, cell_id, cell.get("bbox"))
    return {"boxes": boxes, "warning": None}
