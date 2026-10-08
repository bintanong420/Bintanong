"""Semantic and layout RAG chunks."""

from __future__ import annotations

from typing import Any
from typing import Sequence

from .common import RICH_AVAILABLE
from .prerequisites import EMPTY_RULE_STATES

if RICH_AVAILABLE:
    from .common import track
from .docling_env import load_docling
from .text import clean_str
from .evidence import LoadedDocument
from .courses import _iter_text_pairs, parse_elective_tracks
from .chunking import (PART_LABEL_ROOM, TOKEN_SPLIT_AT, assemble_chunk, canonical_text, estimate_tokens,
                       fits_cap, make_span, pack_items, spans_from_cells, spans_from_text_items)
from .course_checks import loose
from .verify import own_role_cells
from .units import parse_units


NOT_RECORDED = "not recorded in the prospectus (unreviewed)"

# Rejection reasons; the payload reports them under rag.rejected_chunks.
NO_VALID_SOURCE_CELLS = "no_valid_source_cells"
CODE_NOT_IN_SOURCE = "code_not_in_source_text"
TITLE_NOT_IN_SOURCE = "title_not_in_source_text"
PREREQUISITE_NOT_IN_SOURCE = "prerequisite_not_in_source_text"
UNITS_NOT_IN_SOURCE = "units_not_in_source_text"
UNITS_NOT_DERIVABLE = "units_not_derivable_from_source"
OVER_TOKEN_CAP = "over_token_cap"
DUPLICATE_CHUNK_ID = "duplicate_chunk_id"
NO_ACCEPTED_COURSES = "no_accepted_courses"
NO_SOURCE_TEXT_ITEMS = "no_source_text_items"
OPTION_NOT_IN_SOURCE = "option_not_in_source_text"
NO_SOURCE_SPANS = "no_source_spans"
LAYOUT_CHUNKER_FAILED = "layout_chunker_failed"


def _unique(values) -> list:
    return list(dict.fromkeys(values))


def _claimed_cell_ids(course: dict[str, Any]) -> list[str]:
    """The cell ids a course claims, for the rejection record; malformed claims report as empty."""
    provenance = course.get("provenance")
    ids = provenance.get("source_cell_ids") if isinstance(provenance, dict) else None
    return [i for i in ids if isinstance(i, str)] if isinstance(ids, (list, tuple)) else []


def _item_ids(spans: Sequence[dict[str, Any]]) -> list[str]:
    return _unique(i for s in spans for i in s["locator"].get("item_ids", []))


def _claimed_item_ids(options: Sequence[dict[str, Any]]) -> list[str]:
    return _unique(o["source_item_id"] for o in options if isinstance(o.get("source_item_id"), str))


def _rejection(chunk_type: str, label: str, reason: str, *, course_code: str | None = None,
               year_level: str | None = None, semester: str | None = None,
               cell_ids: Sequence[str] = (), item_ids: Sequence[str] = (),
               refs: Sequence[str] = (), **extra: Any) -> dict[str, Any]:
    return {"chunk_type": chunk_type, "label": label, "reason": reason, "course_code": course_code,
            "year_level": year_level, "semester": semester, "source_cell_ids": list(cell_ids),
            "source_item_ids": list(item_ids), "source_refs": list(refs), **extra}


def prerequisite_phrase(course: dict[str, Any], brief: bool = False) -> str:
    """The prerequisite line, worded from prerequisite_state so a blank cell is never "None"."""
    state = course.get("prerequisite_state")
    prereqs = course.get("prerequisites", [])
    codes = ", ".join(prereqs)
    if state in EMPTY_RULE_STATES:
        return "None"
    if state == "blank_unreviewed" or (state is None and not prereqs):
        return NOT_RECORDED
    if state == "resolved":
        return codes
    # Any other state: the rule is not fully understood, so say what was printed and that it is incomplete.
    raw = clean_str(course.get("prerequisites_raw"))
    note = f"rule not fully understood: {state or 'unclassified'}"
    if brief:
        return f"{codes or 'unresolved'} ({note})"
    text = codes or "no resolved course"
    if course.get("prerequisites_unresolved"):
        text += f" (unverified in this document: {', '.join(course['prerequisites_unresolved'])})"
    if course.get("standing_requirements"):
        text += f" (Policy: {'; '.join(course['standing_requirements'])})"
    return text + f' (printed as "{raw}"; {note})'


