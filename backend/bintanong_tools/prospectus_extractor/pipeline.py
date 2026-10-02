"""Payload assembly and single-document processing."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Mapping
import json

from .common import SCHEMA_VERSION
from .evidence import LoadedDocument
from .sections import SemanticRepairProvider
from .parse import parse_curriculum_evidence
from .courses import finalize_courses, link_elective_tracks, parse_elective_tracks
from .metadata import parse_semantic_markdown, resolve_metadata
from .audit import build_audit
from .views import build_curriculum_by_term, build_unlocks_map, make_prerequisite_edges, write_review_csv
from .prolog import generate_prolog_knowledge
from .rag import build_hierarchical_rag_chunks, build_semantic_rag_chunks
from .paths import DEFAULT_SEMANTIC_DOC, SOURCE_PDF_ROOT, find_default_output_root
from .loader import load_document


def build_payload(
    document: LoadedDocument,
    input_path: Path,
    semantic_doc_path: Path | None = DEFAULT_SEMANTIC_DOC,
    raw_json_path: Path | None = None,
    repair_provider: SemanticRepairProvider | None = None,
) -> dict[str, Any]:
    """Evidence -> audited payload. Production artifacts require a passing audit."""
    semantic_map = parse_semantic_markdown(Path(semantic_doc_path)) if semantic_doc_path else {}
    metadata, metadata_warnings = resolve_metadata(
        Path(input_path), doc_text=document.markdown, semantic_map=semantic_map
    )

    parse = parse_curriculum_evidence(document, repair_provider=repair_provider)
    source_document = str(Path(input_path).resolve())
    raw_source = str(Path(raw_json_path).resolve()) if raw_json_path else None
    for raw_course in parse.courses:
        provenance = raw_course.get("provenance") or {}
        provenance["source_document"] = source_document
        provenance["raw_docling_json"] = raw_source
        raw_course["provenance"] = provenance
    courses, _index, duplicates = finalize_courses(parse.courses)
    tracks = link_elective_tracks(courses, parse_elective_tracks(document.text_items))

    audit = build_audit(courses, parse, metadata, duplicates, metadata_warnings)
    term_units = audit["term_unit_audit"]

    verified = audit["status"] != "error"
    if verified:
        prolog = generate_prolog_knowledge(metadata, courses, tracks, term_units)
        prolog["status"] = "verified"
        semantic_chunks = build_semantic_rag_chunks(metadata, courses, tracks, term_units)
        hierarchical_chunks = build_hierarchical_rag_chunks(document, Path(input_path).name)
    else:
        prolog = {
            "status": "blocked",
            "reason": "audit status is error; institutional facts require review",
            "clauses": [],
            "relations": {
                "courses": [],
                "prerequisites": [],
                "standing_requirements": [],
                "elective_tracks": [],
            },
        }
        semantic_chunks = []
        hierarchical_chunks = []

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "program": metadata.get("program_name"),
        "degree": metadata.get("degree"),
        "college": metadata.get("college_code"),
        "college_name": metadata.get("college_name"),
        "campus": metadata.get("campus"),
        "source_file": Path(input_path).name,
        "source_path": str(Path(input_path).resolve()),
        "metadata": metadata,
        "courses": courses,
        "curriculum_by_term": build_curriculum_by_term(courses),
        "prerequisite_edges": make_prerequisite_edges(courses),
        "unlocks": build_unlocks_map(courses),
        "elective_tracks": tracks,
        "policy_notes": parse.policy_notes,
        "evidence": {
            "source_kind": document.source_kind,
            "table_count": len(document.tables),
            "canonical_cell_count": sum(len(table.cells) for table in document.tables),
            "structural_tokens": parse.structural_tokens,
            "curriculum_sections": parse.sections,
        },
        "semantic_repair": {
            "provider_configured": repair_provider is not None,
            "packets": parse.repair_packets,
            "accepted": parse.repairs,
            "rejected": parse.invalid_repairs,
        },
        "prolog": prolog,
        "rag": {"semantic_chunks": semantic_chunks, "hierarchical_chunks": hierarchical_chunks},
        "audit": audit,
        "quality_report": {
            "status": audit["status"],
            "promotion_status": audit["promotion_status"],
            "production_artifacts_emitted": verified,
            "total_courses": len(courses),
            "total_units": audit["computed_total_units"],
            "declared_total_units": audit["declared_total_units"],
            "years_detected": audit["years_detected"],
            "terms_detected": audit["terms_detected"],
            "total_prerequisite_relations": len(prolog["relations"]["prerequisites"]),
            "total_standing_rules": len(prolog["relations"]["standing_requirements"]),
            "total_elective_tracks": len(tracks),
            "total_semantic_chunks": len(semantic_chunks),
            "total_hierarchical_chunks": len(hierarchical_chunks),
            "unresolved_prerequisites": len(audit["unresolved_prerequisites"]),
            "errors": audit["errors"],
            "warnings": audit["warnings"],
            "raw_docling_json_path": str(raw_json_path) if raw_json_path else None,
        },
    }
    return payload


def build_essentials(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Project an audited extraction into portable curriculum facts."""
    source_path = Path(payload["source_path"]).resolve()
    if source_path.suffix.lower() != ".pdf":
        raise ValueError("Essentials require a source PDF")
    try:
        source_pdf = source_path.relative_to(SOURCE_PDF_ROOT.resolve()).as_posix()
    except ValueError:
        source_pdf = source_path.name

    return {
        "schema_version": "palsu-prospectus-essentials-v1",
        "source_pdf": source_pdf,
        "extraction_status": payload["audit"]["promotion_status"],
        "audit_errors": payload["audit"]["errors"],
        "audit_warnings": payload["audit"]["warnings"],
        "program": payload["program"],
        "degree": payload["degree"],
        "college": payload["college"],
        "campus": payload["campus"],
        "effective_school_year": payload["metadata"].get("effective_school_year"),
        "courses": [
            {
                "course_code": course["course_code"],
                "course_title": course["course_title"],
                "year_level": course["year_level"],
                "semester": course["semester"],
                "total_units": course["total_units"],
                "lecture_units": course["lecture_units"],
                "lab_units": course["lab_units"],
                "prerequisites": course["prerequisites"],
                "prerequisites_raw": course["prerequisites_raw"],
                "prerequisites_unresolved": course["prerequisites_unresolved"],
                "standing_requirements": course["standing_requirements"],
                "category": course["category"],
                "is_elective": course["is_elective"],
                "elective_group": course["elective_group"],
                "source_page": course.get("provenance", {}).get("page"),
            }
            for course in payload["courses"]
        ],
        "elective_tracks": payload["elective_tracks"],
    }


