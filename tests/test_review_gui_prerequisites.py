"""Task 10: prerequisite questions, the three states shown live, and what the answers write. Needs the `review` extra."""

import hashlib
import json

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from backend.bintanong_tools.prospectus_extractor.ledger import FIELD_PREREQ, read_entries  # noqa: E402
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate  # noqa: E402
from backend.bintanong_tools.prospectus_review_gui.answers import Answer  # noqa: E402
from backend.bintanong_tools.prospectus_review_gui.app import create_app, new_token  # noqa: E402
from backend.bintanong_tools.prospectus_review_gui.questions import PREREQUISITE, build_questions, order_queue  # noqa: E402
from backend.bintanong_tools.prospectus_review_gui.session import open_session  # noqa: E402

import review_gui_fixtures as rf  # noqa: E402

PORT = 8765
STATES = {"CS 1": "blank_unreviewed", "CC 1/L": "stated_none", "CS 2": "resolved", "CC 3/L": "unreadable", "GE-ET": "blank_unreviewed"}


def with_states():
    payload = rf.mixed()
    for course in payload["courses"]:
        course["prerequisite_state"] = STATES[course["course_code"]]
    payload["courses"][3]["prerequisites_raw"] = "CC 2/L"
    payload["content_review"] = "pending"
    return payload


@pytest.fixture
def env(tmp_path):
    ws = rf.workspace(tmp_path, with_states())
    session = open_session(ws.candidate, ws.identity, "Nestor", ws.review)
    token = new_token()
    client = TestClient(create_app(session, token, port=PORT), base_url=f"http://127.0.0.1:{PORT}")
    yield ws, session, client, token
    session.close()


def prereq_questions(session):
    return {q.reference["code"]: q for q in session.questions() if q.kind == PREREQUISITE}


def test_blank_prerequisite_course_gets_a_prerequisite_question_with_the_no_prerequisite_wording(env):
    _ws, session, *_ = env
    found = prereq_questions(session)
    blank = found["CS 1"]
    assert blank.prompt == 'Is it right that "Discrete Structures 1" (CS 1) has no prerequisite?'
    assert blank.editable_fields == ["prerequisites_raw"] and blank.other_allowed
    assert blank.reference["prerequisites_raw"] == "" and blank.reference["prerequisite_state"] == "blank_unreviewed"
    assert found["CC 3/L"].prompt == 'Is the prerequisite "CC 2/L" of "Computer Programming 2" (CC 3/L) correct?'
    assert "approv" not in blank.prompt.lower()


def test_resolved_prerequisite_gets_no_question(env):
    _ws, session, *_ = env
    assert set(prereq_questions(session)) == {"CS 1", "CC 3/L", "GE-ET"}   # resolved (CS 2) and stated_none (CC 1/L) get none
    for state in ("resolved", "standing_condition", "stated_none", "reviewed_empty"):
        payload = with_states()
        payload["courses"][0]["prerequisite_state"] = state
        found = {q.reference["code"] for q in build_questions(payload, verify_candidate(payload, None), [], rf.HASH)
                 if q.kind == PREREQUISITE}
        assert "CS 1" not in found, state
    for state in ("blank_unreviewed", "unreadable", "unresolved_reference", "alternative_or_exception"):
        payload = with_states()
        payload["courses"][2]["prerequisite_state"] = state
        found = {q.reference["code"] for q in build_questions(payload, verify_candidate(payload, None), [], rf.HASH)
                 if q.kind == PREREQUISITE}
        assert "CS 2" in found, state


def test_a_candidate_without_prerequisite_states_gets_no_prerequisite_questions(tmp_path):
    payload = rf.mixed()   # an older candidate: no prerequisite_state on any course
    ws = rf.workspace(tmp_path, payload)
    with open_session(ws.candidate, ws.identity, "Nestor", ws.review) as session:
        assert prereq_questions(session) == {}
        assert session.state()["prerequisites"]["unclassified_courses"] == len(payload["courses"])


def test_prerequisite_questions_come_after_every_course_field_question(env):
    _ws, session, *_ = env
    for mode in ("attention", "print"):
        kinds = [q.kind for q in session.queue(mode)]
        first = kinds.index(PREREQUISITE)
        assert PREREQUISITE not in kinds[:first] and set(kinds[first:]) == {PREREQUISITE}, mode
    assert [q.reference["code"] for q in session.queue("print") if q.kind == PREREQUISITE] == ["CS 1", "CC 3/L", "GE-ET"]


def test_yes_on_blank_prerequisite_writes_accepted_prerequisites_raw_entry(env):
    ws, session, *_ = env
    q = prereq_questions(session)["CS 1"]
    result = session.answer(q.qid, Answer("yes"), now=rf.NOW)
    assert result == {"written": 1, "skipped": 0, "errors": []}
    (line,) = read_entries(ws.ledger)
    assert (line["field"], line["disposition"], line["old_value"], line["new_value"]) == (FIELD_PREREQ, "accepted", "", "")
    assert line["via"] == "gui" and line["reason"] and line["locator"]["code_at_review"] == "CS 1"
    assert prereq_questions(session)["CS 1"].decided
    assert session.state()["content_review"]["state"] == "partially_reviewed"   # content_review_state is unchanged: any current decision leaves `pending`, but `reviewed` never waits for one


