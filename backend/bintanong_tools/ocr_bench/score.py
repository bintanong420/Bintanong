"""Score an OCR candidate JSON against the born-digital reference JSON.

Both are extractor payloads (`courses`, `audit`). Courses are paired by loose course code
(course_checks.loose: whitespace and hyphens ignored, case folded), in document order for repeated
codes. Anything else is a disagreement, and each disagreement says whether the candidate flagged it
(`confidence_flags` on the course, or the candidate audit's unclaimed candidates and anomalies). An
unflagged disagreement is a silent critical error.

Q11 "supported" (all four, strict): no missing or invented course on any document; critical
fields exact at least 98% (pooled); cell-text CER at most 2% on the worst document; zero silent
critical errors. Pure functions, no I/O.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping

from ..prospectus_extractor.course_checks import _audit_flagged, loose, normalise

CRITICAL_FIELDS = ("course_code", "year_level", "semester", "lecture_units", "lab_units", "total_units", "prerequisites")
CELL_FIELDS = ("course_code", "course_title", "units_raw", "prerequisites_raw")
MIN_CRITICAL_RATE = 0.98
MAX_WORST_CER = 0.02


def edit_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a or not b:
        return len(a) or len(b)
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def _key(code) -> str:
    return loose(code).casefold()


def _critical_value(course: Mapping[str, Any], field: str):
    if field == "prerequisites":
        return sorted(normalise(p) for p in course.get("prerequisites") or [])
    if field in ("course_code", "year_level", "semester"):
        return normalise(course.get(field))
    return course.get(field)


def _cell_text(course: Mapping[str, Any], field: str) -> str:
    if field == "units_raw":
        return normalise((course.get("units") or {}).get("raw"))
    return normalise(course.get(field))


def _pair(reference_courses, candidate_courses):
    """(matched [(ref, cand)], missing [ref], invented [cand])."""
    pool = defaultdict(list)
    for c in candidate_courses:
        pool[_key(c.get("course_code"))].append(c)
    matched, missing = [], []
    for r in reference_courses:
        bucket = pool.get(_key(r.get("course_code")))
        if bucket:
            matched.append((r, bucket.pop(0)))
        else:
            missing.append(r)
    invented = [c for bucket in pool.values() for c in bucket]
    invented.sort(key=lambda c: candidate_courses.index(c))
    return matched, missing, invented


def q11_verdict(*, missing: int, invented: int, critical_rate: float, worst_cer: float, silent: int) -> dict:
    criteria = {
        "no_missing_or_invented": missing == 0 and invented == 0,
        "critical_exact_rate": critical_rate >= MIN_CRITICAL_RATE,
        "worst_document_cer": worst_cer <= MAX_WORST_CER,
        "zero_silent_critical": silent == 0,
    }
    failures = []
    if missing:
        failures.append(f"{missing} missing course(s)")
    if invented:
        failures.append(f"{invented} invented course(s)")
    if not criteria["critical_exact_rate"]:
        failures.append(f"critical fields exact {critical_rate:.2%}, need at least {MIN_CRITICAL_RATE:.0%}")
    if not criteria["worst_document_cer"]:
        failures.append(f"worst-document CER {worst_cer:.2%}, need at most {MAX_WORST_CER:.0%}")
    if silent:
        failures.append(f"{silent} silent critical error(s)")
    return {"supported": all(criteria.values()), "criteria": criteria, "failures": failures}


def score_document(reference: Mapping[str, Any], candidate: Mapping[str, Any], name: str = "") -> dict:
    ref_courses = list(reference.get("courses") or [])
    cand_courses = list(candidate.get("courses") or [])
    matched, missing, invented = _pair(ref_courses, cand_courses)
    flag_ids, flag_texts = _audit_flagged(candidate.get("audit"))
    flag_keys = [_key(t) for t in flag_texts if _key(t)]

    def flagged(course, code) -> bool:
        ids = set((course.get("provenance") or {}).get("source_cell_ids") or []) if course else set()
        key = _key(code)
        return bool((course or {}).get("confidence_flags")) or bool(ids & flag_ids) or any(
            key and (key in f or f in key) for f in flag_keys)

    def page_of(course):
        return (course.get("provenance") or {}).get("page")

    def cells_of(course):
        return sorted((course.get("provenance") or {}).get("source_cell_ids") or [])

    disagreements, exact, total = [], 0, 0
    cells, edits, chars = [], 0, 0
    for r, c in matched:
        code = r.get("course_code")
        for field in CRITICAL_FIELDS:
            total += 1
            want, got = _critical_value(r, field), _critical_value(c, field)
            if want == got:
                exact += 1
            else:
                disagreements.append({"kind": "mismatch", "code": code, "field": field, "reference": want, "candidate": got,
                                      "silent": not flagged(c, c.get("course_code")), "page": page_of(r), "cell_ids": cells_of(c)})
        for field in CELL_FIELDS:
            want, got = _cell_text(r, field), _cell_text(c, field)
            if not want and not got:
                continue
            n = edit_distance(want, got)
            cells.append({"course": code, "field": field, "reference": want, "candidate": got, "edits": n,
                          "cer": n / max(len(want), 1)})
            edits += n
            chars += len(want)
    for r in missing:
        total += len(CRITICAL_FIELDS)
        code = r.get("course_code")
        disagreements.append({"kind": "missing", "code": code, "field": "row", "reference": code, "candidate": None,
                              "silent": not flagged(None, code), "page": page_of(r), "cell_ids": cells_of(r)})
        for field in CELL_FIELDS:
            want = _cell_text(r, field)
            cells.append({"course": code, "field": field, "reference": want, "candidate": "", "edits": len(want),
                          "cer": 1.0 if want else 0.0})
            edits += len(want)
            chars += len(want)
    for c in invented:
        code = c.get("course_code")
        disagreements.append({"kind": "invented", "code": code, "field": "row", "reference": None, "candidate": code,
                              "silent": not flagged(c, code), "page": page_of(c), "cell_ids": cells_of(c)})
        edits += sum(len(_cell_text(c, f)) for f in CELL_FIELDS)

    silent = sum(1 for d in disagreements if d["silent"])
    rate = exact / total if total else 1.0
    cer_rate = edits / chars if chars else (0.0 if not edits else 1.0)
    return {
        "name": name, "reference_courses": len(ref_courses), "candidate_courses": len(cand_courses), "matched": len(matched),
        "missing": [r.get("course_code") for r in missing], "invented": [c.get("course_code") for c in invented],
        "critical": {"total": total, "exact": exact, "rate": rate},
        "cer": {"edits": edits, "chars": chars, "rate": cer_rate, "cells": cells},
        "silent_critical": silent, "disagreements": disagreements,
        "verdict": q11_verdict(missing=len(missing), invented=len(invented), critical_rate=rate, worst_cer=cer_rate, silent=silent),
    }


def score_corpus(documents: Mapping[str, Mapping[str, Any]]) -> dict:
    """Aggregate per-document reports (from score_document) into the Q11 corpus verdict."""
    if not documents:
        return {"documents": 0, "worst_document": None, "critical": {"total": 0, "exact": 0, "rate": 0.0},
                "verdict": {"supported": False, "criteria": {}, "failures": ["no documents scored"]}}
    reports = list(documents.values())
    total = sum(r["critical"]["total"] for r in reports)
    exact = sum(r["critical"]["exact"] for r in reports)
    worst_name, worst = max(documents.items(), key=lambda item: item[1]["cer"]["rate"])
    rate = exact / total if total else 1.0
    verdict = q11_verdict(
        missing=sum(len(r["missing"]) for r in reports), invented=sum(len(r["invented"]) for r in reports),
        critical_rate=rate, worst_cer=worst["cer"]["rate"], silent=sum(r["silent_critical"] for r in reports))
    return {"documents": len(reports), "worst_document": {"name": worst_name, "cer": worst["cer"]["rate"]},
            "critical": {"total": total, "exact": exact, "rate": rate}, "verdict": verdict}