def process_prospectus(
    input_path: Path,
    output_path: Path | None = None,
    export_pl: bool = False,
    export_jsonl: bool = False,
    export_csv: bool = False,
    device: str = "auto",
    semantic_doc_path: Path | None = DEFAULT_SEMANTIC_DOC,
    force_reconvert: bool = True,
    converter: Any = None,
    repair_provider: SemanticRepairProvider | None = None,
    quiet: bool = False,
) -> dict[str, Any]:
    """Full pipeline for one prospectus: convert, parse, audit, write."""
    input_path = Path(input_path).resolve()
    stem = input_path.stem
    if stem.endswith("_docling"):
        stem = stem[: -len("_docling")]
    if output_path:
        final_path = Path(output_path)
    elif input_path.suffix.lower() == ".pdf":
        try:
            relative_parent = input_path.relative_to(SOURCE_PDF_ROOT.resolve()).parent
        except ValueError:
            relative_parent = Path()
        final_path = find_default_output_root() / relative_parent / f"{stem}_prospectus.json"
    else:
        final_path = input_path.parent / f"{stem}_prospectus.json"
    if final_path.suffix.lower() != ".json" or final_path.resolve() == input_path:
        raise ValueError("Output must be a JSON file distinct from the source")
    base = final_path.stem.replace("_prospectus", "")
    essentials_path = final_path.with_name(f"{base}_essentials.json")
    for stale in (
        final_path,
        essentials_path,
        final_path.with_name(f"{base}_prospectus.pl"),
        final_path.with_name(f"{base}_rag.jsonl"),
        final_path.with_name(f"{base}_review.csv"),
    ):
        stale.unlink(missing_ok=True)
    raw_cache_path = final_path.parent / f"{stem}_docling.json" if input_path.suffix.lower() == ".pdf" else None
    document, raw_json_path = load_document(
        input_path, device=device, force_reconvert=force_reconvert,
        converter=converter, raw_json_path=raw_cache_path,
    )
    payload = build_payload(
        document,
        input_path,
        semantic_doc_path,
        raw_json_path,
        repair_provider=repair_provider,
    )

    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    if not quiet:
        print(f"[+] Prospectus JSON -> {final_path}")

    if input_path.suffix.lower() == ".pdf":
        essentials_path.write_text(
            json.dumps(build_essentials(payload), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        if not quiet:
            print(f"[+] Curriculum essentials -> {essentials_path}")

    if payload["audit"]["status"] == "error":
        if not quiet:
            print(f"[!] Audit failed with ERROR status. Blocking downstream exports (.pl, _rag.jsonl).")
    else:
        if export_pl:
            pl_path = final_path.with_name(f"{base}_prospectus.pl")
            pl_path.write_text("\n".join(payload["prolog"]["clauses"]) + "\n", encoding="utf-8")
            if not quiet:
                print(f"[+] Prolog knowledge base -> {pl_path}")
        if export_jsonl:
            jsonl_path = final_path.with_name(f"{base}_rag.jsonl")
            with jsonl_path.open("w", encoding="utf-8") as handle:
                for chunk in payload["rag"]["semantic_chunks"] + payload["rag"]["hierarchical_chunks"]:
                    handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            if not quiet:
                print(f"[+] RAG corpus -> {jsonl_path}")
    if export_csv:
        csv_path = final_path.with_name(f"{base}_review.csv")
        write_review_csv(payload["courses"], csv_path)
        if not quiet:
            print(f"[+] Review CSV -> {csv_path}")

    if not quiet:
        print_audit_summary(payload)
    return payload


def print_audit_summary(payload: dict[str, Any]) -> None:
    audit = payload["audit"]
    status = audit["status"].upper()
    print(
        f"[{status}] {payload.get('degree') or payload.get('program') or 'unknown program'}: "
        f"{audit['total_courses']} courses, {audit['computed_total_units']} units, "
        f"years {audit['years_detected']}"
    )
    for message in audit["errors"]:
        print(f"    ERROR: {message}")
    for message in audit["warnings"][:12]:
        print(f"    warn:  {message}")
    remaining = len(audit["warnings"]) - 12
    if remaining > 0:
        print(f"    ...and {remaining} more warning(s) in audit.warnings")
