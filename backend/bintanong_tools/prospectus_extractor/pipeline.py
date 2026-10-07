"""Payload assembly and single-document processing."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Iterable
from typing import Mapping
import json
import shutil

from .authority import build_authority
from .common import SCHEMA_VERSION
from .evidence import LoadedDocument
from .sections import SemanticRepairProvider
from .parse import parse_curriculum_evidence
from .courses import finalize_courses, link_elective_tracks, parse_elective_tracks
from .prerequisites import annotate_prerequisite_states
from .metadata import parse_semantic_markdown, resolve_metadata
from .audit import build_audit
from .ledger import content_review_state
from .views import build_curriculum_by_term, build_unlocks_map, make_prerequisite_edges, write_review_csv
from .prolog import generate_prolog_knowledge
from .rag import build_hierarchical_rag_chunks, build_semantic_rag_chunks
from .markup import render_prospectus_markup
from .paths import DEFAULT_SEMANTIC_DOC, SOURCE_PDF_ROOT, find_default_output_root
from .identity import InputSnapshot, run_identity
from .loader import _cache_meta_path, load_document_result
from .publish import (
    clear_failure, new_staging_dir, output_names, publish_staged, write_failure, write_text_lf,
)

REVIEW_INPUT_NOTE = (
    "Docling JSON given without its source PDF: the PDF hash and conversion settings are "
    "not verified, so this output is a review input only."
)


def build_payload(
    document: LoadedDocument,
    input_path: Path,
    semantic_doc_path: Path | None = DEFAULT_SEMANTIC_DOC,
    raw_json_path: Path | None = None,
    repair_provider: SemanticRepairProvider | None = None,
    *,
    source: Any = None,
    approved_scope: Mapping[str, str] | None = None,
    pdf_hash_check: str = "not_checked",
    review_entries: Iterable[Mapping[str, Any]] | None = None,
    semantic_map: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evidence -> audited payload. Production artifacts require a passing audit; no state here is approval."""
    if semantic_map is None:
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
    annotate_prerequisite_states(courses, parse.anomalies)

    audit = build_audit(courses, parse, metadata, duplicates, metadata_warnings)
    term_units = audit["term_unit_audit"]

    # A decision ledger only counts when it names the same PDF the source record declares.
    review = None
    if review_entries is not None:
        review_entries = list(review_entries)
        if source is not None:
            review = content_review_state(
                {"courses": courses, "audit": audit}, review_entries, source.pdf_sha256
            )
        else:  # say so instead of dropping the ledger silently
            review = {
                "state": "pending",
                "ignored": "no source hash to apply the ledger against",
                "entries": len(review_entries),
            }
    authority = build_authority(
        audit_status=audit["status"], metadata=metadata, courses=courses,
        source=source, approved_scope=approved_scope, pdf_hash_check=pdf_hash_check,
        content_review=review,
    )

    verified = audit["status"] != "error"
    if verified:
        prolog = generate_prolog_knowledge(metadata, courses, tracks, term_units)
        prolog["status"] = "extracted"  # the audit found no error; not a verification
        semantic_chunks = build_semantic_rag_chunks(
            metadata, courses, tracks, term_units, document=document, layout=audit["table_layout"],
            evidence_ids=[i for s in audit["curriculum_sections"] for i in s.get("evidence_cells") or []],
        )
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
                "prerequisite_states": [],
                "rule_complete": [],
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
        **authority,
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


def essentials_extraction_status(audit_status: str) -> str:
    """Name the extractor's own result; none of these values means reviewed, verified or approved."""
    return {"ok": "EXTRACTED", "warn": "EXTRACTED_WITH_WARNINGS"}.get(audit_status, "REVIEW_REQUIRED")


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
        "schema_version": "palsu-prospectus-essentials-v2",
        "source_pdf": source_pdf,
        "extraction_status": essentials_extraction_status(payload["extraction_audit"]),
        "extraction_audit": payload["extraction_audit"],
        "content_review": payload["content_review"],
        "source_verification": payload["source_verification"],
        "eligibility_executable": payload["authority"]["eligibility_executable"],
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
                "prerequisite_state": course["prerequisite_state"],
                "category": course["category"],
                "is_elective": course["is_elective"],
                "elective_group": course["elective_group"],
                "source_page": course.get("provenance", {}).get("page"),
            }
            for course in payload["courses"]
        ],
        "elective_tracks": payload["elective_tracks"],
    }


def _stage_outputs(
    stage: Path, names: Any, document: LoadedDocument, payload: dict[str, Any], is_pdf: bool,
    export_pl: bool, export_jsonl: bool, export_csv: bool, export_md: bool,
) -> list[str]:
    """Write every companion into `stage`; returns file names in publish order, main JSON last."""
    produced: list[str] = []
    if is_pdf:
        write_text_lf(
            stage / names.essentials.name,
            json.dumps(build_essentials(payload), indent=2, ensure_ascii=False),
        )
        produced.append(names.essentials.name)
    if payload["audit"]["status"] != "error":
        if export_pl:
            write_text_lf(stage / names.prolog.name, "\n".join(payload["prolog"]["clauses"]) + "\n")
            produced.append(names.prolog.name)
        if export_jsonl:
            chunks = payload["rag"]["semantic_chunks"] + payload["rag"]["hierarchical_chunks"]
            write_text_lf(
                stage / names.rag.name,
                "".join(json.dumps(chunk, ensure_ascii=False) + "\n" for chunk in chunks),
            )
            produced.append(names.rag.name)
    if export_csv:
        write_review_csv(payload["courses"], stage / names.csv.name)
        produced.append(names.csv.name)
    if export_md:  # written for every audit status: the reviewer needs it most when the audit failed
        write_text_lf(stage / names.markup.name, render_prospectus_markup(
            document, payload, pdf_sha256=payload["run_identity"]["pdf_sha256"],
        ))
        produced.append(names.markup.name)
    write_text_lf(stage / names.final.name, json.dumps(payload, indent=2, ensure_ascii=False))
    produced.append(names.final.name)
    return produced


