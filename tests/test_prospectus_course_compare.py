import copy
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "prospectus_course_compare", Path(__file__).resolve().parents[1] / "scripts" / "prospectus_course_compare.py"
)
compare = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compare)


def payload():
    return {
        "courses": [{"course_code": "CS 101", "course_title": "Intro", "total_units": 3}],
        "audit": {"status": "ok", "total_courses": 1},
    }


def test_identical_payloads_have_no_differences_and_timestamps_are_ignored():
    new = payload()
    new["generated_at"] = "later"
    assert compare.compare_payloads(payload(), new) == []


def test_one_changed_course_field_is_reported():
    new = copy.deepcopy(payload())
    new["courses"][0]["course_title"] = "Changed"
    assert compare.compare_payloads(payload(), new) == ["course 0 differs: ['course_title']"]


def test_audit_and_count_changes_are_reported():
    new = payload()
    new["audit"]["status"] = "error"
    new["courses"].append(dict(new["courses"][0]))
    issues = compare.compare_payloads(payload(), new)
    assert any(i.startswith("audit differs") for i in issues) and any("course count" in i for i in issues)
