"""Corpus gate report: blocked audits, per-file course rejections, title classes, layout losses, totals."""

import importlib.util
import json
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "prospectus_course_compare", Path(__file__).resolve().parents[1] / "scripts" / "prospectus_course_compare.py"
)
compare = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compare)

LAYOUT = [{"table_index": 0, "column_groups": [{"index": 0, "code_idx": 0, "title_idx": 1, "unit_idx": 2, "prereq_idx": 3}]}]


def _cell(cid, col, text, row=2):
    return {"cell_id": cid, "table_index": 0, "row_start": row, "row_end": row + 1,
            "col_start": col, "col_end": col + 1, "text": text}


def _course(code, claimed, printed, row=2):
    cells = [_cell(f"{code}-c", 0, code, row), _cell(f"{code}-t", 1, printed, row),
             _cell(f"{code}-u", 2, "3", row), _cell(f"{code}-p", 3, "None", row)]
    return {"course_code": code, "course_title": claimed, "year_level": "1st Year", "semester": "1st Semester",
            "_source": {"table_index": 0, "row_index": row, "column_group": 0},
            "provenance": {"source_cell_ids": [c["cell_id"] for c in cells], "source_cells": cells}}


def _reject(code, reason, **extra):
    return {"chunk_type": "course", "label": code, "reason": reason, "course_code": code,
            "year_level": "1st Year", "semester": "1st Semester", "source_cell_ids": [f"{code}-c", f"{code}-t", f"{code}-u", f"{code}-p"],
            "source_item_ids": [], "source_refs": [], **extra}


def _payload(status, courses=(), accepted=(), rejected=(), hier=(), semantic_extra=()):
    chunks = [{"chunk_type": "course", "token_count": 80, "source_anchored": False} for _ in accepted]
    return {"audit": {"status": status, "errors": ["e"] if status == "error" else [], "table_layout": LAYOUT,
                      "curriculum_sections": []},
            "courses": list(courses),
            "rag": {"semantic_chunks": chunks + list(semantic_extra), "hierarchical_chunks": list(hier),
                    "rejected_chunks": list(rejected)}}


def _write(root, number, name, payload, exit_code=0):
    folder = root / f"{number:02d}"
    folder.mkdir(parents=True)
    (folder / "source.txt").write_text(f"C:/x/{name}_docling.json", encoding="utf-8")
    (folder / "exit.txt").write_text(str(exit_code), encoding="utf-8")
    if payload is not None:
        (folder / "candidate.json").write_text(json.dumps(payload), encoding="utf-8")


@pytest.fixture
def corpus(tmp_path):
    _write(tmp_path, 1, "blocked", _payload("error", courses=[_course("BL 1", "Blocked", "Blocked")]))
    courses = [
        _course("OK 1", "Fine", "Fine"),
        _course("BN 1", "Intro", "Intro TOTAL"),
        _course("FN 1", "Algebra", "Algebra 1"),
        _course("PR 1", "Algebra", "First Semester Algebra"),
        _course("CR 1", "Intro to Computing Lab", "Intro to Computing"),
        _course("OT 1", "Bar", "Foo"),
        _course("PQ 1", "Physics", "Physics"),
    ]
    rejected = [_reject("BN 1", "title_not_in_source_text"), _reject("FN 1", "title_not_in_source_text"),
                _reject("PR 1", "title_not_in_source_text"), _reject("CR 1", "title_not_in_source_text"),
                _reject("OT 1", "title_not_in_source_text"), _reject("PQ 1", "prerequisite_not_in_source_text"),
                {"chunk_type": "term_schedule", "label": "1st Year 1st Semester", "reason": "no_accepted_courses",
                 "course_code": None, "source_cell_ids": [], "source_item_ids": [], "source_refs": []},
                {"chunk_type": "hierarchical_layout", "label": "docling_hierarchical:3", "reason": "over_token_cap",
                 "token_count": 900, "source_cell_ids": [], "source_item_ids": [], "source_refs": ["#/tables/0"]},
                {"chunk_type": "hierarchical_layout", "label": "docling_hierarchical:5", "reason": "no_source_spans",
                 "source_cell_ids": [], "source_item_ids": [], "source_refs": []}]
    _write(tmp_path, 2, "emits", _payload(
        "warn", courses, accepted=["OK 1"], rejected=rejected,
        hier=[{"chunk_type": "hierarchical_layout", "token_count": 40, "source_anchored": False}],
        semantic_extra=[{"chunk_type": "term_schedule", "token_count": 200, "source_anchored": False}]))
    _write(tmp_path, 3, "clean", _payload("ok", [_course("A 1", "Art", "Art"), _course("A 2", "Bio", "Bio")], accepted=["A 1", "A 2"]))
    _write(tmp_path, 4, "crashed", None, exit_code=1)
    return tmp_path


def test_blocked_audits_are_reported_apart_and_not_counted_as_courses(corpus):
    report = compare.corpus_gate(corpus)
    assert report["inputs"] == 4
    assert [b["input"] for b in report["blocked"]] == ["blocked_docling.json"]
    assert report["totals"]["emitting_files"] == 2
    assert report["totals"]["courses"] == 9  # 7 + 2; the blocked file's course is not counted
    assert [f["input"] for f in report["failed_runs"]] == ["crashed_docling.json"]


