"""Semantic and layout RAG chunks."""

from __future__ import annotations

from typing import Any
from typing import Sequence

from .common import RICH_AVAILABLE

if RICH_AVAILABLE:
    from .common import track
from .docling_env import load_docling
from .text import clean_str
from .evidence import LoadedDocument
from .courses import _iter_text_pairs
from .views import build_unlocks_map


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
        prereqs = course.get("prerequisites", [])
        unresolved = course.get("prerequisites_unresolved", [])
        standing = course.get("standing_requirements", [])
        prereq_text = ", ".join(prereqs) if prereqs else "None"
        if unresolved:
            prereq_text += f" (unverified in this document: {', '.join(unresolved)})"
        if standing:
            prereq_text += f" (Policy: {'; '.join(standing)})"
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
            f"{', '.join(c.get('prerequisites', [])) or 'None'})"
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
