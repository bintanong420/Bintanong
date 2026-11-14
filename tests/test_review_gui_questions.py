import copy
import json

import pytest

from backend.bintanong_tools.prospectus_review_gui.questions import (
    SECTION_CONFIRM, build_questions, confirmable, order_queue,
)

import fixer_fixtures as fx
import review_gui_fixtures as rf
from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate


def built(payload=None, entries=(), v=None):
    payload = payload or rf.mixed()
    v = v or rf.verified(payload)
    return payload, v, build_questions(payload, v, entries, rf.HASH)


def by_id(questions):
    return {q.qid: q for q in questions}


def ids(questions):
    return [q.qid for q in questions]


def test_fixture_has_the_three_healths():
    _p, v, _q = built()
    assert {s.sid: s.health for s in v.sections}["S1"] == "clean"
    assert {s.sid: s.health for s in v.sections}["S2"] == "review"
    assert {s.sid: s.health for s in v.sections}["S3"] == "broken"


def test_one_question_per_course_row_and_per_unclaimed_item():
    payload, v, questions = built()
    rows = [r for s in v.sections for r in s.rows]
    assert sum(r.item is not None for r in rows) == 1
    row_questions = [q for q in questions if q.kind != SECTION_CONFIRM]
    assert sorted(ids(row_questions)) == sorted(r.rid for r in rows)
    assert len(row_questions) == len(payload["courses"]) + 1
    assert len(set(ids(questions))) == len(questions)


def test_course_prompt_names_title_and_code():
    _p, _v, questions = built()
    q = next(q for q in questions if q.reference.get("code") == "GE-ET")
    assert q.prompt == f'Is the subject "{rf.ODD_TITLE}" with course code "GE-ET" correct?'
    assert q.reference["title"] == rf.ODD_TITLE and '"Applied"' in q.reference["title"] and "á" in q.reference["title"]
    assert q.kind == "course" and q.other_allowed is True and "lecture_units" in q.editable_fields
    assert q.pages == [2]
    assert q.section["sid"] == "S3" and q.section["health"] == "broken"


def test_unclaimed_prompt_names_code_and_page():
    _p, _v, questions = built()
    q = next(q for q in questions if q.kind == "unclaimed")
    assert q.prompt == 'The PDF prints "CS 9" on page 3 but no course uses it. Is it right to leave it out?'
    assert q.other_allowed is False and q.editable_fields == [] and q.pages == [3]
    assert q.flags and q.flags[0]["kind"] == "unclaimed_code"


def test_clean_section_gets_one_bulk_question_and_flagged_section_does_not():
    _p, _v, questions = built()
    bulk = [q for q in questions if q.kind == SECTION_CONFIRM]
    assert ids(bulk) == ["S1:confirm"]
    q = bulk[0]
    assert q.prompt == "Are all 2 courses in 1st Year - 1st Semester correct as extracted?"
    assert q.other_allowed is False and q.members == ["S1-01", "S1-02"] and q.reference["count"] == 2
    assert q.locator is None and q.pages == [1]
    assert ids(questions)[:3] == ["S1:confirm", "S1-01", "S1-02"]   # the bulk question leads its section


def test_bulk_question_still_offered_when_only_info_flags():
    _p, v, questions = built()
    s1 = v.sections[0]
    assert [f.severity for r in s1.rows for f in r.flags] == ["info"]   # the parser stripped a banner from a cell
    assert confirmable(s1) and "S1:confirm" in ids(questions)



def test_bulk_question_absent_when_a_warn_or_error_flag_exists():
    _p, v, questions = built()
    assert not confirmable(v.sections[1]) and not confirmable(v.sections[2])
    assert "S2:confirm" not in ids(questions) and "S3:confirm" not in ids(questions)


def test_queue_order_attention_puts_broken_then_review_then_clean_and_errors_before_warnings():
    _p, _v, questions = built()
    queue = order_queue(questions, "attention")
    assert ids(queue) == ["S3-01", "SU-U1", "S2-01", "S2-02", "S1:confirm", "S1-01", "S1-02"]
    assert [q.section["health"] for q in queue] == ["broken", "broken", "review", "review", "clean", "clean", "clean"]


def test_flagged_rows_come_before_clean_rows_and_errors_before_warnings_inside_a_section():
    payload = fx.architecture()
    v = verify_candidate(payload, {1: PdfPage(fx.ARCH_PAGE_TEXT)})
    queue = order_queue(build_questions(payload, v, [], rf.HASH), "attention")
    rank_of = {"broken": 0, "review": 1, "clean": 2}
    healths = [rank_of[q.section["health"]] for q in queue]
    assert healths == sorted(healths)
    sids = [q.section["sid"] for q in queue]
    assert sids == sorted(sids, key=sids.index)
    assert [s for i, s in enumerate(sids) if i == 0 or s != sids[i - 1]] == list(dict.fromkeys(sids))   # a section is never split
    for sid in dict.fromkeys(sids):
        group = [q for q in queue if q.section["sid"] == sid and q.kind != SECTION_CONFIRM]
        rank = [min((0 if f["severity"] == "error" else 1 for f in q.flags if f["severity"] != "info"), default=2) for q in group]
        assert rank == sorted(rank), (sid, ids(group), rank)
        for r in range(3):   # printed order breaks ties
            same = [q.position for q, k in zip(group, rank) if k == r]
            assert same == sorted(same)


