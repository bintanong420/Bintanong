"""Phase 1 Task 5 group 4: the committed synthetic development examples."""

from __future__ import annotations

import json
import re
from pathlib import Path


from evaluation import case as ec
from evaluation import protocol as pr

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evaluation"
CASES = pr.load_cases(EVAL / "cases")
SCHEMA = json.loads((EVAL / "case.schema.json").read_text(encoding="utf-8"))


def schema_errors(value, sch, path="$"):
    """Test-local JSON Schema subset; an unsupported keyword raises so the schema cannot outgrow it."""
    ignored = {"$schema", "$id", "title", "description"}
    types = {"null": type(None), "string": str, "boolean": bool, "object": dict, "array": list}
    errs = []
    for key, rule in sch.items():
        if key in ignored:
            continue
        if key == "type":
            names = rule if isinstance(rule, list) else [rule]

            def is_type(n):
                if n == "integer":
                    return isinstance(value, int) and not isinstance(value, bool)
                return isinstance(value, types[n]) and not (n == "string" and isinstance(value, bool))
            if not any(is_type(n) for n in names):
                errs.append(f"{path}: type")
        elif key == "enum":
            if value not in rule:
                errs.append(f"{path}: enum")
        elif key == "const":
            if value != rule:
                errs.append(f"{path}: const")
        elif key == "pattern":
            if isinstance(value, str) and not re.search(rule, value):
                errs.append(f"{path}: pattern")
        elif key == "minLength":
            if isinstance(value, str) and len(value) < rule:
                errs.append(f"{path}: minLength")
        elif key == "minimum":
            if isinstance(value, int) and value < rule:
                errs.append(f"{path}: minimum")
        elif key == "required":
            errs += [f"{path}.{k}: required" for k in rule if isinstance(value, dict) and k not in value]
        elif key == "additionalProperties":
            if rule is False and isinstance(value, dict):
                errs += [f"{path}.{k}: extra" for k in value if k not in sch["properties"]]
        elif key == "properties":
            if isinstance(value, dict):
                for k, sub in rule.items():
                    if k in value:
                        errs += schema_errors(value[k], sub, f"{path}.{k}")
        elif key == "items":
            if isinstance(value, list):
                for i, v in enumerate(value):
                    errs += schema_errors(v, rule, f"{path}[{i}]")
        else:
            raise AssertionError(f"unsupported schema keyword {key}")
    return errs


def test_at_least_fifteen_synthetic_dev_cases():
    assert len(CASES) >= 15
    assert all(c["status"] == "synthetic" and c["split"] == "dev" for c in CASES)
    assert not [c for c in CASES if c["split"] == "final" or c["status"] == "verified"]


def test_every_case_is_well_formed_and_schema_valid():
    for c in CASES:
        assert ec.case_findings(c) == [], c["case_id"]
        assert schema_errors(c, SCHEMA) == [], c["case_id"]


def test_schema_checker_catches_a_bad_case():
    bad = dict(CASES[0], category="housing")
    assert schema_errors(bad, SCHEMA)


def test_cases_span_categories_languages_and_every_adversarial_kind():
    assert {c["category"] for c in CASES} == set(ec.CATEGORIES)
    assert {c["language"] for c in CASES} == set(ec.LANGUAGES)
    assert {k for c in CASES for k in c["adversarial_kinds"]} == set(ec.ADVERSARIAL_KINDS)
    assert {c["expected_outcome"] for c in CASES} >= {"eligible", "ineligible", "unknown", "unsupported", "error"}
    assert {c["expected_route"] for c in CASES} >= {"RAG", "Symbolic"}
    assert {c["expected_control"] for c in CASES} >= {"clarify", "unsupported_scope", "evidence_unavailable"}


def test_three_groups_have_paraphrase_variants_in_every_language():
    by_group = {}
    for c in CASES:
        by_group.setdefault(c["group_id"], []).append(c)
    variant_groups = [g for g, cs in by_group.items() if {c["language"] for c in cs} == set(ec.LANGUAGES)]
    assert len(variant_groups) >= 3
    for g in variant_groups:
        assert len({c["category"] for c in by_group[g]}) == 1


def test_taglish_cases_are_written_in_mixed_language():
    taglish = [c for c in CASES if c["language"] == "taglish"]
    assert len(taglish) >= 4
    fil = re.compile(r"\b(ba|ko|ang|ng|sa|na|kung|pa|po|ako|namin|mo|pwede|hindi|wala|may|bakit|ba't)\b", re.I)
    assert all(fil.search(c["query"]) for c in taglish)


def test_set_is_clean_and_coverage_is_honestly_not_met():
    rep = pr.validate_case_set(CASES)
    assert rep["findings"] == [] and rep["integrity_ok"] is True
    assert rep["split_counts"] == {"dev": len(CASES), "final": 0}
    cov = rep["coverage"]
    assert cov["met"] is False and cov["status_line"].startswith("NOT MET: 0 verified final cases, 0 Taglish")


def test_no_private_identity_and_every_scope_is_fictional_or_null_with_reason():
    blob = json.dumps(CASES)
    assert not ec.PRIVATE_IDENTITY.search(blob)
    for c in CASES:
        assert c["scope"] is None and c["scope_null_reason"]
        assert c["gold_spans"] == [] and c["gold_rules"] == [] and c["synthetic_policy"]
        assert c["review"]["reviewer"] is None


def test_traceability_example_is_labelled_synthetic_and_binds_a_dev_case():
    from evaluation.traceability import SCHEMA_VERSION, check_trace

    ex = json.loads((EVAL / "examples" / "traceability-synthetic.json").read_text(encoding="utf-8"))
    assert ex["schema_version"] == SCHEMA_VERSION
    assert ex["relation"] == "synthetic_exercise_only"
    case = next(c for c in CASES if c["case_id"] == ex["binding"]["case_id"])
    assert case["status"] == "synthetic"
    assert ex["case"] == case
    assert check_trace(ex) is None
    assert ex["verification_state"] == "synthetic_only"
    assert "verified" not in {v for v in ex.values() if isinstance(v, str)}
    assert not re.search(r"[A-Za-z]:[\\/]", json.dumps(ex))


def test_committed_case_files_are_canonical_lf_json():
    for path in sorted((EVAL / "cases").rglob("*.json")):
        raw = path.read_bytes().replace(b"\r\n", b"\n")     # a CRLF checkout (autocrlf) is still the same content
        assert raw.decode("utf-8") == pr.canonical_json(json.loads(raw.decode("utf-8"))), path.name


def test_case_ids_and_queries_are_unique():
    assert len({c["case_id"] for c in CASES}) == len(CASES)
    assert len({c["query"] for c in CASES}) == len(CASES)