def printed_own_fields(course: dict[str, Any], layout: Sequence[dict[str, Any]], evidence_ids: Sequence[str]
                       ) -> tuple[dict[str, list] | None, dict[str, str]]:
    """The course's own role cells on its own source row, and the printed text of each role.

    Returns (None, {}) when the row index is missing or malformed. Shared with the corpus report."""
    src = course.get("_source")
    row = src.get("row_index") if isinstance(src, dict) else None
    if not isinstance(row, int) or isinstance(row, bool):
        return None, {}
    roles = own_role_cells(course, layout, set(evidence_ids))
    roles = {role: [c for c in group if c["table_index"] == src.get("table_index")
                   and c["row_start"] <= row < c["row_end"]]
             for role, group in roles.items()}
    printed = {role: canonical_text(" ".join(c["text"] for c in sorted(
        group, key=lambda c: (c["row_start"], c["col_start"], c["cell_id"]))))
        for role, group in roles.items()}
    return roles, printed


def _course_source(course: dict[str, Any], document: LoadedDocument | None,
                   layout: Sequence[dict[str, Any]], evidence_ids: Sequence[str]
                   ) -> tuple[str | None, list[dict[str, Any]]]:
    """Resolve locators against canonical cells, then verify each asserted printed field."""
    provenance = course.get("provenance")
    if not isinstance(provenance, dict):
        return NO_VALID_SOURCE_CELLS, []
    ids, stored = provenance.get("source_cell_ids") or [], provenance.get("source_cells") or []
    if not document or not provenance.get("valid") or not ids or not stored:
        return NO_VALID_SOURCE_CELLS, []
    if not isinstance(ids, (list, tuple)) or any(not isinstance(i, str) or not i for i in ids):
        return NO_VALID_SOURCE_CELLS, []
    if not isinstance(stored, (list, tuple)) or any(
            not isinstance(c, dict) or not isinstance(c.get("cell_id"), str) for c in stored):
        return NO_VALID_SOURCE_CELLS, []
    if len(ids) != len(set(ids)) or set(ids) != {c["cell_id"] for c in stored} or len(stored) != len(ids):
        return NO_VALID_SOURCE_CELLS, []
    canonical = document.all_cells()
    cells = []
    for c in stored:
        actual = canonical.get(c["cell_id"])
        if actual is None:
            return NO_VALID_SOURCE_CELLS, []
        source = actual.as_evidence_dict()
        if any(c.get(k) != source[k] for k in ("table_index", "row_start", "row_end", "col_start", "col_end")):
            return NO_VALID_SOURCE_CELLS, []
        if canonical_text(c.get("text", "")) != canonical_text(source["text"]):
            return NO_VALID_SOURCE_CELLS, []
        source["bbox_origin"] = actual.bbox.origin if actual.bbox else None
        cells.append(source)
    canonical_course = {**course, "provenance": {**provenance, "source_cells": cells}}
    roles, printed = printed_own_fields(canonical_course, layout, evidence_ids)
    if roles is None or not roles["code"] or not roles["title"]:
        return NO_VALID_SOURCE_CELLS, []
    for role, value, reason in (
        ("code", course.get("course_code"), CODE_NOT_IN_SOURCE),
        ("title", course.get("course_title"), TITLE_NOT_IN_SOURCE),
        ("prereq", course.get("prerequisites_raw"), PREREQUISITE_NOT_IN_SOURCE),
    ):
        claimed = canonical_text(value or "")
        if role in {"code", "title"} and not claimed:
            return reason, []
        if claimed != printed[role]:
            # Code spelling can be canonicalised by the existing parser; mark it as derived below.
            if role != "code" or loose(value).lower() != loose(printed[role]).lower():
                return reason, []
    units = course.get("units") or {}
    raw = units.get("raw") or ""
    numeric = any(units.get(k) is not None for k in ("lecture", "lab", "total"))
    if (raw or numeric) and (not raw or canonical_text(raw) != printed["unit"]):
        return UNITS_NOT_IN_SOURCE, []
    parsed = parse_units(printed["unit"])
    if any(units.get(k) != parsed[k] for k in ("lecture", "lab", "total")) or course.get("total_units") != parsed["total"]:
        return UNITS_NOT_DERIVABLE, []
    return None, cells