def process_prospectus(
    input_path: Path,
    output_path: Path | None = None,
    export_pl: bool = False,
    export_jsonl: bool = False,
    export_csv: bool = False,
    device: str = "auto",
    semantic_doc_path: Path | None = DEFAULT_SEMANTIC_DOC,
    force_reconvert: bool = False,
    converter: Any = None,
    repair_provider: SemanticRepairProvider | None = None,
    quiet: bool = False,
    export_md: bool = False,
    *,
    source: Any = None,
    approved_scope: Mapping[str, str] | None = None,
    review_entries: Iterable[Mapping[str, Any]] | None = None,
    _snapshot: InputSnapshot | None = None,
) -> dict[str, Any]:
    """Full pipeline for one prospectus: convert, parse, audit, then publish.

    Nothing already published is touched until conversion and audit have finished. On any
    exception the staged files go to <output dir>/failed/<base>/ and the exception propagates.
    """
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
    pdf_hash_check = "not_checked"
    captured = _snapshot if _snapshot is not None else InputSnapshot(input_path)
    captured.require_path(input_path)
    if source is not None and input_path.suffix.lower() == ".pdf":
        source.verify_digest(captured.sha256)  # before any output is touched
        pdf_hash_check = "matched"

    names = output_names(final_path)
    is_pdf = input_path.suffix.lower() == ".pdf"
    raw_cache_path = final_path.parent / f"{stem}_docling.json" if is_pdf else None
    final_path.parent.mkdir(parents=True, exist_ok=True)
    stage = new_staging_dir(final_path.parent, names.base)
    run_id: dict[str, Any] | None = None
    try:
        semantic_path = Path(semantic_doc_path).resolve() if semantic_doc_path else None
        semantic_capture = InputSnapshot(semantic_path) if semantic_path and semantic_path.exists() else None
        semantic_map = parse_semantic_markdown(
            semantic_path, text=semantic_capture.data.decode("utf-8", errors="replace"),
        ) if semantic_capture is not None else {}
        run_id = run_identity(
            input_path, semantic_path if semantic_capture is not None else None,
            snapshot=captured, semantic_snapshot=semantic_capture,
        )
        loaded = load_document_result(
            input_path, device=device, force_reconvert=force_reconvert,
            converter=converter, raw_json_path=raw_cache_path, stage_dir=stage, snapshot=captured,
        )
        document, raw_json_path = loaded.document, loaded.raw_json_path
        payload = build_payload(
            document,
            input_path,
            semantic_doc_path,
            raw_json_path,
            repair_provider=repair_provider,
            source=source,
            approved_scope=approved_scope,
            pdf_hash_check=pdf_hash_check,
            review_entries=review_entries,
            semantic_map=semantic_map,
        )

        cache_files: list[str] = []
        cache_hashes: dict[str, str] = {}
        if raw_cache_path is not None:
            if (loaded.cache_status not in ("converted", "reused")
                    or not isinstance(loaded.raw_json_bytes, bytes)
                    or not isinstance(loaded.meta_bytes, bytes)
                    or loaded.raw_json_sha256 is None or loaded.meta_sha256 is None):
                raise ValueError("PDF load result has no complete captured cache pair")
            cache_files = [raw_cache_path.name, _cache_meta_path(raw_cache_path).name]
            cache_hashes = dict(zip(cache_files, (loaded.raw_json_sha256, loaded.meta_sha256)))
            if loaded.cache_status == "reused":
                for name, data in zip(cache_files, (loaded.raw_json_bytes, loaded.meta_bytes)):
                    (stage / name).write_bytes(data)
        payload["run_identity"] = {
            **run_id, "cache": loaded.cache_status, "cache_files": cache_hashes,
            "skip_reusable": all(value is None for value in (
                source, approved_scope, review_entries, repair_provider,
            )),
        }
        if run_id["review_input_only"]:
            payload["run_identity"]["review_note"] = REVIEW_INPUT_NOTE

        outputs = _stage_outputs(
            stage, names, document, payload, is_pdf, export_pl, export_jsonl, export_csv, export_md,
        )
        captured.verify_unchanged()
        if semantic_capture is not None:
            semantic_capture.verify_unchanged()
        elif semantic_path and semantic_path.exists():
            raise ValueError(f"Semantic map appeared since capture: {semantic_path}")
        publish_staged(
            stage, names, outputs, cache_files, payload["run_identity"], payload["audit"]["status"],
            cache_hashes=cache_hashes,
        )
        clear_failure(names)
    except Exception as exc:
        write_failure(names, exc, input_path, run_id, stage)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)

    if not quiet:
        for name in outputs:
            print(f"[+] {name} -> {final_path.parent}")
        if payload["run_identity"]["review_input_only"]:
            print(f"[!] {REVIEW_INPUT_NOTE}")
        if payload["audit"]["status"] == "error":
            print("[!] Audit failed with ERROR status. Blocking downstream exports (.pl, _rag.jsonl).")
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
