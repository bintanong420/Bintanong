"""Phase 1 Task 5 group 5: adversarial and determinism tests for the evaluation machinery."""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import test_evaluation_fixtures as fx
from evaluation import protocol as pr
from test_evaluation_protocol import DEV, FINAL, codes, dev_case, final_case, group_for

ROOT = Path(__file__).resolve().parents[1]

SCRIPT = (
    "import sys\n"
    "from pathlib import Path\n"
    "from evaluation import protocol as pr\n"
    "cases = pr.load_cases(Path(sys.argv[1]))\n"
    "sys.stdout.buffer.write(pr.canonical_json(pr.validate_case_set(cases)).encode('utf-8'))\n"
)


def run_report(folder: Path, hashseed: str) -> bytes:
    env = {"PATH": "", "SYSTEMROOT": "C:\\Windows", "PYTHONHASHSEED": hashseed, "PYTHONIOENCODING": "utf-8"}
    done = subprocess.run([sys.executable, "-c", SCRIPT, str(folder)], cwd=ROOT, env=env, capture_output=True,
                          check=True)
    return done.stdout


def test_report_bytes_identical_across_folders_runs_and_hash_seeds(tmp_path):
    a, b = tmp_path / "one" / "cases", tmp_path / "two" / "deeper" / "cases"
    shutil.copytree(ROOT / "evaluation" / "cases", a)
    shutil.copytree(ROOT / "evaluation" / "cases", b)
    runs = [run_report(a, "0"), run_report(a, "1"), run_report(b, "4242"), run_report(b, "random")]
    assert len(set(runs)) == 1
    text = runs[0].decode("utf-8")
    assert "\r" not in text and text.endswith("}\n")
    assert json.loads(text)["coverage"]["met"] is False
    assert str(tmp_path) not in text


def test_load_cases_order_is_path_sorted_and_rejects_non_lists(tmp_path):
    (tmp_path / "b.json").write_text(json.dumps([dev_case(2)]), encoding="utf-8")
    (tmp_path / "a.json").write_text(json.dumps([dev_case(1)]), encoding="utf-8")
    assert [c["case_id"] for c in pr.load_cases(tmp_path)] == ["syn-case-001", "syn-case-002"]
    (tmp_path / "c.json").write_text(json.dumps(dev_case(3)), encoding="utf-8")
    with pytest.raises(ValueError):
        pr.load_cases(tmp_path)


def test_every_emitted_code_is_a_declared_code():
    faulty = [dev_case(1, group=FINAL), dev_case(2, language="ceb"), dev_case(2), final_case(3, group=DEV)]
    rep = pr.validate_case_set(faulty, registry={}, freeze={"x": 1}, prompt_examples=["Verified final question 3"],
                               coverage_claim={"met": True})
    assert set(codes(rep)) <= set(pr.FINDING_CODES)
    assert rep["integrity_ok"] is False


def test_malformed_members_do_not_crash_the_set_check():
    rep = pr.validate_case_set([None, 5, {"case_id": 7}, [], dev_case(1)])
    assert codes(rep) == ["case_invalid"]
    assert rep["case_count"] == 5 and rep["split_counts"] == {"dev": 1, "final": 0}


def test_verified_final_without_independent_reviewer_never_counts_toward_coverage():
    same = {"author": "pat", "reviewer": "PAT", "evidence_ref": "ev-1", "review_version": "rv-1"}
    cov = pr.validate_case_set([final_case(1, review=same)], registry=fx.REGISTRY)["coverage"]
    assert cov["verified_final_total"] == 0 and cov["met"] is False


def test_verified_without_review_evidence_never_counts():
    for key in ("reviewer", "evidence_ref", "review_version"):
        review = dict(final_case(1)["review"])
        review[key] = None
        rep = pr.validate_case_set([final_case(1, review=review)], registry=fx.REGISTRY)
        assert "case_invalid" in codes(rep) and rep["coverage"]["verified_final_total"] == 0


def test_synthetic_cannot_be_promoted_by_flipping_status():
    promoted = dev_case(1, status="verified")
    rep = pr.validate_case_set([promoted], registry=fx.REGISTRY)
    assert "case_invalid" in codes(rep) and rep["coverage"]["verified_final_total"] == 0


def test_adding_cases_never_moves_an_existing_group():
    base = [dev_case(1), final_case(2)]
    before = {c["group_id"]: pr.derive_split(c["group_id"]) for c in base}
    grown = base + [dev_case(i, group=group_for("dev", f"grp-grow{i}")) for i in range(3, 9)]
    after = {c["group_id"]: pr.derive_split(c["group_id"]) for c in grown}
    assert all(after[g] == s for g, s in before.items())


def test_case_content_cannot_pick_the_split():
    a = dev_case(1, query="completely different words here one")
    b = copy.deepcopy(a)
    b["query"] = "other words altogether two"
    assert pr.derive_split(a["group_id"]) == pr.derive_split(b["group_id"])


def test_combined_faults_all_reported_together():
    cases = [dev_case(1), final_case(2, group=DEV), dev_case(3, group=FINAL)]
    rep = pr.validate_case_set(cases, registry=fx.REGISTRY)
    assert {"group_split_leak", "split_not_derived"} <= set(codes(rep))
