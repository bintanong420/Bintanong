"""PDF-backed frozen manual reference gate, never a policy certification."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher

from ..ocr_bench.score import edit_distance
from ..prospectus_extractor.identity import InputSnapshot, bytes_sha256
from .ocr_run import _json_bytes, validate_candidate

KINDS = {"negation", "threshold", "fee", "date", "requirement", "exception"}


@dataclass(frozen=True)
class FrozenReference:
    payload: bytes
    sha256: str
    frozen_at_ns: int


def _pdf_pages(snapshot: InputSnapshot) -> int:
    if not isinstance(snapshot, InputSnapshot) or snapshot.path.suffix.lower() != ".pdf":
        raise ValueError("manual references require captured PDF bytes")
    snapshot.verify_unchanged()
    import pypdfium2 as pdfium

    with pdfium.PdfDocument(snapshot.data) as pdf:
        if not len(pdf):
            raise ValueError("manual reference PDF has no pages")
        return len(pdf)


def _line_range(text: str, start: int, end: int) -> tuple[int, int]:
    """A manual region selects complete lines, preserving physical-page positions."""
    if (type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text)
            or (start and text[start - 1] != "\n") or (end < len(text) and text[end] != "\n")
            or not text[start:end].strip()):
        raise ValueError("critical range must select nonempty complete reference lines")
    first = text[:start].count("\n")
    return first, first + text[start:end].count("\n") + 1


def _validate_reference(reference: dict, snapshot: InputSnapshot) -> None:
    n = _pdf_pages(snapshot)
    if (not isinstance(reference, dict) or reference.get("origin") != "human_pdf_manual"
            or reference.get("source_sha256") != snapshot.sha256 or reference.get("page_count") != n):
        raise ValueError("manual reference source identity mismatch")
    for key in ("reviewer", "reference_id"):
        if not isinstance(reference.get(key), str) or not reference[key].strip():
            raise ValueError("manual reference reviewer and identity required")
    try:
        reviewed = date.fromisoformat(reference["review_date"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("manual reference needs a real review date") from exc
    if reviewed > date.today():
        raise ValueError("manual review date cannot be in the future")
    pages = reference.get("pages")
    if (not isinstance(pages, list) or len(pages) != n or any(not isinstance(p, dict)
            or set(p) != {"page", "printed_page_label", "text"} or type(p["page"]) is not int
            or p["page"] != i or not isinstance(p["text"], str) or not p["text"].strip()
            or (p["printed_page_label"] is not None and not isinstance(p["printed_page_label"], str))
            for i, p in enumerate(pages, 1))):
        raise ValueError("manual reference must cover every physical PDF page exactly once")
    critical = reference.get("critical_regions")
    if not isinstance(critical, list) or not critical:
        raise ValueError("manual critical evidence is required")
    seen = set()
    for region in critical:
        if (not isinstance(region, dict) or set(region) != {"id", "kind", "page", "start", "end"}
                or not isinstance(region["id"], str) or not region["id"].strip() or region["id"] in seen
                or region["kind"] not in KINDS or type(region["page"]) is not int
                or not 1 <= region["page"] <= n):
            raise ValueError("invalid manual critical region identity/page/kind")
        seen.add(region["id"])
        _line_range(pages[region["page"] - 1]["text"], region["start"], region["end"])


def freeze_reference(snapshot: InputSnapshot, annotation: dict) -> FrozenReference:
    """Freeze trusted human declarations before OCR; digest catches later edits."""
    if (not isinstance(annotation, dict) or annotation.get("origin") != "human_pdf_manual"
            or set(annotation) != {"origin", "reference_id", "reviewer", "review_date", "pages", "critical_regions"}):
        raise ValueError("only explicit human PDF manual annotations can be frozen; candidate artifacts refused")
    reference = json.loads(_json_bytes(annotation))
    reference.update(source_sha256=snapshot.sha256, page_count=_pdf_pages(snapshot))
    _validate_reference(reference, snapshot)
    frozen_at = time.time_ns()
    reference["frozen_at_ns"] = frozen_at
    payload = _json_bytes(reference)
    return FrozenReference(payload, bytes_sha256(payload), frozen_at)


def score_document(snapshot: InputSnapshot, reference: FrozenReference, candidate: dict) -> dict:
    if candidate is reference or not isinstance(reference, FrozenReference):
        raise ValueError("candidate cannot be its own manual reference")
    if bytes_sha256(reference.payload) != reference.sha256:
        raise ValueError("frozen reference digest mismatch")
    manual = json.loads(reference.payload)
    _validate_reference(manual, snapshot)
    validate_candidate(candidate)
    if (type(reference.frozen_at_ns) is not int or manual.get("frozen_at_ns") != reference.frozen_at_ns
            or reference.frozen_at_ns > candidate["started_at_ns"]):
        raise ValueError("manual reference must be frozen before candidate run")
    if (candidate["source_sha256"] != snapshot.sha256 or candidate["source_format"] != "pdf"
            or candidate["page_count"] != manual["page_count"]
            or candidate.get("artifact_id") == manual["reference_id"]):
        raise ValueError("candidate and manual reference source/page/artifact binding mismatch")
    edits = chars = missing = invented = 0
    for ref_page, page in zip(manual["pages"], candidate["pages"]):
        want, got = ref_page["text"], page["text"]
        edits += edit_distance(want, got)
        chars += len(want)
        for tag, a, b, c, d in SequenceMatcher(None, want, got, autojunk=False).get_opcodes():
            if tag != "equal":
                missing += sum(not char.isspace() for char in want[a:b])
                invented += sum(not char.isspace() for char in got[c:d])
    errors = []
    flags = candidate.get("review_flags", [])
    if not isinstance(flags, list) or any(not isinstance(flag, str) for flag in flags):
        raise ValueError("review flags must name manual critical region IDs")
    known_ids = {r["id"] for r in manual["critical_regions"]}
    if set(flags) - known_ids:
        raise ValueError("review flag does not bind a manual critical region")
    for region in manual["critical_regions"]:
        ref_text = manual["pages"][region["page"] - 1]["text"]
        candidate_text = candidate["pages"][region["page"] - 1]["text"]
        first, stop = _line_range(ref_text, region["start"], region["end"])
        want = ref_text.split("\n")[first:stop]
        got = candidate_text.split("\n")[first:stop]
        # shortcut: line drift is a conservative critical error, upgrade only with reviewed layout-bound alignment.
        if want != got:
            errors.append({"id": region["id"], "kind": region["kind"], "page": region["page"],
                "reference_lines": want, "candidate_lines": got, "silent": region["id"] not in flags})
    snapshot.verify_unchanged()
    return {"source_sha256": snapshot.sha256, "reference_id": manual["reference_id"],
        "reference_sha256": reference.sha256, "cer": edits / chars, "edits": edits, "chars": chars,
        "missing_chars": missing, "invented_chars": invented,
        "content_granularity": "non-whitespace characters in positional diff replacements/deletions/insertions",
        "critical_total": len(manual["critical_regions"]), "critical_errors": errors,
        "silent_critical": sum(error["silent"] for error in errors), "metadata": candidate["metadata"]}


def evaluate(documents) -> dict:
    """Triples of (captured PDF, frozen human reference, candidate), ten distinct bytes minimum."""
    distinct = {}
    for snapshot, reference, candidate in documents:
        report = score_document(snapshot, reference, candidate)
        if snapshot.sha256 in distinct:
            raise_duplicate = distinct[snapshot.sha256][0] != report
            if raise_duplicate:
                raise ValueError("conflicting evaluation aliases for one source byte version")
        else:
            distinct[snapshot.sha256] = (report, candidate)
    base = {"distinct_sources": len(distinct), "institutional_certification": False,
        "threshold_policy": "draft owner defaults, not approved policy", "minimum_critical_rate": 0.98,
        "maximum_worst_cer": 0.02}
    if len(distinct) < 10:
        return {**base, "status": "blocked", "evaluation": "NOT RUN",
                "reason": "at least ten distinct source byte versions with reviewed frozen references required"}
    reports = [r for r, _ in distinct.values()]
    total = sum(r["critical_total"] for r in reports)
    exact = total - sum(len(r["critical_errors"]) for r in reports)
    worst = max(reports, key=lambda r: r["cer"])
    criteria = {"critical_exact_rate": exact / total >= 0.98, "worst_document_cer": worst["cer"] <= 0.02,
        "zero_silent_critical": sum(r["silent_critical"] for r in reports) == 0,
        "no_missing_or_invented": sum(r["missing_chars"] + r["invented_chars"] for r in reports) == 0}
    return {**base, "status": "pass" if all(criteria.values()) else "fail", "evaluation": "RUN",
        "criteria": criteria, "documents": reports, "critical_rate": exact / total,
        "pooled_cer": sum(r["edits"] for r in reports) / sum(r["chars"] for r in reports),
        "worst_document": {"source_sha256": worst["source_sha256"], "cer": worst["cer"]}}
