import copy

import pytest

from backend.bintanong_tools.ocr_bench import score


def _course(code, title, term, units, prereq="", cells=()):
    year, semester = term
    lecture, lab = units
    return {
        "course_code": code, "course_title": title, "title_raw": title, "year_level": year, "semester": semester,
        "units": {"raw": f"{lecture}/{lab}", "lecture": lecture, "lab": lab, "total": lecture + lab},
        "total_units": lecture + lab, "lecture_units": lecture, "lab_units": lab,
        "prerequisites": [p for p in prereq.split(",") if p], "prerequisites_raw": prereq,
        "confidence_flags": [], "provenance": {"page": 1, "source_cell_ids": list(cells)},
    }


def reference():
    return {"courses": [
        _course("CS 101", "Introduction to Computing", ("1st Year", "1st Semester"), (2, 1), "", ["c1", "c2"]),
        _course("CS 102", "Computer Programming 1", ("1st Year", "2nd Semester"), (2, 1), "CS 101", ["c3", "c4"]),
        _course("MATH 101", "Calculus", ("1st Year", "2nd Semester"), (3, 0), "", ["c5", "c6"]),
    ], "audit": {}}


def test_a_document_scored_against_itself_is_supported_with_perfect_numbers():
    report = score.score_document(reference(), reference(), name="bs")
    assert report["missing"] == [] and report["invented"] == []
    assert report["critical"]["rate"] == 1.0
    assert report["cer"]["rate"] == 0.0
    assert report["silent_critical"] == 0
    assert report["verdict"]["supported"] is True
    assert report["verdict"]["failures"] == []


def test_a_missing_course_and_an_invented_course_are_both_reported_and_fail_the_verdict():
    cand = reference()
    ghost = _course("ZZ 999", "Ghost", ("1st Year", "1st Semester"), (1, 0), "", ["g1"])
    cand["courses"] = [cand["courses"][0], cand["courses"][2], ghost]
    report = score.score_document(reference(), cand)
    assert report["missing"] == ["CS 102"]
    assert report["invented"] == ["ZZ 999"]
    assert report["verdict"]["supported"] is False
    assert any("missing" in f for f in report["verdict"]["failures"])
    assert any("invented" in f for f in report["verdict"]["failures"])
    assert report["critical"]["rate"] < 1.0  # the lost course's fields count as wrong


def test_an_ocr_slip_in_a_code_shows_up_as_one_missing_and_one_invented():
    cand = reference()
    cand["courses"][1]["course_code"] = "CS 1O2"
    report = score.score_document(reference(), cand)
    assert report["missing"] == ["CS 102"] and report["invented"] == ["CS 1O2"]


def test_spacing_only_code_difference_matches_the_course_but_not_the_exact_field():
    cand = reference()
    cand["courses"][0]["course_code"] = "CS101"
    report = score.score_document(reference(), cand)
    assert report["missing"] == [] and report["invented"] == []
    assert [d["field"] for d in report["disagreements"]] == ["course_code"]


def test_wrong_critical_fields_lower_the_exact_rate_and_name_the_field():
    cand = reference()
    cand["courses"][1]["lecture_units"] = 3
    cand["courses"][2]["semester"] = "1st Semester"
    cand["courses"][2]["prerequisites"] = ["CS 101"]
    report = score.score_document(reference(), cand)
    fields = sorted(d["field"] for d in report["disagreements"] if d["kind"] == "mismatch")
    assert fields == ["lecture_units", "prerequisites", "semester"]
    assert report["critical"]["total"] == 21 and report["critical"]["exact"] == 18
    assert report["critical"]["rate"] == pytest.approx(18 / 21)
    assert any("critical" in f for f in report["verdict"]["failures"])


def test_cer_is_per_cell_and_summed_per_document():
    cand = reference()
    cand["courses"][0]["course_title"] = "Introduction to Computlng"  # 1 substitution of 25
    report = score.score_document(reference(), cand)
    cell = next(c for c in report["cer"]["cells"] if c["field"] == "course_title" and c["course"] == "CS 101")
    assert cell["edits"] == 1 and cell["cer"] == pytest.approx(1 / 25)
    assert report["cer"]["rate"] == pytest.approx(1 / report["cer"]["chars"])


def test_levenshtein():
    assert score.edit_distance("kitten", "sitting") == 3
    assert score.edit_distance("", "abc") == 3
    assert score.edit_distance("same", "same") == 0


def test_an_error_nobody_flagged_is_silent_and_a_flagged_one_is_not():
    cand = reference()
    cand["courses"][1]["total_units"] = 9
    cand["courses"][2]["lab_units"] = 2
    cand["courses"][2]["confidence_flags"] = ["low_ocr_confidence"]
    report = score.score_document(reference(), cand)
    by_course = {(d["code"], d["field"]): d["silent"] for d in report["disagreements"]}
    assert by_course[("CS 102", "total_units")] is True
    assert by_course[("MATH 101", "lab_units")] is False
    assert report["silent_critical"] == 1
    assert any("silent" in f for f in report["verdict"]["failures"])


def test_a_missing_course_the_candidate_audit_lists_is_flagged_not_silent():
    cand = reference()
    cand["courses"].pop(1)
    cand["audit"] = {"unclaimed_course_candidates": [{"code": "CS 102", "cell_ids": ["c3"]}]}
    report = score.score_document(reference(), cand)
    row = next(d for d in report["disagreements"] if d["kind"] == "missing")
    assert row["silent"] is False
    assert report["silent_critical"] == 0
    cand["audit"] = {}
    assert score.score_document(reference(), cand)["silent_critical"] == 1


def test_missing_course_text_counts_against_cer_so_losing_a_course_cannot_hide():
    cand = reference()
    cand["courses"].pop(2)
    report = score.score_document(reference(), cand)
    assert report["cer"]["rate"] > 0.05


def test_the_four_q11_criteria_are_independent():
    ok = dict(missing=0, invented=0, critical_rate=0.99, worst_cer=0.01, silent=0)
    assert score.q11_verdict(**ok)["supported"] is True
    assert score.q11_verdict(**{**ok, "critical_rate": 0.979})["supported"] is False
    assert score.q11_verdict(**{**ok, "critical_rate": 0.98})["supported"] is True
    assert score.q11_verdict(**{**ok, "worst_cer": 0.021})["supported"] is False
    assert score.q11_verdict(**{**ok, "worst_cer": 0.02})["supported"] is True
    assert score.q11_verdict(**{**ok, "silent": 1})["supported"] is False
    assert score.q11_verdict(**{**ok, "missing": 1})["supported"] is False
    assert score.q11_verdict(**{**ok, "invented": 1})["supported"] is False


def test_corpus_verdict_uses_the_worst_document_and_pooled_exact_rate():
    bad = copy.deepcopy(reference())
    bad["courses"][0]["course_title"] = "Xxxxxxxxxxxxxxxxxxxxxxxxx"
    docs = {"good": score.score_document(reference(), reference()), "bad": score.score_document(reference(), bad)}
    corpus = score.score_corpus(docs)
    assert corpus["worst_document"]["name"] == "bad"
    assert corpus["verdict"]["supported"] is False
    assert any("CER" in f for f in corpus["verdict"]["failures"])
    assert corpus["verdict"]["criteria"]["no_missing_or_invented"] is True
    assert score.score_corpus({"good": docs["good"]})["verdict"]["supported"] is True


def test_empty_corpus_is_not_supported():
    assert score.score_corpus({})["verdict"]["supported"] is False
