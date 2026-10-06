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
from .courses import _iter_text_pairs
from .views import build_unlocks_map


NOT_RECORDED = "not recorded in the prospectus (unreviewed)"


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
        prereq_text = prerequisite_phrase(course)
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
                "prerequisite_state": course.get("prerequisite_state"),
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
            f"{prerequisite_phrase(c, brief=True)})"
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