def test_other_on_prerequisite_accepts_text_and_empty_text_but_not_a_number(env):
    ws, session, *_ = env
    qs = prereq_questions(session)
    ok = session.answer(qs["CS 1"].qid, Answer("other", edits={FIELD_PREREQ: "CS 2"}, reason="read from the PDF"), now=rf.NOW)
    assert ok["errors"] == []
    gone = session.answer(qs["CC 3/L"].qid, Answer("other", edits={FIELD_PREREQ: ""}, reason="the cell is empty in the PDF"), now=rf.NOW)
    assert gone["errors"] == []
    lines = read_entries(ws.ledger)
    assert [(e["disposition"], e["old_value"], e["new_value"]) for e in lines] == [("corrected", "", "CS 2"), ("corrected", "CC 2/L", "")]
    before = ws.ledger.read_bytes()
    for bad in (5, "5", " 42 "):
        refused = session.answer(qs["GE-ET"].qid, Answer("other", edits={FIELD_PREREQ: bad}, reason="r"))
        assert refused["written"] == 0 and refused["errors"], bad
    assert ws.ledger.read_bytes() == before


def test_prerequisite_answers_are_refused_when_they_say_nothing_or_nothing_changes(env):
    ws, session, *_ = env
    qs = prereq_questions(session)
    cases = [
        (qs["CS 1"], Answer("other", reason="r")),                                        # Other with nothing typed
        (qs["CS 1"], Answer("other", edits={FIELD_PREREQ: ""}, reason="r")),              # blank to blank is a Yes
        (qs["CC 3/L"], Answer("other", edits={FIELD_PREREQ: "CC 2/L"}, reason="r")),      # same as printed
        (qs["CS 1"], Answer("other", edits={FIELD_PREREQ: "CS 2"})),                      # a correction needs a reason
        (qs["CS 1"], Answer("no")),                                                       # No needs a reason
        (qs["CS 1"], Answer("yes", edits={FIELD_PREREQ: "CS 2"})),                        # Yes carries no value
        (qs["CS 1"], Answer("other", edits={"course_title": "x"}, reason="r")),           # only prerequisites_raw here
        (qs["CS 1"], Answer("other", edits={FIELD_PREREQ: "CS 2"}, proposals=["a"], reason="r")),
    ]
    for question, answer in cases:
        result = session.answer(question.qid, answer)
        assert result["written"] == 0 and result["errors"], (question.qid, answer)
    assert not ws.ledger.exists()


def test_no_on_prerequisite_writes_unresolved_and_the_question_stays_open(env):
    ws, session, *_ = env
    q = prereq_questions(session)["GE-ET"]
    assert session.answer(q.qid, Answer("no", reason="cannot tell from the page"), now=rf.NOW)["errors"] == []
    (line,) = read_entries(ws.ledger)
    assert (line["field"], line["disposition"], line["new_value"]) == (FIELD_PREREQ, "unresolved", None)
    again = prereq_questions(session)["GE-ET"]
    assert not again.decided and again.decision["disposition"] == "unresolved"
    assert any(x.qid == again.qid for x in order_queue(session.questions()))
    assert session.state()["content_review"]["unresolved"] == 1   # B2 rule, unchanged: an unresolved decision on any field keeps the state partial


def test_a_prerequisite_answer_never_changes_a_course_question_or_a_section_yes(env):
    _ws, session, *_ = env
    session.answer(prereq_questions(session)["CS 1"].qid, Answer("other", edits={FIELD_PREREQ: "CS 2"}, reason="r"), now=rf.NOW)
    course_q = next(q for q in session.questions() if q.kind == "course" and q.reference["code"] == "CS 1")
    assert course_q.decision is None and not course_q.decided
    confirm = session.answer("S1:confirm", Answer("yes"), now=rf.NOW)
    assert confirm["errors"] == [] and confirm["written"] >= 1   # the section Yes still covers CS 1


def test_state_badges_come_from_the_ledger_not_the_payload(env):
    ws, session, client, token = env
    before = hashlib.sha256(ws.candidate.read_bytes()).hexdigest()
    assert ws.payload["content_review"] == "pending"
    state = client.get("/api/state").json()
    assert state["content_review"]["state"] == "pending"
    words = {s["name"]: s["word"] for s in state["review_states"]}
    assert set(words) == {"extraction audit", "content review", "source verification"}
    assert words["content review"] == "pending" and words["source verification"] == "pending"
    assert state["approval_line"] == "A reviewed prospectus is not an approved curriculum"
    first = next(q for q in session.queue("print") if q.kind == "course")
    post = client.post("/api/answer", content=json.dumps({"qid": first.qid, "choice": "yes", "reason": "checked"}),
                       headers={"X-Review-Token": token, "Content-Type": "application/json"})
    assert post.status_code == 200
    assert post.json()["state"]["content_review"]["state"] == "partially_reviewed"
    for q in session.queue("print"):
        if q.kind not in (PREREQUISITE, "section_confirm"):
            result = session.answer(q.qid, Answer("yes", reason="checked"))
            assert result["errors"] == [], (q.qid, result)
    live = client.get("/api/state").json()
    assert live["content_review"]["state"] == "reviewed"
    assert {s["name"]: s["word"] for s in live["review_states"]}["content review"] == "reviewed"
    assert live["prerequisites"] == {"questions": 3, "decided": 0, "unclassified_courses": 0}
    assert hashlib.sha256(ws.candidate.read_bytes()).hexdigest() == before        # the payload file is untouched
    assert json.loads(ws.candidate.read_text(encoding="utf-8"))["content_review"] == "pending"