def test_queue_order_print_is_printed_order():
    _p, _v, questions = built()
    assert ids(order_queue(questions, "print")) == ["S1:confirm", "S1-01", "S1-02", "S2-01", "S2-02", "S3-01", "SU-U1"]
    with pytest.raises(ValueError):
        order_queue(questions, "random")

def test_reference_value_is_never_preselected():
    _p, _v, questions = built(fx.architecture(), v=verify_candidate(fx.architecture(), {1: PdfPage(fx.ARCH_PAGE_TEXT)}))
    assert any(q.proposals for q in questions)
    for q in questions:
        data = q.to_dict()
        assert not {"selected", "default_answer", "answer", "choice"} & set(data)
        for proposal in data["proposals"]:
            assert not {"selected", "default", "chosen"} & set(proposal)
            assert set(proposal) == {"letter", "kind", "field", "old", "new", "note", "fix_id"}
        json.dumps(data)   # plain data, ready for the API


def test_decided_questions_leave_the_attention_queue_but_stay_listed():
    payload = rf.mixed()
    v = rf.verified(payload)
    entries = rf.decision(payload, v, "S3-01")
    questions = build_questions(payload, v, entries, rf.HASH)
    q = by_id(questions)["S3-01"]
    assert q.decision["disposition"] == "accepted" and q.decided and q.decision["reviewer"] == "Nestor"
    assert "S3-01" not in ids(order_queue(questions, "attention")) and "S3-01" not in ids(order_queue(questions, "print"))
    assert "S3-01" in ids(questions)
    assert by_id(questions)["SU-U1"].decision is None


def test_corrected_course_counts_as_decided_with_the_corrected_reason():
    payload = rf.mixed()
    v = rf.verified(payload)
    entries = rf.decision(payload, v, "S3-01", "edit", reason="PDF prints another title", edits={"course_title": "Ethics"})
    q = by_id(build_questions(payload, v, entries, rf.HASH))["S3-01"]
    assert q.decided and q.decision["disposition"] == "corrected" and q.decision["reason"] == "PDF prints another title"


def test_unclaimed_decision_and_unresolved_stays_in_queue():
    payload = rf.mixed()
    v = rf.verified(payload)
    ok = build_questions(payload, v, rf.decision(payload, v, "SU-U1", "ok", reason="footnote"), rf.HASH)
    assert by_id(ok)["SU-U1"].decided and "SU-U1" not in ids(order_queue(ok))
    unresolved = build_questions(payload, v, rf.decision(payload, v, "SU-U1", "unresolved", reason="cannot tell"), rf.HASH)
    q = by_id(unresolved)["SU-U1"]
    assert q.decision["disposition"] == "unresolved" and not q.decided and "SU-U1" in ids(order_queue(unresolved))


def test_entry_for_another_pdf_does_not_count_as_decided():
    payload = rf.mixed()
    v = rf.verified(payload)
    entries = rf.decision(payload, v, "S3-01", pdf_sha256="e" * 64)
    q = by_id(build_questions(payload, v, entries, rf.HASH))["S3-01"]
    assert q.decision is None and not q.decided


def test_stale_entry_does_not_count_as_decided():
    payload = rf.mixed()
    v = rf.verified(payload)
    entries = rf.decision(payload, v, "S3-01")
    changed = copy.deepcopy(payload)
    changed["courses"][-1]["course_title"] = "Another title now"   # the value reviewed is no longer the candidate's
    q = by_id(build_questions(changed, verify_candidate(changed, None), entries, rf.HASH))["S3-01"]
    assert q.decision is None


def test_invalid_line_does_not_count_as_decided():
    payload = rf.mixed()
    v = rf.verified(payload)
    entry = rf.decision(payload, v, "S3-01")[0]
    entry["reason"] = "edited after it was written"   # entry_id no longer matches
    assert by_id(build_questions(payload, v, [entry, {"_unreadable": "line 2 is not JSON"}], rf.HASH))["S3-01"].decision is None


def test_later_entry_wins():
    payload = rf.mixed()
    v = rf.verified(payload)
    entries = rf.decision(payload, v, "S3-01") + rf.decision(payload, v, "S3-01", "unresolved", reason="second look: unclear")
    questions = build_questions(payload, v, entries, rf.HASH)
    q = by_id(questions)["S3-01"]
    assert q.decision["disposition"] == "unresolved" and q.decision["reason"] == "second look: unclear" and not q.decided
    assert "S3-01" in ids(order_queue(questions))


def test_bulk_question_is_decided_when_every_course_is():
    payload = rf.mixed()
    v = rf.verified(payload)
    one = build_questions(payload, v, rf.decision(payload, v, "S1-01"), rf.HASH)
    assert not by_id(one)["S1:confirm"].decided
    both = build_questions(payload, v, rf.decision(payload, v, "S1-01") + rf.decision(payload, v, "S1-02"), rf.HASH)
    q = by_id(both)["S1:confirm"]
    assert q.decided and q.decision == {"disposition": "accepted", "count": 2}
    assert "S1:confirm" not in ids(order_queue(both))


def test_questions_do_not_mutate_the_payload():
    payload = rf.mixed()
    before = copy.deepcopy(payload)
    v = rf.verified(payload)
    entries = rf.decision(payload, v, "S3-01")
    order_queue(build_questions(payload, v, entries, rf.HASH))
    assert payload == before