def test_accepted_and_rejected_per_file_by_reason_and_totals(corpus):
    report = compare.corpus_gate(corpus)
    emits = next(f for f in report["files"] if f["input"] == "emits_docling.json")
    assert emits["courses"] == 7 and emits["accepted"] == 1 and emits["rejected"] == 6
    assert emits["rejected_by_reason"] == {"prerequisite_not_in_source_text": 1, "title_not_in_source_text": 5}
    totals = report["totals"]
    assert (totals["accepted"], totals["rejected"]) == (3, 6)
    assert totals["rejected_pct"] == "66.7"
    assert totals["rejected_by_reason"] == {"prerequisite_not_in_source_text": 1, "title_not_in_source_text": 5}


def test_title_rejections_are_classified_into_three_groups_with_the_printed_text(corpus):
    report = compare.corpus_gate(corpus)
    assert report["title_groups"] == {"claim_longer_than_cell": 1, "other": 1, "printed_equals_claim_plus_token": 3}
    by_code = {d["course_code"]: d for d in report["title_details"]}
    assert by_code["BN 1"]["group"] == "printed_equals_claim_plus_token" and by_code["BN 1"]["extra"] == "TOTAL"
    assert by_code["FN 1"]["group"] == "printed_equals_claim_plus_token" and by_code["FN 1"]["extra"] == "1"
    assert by_code["PR 1"]["group"] == "printed_equals_claim_plus_token" and by_code["PR 1"]["extra"] == "First Semester"
    assert by_code["CR 1"]["group"] == "claim_longer_than_cell" and by_code["CR 1"]["printed"] == "Intro to Computing"
    assert by_code["OT 1"]["group"] == "other" and by_code["OT 1"]["claimed"] == "Bar"


def test_an_unknown_extra_word_is_not_called_a_banner(tmp_path):
    course = _course("X 1", "Intro", "Intro Mechanics")
    _write(tmp_path, 1, "f", _payload("ok", [course], rejected=[_reject("X 1", "title_not_in_source_text")]))
    assert compare.corpus_gate(tmp_path)["title_groups"]["other"] == 1


def test_layout_rejections_are_listed_and_table_losses_counted(corpus):
    report = compare.corpus_gate(corpus)
    assert report["layout"]["rejected_by_reason"] == {"no_source_spans": 1, "over_token_cap": 1}
    assert report["layout"]["emitting_files_with_table_over_cap"] == 1
    emits = next(f for f in report["files"] if f["input"] == "emits_docling.json")
    assert emits["layout_rejections"][0] == {"label": "docling_hierarchical:3", "reason": "over_token_cap",
                                             "refs": ["#/tables/0"], "token_count": 900}
    assert report["other_rejected_by_type"] == {"term_schedule:no_accepted_courses": 1}

def test_an_over_cap_text_chunk_is_not_counted_as_a_lost_table(tmp_path):
    lost = {"chunk_type": "hierarchical_layout", "label": "docling_hierarchical:1", "reason": "over_token_cap",
            "token_count": 900, "source_cell_ids": [], "source_item_ids": [], "source_refs": ["#/texts/1"]}
    _write(tmp_path, 1, "f", _payload("ok", [_course("A 1", "Art", "Art")], accepted=["A 1"], rejected=[lost]))
    layout = compare.corpus_gate(tmp_path)["layout"]
    assert layout == {"rejected_by_reason": {"over_token_cap": 1}, "emitting_files_with_table_over_cap": 0}


def test_chunk_statistics_and_cap_check(corpus):
    stats = compare.corpus_gate(corpus)["chunk_statistics"]
    assert stats["inputs_with_chunks"] == 2
    assert stats["by_type"]["course"] == {"count": 3, "min": 80, "median": 80, "max": 80}
    assert stats["anchored"] == {"false": 5, "true": 0}
    assert stats["over_cap_course_or_term"] == 0


def test_a_course_chunk_over_the_cap_fails_the_cap_check(tmp_path):
    over = {"chunk_type": "term_schedule", "token_count": 481, "source_anchored": False}
    _write(tmp_path, 1, "f", _payload("ok", [_course("A 1", "Art", "Art")], accepted=["A 1"], semantic_extra=[over]))
    assert compare.corpus_gate(tmp_path)["chunk_statistics"]["over_cap_course_or_term"] == 1


def test_accepted_plus_rejected_must_match_the_course_count(tmp_path):
    _write(tmp_path, 1, "f", _payload("ok", [_course("A 1", "Art", "Art"), _course("A 2", "Bio", "Bio")], accepted=["A 1"]))
    report = compare.corpus_gate(tmp_path)
    assert report["files"][0]["unaccounted"] == 1 and report["totals"]["unaccounted"] == 1


def test_rendered_report_and_file_are_deterministic_lf_and_leave_inputs_alone(corpus, tmp_path_factory):
    before = {p: p.read_bytes() for p in corpus.rglob("*") if p.is_file()}
    out = tmp_path_factory.mktemp("out") / "gate.txt"
    compare.write_corpus_report(corpus, out)
    first = out.read_bytes()
    compare.write_corpus_report(corpus, out)
    assert out.read_bytes() == first
    assert b"\r" not in first and first.endswith(b"\n")
    assert before == {p: p.read_bytes() for p in corpus.rglob("*") if p.is_file()}
    text = first.decode("utf-8")
    assert "BLOCKED AUDIT (1)" in text and "blocked_docling.json" in text
    assert "rejected 6 of 9 (66.7%)" in text
    assert json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))["inputs"] == 4