def build_semantic_rag_chunks(
    metadata: dict[str, Any],
    courses: Sequence[dict[str, Any]],
    elective_tracks: Sequence[dict[str, Any]],
    term_units: Sequence[dict[str, Any]],
    *,
    pdf_sha256: str | None = None,
    document: LoadedDocument | None = None,
    layout: Sequence[dict[str, Any]] = (),
    evidence_ids: Sequence[str] = (),
    rejected: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Advising-shaped chunks: one per course, per term, per elective pool, plus an overview.

    Every rejection is appended to `rejected`; the caller must report it, so it is required."""
    all_courses = list(courses)
    chunks: list[dict[str, Any]] = []
    degree = metadata.get("degree") or metadata.get("program_name") or "the program"
    college = metadata.get("college_name") or "PalSU"
    school_year = metadata.get("effective_school_year") or "n/a"
    source = metadata.get("source_file", "")
    accepted, course_chunks, omitted_ids = [], [], set()
    source_kind = document.source_kind if document else ""
    for course in courses:
        reason, cells = _course_source(course, document, layout, evidence_ids)
        code = course["course_code"]
        where = {"course_code": code, "year_level": course.get("year_level"), "semester": course.get("semester"),
                 "cell_ids": _claimed_cell_ids(course)}
        if reason:
            rejected.append(_rejection("course", code, reason, **where))
            omitted_ids.add(id(course))
            continue
        units = course.get("units") or {}
        body = [
            f"### Course: {code} - {course['course_title']}",
            f"- **Program**: {degree} ({college}, SY {school_year})",
            f"- **When taken**: {course['year_level']}, {course['semester']}",
            f"- **Units**: {units.get('total') if units.get('total') is not None else 'n/a'} total "
            f"(lecture {units.get('lecture') if units.get('lecture') is not None else 'n/a'}, "
            f"laboratory {units.get('lab') if units.get('lab') is not None else 'n/a'})",
            f"- **Prerequisites**: {prerequisite_phrase(course)}",
            f"- **Classification**: {course.get('category')}",
        ]
        provenance = course.get("provenance") or {}
        chunk = assemble_chunk("course", {
            "course_code": code, "course_title": course["course_title"],
            "prerequisite_state": course.get("prerequisite_state"),
            "year_level": course["year_level"], "semester": course["semester"],
            "college": metadata.get("college_code"), "program": degree,
            "section_path": [degree, course["year_level"], course["semester"]],
            "derived_fields": ["course_code", "year_level", "semester", "units", "prerequisites", "unlocks", "category"],
            "unsourced_fields": ["program", "college", "effective_school_year"],
        }, "\n".join(body) + "\n", spans_from_cells(cells, pdf_sha256, source_kind,
            provenance.get("resolution_method") or "deterministic", provenance.get("repair_id")),
            pdf_sha256=pdf_sha256, source=source)
        if not fits_cap(chunk["token_count"]):
            rejected.append(_rejection("course", code, OVER_TOKEN_CAP, **where, token_count=chunk["token_count"]))
            omitted_ids.add(id(course))
            continue
        if chunk["chunk_id"] in {c["chunk_id"] for c in course_chunks}:
            # An identical course already stands for this one, so nothing is omitted from the summaries.
            rejected.append(_rejection("course", code, DUPLICATE_CHUNK_ID, **where))
            continue
        accepted.append(course)
        course_chunks.append(chunk)
    omitted = [c["course_code"] for c in all_courses if id(c) in omitted_ids]
    courses = accepted
    chunks.extend(course_chunks)
    by_course = {id(c): ch for c, ch in zip(courses, course_chunks)}
    by_code = {c["course_code"]: c for c in courses}
    common = {"college": metadata.get("college_code"), "program": degree,
              "unsourced_fields": ["program", "college", "effective_school_year"]}

    def spans_of(members):
        # Retain each contributor's extraction method/repair and native coordinate origin.
        spans, seen = [], set()
        for c in members:
            for span in by_course[id(c)]["source_spans"]:
                key = str(span)
                if key not in seen:
                    seen.add(key)
                    spans.append(span)
        return spans

    def refuse(kind, label, reason, **where):
        rejected.append(_rejection(kind, label, reason, **where))

    def emit(kind, label, fields, text, spans):
        chunk = assemble_chunk(kind, {**common, **fields}, text, spans,
                               pdf_sha256=pdf_sha256, source=source)
        where = {"year_level": fields.get("year_level"), "semester": fields.get("semester"),
                 "cell_ids": chunk["cell_ids"], "item_ids": _item_ids(spans)}
        if not fits_cap(chunk["token_count"]):
            refuse(kind, label, OVER_TOKEN_CAP, token_count=chunk["token_count"], **where)
        elif chunk["chunk_id"] in {c["chunk_id"] for c in chunks}:
            refuse(kind, label, DUPLICATE_CHUNK_ID, **where)
        else:
            chunks.append(chunk)

    def emit_parts(kind, label, header, items, fields, sources):
        # Leave room for the repeated part label; the final rendered estimate is checked again.
        parts = pack_items(header(""), items, limit=TOKEN_SPLIT_AT - PART_LABEL_ROOM)
        for number, (lines, members) in enumerate(parts, 1):
            suffix = f" (part {number} of {len(parts)})" if len(parts) > 1 else ""
            emit(kind, label, {**fields, "part_index": number, "part_count": len(parts)},
                 header(suffix) + "\n" + "\n".join(lines) + "\n", sources(members))

    if courses:
        total = sum(c.get("total_units") or 0 for c in courses)
        overview = [f"### Program Overview: {metadata.get('program_name') or degree}",
                    f"- **Degree**: {degree}",
                    f"- **College**: {college} ({metadata.get('college_code') or 'n/a'}), {metadata.get('campus')}",
                    f"- **Effective School Year**: {school_year}",
                    f"- **Total Units**: {total} across {len(courses)} courses",
                    "- **Terms**: " + ", ".join(dict.fromkeys(
                        f"{c['year_level']} {c['semester']}" for c in courses))]
        emit("program_overview", "program", {"section_path": [degree],
             "derived_fields": ["total_units", "course_count", "terms"], "omitted_course_codes": omitted},
             "\n".join(overview) + "\n", spans_of(courses))
    else:
        refuse("program_overview", "program", NO_ACCEPTED_COURSES,
               cell_ids=_unique(i for c in all_courses for i in _claimed_cell_ids(c)))

    for term in term_units:
        year, semester = term["year_level"], term["semester"]
        in_term = [c for c in all_courses if (c["year_level"], c["semester"]) == (year, semester)]
        members = [c for c in courses if (c["year_level"], c["semester"]) == (year, semester)]
        omitted_term = [c["course_code"] for c in in_term if id(c) in omitted_ids]
        label = f"{year} {semester}"
        if not members:
            refuse("term_schedule", label, NO_ACCEPTED_COURSES, year_level=year, semester=semester,
                   cell_ids=_unique(i for c in in_term for i in _claimed_cell_ids(c)))
            continue
        total = sum(c.get("total_units") or 0 for c in members)

        def header(suffix, year=year, semester=semester, count=len(members), total=total):
            return (f"### Term Schedule: {degree} - {year}, {semester}{suffix}\n"
                    f"- **College**: {college}\n- **Effective School Year**: {school_year}\n"
                    f"- **Courses**: {count}\n- **Total units this term**: {total}\n- **Course list**:")

        items = [(f"  - **{c['course_code']}**: {c['course_title']} "
                  f"({c.get('total_units')} units; prerequisites: {prerequisite_phrase(c, brief=True)})", c)
                 for c in members]
        emit_parts("term_schedule", label, header, items,
                   {"year_level": year, "semester": semester, "section_path": [degree, year, semester],
                    "derived_fields": ["total_units", "course_count", "year_level", "semester", "prerequisites"],
                    "omitted_course_codes": omitted_term}, spans_of)

    text_items = document.text_items if document else []
    by_item = {i.get("item_id"): i for i in text_items if isinstance(i, dict)}
    for track in elective_tracks:
        options, omitted_options = [], []
        for option in track.get("options") or []:
            item = by_item.get(option.get("source_item_id"))
            printed = canonical_text(item.get("text", "")) if item else ""
            # Reuse the elective parser rather than guessing an option from unrelated words.
            parsed = parse_elective_tracks([item]) if item else []
            supported = any(o["course_code"] == option["course_code"] and o["course_title"] == option["course_title"]
                            for pool in parsed for o in pool["options"])
            if not printed or not supported:
                omitted_options.append(option["course_code"])
                refuse("elective_option", option["course_code"],
                       NO_SOURCE_TEXT_ITEMS if item is None else OPTION_NOT_IN_SOURCE,
                       course_code=option["course_code"], item_ids=_claimed_item_ids([option]))
            else:
                options.append(option)
        if not options:
            refuse("elective_pool", track["group"], NO_SOURCE_TEXT_ITEMS,
                   item_ids=_claimed_item_ids(track.get("options") or []))
            continue
        slots = track.get("curriculum_slots") or []
        slot_courses = [by_code[code] for code in slots if code in by_code]
        accepted_slots = [c["course_code"] for c in slot_courses]
        omitted_slots = [code for code in slots if code not in by_code]

        def pool_header(suffix, group=track["group"], slots=accepted_slots):
            return (f"### Elective Pool: {group} ({degree}){suffix}\n"
                    f"- **Taken as**: {', '.join(slots) if slots else 'no verified curriculum slot'}\n"
                    "- **Choose one of**:")

        def option_spans(members, slot_courses=slot_courses):
            return spans_from_text_items(text_items, [o.get("source_item_id") for o in members],
                                         pdf_sha256, source_kind) + spans_of(slot_courses)

        items = [(f"  - **{o['course_code']}**: {o['course_title']}", o) for o in options]
        emit_parts("elective_pool", track["group"], pool_header, items,
                   {"elective_group": track["group"], "section_path": [degree, track["group"]],
                    "derived_fields": ["elective_group", "curriculum_slots"],
                    "omitted_course_codes": omitted_slots, "omitted_option_codes": omitted_options}, option_spans)

    policy_courses = [c for c in courses if c.get("standing_requirements")]
    if policy_courses:
        def policy_header(suffix):
            return (f"### Enrolment Policies and Standing Requirements ({degree}){suffix}\n"
                    "Extracted standing conditions requiring review:")

        items = [(f"  - **{c['course_code']}** ({c['year_level']}, {c['semester']}): "
                  f"{'; '.join(c['standing_requirements'])}", c) for c in policy_courses]
        emit_parts("enrolment_policy", "program", policy_header, items,
                   {"section_path": [degree, "Enrolment policies"], "derived_fields": ["standing_requirements"],
                    "omitted_course_codes": [c["course_code"] for c in all_courses
                                             if c.get("standing_requirements") and id(c) in omitted_ids]}, spans_of)
    return chunks


LAYOUT_LABELS = {"hierarchical_layout": "docling_hierarchical", "hierarchical_layout_fallback": "layout_fallback"}
PRINTED_TEXT = "printed_text"
TABLE_SERIALIZATION = "docling_table_serialization"


def _layout_chunk(chunk_type: str, index: int, fields: dict[str, Any], text: str,
                  spans: list[dict[str, Any]], *, source_text: str | None, pdf_sha256: str | None,
                  source: str, rejected: list[dict[str, Any]], seen: set[str]) -> dict[str, Any] | None:
    """One layout chunk, or None after recording why it is not a candidate."""
    label = f"{LAYOUT_LABELS[chunk_type]}:{index}"
    where = {"item_ids": _item_ids(spans), "refs": _unique(s["locator"]["ref"] for s in spans if "ref" in s["locator"])}
    tokens = estimate_tokens(text)
    if not fits_cap(tokens):
        rejected.append(_rejection(chunk_type, label, OVER_TOKEN_CAP, token_count=tokens, **where))
    elif not spans:
        rejected.append(_rejection(chunk_type, label, NO_SOURCE_SPANS, **where))
    else:
        chunk = assemble_chunk(chunk_type, {"chunk_index": index, **fields}, text, spans,
                               pdf_sha256=pdf_sha256, source=source, source_text=source_text)
        if chunk["chunk_id"] in seen:
            rejected.append(_rejection(chunk_type, label, DUPLICATE_CHUNK_ID, **where))
            return None
        seen.add(chunk["chunk_id"])
        return chunk
    return None


def _docling_layout_chunks(doc: Any, source_name: str, kind: str, pdf_sha256: str | None,
                           rejected: list[dict[str, Any]]) -> list[dict[str, Any]] | None:
    """Docling's own chunks; None when it produced no text at all (the caller then falls back).

    `source_text` is Docling's text unchanged. A table chunk is Docling's serialization of cells, not
    printed text, so it is marked and carries no `source_text`; its cells stay behind its refs."""
    chunks, produced, seen = [], False, set()
    for index, chunk in enumerate(load_docling()["HierarchicalChunker"]().chunk(doc)):
        raw = getattr(chunk, "text", "")
        text = clean_str(raw)
        if not text:  # a blank Docling item has nothing to cite; skipping it is deliberate and documented
            continue
        produced = True
        meta = getattr(chunk, "meta", None)
        meta_dict = meta.model_dump(mode="json") if hasattr(meta, "model_dump") else {}
        items = [item for item in meta_dict.get("doc_items") or [] if item.get("self_ref")]
        spans = [make_span(pdf_sha256, prov.get("page_no"), {"kind": "docling_ref", "ref": item["self_ref"]},
                           None, None, kind)
                 for item in items for prov in item.get("prov") or [{}]]
        table = any(str(item["self_ref"]).startswith("#/tables/") for item in items)
        built = _layout_chunk(
            "hierarchical_layout", index,
            {"section_path": list(meta_dict.get("headings") or []), "metadata": meta_dict,
             "text_kind": TABLE_SERIALIZATION if table else PRINTED_TEXT},
            text, spans, source_text=raw, pdf_sha256=pdf_sha256, source=source_name, rejected=rejected,
            seen=seen)
        if built:
            if table:
                built["source_text"] = None
            chunks.append(built)
    return chunks if produced else None


def build_hierarchical_rag_chunks(document: LoadedDocument, source_name: str, *,
                                  pdf_sha256: str | None = None,
                                  rejected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Docling's own layout chunks when available, otherwise a labelled text fallback.

    Layout chunks over the review cap are rejected, not split: they are Docling's own units and the
    curriculum facts are covered by the course and term chunks. Every rejection is appended to `rejected`;
    a Docling failure is recorded with its exception class before the text fallback is used.
    """
    kind = document.source_kind
    if document.docling_doc is not None:
        local: list[dict[str, Any]] = []
        try:
            found = _docling_layout_chunks(document.docling_doc, source_name, kind, pdf_sha256, local)
        except Exception as error:
            found = None
            rejected.append(_rejection(
                "hierarchical_layout", "docling_chunker", LAYOUT_CHUNKER_FAILED,
                error=type(error).__name__.encode("ascii", "replace").decode("ascii")))
        if found is not None:
            rejected.extend(local)
            return found

    chunks, seen = [], set()
    for index, item in enumerate(document.text_items):
        item_id = item.get("item_id") if isinstance(item, dict) else None
        for label, text in _iter_text_pairs([item]):
            if not text:
                continue
            built = _layout_chunk(
                "hierarchical_layout_fallback", index,
                {"section_path": [], "metadata": {"label": label}, "text_kind": PRINTED_TEXT}, text,
                spans_from_text_items([item], [item_id], pdf_sha256, kind) if item_id else [],
                source_text=None, pdf_sha256=pdf_sha256, source=source_name, rejected=rejected, seen=seen)
            if built:
                chunks.append(built)
    return chunks
