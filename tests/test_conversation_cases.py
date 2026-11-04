"""Offline structure checks for evaluation/conversations/cases.json (no network)."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "evaluation/conversations/cases.json").read_text(encoding="utf-8"))
SAMPLE = (ROOT / "Context/sample-query-results-20261103.md").read_text(encoding="utf-8")
# curriculum id -> the "### <program> · <edition>" heading in the recorded sample results
HEADINGS = {
    "bscs-2018-2019": "Bachelor of Science in Computer Science · 2018-2019",
    "bsit-2018-2019": "Bachelor of Science in Information Technology · 2018-2019",
    "bsce-2018-2019": "Bachelor of Science in Civil Engineering · 2018-2019",
    "bsacct-2023-2024": "Bachelor of Science in Accountancy · 2023-2024",
    "bsed-math-2018-2019": "Bachelor of Secondary Education (major in Mathematics) · 2018-2019",
    "bshm-culinary-2018-2019": "Bachelor of Science in Hospitality Management (Specialized Track for Culinary Arts and Kitchen Management) · 2018-2019",
}
STATUSES = {None, "answered", "clarification_needed"}


def load_runner():
    spec = importlib.util.spec_from_file_location("run_conversations", ROOT / "evaluation/conversations/run_conversations.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_structure():
    cases = CASES["conversations"]
    assert len(cases) >= 30
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids))
    for c in cases:
        assert c["category"] and c["language"] and c["note"]
        assert 1 <= len(c["turns"]) <= 4, c["id"]
        if c["curriculum_id"] is not None:
            assert c["curriculum_id"] in HEADINGS, c["id"]
            assert f"### {HEADINGS[c['curriculum_id']]}" in SAMPLE, c["id"]
        for t in c["turns"]:
            assert t["text"].strip()
            e = t["expect"]
            assert e["status"] in STATUSES
            assert set(e) <= {"status", "required", "required_any", "forbidden"}
            for key in ("required", "required_any", "forbidden"):
                assert all(isinstance(s, str) and s for s in e.get(key, [])), (c["id"], key)
    assert all(isinstance(s, str) for s in CASES["defaults"]["forbidden"])


def test_pending_cases_are_marked_and_few():
    pending = {c["pending"] for c in CASES["conversations"] if c.get("pending")}
    assert {"bare-program", "track-switch", "shifting-referral", "recovery-ask"} <= pending


def test_checker_and_program_ids():
    run = load_runner()
    assert run.program_id("bscs-proposed-2025-2026") == "palsu-bscs"
    assert run.program_id("bshm-culinary-2018-2019") == "palsu-bshm-culinary"
    expect = {"status": "answered", "required": ["Php 100.00"], "forbidden": ["Paki-clarify"]}
    assert run.check(expect, {}, "Total: Php  100.00", {"status": "answered"}) == []
    assert len(run.check(expect, {}, "Paki-clarify muna", {"status": "clarification_needed"})) == 3
    assert run.check({"status": None}, {"forbidden": ["temporarily unavailable"]}, "x", {}) == []
    assert run.check({"status": None}, {"forbidden": ["temporarily unavailable"]}, "Temporarily   unavailable", {})


def test_track_switch_fixture_matches_reviewed_bshm_hotel_ledger():
    case = next(c for c in CASES["conversations"] if c["id"] == "track-switch")
    expect = case["turns"][1]["expect"]
    assert expect["status"] == "clarification_needed"
    assert "HMPE 5" in expect["required"] and "THC-LA" in expect["required"]
    assert "Hotel" not in expect.get("required", [])