def test_prerequisite_question_view_shows_the_course_and_materialise_stamps_reviewed_empty(env):
    ws, session, client, _token = env
    q = prereq_questions(session)["CS 1"]
    view = client.get(f"/api/question/{q.qid}").json()
    assert view["question"]["kind"] == PREREQUISITE and view["course"]["course"]["course_code"] == "CS 1"
    session.answer(q.qid, Answer("yes"), now=rf.NOW)
    result = session.materialise()
    corrected = json.loads(ws.review.joinpath(result["file"]).read_text(encoding="utf-8"))
    assert {c["course_code"]: c["prerequisite_state"] for c in corrected["courses"]}["CS 1"] == "reviewed_empty"
    assert json.loads(ws.candidate.read_text(encoding="utf-8"))["courses"][0]["prerequisite_state"] == "blank_unreviewed"


def test_a_stale_prerequisite_decision_reopens_the_question(env, tmp_path):
    ws, session, *_ = env
    session.answer(prereq_questions(session)["CS 1"].qid, Answer("yes"), now=rf.NOW)
    session.close()
    changed = with_states()
    changed["courses"][0]["prerequisites_raw"] = "CS 9"          # a re-run of the extractor read something else
    changed["courses"][0]["prerequisite_state"] = "unresolved_reference"
    ws2 = rf.workspace(tmp_path, changed, folder="work2")
    ws2.review.mkdir(parents=True)
    ws2.ledger.write_bytes(ws.ledger.read_bytes())
    with open_session(ws2.candidate, ws2.identity, "Nestor", ws2.review) as again:
        q = prereq_questions(again)["CS 1"]
        assert not q.decided and q.prompt.startswith('Is the prerequisite "CS 9"')
        assert again.state()["content_review"]["stale_entries"] == 1


def test_page_and_script_carry_the_approval_line_and_the_three_state_words():
    from backend.bintanong_tools.prospectus_review_gui.app import STATIC
    page = (STATIC / "index.html").read_text(encoding="utf-8")
    script = (STATIC / "review.js").read_text(encoding="utf-8")
    assert "A reviewed prospectus is not an approved curriculum" in page and 'id="approval"' in page
    assert "state.review_states" in script and "state.approval_line" in script
    assert 'kind === "prerequisite"' in script   # an empty prerequisite is sent: it is the answer "none"

def test_prerequisite_yes_and_other_never_hold_back_reviewed(env):
    _ws, session, *_ = env
    for q in session.queue("print"):
        if q.kind not in (PREREQUISITE, "section_confirm"):
            assert session.answer(q.qid, Answer("yes", reason="checked"))["errors"] == []
    qs = prereq_questions(session)
    assert session.answer(qs["CS 1"].qid, Answer("yes"), now=rf.NOW)["errors"] == []
    assert session.answer(qs["CC 3/L"].qid, Answer("other", edits={FIELD_PREREQ: "CC 2/L, CS 1"}, reason="read from the PDF"), now=rf.NOW)["errors"] == []
    state = session.state()
    assert state["content_review"]["state"] == "reviewed"
    assert state["prerequisites"] == {"questions": 3, "decided": 2, "unclassified_courses": 0}

def test_badge_text_does_not_claim_prerequisites_never_hold_back_review():
    from backend.bintanong_tools.prospectus_review_gui.app import STATIC
    for name in ("review.js", "index.html"):
        text = (STATIC / name).read_text(encoding="utf-8")
        assert "never hold back" not in text.replace("Yes and Other never hold back content review; a No does", ""), name
    script = (STATIC / "review.js").read_text(encoding="utf-8")
    assert "Yes and Other never hold back content review; a No does" in script


def test_a_prerequisite_no_holds_back_review_but_yes_and_other_do_not(env):
    _ws, session, *_ = env
    for q in session.queue("print"):
        if q.kind not in (PREREQUISITE, "section_confirm"):
            assert session.answer(q.qid, Answer("yes", reason="checked"))["errors"] == []
    qs = prereq_questions(session)
    assert session.answer(qs["CS 1"].qid, Answer("yes"), now=rf.NOW)["errors"] == []
    assert session.state()["content_review"]["state"] == "reviewed"
    assert session.answer(qs["GE-ET"].qid, Answer("no", reason="cannot tell"), now=rf.NOW)["errors"] == []
    assert session.state()["content_review"]["state"] == "partially_reviewed"
    assert session.state()["content_review"]["unresolved"] == 1
